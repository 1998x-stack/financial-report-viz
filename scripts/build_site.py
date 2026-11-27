#!/usr/bin/env python3
"""Build a multi-issuer static financial-report publication (stdlib only)."""
from __future__ import annotations

import json
import os
import shutil
import sys
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SRC = ROOT / "src"
BASE_URL = "https://1998x-stack.github.io/financial-report-viz/"
GITHUB = "https://github.com/1998x-stack/financial-report-viz"
sys.path.insert(0, str(ROOT))
from src.charts import build_figures  # noqa: E402
from src.concepts import build_glossary  # noqa: E402

PAGES = []
KINDS = [("sectors", "sector", "行业"), ("markets", "market", "上市市场"),
         ("periods", "period_type", "报告期间"), ("topics", "topics", "研究主题")]


def H(x):
    return escape(str(x), quote=True)


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def template(template_name, **data):
    source = (SRC / "templates" / (template_name + ".html")).read_text(encoding="utf-8")
    return Template(source).substitute(data)


def mkdir_file(relative, content):
    dest = DIST / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return dest


def link(page, dest):
    path = os.path.relpath(DIST / dest, start=(DIST / page).parent)
    return path.replace(os.sep, "/")


def canonical(relative):
    if relative.endswith("index.html"):
        relative = relative[:-10]
    return BASE_URL + relative


def page(relative, title, description, content, structured=None):
    # HTML and schema JSON-LD render into independent static files.
    jsonld = ""
    if structured is not None:
        payload = json.dumps(structured, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        jsonld = '<script type="application/ld+json">' + payload + "</script>"
    rendered = template(
        "layout", page_title=H(title), description=H(description),
        canonical=H(canonical(relative)), css_path=H(link(relative, "assets/site.css")),
        js_path=H(link(relative, "assets/site.js")),
        home_path=H(link(relative, "index.html")),
        reports_path=H(link(relative, "reports/index.html")),
        companies_path=H(link(relative, "companies/index.html")),
        source_repo=GITHUB, jsonld=jsonld, content=content,
        concepts_path=H(link(relative,"concepts/index.html")),
        concepts_css=H(link(relative,"assets/concepts.css")),
        concepts_js=H(link(relative,"assets/concepts.js"))
    )
    mkdir_file(relative, rendered)
    PAGES.append(relative)


def source_link(report, page_num=None):
    url = report["source"]["url"]
    if page_num is not None:
        url += "#page=" + str(page_num + report["source"]["pdf_page_offset"])
    return H(url)


def pages_html(report, pages):
    return '<div class="source-links">' + " ".join(
        '<a href="' + source_link(report, p) + '" target="_blank" rel="noopener noreferrer">'
        '来源 p.' + str(p) + " ↗</a>" for p in sorted(set(pages))) + "</div>"


def published(report):
    return report.get("status") == "published"


def record_search(report, issuer, taxonomy):
    terms = [issuer["name"], issuer["legal_name"], issuer["ticker"],
             report["year"], report["period_type"], report["title"]]
    lookup = {x["id"]: x["name"] for x in taxonomy["topics"]}
    terms.extend(lookup.get(t, t) for t in report["topics"])
    return " ".join(map(str, terms))


def card(report, issuer, page_path, taxonomy):
    dest = f'reports/{report["issuer_id"]}/{report["slug"]}/index.html'
    url = H(link(page_path, dest))
    search = H(record_search(report, issuer, taxonomy))
    period = "上半年" if report["period_type"] == "h1" else report["period_type"].upper()
    return (
        '<a class="report-card" data-search="' + search + '" href="' + url + '">'
        '<div class="report-card-top"><span class="flag">' + H(issuer["market"].upper()) + " · " + H(issuer["ticker"]) +
        '</span><span>' + str(report["year"]) + " " + H(period) + '</span></div>'
        '<h3>' + H(report["title"]) + '</h3><p>' + H(report["description"]) + '</p>'
        '<div class="report-card-bottom"><span>' + H(issuer["name"]) +
        ' · 原始 PDF 可核验</span><b aria-hidden="true">↗</b></div></a>'
    )


def category_target(kind, slug):
    return f"categories/{kind}/{slug}/index.html"


def facet_matches(report, issuer, kind, ident):
    if kind == "sectors":
        return issuer["sector"] == ident
    if kind == "markets":
        return issuer["market"] == ident
    if kind == "periods":
        return report["period_type"] == ident
    return ident in report["topics"]


def taxonomy_entries(reports, issuers, taxonomy):
    result = []
    for kind, _field, label in KINDS:
        for item in taxonomy[kind]:
            matches = [r for r in reports if facet_matches(r, issuers[r["issuer_id"]], kind, item["id"])]
            if matches:
                result.append((kind, label, item, matches))
    return result


def yoy(metric):
    prev, curr = metric["values"]["prior"], metric["values"]["current"]
    if prev is None or curr is None or prev <= 0 or curr < 0:
        return None
    return (curr / prev - 1) * 100


def yoy_label(pct):
    return "—" if pct is None else ("+" if pct >= 0 else "") + f"{pct:.1f}%"


def money(v, unit="CNY_thousand"):
    divisor = 100 if unit == "CNY_million" else 100000
    return f"{v / divisor:,.2f}"


def kpi_cards(report):
    v = report["values"]
    if report["issuer_id"] == "moutai":
        def mv(k,p="current"): return v[k]["values"][p]
        def item(label,k,note):
            m=v[k]; val=mv(k)/10000000000
            change=yoy_label(yoy(m))
            return (f'<div class="kpi-card"><span class="label">{H(label)}</span>'
                    f'<strong>{val:,.2f}<small style="display:inline;font-size:13px;margin-left:5px">亿元</small></strong>'
                    f'<span class="change {"neg" if change.startswith("-") else ""}">{H(change)}</span><small>{H(note)}</small></div>')
        margin=lambda p:(1-mv("cost_of_revenue",p)/mv("revenue",p))*100
        delta=margin("current")-margin("prior")
        return (item("营业收入","revenue","2026年1—9月 · 同比")
                +item("归母净利润","parent_profit","2026年1—9月 · 同比")
                +f'<div class="kpi-card"><span class="label">营业毛利率（计算）</span><strong>{margin("current"):.2f}%</strong><span class="change neg">{delta:+.2f} pp</span><small>收入减成本 / 收入，不含金融利息</small></div>'
                +item("经营现金流净额","operating_cash_flow","含集团财务公司业务"))
    if report["issuer_id"] == "tencent":
        unit = report["unit"]
        signals = [
            ("营业收入", money(v["revenue"]["values"]["current"],unit), "亿元",
             yoy_label(yoy(v["revenue"])), "2026 Q3 · 同比2025 Q3"),
            ("IFRS归母净利润", money(v["attributable_profit"]["values"]["current"],unit), "亿元",
             yoy_label(yoy(v["attributable_profit"])), "报告准则利润；非调整口径"),
            ("Non-IFRS经营利润", money(v["non_ifrs_operating_profit"]["values"]["current"],unit), "亿元",
             yoy_label(yoy(v["non_ifrs_operating_profit"])), "经调整；不同于IFRS经营利润"),
            ("应计资本开支", money(v["accrual_capex"]["values"]["current"],unit), "亿元",
             yoy_label(yoy(v["accrual_capex"])), "非资本开支现金付款额")
        ]
        return "".join(
            f'<div class="kpi-card"><span class="label">{H(name)}</span>'
            f'<strong>{H(value)}<small style="display:inline;font-size:13px;margin-left:5px">{H(unit_name)}</small></strong>'
            f'<span class="change {"neg" if change.startswith("-") else ""}">{H(change)}</span><small>{H(foot)}</small></div>'
            for name,value,unit_name,change,foot in signals
        )
    growth = yoy(v["revenue"])
    margin = lambda term, p: v[term]["values"][p] / v["revenue"]["values"][p] * 100
    m_curr, m_prior = margin("gross_profit", "current"), margin("gross_profit", "prior")
    signal = [
        ("营业收入", money(v["revenue"]["values"]["current"]), "亿元", yoy_label(growth),
         "同比 · 同期 6 个月"),
        ("期内利润", money(v["period_profit"]["values"]["current"]), "亿元",
         yoy_label(yoy(v["period_profit"])), "IFRS 报告利润"),
        ("毛利率", f"{m_curr:.1f}", "%", f"{m_curr-m_prior:+.1f} pp", "按毛利润 / 收入计算"),
        ("经营现金流", money(v["operating_cash_flow"]["values"]["current"]), "亿元",
         yoy_label(yoy(v["operating_cash_flow"])), "经营活动现金净额")
    ]
    output = []
    for name, value, unit, change, foot in signal:
        cls = "neg" if change.startswith("-") else ""
        output.append(
            f'<div class="kpi-card"><span class="label">{H(name)}</span>'
            f'<strong>{H(value)}<small style="display:inline;font-size:13px;margin-left:5px">{H(unit)}</small></strong>'
            f'<span class="change {cls}">{H(change)}</span><small>{H(foot)}</small></div>'
        )
    return "".join(output)


def figures_markup(report, report_path):
    asset_folder = DIST / Path(report_path).parent / "assets"
    if report["issuer_id"] == "moutai":
        from src.moutai import charts
        figure_list = charts(report, asset_folder)
    else:
        figure_list = build_figures(report, asset_folder)
    parts = []
    for i, fig in enumerate(figure_list, 1):
        p = fig["filename"]
        img = H(link(report_path, str(Path(report_path).parent / "assets" / p)))
        parts.append(
            f'<figure class="figure-card" id="figure-{H(fig["slug"])}">'
            f'<p class="kicker">FIGURE {i:02d} / SOURCE-ALIGNED SVG</p>'
            f'<h3>{H(fig["title"])}</h3><p>{H(fig["caption"])}</p>'
            f'<div class="figure-scroll"><img loading="lazy" src="{img}" '
            f'alt="{H(fig["title"] + "。图中数值均来自财报，详见来源页和下方数据表。")}" '
            f'width="{fig.get("width",1040)}" height="{fig.get("height",426)}"></div>'
            f'<figcaption>{H(fig["caption"])}。所有图表均不使用外部市场估值数据。</figcaption>'
            + pages_html(report, fig["pages"]) + "</figure>"
        )
    return "".join(parts)


def metric_tables(report):
    if report["issuer_id"] == "moutai":
        rows=[]
        for key,m in report["values"].items():
            a,b=m["source_values"]["prior"],m["source_values"]["current"]
            unit="万元" if m["source_unit"]=="CNY_10000" else "元"
            change=yoy_label(yoy(m)) if m["comparison"]=="2025/2026 Jan-Sep" else "—"
            rows.append(
                f'<tr data-metric-row="{H(m["label"]+" "+key)}"><th scope="row">{H(m["label"])}</th>'
                f'<td>{H(a if a is not None else "—")}</td><td>{H(b if b is not None else "—")}</td>'
                f'<td>{H(unit)}</td><td>{H(m["comparison"])}</td><td>{change}</td>'
                f'<td><a href="{source_link(report,m["page"])}" target="_blank" rel="noopener noreferrer">p.{m["page"]}</a></td></tr>')
        return ('<div class="table-wrap"><table><caption>财报原始精确数值 · 金额不预先四舍五入</caption>'
            '<thead><tr><th>项目</th><th>比较期</th><th>本期</th><th>单位</th><th>比较口径</th><th>变化</th><th>财报页码</th></tr></thead><tbody>'
            + "".join(rows)+"</tbody></table></div>")
    finance, users = [], []
    term = "H1" if report["period_type"] == "h1" else report["period_type"].upper()
    prior_label = str(report["year"]-1)+" "+term
    current_label = str(report["year"])+" "+term
    for key, m in report["values"].items():
        target = users if m.get("unit") in ("thousand_users","million_users") else finance
        unit = {"thousand_users":"千人","million_users":"百万人"}.get(m.get("unit"),report["unit_display"])
        a, b = m["values"]["prior"], m["values"]["current"]
        if a is None or b is None:
            change = "—"
        else:
            change = yoy_label(yoy(m))
        pg = m["page"]
        priorpg = m.get("pages", {}).get("prior", pg)
        currpg = m.get("pages", {}).get("current", pg)
        def v(x):
            return "—" if x is None else f"{x:,.0f}"
        target.append(
            f'<tr data-metric-row="{H(m["label"] + " " + key)}">'
            f'<th scope="row">{H(m["label"])}</th><td>{v(a)}</td><td>{v(b)}</td>'
            f'<td>{H(change)}</td><td><a href="{source_link(report,currpg)}" '
            f'target="_blank" rel="noopener noreferrer">p.{currpg}</a>'
            f' / <a href="{source_link(report,priorpg)}" '
            f'target="_blank" rel="noopener noreferrer">p.{priorpg}</a></td></tr>'
        )
    output = []
    for title, rows, unit in (
        ("合并财务与业务分部", finance, report["unit_display"]),
        ("用户运营指标", users, "百万人" if report["issuer_id"]=="tencent" else "千人"),
    ):
        output.append(
            '<div class="table-wrap"><table>'
            '<caption>' + H(title) + " · " + H(unit) + '</caption>'
            '<thead><tr><th scope="col">项目</th><th scope="col">' + H(prior_label) + '</th>'
            '<th scope="col">' + H(current_label) + '</th><th scope="col">同比</th>'
            '<th scope="col">原文页码 (2026 / 2025)</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>"
        )
    return "".join(output)


def report_page(report, issuer, tax):
    path = f'reports/{report["issuer_id"]}/{report["slug"]}/index.html'
    lookup = {item["id"]:item["name"] for item in tax["markets"]}
    issues = []
    for i, item in enumerate(report["narrative"]["findings"], 1):
        issues.append(
            f'<section class="insight-card"><small>OBSERVATION {i:02d}</small>'
            f'<h3>{H(item["title"])}</h3><p>{H(item["body"])}</p>'
            + pages_html(report, item["pages"]) + "</section>"
        )
    period = str(report["year"]) + (" H1" if report["period_type"] == "h1" else (" Q3 · 1—9月累计" if report["issuer_id"] == "moutai" else " Q3"))
    content = template(
        "report", home_href=H(link(path, "index.html")),
        issuer_href=H(link(path, f'companies/{report["issuer_id"]}/index.html')),
        issuer_name=H(issuer["name"]), ticker=H(issuer["ticker"]),
        market=H(lookup.get(issuer["market"],issuer["market"])),
        period_label=H(period), eyebrow=H(report["narrative"]["eyebrow"]),
        title=H(report["title"]), lead=H(report["narrative"]["lead"]),
        source_href=source_link(report), source_title=H(report["source"]["title"]),
        assurance_label=H({"reviewed_unaudited":"经审阅 · 未经审计","audited":"已经审计","unaudited":"未经审计","unknown":"审计状态未确认"}.get(report["source"]["assurance"],"未确认")),
        currency_label=H(report["currency"]),source_unit=H(report["unit_display"]),
        comparison_text=H(report["comparison_period_start"]+" 至 "+report["comparison_period_end"]+" / "+report["period_start"]+" 至 "+report["period_end"]),
        accounting_text=H(report["source"]["statement"]),
        approval_text=H(("公告发布日期："+report["publication_date"]+"；未经审计中期财务资料已由核数师审阅。") if report.get("publication_date") else (("批准／审阅日："+report["review_approval_date"]+"；不得与公开发布日期混同。") if report.get("review_approval_date") else "报告批准日未明确。")),
        kpi_cards=kpi_cards(report), insight_cards="".join(issues),
        figures=figures_markup(report,path), metric_tables=metric_tables(report)
    )
    if report.get("analysis_sections"):
        chapters=['<section class="block" id="deep-analysis"><div class="section-head"><div><p class="kicker">04 / DEEP RESEARCH</p><h2>调查笔记：数据驱动的投资问题</h2><p>先列可核算事实，再明确管理层解释、分析推论与尚未披露的信息。</p></div></div>']
        for idx,section in enumerate(report["analysis_sections"],1):
            chapters.append('<div class="figure-card"><p class="kicker">RESEARCH NOTE '+f'{idx:02d}'+'</p><h3>'+H(section["heading"])+'</h3>')
            for paragraph in section["body"]:
                chapters.append('<p style="font-size:14px;color:#334c50;line-height:1.95">'+H(paragraph)+'</p>')
            chapters.append(pages_html(report,section["pages"])+'</div>')
        chapters.append('</section>')
        content=content.replace('<section class="block" id="source-table">',"".join(chapters)+'<section class="block" id="source-table">')
        content=content.replace('<a href="#source-table">财务表格</a>', '<a href="#deep-analysis">深度研究</a><a href="#source-table">财务表格</a>')
    if report.get("research_context"):
        blocks=['<section class="block" id="research-context"><div class="section-head"><div><p class="kicker">CONTEXT / ATTRIBUTED COMMENTARY</p><h2>行业与外部研究视角</h2><p>仅作为外部观点，不属于公司公告事实；不得直接代替实证判断。</p></div></div><div class="method-grid">']
        for q in report["research_context"]:
            blocks.append('<div><h3><a target="_blank" rel="noopener noreferrer" href="'+H(q["url"])+'">'+H(q.get("title","外部研究"))+'</a></h3><p>'+H(q["note"])+'</p></div>')
        blocks.append('</div></section>')
        content=content.replace('</article>',"".join(blocks)+'</article>')
    if report.get("external_research"):
        research = ['<section class="block" id="external-research"><div class="section-head"><div><p class="kicker">06 / INDEPENDENT CONTEXT</p><h2>外部调查与反证</h2><p>第三方资料并非港交所披露；只用于对照市场预期及管理层问答。</p></div></div><div class="method-grid">']
        for ext in report["external_research"]:
            research.append('<div><h3><a target="_blank" rel="noopener noreferrer" href="'+H(ext["url"])+'">'+H(ext["label"])+'</a></h3><p>'+H(ext["publisher"])+' · '+H(ext["date"])+'</p><p>'+H(ext["note"])+'</p></div>')
        research.append('</div><p>本研究的判断属于分析而非管理层指引。财报未单独披露云服务营收规模或AI新品单项损益，故不外推。</p></section>')
        content += "".join(research)
    structured = {
        "@context":"https://schema.org","@type":"Article",
        "headline":report["title"],"description":report["description"],
        "inLanguage":report["language"],"isAccessibleForFree":True,
        "mainEntityOfPage":canonical(path),"citation":report["source"]["url"],
        "about":{"@type":"Organization","name":issuer["legal_name"]},
        "publisher":{"@type":"Organization","name":"Financial Report Atlas"}
    }
    if report.get("publication_date"):
        structured["datePublished"] = report["publication_date"]
    page(path,report["title"],report["description"],content,structured)


def main():
    from scripts.validate_data import validate_all
    errors = validate_all()
    if errors:
        raise SystemExit("Dataset failed validation:\n" + "\n".join(errors))
    taxonomy = load("data/taxonomy.json")
    issuers = {}
    for f in sorted((ROOT / "data/issuers").glob("*.json")):
        r=json.loads(f.read_text(encoding="utf-8"))
        issuers[r["id"]] = r
    reports = []
    for f in sorted((ROOT / "data/reports").glob("*/*.json")):
        item = json.loads(f.read_text(encoding="utf-8"))
        if published(item):
            reports.append(item)
    reports.sort(key=lambda r: (r["period_end"],r["report_id"]),reverse=True)
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST/"assets").mkdir(parents=True)
    shutil.copy2(SRC/"static/site.css",DIST/"assets/site.css")
    shutil.copy2(SRC/"static/site.js",DIST/"assets/site.js")
    shutil.copy2(SRC/"static/concepts.css",DIST/"assets/concepts.css")
    shutil.copy2(SRC/"static/concepts.js",DIST/"assets/concepts.js")
    (DIST/".nojekyll").write_text("",encoding="utf-8")

    facets = taxonomy_entries(reports,issuers,taxonomy)
    report_cards = lambda where, data: "".join(card(r,issuers[r["issuer_id"]],where,taxonomy) for r in data)
    chosen = reports[0]
    latest_url=f'reports/{chosen["issuer_id"]}/{chosen["slug"]}/index.html'
    facet_cards=[]
    for kind,kind_label,item,matches in facets[:9]:
        target=category_target(kind,item["id"])
        facet_cards.append(
            f'<a class="facet-card" href="{H(link("index.html",target))}">'
            f'<span>{H(kind_label)} / {len(matches)} 篇<i aria-hidden="true">↗</i></span>'
            f'<strong>{H(item["name"])}</strong><small>{H(item["description"])}</small></a>')
    growth = yoy(chosen["values"]["revenue"])
    homepage = template(
        "home",featured_href=H(link("index.html",latest_url)),
        reports_href=H(link("index.html","reports/index.html")),
        report_cards=report_cards("index.html",reports[:6]),
        report_count=len(reports),issuer_count=len({r["issuer_id"] for r in reports}),
        market_count=len({issuers[r["issuer_id"]]["market"] for r in reports}),
        facet_cards="".join(facet_cards), lead_growth_value=f"{growth:.1f}",
        source_repo=GITHUB,
        glossary_href=H(link("index.html","concepts/index.html")),
        glossary_count=len(load("data/concepts.json")["concepts"])
    )
    page("index.html","有来源的上市公司财报可视化","源自公开财报的可视化研究，按公司、行业和市场持续归档。",homepage,
         {"@context":"https://schema.org","@type":"CollectionPage",
          "name":"Financial Report Atlas","url":BASE_URL})
    def facetlinks(where):
        return " ".join(f'<a href="{H(link(where,category_target(kind,item["id"])))}">{H(item["name"])}</a>'
                        for kind,_label,item,_matches in facets)
    archive="reports/index.html"
    page(archive,"全部财报","本站已经标准化核对并收录的上市公司财报研究档案。",
         template("listing",heading="全部财报研究",intro="从报告期、公司、行业与主题出发，浏览已完成原始披露校验的研究。",
                  report_cards=report_cards(archive,reports),facet_links=facetlinks(archive)))
    companies="companies/index.html"
    company_cards=[]
    for company_id,issuer in sorted(issuers.items()):
        if not any(r["issuer_id"]==company_id for r in reports):continue
        card_link=link(companies,f"companies/{company_id}/index.html")
        company_cards.append(
            f'<a class="report-card" data-search="{H(issuer["name"]+" "+issuer["ticker"])}" href="{H(card_link)}">'
            f'<div class="report-card-top"><span class="flag">{H(issuer["market"].upper())}</span><span>{H(issuer["ticker"])}</span></div>'
            f'<h3>{H(issuer["name"])}</h3><p>{H(issuer["description"])}</p>'
            f'<div class="report-card-bottom"><span>公司档案</span><b aria-hidden="true">↗</b></div></a>'
        )
    page(companies,"公司目录","已收录公司名单与财报档案。",
         template("listing",heading="公司目录",intro="每家公司对应一个独立档案页，后续各期报告沿用相同公司 ID。",
                  report_cards="".join(company_cards),facet_links=facetlinks(companies)))
    for issuer_id,issuer in issuers.items():
        subset=[r for r in reports if r["issuer_id"]==issuer_id]
        if not subset:continue
        where=f"companies/{issuer_id}/index.html"
        mk=next((x["name"] for x in taxonomy["markets"] if x["id"]==issuer["market"]),issuer["market"])
        se=next((x["name"] for x in taxonomy["sectors"] if x["id"]==issuer["sector"]),issuer["sector"])
        body=template("issuer",ticker=H(issuer["ticker"]),name=H(issuer["name"]),
                      description=H(issuer["description"]),market=H(mk),sector=H(se),
                      country=H(issuer["country"]),report_cards=report_cards(where,subset))
        page(where,issuer["name"]+" · 公司档案",issuer["description"],body)
    for kind,kindlabel,item,matches in facets:
        where=category_target(kind,item["id"])
        body=template("listing",heading=H(item["name"]),intro=H(item["description"]+" · 已收录 "+str(len(matches))+" 篇报告"),
                      report_cards=report_cards(where,matches),facet_links=facetlinks(where))
        page(where,item["name"]+" · 财报分类",item["description"],body)
    for report in reports:
        report_page(report,issuers[report["issuer_id"]],taxonomy)
    concept_pages=build_glossary(
        data_path=ROOT/"data/concepts.json",output_dir=DIST,template=template,
        page=page,link=link,canonical=canonical,H=H
    )
    catalog=[]
    for report in reports:
        issuer=issuers[report["issuer_id"]]
        catalog.append(dict(
            report_id=report["report_id"],title=report["title"],
            issuer=issuer["name"],issuer_id=issuer["id"],ticker=issuer["ticker"],
            market=issuer["market"],sector=issuer["sector"],topics=report["topics"],
            year=report["year"],period=report["period_type"],period_end=report["period_end"],
            url=canonical(f'reports/{report["issuer_id"]}/{report["slug"]}/index.html'),
            source_url=report["source"]["url"]
        ))
    mkdir_file("catalog.json",json.dumps({"schema_version":"1","reports":catalog},
                                        ensure_ascii=False,indent=2)+"\n")
    urls=[BASE_URL]+[canonical(p) for p in PAGES if p!="index.html"]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap+="".join("  <url><loc>"+H(u)+"</loc></url>\n" for u in urls)+"</urlset>\n"
    mkdir_file("sitemap.xml",sitemap)
    mkdir_file("robots.txt","User-agent: *\nAllow: /\nSitemap: "+BASE_URL+"sitemap.xml\n")
    print(f"PASS: generated {len(PAGES)} pages, {len(reports)} reports, {len(issuers)} issuers, {concept_pages} concept HTMLs")


if __name__ == "__main__":
    main()
