"""US-dollar Tesla report widgets and grounded research context."""
from html import escape

def H(s):return escape(str(s),quote=True)
def metric(r,k,p="current"):return r["values"][k]["values"][p]
def yoy(r,k):
    a,b=metric(r,k,"prior"),metric(r,k)
    return None if a in (None,0) or b is None else (b/a-1)*100
def pctlabel(v):return "—" if v is None else f"{v:+.1f}%"

def kpi_cards(report):
    keys=[
       ("营业收入","revenue","业务营收 · GAAP"),
       ("GAAP 归母净利润","attributable_profit","普通股股东应占利润"),
       ("营业利润","operating_profit","经营利润，不等于现金流"),
       ("自由现金流","free_cash_flow","经营现金流 − 资本开支")
    ]
    html=[]
    for label,key,note in keys:
        current=metric(report,key)
        growth=yoy(report,key)
        tag=pctlabel(growth)
        cls="neg" if tag.startswith("-") else ""
        html.append(f'<div class="kpi-card"><span class="label">{H(label)}</span>'
                    f'<strong>{current/1000:,.2f}<small style="display:inline;font-size:13px;margin-left:5px">十亿美元</small></strong>'
                    f'<span class="change {cls}">{H(tag)}</span><small>{H(note)}</small></div>')
    return "".join(html)

def metric_tables(report,source_link):
    finance=[];operations=[]
    for key,item in report["values"].items():
        unit=item.get("unit","USD_million")
        target=finance if unit=="USD_million" else operations
        labels={"USD_million":"百万美元","vehicles":"辆","million_subscriptions":"百万活跃订阅",
          "GWh":"GWh","days":"天","stations":"座","connectors":"个"}
        a,b=item["values"]["prior"],item["values"]["current"]
        diff=pctlabel(yoy(report,key)) if a is not None and b is not None and a>0 else "—"
        def f(v):
            if v is None:return "—"
            return f"{v:,.2f}" if isinstance(v,float) else f"{v:,}"
        pg=item["page"]
        target.append(f'<tr data-metric-row="{H(item["label"]+" "+key)}">'
          f'<th scope="row">{H(item["label"])}</th><td>{f(a)}</td><td>{f(b)}</td>'
          f'<td>{H(labels.get(unit,unit))}</td><td>{H(diff)}</td>'
          f'<td><a href="{source_link(report,pg)}" target="_blank" rel="noopener noreferrer">p.{pg}</a></td></tr>')
    out=[]
    for title,rows in (("合并财务与资产负债（原始百万美元）",finance),("运营指标（独立原始单位）",operations)):
        out.append('<div class="table-wrap"><table><caption>'+H(title)+'</caption>'
        '<thead><tr><th scope="col">指标</th><th scope="col">2025 Q3</th>'
        '<th scope="col">2026 Q3</th><th scope="col">原始单位</th>'
        '<th scope="col">同比</th><th scope="col">原文</th></tr></thead><tbody>'
        +"".join(rows)+'</tbody></table></div>')
    return "".join(out)

def research_block(report):
    consensus=report["consensus"]
    rows=[]
    for item in consensus["items"]:
        actual=item["actual"]
        expected=item["mean"]
        gap=actual-expected
        rows.append(f'<tr><th scope="row">{H(item["label"])}</th><td>{expected:,.0f}</td>'
                    f'<td>{actual:,.0f}</td><td>{gap:+,.0f}</td></tr>')
    source_url=H(consensus["url"])
    sec=H("https://www.sec.gov/Archives/edgar/data/1318605/000162828026066775/tsla-20260930.htm")
    reuters=H("https://www.reuters.com/business/autos-transportation/tesla-drops-spending-pullback-clouds-ai-robotics-ambitions-2026-10-22/")
    return f"""
<section class="block" id="research-context">
 <div class="section-head"><div><p class="kicker">06 / RESEARCH CONTEXT</p>
 <h2>市场预期、经营分歧与下一季验证点</h2>
 <p>本节市场一致预期来自 2026-10-19 的 Tesla 投资者关系页面，并非业绩披露，也不代表特斯拉认可。</p></div></div>
 <div class="table-wrap"><table><caption>财报发布前一致预期 vs 实际 · 百万美元</caption>
 <thead><tr><th>指标</th><th>卖方平均预期</th><th>实际披露</th><th>实际 − 预期</th></tr></thead>
 <tbody>{''.join(rows)}</tbody></table></div>
 <p class="evidence-note">预期来源：<a href="{source_url}" rel="noopener noreferrer" target="_blank">Tesla 汇总的分析师预期（2026-10-19）</a>。
 仅作发布前预期对照，非股价预测，亦不保证各家统计方法一致。</p>
 <div class="research-grid">
 <div class="research-panel"><h3>较积极的证据</h3><p>剔除监管积分的汽车毛利率由 15.4% 升至 18.1%；
 服务及其他收入同比 +32.5%，季度 FSD 活跃订阅达到 174 万。储能部署 13.7 GWh，同比增长约 10%。</p></div>
 <div class="research-panel"><h3>需要警惕的风险</h3><p>总营收同比 -0.2%、营业利润 -55.8%；储能收入 -15.6% 与部署量正增长形成背离。
 管理层披露该业务收入受关税相关客户退款影响。Q3 资本开支同比翻倍，自由现金流同比 -61.6%。</p></div>
 <div class="research-panel"><h3>未来的可证伪问题</h3><p>观察 FSD 付费增长能否转化为可单独核验的利润；储能交付量增长能否转化为收入、毛利；
 资本开支转化为商业化现金流的速度；以及车辆交付与库存能否重新趋于平衡。</p></div>
 </div>
 <p class="evidence-note">独立核查：
 <a href="{sec}" target="_blank" rel="noopener noreferrer">SEC 2026 Q3 Form 10-Q</a>（经营、现金流、监管积分、资本开支与风险）；
 <a href="{reuters}" target="_blank" rel="noopener noreferrer">Reuters，2026-10-22</a>（对投资缩减的市场讨论，属外部评论而非发行人事实）。
 本文对管理层未来计划只做归因性引用，不视为已实现的收入或盈利。</p>
</section>
"""
