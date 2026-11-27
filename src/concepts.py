"""100-concept encyclopedia: education-only, standalone SVG, deterministic 101 HTML pages."""
from __future__ import annotations

import json
import math
from html import escape
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

COLORS=["#226e6a","#346b99","#b77d53","#7c8150","#8770a4","#b86758"]
INK="#243438"
MUTED="#657678"
PAPER="#fffdfa"
BORDER="#dce5de"


def h(v):
    return escape(str(v), quote=True)


def fmt(v):
    if abs(v-round(v))<1e-8:
        return f"{round(v):,}"
    return f"{v:,.1f}"


def node_text(x,y,text,size=20,color=INK,anchor="start",weight=500):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{h(text)}</text>')


def rect(x,y,w,hh,fill,stroke="none",radius=9,opacity=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" '
            f'height="{max(hh,0):.1f}" rx="{radius}" fill="{fill}" '
            f'stroke="{stroke}" opacity="{opacity}"/>')


def line(x1,y1,x2,y2,color=BORDER,width=2,dash=""):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')


def pill(x,y,label,color,fill="#f0f5f0"):
    size=max(114,14*len(label)+40)
    return rect(x,y,size,36,fill,color,18)+node_text(x+size/2,y+24,label,14,color,"middle",650)


def svg_balance(items,accent):
    total, a, b=[p["value"] for p in items]
    labels=[p["label"] for p in items]
    scale=240/max(total,1)
    parts=[]
    parts.append(node_text(264,142,"资源一侧",15,MUTED,"middle",650))
    parts.append(node_text(806,142,"资金来源一侧",15,MUTED,"middle",650))
    parts.append(rect(112,171,310,240,accent))
    parts.append(node_text(267,266,labels[0],24,"white","middle",650))
    parts.append(node_text(267,310,fmt(total),42,"white","middle",800))
    y=171
    for i,v in enumerate([a,b]):
        ht=v*scale
        color=["#dceae3","#f5dfc8"][i]
        parts.append(rect(651,y,310,ht-4,color,radius=5))
        parts.append(node_text(807,y+ht/2-6,labels[i+1],21,INK,"middle",650))
        parts.append(node_text(807,y+ht/2+27,fmt(v),25,INK,"middle",750))
        y+=ht
    parts.append(line(433,289,638,289,accent,3))
    parts.append(node_text(537,270,"＝",31,accent,"middle",750))
    return "".join(parts)


def svg_bridge(items,accent):
    start=items[0]["value"]
    mid=items[1:-1]
    end=items[-1]["value"]
    running=start
    positions=[start]
    for p in mid:
        running+=p["value"];positions.append(running)
    high=max(start,end,*positions,1)*1.15
    low=min(0,*positions)
    span=high-low
    top,bottom=163,375
    yy=lambda v:bottom-(v-low)/span*(bottom-top)
    yzero=yy(0)
    out=line(75,yzero,1035,yzero,BORDER,1.5)
    n=len(items);step=930/n;left=85
    running=start
    for i,p in enumerate(items):
        val=p["value"]
        if i==0 or i==n-1:
            bottom_val,top_val=0,val
        else:
            bottom_val,top_val=running,running+val
            running=top_val
        hi,lo=max(bottom_val,top_val),min(bottom_val,top_val)
        x=left+i*step+step*.17
        y=yy(hi)
        height=max(3,yy(lo)-yy(hi))
        color=accent if i==0 else "#308b7c" if i==n-1 else "#d07762" if val<0 else "#d8a456"
        out+=rect(x,y,step*.64,height,color,radius=4)
        out+=node_text(x+step*.32,y-14,("+" if i not in(0,n-1) and val>=0 else "")+fmt(val),
                       17,INK,"middle",750)
        out+=node_text(x+step*.32,405,p["label"],14,MUTED,"middle",650)
        if i!=n-1 and i!=0:
            nx=left+(i+1)*step+step*.17
            out+=line(x+step*.64,yy(running),nx,yy(running),"#adbeb4",1,"4 4")
    return out


def svg_compare(items,accent):
    values=[p["value"] for p in items]
    maxi=max(0,*values);mini=min(0,*values)
    spread=max(maxi-mini,1)
    top,bottom=154,369
    yy=lambda v:bottom-(v-mini)/spread*(bottom-top)
    zero=yy(0)
    out=line(75,zero,1035,zero,"#9caeaa",1.5)
    span=900/len(items)
    for i,p in enumerate(items):
        val=p["value"]
        x=93+i*span+span*.22
        topy=min(yy(val),zero)
        height=max(3,abs(yy(val)-zero))
        col=accent if val>=0 else "#c76b5b"
        out+=rect(x,topy,span*.55,height,col)
        ly=topy-12 if val>=0 else topy+height+22
        out+=node_text(x+span*.275,ly,fmt(val),22,INK,"middle",750)
        out+=node_text(x+span*.275,418,p["label"],15,MUTED,"middle",650)
    return out


def svg_stack(items,accent):
    values=[p["value"] for p in items]
    total=sum(values)
    out=node_text(77,156,"组成部分 / PARTS",15,MUTED,weight=700)
    out+=node_text(1002,156,"合计 "+fmt(total),21,accent,"end",750)
    x=77
    palette=[accent,"#76a99e","#d4aa67","#9b9bc2","#d77762"]
    for i,p in enumerate(items):
        width=925*p["value"]/total
        color=palette[i%len(palette)]
        out+=rect(x,188,width-4,116,color,radius=4)
        if width>=90:
            out+=node_text(x+width/2,236,p["label"],15,"white","middle",700)
            out+=node_text(x+width/2,270,f'{p["value"]/total*100:.1f}%',23,"white","middle",750)
        x+=width
    out+=line(77,331,1002,331)
    for i,p in enumerate(items):
        col=i%3
        row=i//3
        x=86+col*310
        y=364+row*45
        out+=rect(x,y-15,14,14,palette[i%len(palette)],radius=3)
        out+=node_text(x+23,y-2,p["label"]+"  "+fmt(p["value"]),16,INK)
    return out


def ratio_result(item):
    ident=item["id"]
    a,b=[p["value"] for p in item["diagram"]["items"][:2]]
    if ident=="market-cap":
        return fmt(a*b)+"（单位按示例说明）"
    result=a/b
    if ident in {"gross-margin","operating-margin","net-margin","cash-conversion",
                 "roe","roa","roic","dividend-payout","dividend-yield",
                 "debt-to-assets","effective-tax-rate"}:
        return f"{100*result:.1f}%"
    if ident in {"dso","dio","dpo"}:
        return f"{365*result:.1f} 天"
    if ident in {"eps","bvps"}:
        return f"{result:.2f} / 股（示意）"
    return f"{result:.2f} ×"


def svg_ratio(item,accent):
    a,b=item["diagram"]["items"][:2]
    sign="×" if item["id"]=="market-cap" else "÷"
    result=ratio_result(item)
    result_size=29 if len(result)>22 else 40
    out=""
    for i,p in enumerate([a,b]):
        x=80+i*505
        out+=rect(x,177,435,146,"#eef4ef",stroke="#d4e4dc",radius=10)
        out+=node_text(x+26,218,p["label"],19,MUTED)
        out+=node_text(x+26,283,fmt(p["value"]),43,accent,weight=780)
    out+=rect(514,232,77,52,accent,radius=25)
    out+=node_text(552,266,sign,30,"white","middle",800)
    out+=node_text(548,376,"计算结果",15,MUTED,"middle",600)
    out+=node_text(548,427,result,result_size,INK,"middle",800)
    return out


def svg_timeline(items,accent):
    n=len(items)
    x0,x1=100,1000
    y=282
    out=line(x0,y,x1,y,"#9cbdb1",5)
    for i,p in enumerate(items):
        x=x0+(x1-x0)*i/(n-1)
        color=accent if i in (0,n-1) else "#9aacb2"
        out+=f'<circle cx="{x:.1f}" cy="{y}" r="15" fill="{PAPER}" stroke="{color}" stroke-width="5"/>'
        out+=node_text(x,205,p["label"],18,INK,"middle",700)
        out+=node_text(x,344,"示意值 "+fmt(p["value"]),14,MUTED,"middle")
        if i+1<n:
            out+=node_text(x+(x1-x0)/(n-1)/2,272,"→",24,accent,"middle",750)
    out+=node_text(83,144,"事件顺序 / TIMING — 不表示条目金额可以相加",14,MUTED)
    return out


def svg_layers(items,accent):
    out=""
    length=len(items)
    w=860/(length)
    for i,p in enumerate(items):
        x=90+i*w
        out+=rect(x,180,w-24,158,["#e7f1eb","#d2e7df","#dfe8eb","#eee7dc"][i%4],radius=11)
        out+=node_text(x+20,218,f"0{i+1}",14,accent,weight=780)
        out+=node_text(x+(w-24)/2,277,p["label"],18,INK,"middle",680)
        if i+1<length:
            out+=node_text(x+w-13,264,"→",23,accent,"middle",750)
    out+=node_text(95,396,"结构与顺序是教学示意；方块面积不代表货币金额或风险概率。",16,MUTED)
    return out


def svg_tree(items,accent):
    a,b,c=[x["value"] for x in items]
    roe=a/100*b*c*100
    out=rect(393,139,312,93,accent,radius=10)
    out+=node_text(550,175,"ROE = 三因素相乘",17,"white","middle",650)
    out+=node_text(550,215,f"{roe:.1f}%",33,"white","middle",820)
    for i,p in enumerate(items):
        x=52+i*352
        out+=line(550,232,x+160,291,"#a5c2b6",2.5)
        out+=rect(x,298,318,98,"#e9f1ec",stroke="#c8dbd0",radius=8)
        out+=node_text(x+159,332,p["label"],16,MUTED,"middle",670)
        unit="%" if i==0 else "×"
        out+=node_text(x+159,375,fmt(p["value"])+unit,27,accent,"middle",780)
    return out


def render_svg(item,category):
    title=item["title"]
    accent=category["color"]
    kind=item["diagram"]["kind"]
    items=item["diagram"]["items"]
    renderer={
        "balance":lambda:svg_balance(items,accent),
        "bridge":lambda:svg_bridge(items,accent),
        "compare":lambda:svg_compare(items,accent),
        "stack":lambda:svg_stack(items,accent),
        "ratio":lambda:svg_ratio(item,accent),
        "timeline":lambda:svg_timeline(items,accent),
        "layers":lambda:svg_layers(items,accent),
        "tree":lambda:svg_tree(items,accent),
    }
    content=renderer[kind]()
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 470" '
        'role="img" font-family="system-ui,-apple-system,Microsoft YaHei,Arial,sans-serif">'
        f'<title>{h(title)} · 财报概念图解</title>'
        f'<desc>{h(item["definition"])}。数字仅用于教学示意，不代表任何上市公司实际披露。</desc>'
        +rect(0,0,1100,470,PAPER,radius=0)
        +rect(45,33,5,61,accent,radius=2)
        +node_text(67,54,f'FINANCIAL CONCEPT  /  {item["order"]:03d}',13,accent,weight=760)
        +node_text(67,91,title,28,INK,weight=760)
        +content
        +line(55,450,1045,450,BORDER,1)
        +node_text(55,462,"ILLUSTRATIVE ONLY · 合成教学数值 · 非真实财报或实时市场数据",11,MUTED)
        +"</svg>"
    )


def _reading_tip(category):
    return {
        "statements":"先看这项内容属于时点余额、期间损益，还是披露口径；跨表比较前先统一范围。",
        "revenue":"核对收入确认政策、业务分部和同期间比较；现金收款与会计收入可能错位。",
        "profit":"辨别 IFRS/GAAP 报告利润与企业自定义的调整指标，检查非现金费用和税项。",
        "assets":"先辨别流动/非流动及计量基础，判断余额是否可以按账面金额变现。",
        "capital":"留意负债的实际到期日、利息及权益性质；不要把所有负债视为有息贷款。",
        "cash":"现金流按期间计量，与利润和期末现金分别比较，并核对非现金变化。",
        "returns":"确保分子与分母覆盖同一主体及期间，通常用平均余额而非单一期末余额。",
        "risk":"杠杆比率要结合债务期限、可用现金、利息与经营现金流共同解释。",
        "valuation":"估值示例不是市场报价；使用真实价格前必须标注交易日、币种和利润期间。",
        "analysis":"先处理重述、异常项目、会计政策与期间不一致，再解读增长率与利润质量。"
    }[category["id"]]


def _card(c,where,link,H):
    u=H(link(where,f'concepts/{c["id"]}/index.html'))
    return (f'<a class="glossary-card" data-glossary-card '
            f'data-category="{H(c["category"])}" '
            f'data-search="{H(c["title"]+" "+c["en"]+" "+c["definition"]+" "+c["id"])}" '
            f'href="{u}">'
            f'<span class="glossary-card-num">{c["order"]:03d}</span>'
            f'<strong>{H(c["title"])}</strong>'
            f'<span class="glossary-card-en">{H(c["en"])}</span>'
            f'<p>{H(c["definition"])}</p>'
            f'<span class="glossary-card-arrow" aria-hidden="true">↗</span></a>')


def _related(c,all_items):
    same=[x for x in all_items if x["category"]==c["category"] and x["id"]!=c["id"]]
    pos=[x for x in all_items if x["id"]==c["id"]][0]["order"]-1
    return (same[:3] if len(same)>2 else all_items[max(0,pos-1):pos+2])


def build_glossary(*, data_path, output_dir, template, page, link, canonical, H):
    """Generate exactly 101 concept HTML pages via the existing site page() contract."""
    data=json.loads(Path(data_path).read_text(encoding="utf-8"))
    check_concepts(data)
    cats={c["id"]:c for c in data["categories"]}
    concepts=data["concepts"]
    root=Path(output_dir)
    index="concepts/index.html"
    cat_links=[]
    sections=[]
    for j,category in enumerate(data["categories"],1):
        cid=category["id"]
        contained=[c for c in concepts if c["category"]==cid]
        cards="".join(_card(c,index,link,H) for c in contained)
        cat_links.append(
            f'<a class="glossary-category-card" href="#category-{H(cid)}">'
            f'<span>CHAPTER {j:02d} / 10</span><strong>{H(category["name"])}</strong>'
            f'<small>{H(category["en"])}</small><p>{H(category["description"])}</p>'
            f'<span class="glossary-cat-count">10 TERMS →</span></a>')
        sections.append(
            f'<section class="glossary-section" id="category-{H(cid)}" data-glossary-section '
            f'data-category="{H(cid)}"><div class="glossary-section-head">'
            f'<div><span class="glossary-chapter-no">CHAPTER {j:02d}</span>'
            f'<h2>{H(category["name"])}</h2><p>{H(category["description"])}</p></div>'
            f'<a href="#glossary-top" class="glossary-back">返回顶部 ↑</a></div>'
            f'<div class="glossary-grid">{cards}</div></section>')
    content=template(
        "concept-index", category_cards="".join(cat_links),
        concept_sections="".join(sections),
        concept_count=str(len(concepts)),
        editorial_note=H(data["editorial_note"]),
        source_href=H(link(index,"reports/index.html"))
    )
    structure={
        "@context":"https://schema.org","@type":"DefinedTermSet",
        "name":"财报核心概念图鉴 100","inLanguage":"zh-CN",
        "url":canonical(index),
        "description":"100 个按教学路径编排、配独立原创 SVG 的财报核心概念。",
        "hasDefinedTerm":[{"@type":"DefinedTerm","name":c["title"],
                           "url":canonical(f'concepts/{c["id"]}/index.html')}
                          for c in concepts]
    }
    page(index,"财报概念图鉴 100","系统学习100个最常见的财务报表概念：从会计等式到现金流、ROE和DCF，每个概念都有原创矢量图解。",content,structure)
    for c in concepts:
        detail=f'concepts/{c["id"]}/index.html'
        category=cats[c["category"]]
        assets=root/Path(detail).parent/"assets"
        assets.mkdir(parents=True,exist_ok=True)
        filename=assets/"concept.svg"
        filename.write_text(render_svg(c,category),encoding="utf-8")
        visual_url=H(link(detail,f'concepts/{c["id"]}/assets/concept.svg'))
        rows="".join(
            f'<tr><th scope="row">{H(p["label"])}</th>'
            f'<td>{H(fmt(p["value"]))}</td></tr>'
            for p in c["diagram"]["items"]
        )
        result_html=""
        if c["diagram"]["kind"]=="ratio":
            result_html=(f'<p class="glossary-result">此例计算结果：'
                         f'<strong>{H(ratio_result(c))}</strong></p>')
        if c["diagram"]["kind"]=="bridge":
            result_html=(f'<p class="glossary-result">按示例加减后的终点：'
                         f'<strong>{H(fmt(c["diagram"]["items"][-1]["value"]))}</strong></p>')
        items=concepts
        index0=c["order"]-1
        previous=items[index0-1] if index0>0 else None
        nxt=items[index0+1] if index0+1<len(items) else None
        def navigation(cand,label):
            if not cand:
                return f'<span class="glossary-nav-empty">{label} · 无</span>'
            href=H(link(detail,f'concepts/{cand["id"]}/index.html'))
            return (f'<a href="{href}"><small>{label} · {cand["order"]:03d}</small>'
                    f'<strong>{H(cand["title"])}</strong></a>')
        suggestions=_related(c,concepts)
        related_parts=[]
        for related in suggestions:
            related_href=H(link(detail,"concepts/"+related["id"]+"/index.html"))
            related_parts.append(
                f'<a class="glossary-related-card" href="{related_href}">'
                f'<span>{related["order"]:03d}</span><strong>{H(related["title"])}</strong>'
                f'<small>{H(related["en"])}</small></a>'
            )
        related_html="".join(related_parts)
        content=template(
            "concept-detail",title=H(c["title"]),english=H(c["en"]),
            chapter_title=H(category["name"]),category_id=H(category["id"]),
            category_desc=H(category["description"]),description=H(c["definition"]),
            formula=H(c["formula"]),pitfall=H(c["pitfall"]),
            chart_src=visual_url,
            chart_alt=H(c["title"]+"的教学用 SVG 图解；示例数值是合成的，不是公司财报数值。"),
            svg_href=visual_url, index_href=H(link(detail,index)),
            report_href=H(link(detail,"reports/index.html")),order=f'{c["order"]:03d}',
            reading_tip=H(_reading_tip(category)),
            input_rows=rows,example_result=result_html,
            prev_link=navigation(previous,"上一个概念"),
            next_link=navigation(nxt,"下一个概念"),
            related_cards=related_html,
        )
        structured={
            "@context":"https://schema.org","@type":"DefinedTerm",
            "name":c["title"],"alternateName":c["en"],
            "description":c["definition"],"termCode":c["id"],
            "inDefinedTermSet":canonical(index),
            "url":canonical(detail)
        }
        page(detail,c["title"]+" · 财报图解",c["definition"],content,structured)
    catalog={
        "schema_version":"1.0",
        "editorial_note":data["editorial_note"],
        "categories":data["categories"],
        "concepts":[{"order":c["order"],"id":c["id"],"title":c["title"],"en":c["en"],
                     "category":c["category"],"definition":c["definition"],
                     "url":canonical(f'concepts/{c["id"]}/index.html')}
                    for c in concepts]
    }
    (root/"concepts/catalog.json").write_text(
        json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return len(concepts)+1


def check_concepts(data):
    """Fail closed on malformed educational content and numerically false diagrams."""
    errors=[]
    cats=data.get("categories",[])
    all_items=data.get("concepts",[])
    if len(cats)!=10:errors.append("require exactly ten pedagogical categories")
    if len(all_items)!=100:errors.append("require exactly 100 concept records")
    category_ids=[x.get("id") for x in cats]
    if len(set(category_ids))!=len(category_ids):
        errors.append("category IDs duplicated")
    seen=set()
    for i,c in enumerate(all_items,1):
        ident=c.get("id","")
        if not ident or ident in seen or not all(ch.islower() or ch.isdigit() or ch=="-" for ch in ident):
            errors.append(f"bad or duplicate concept slug: {ident}")
        seen.add(ident)
        if c.get("order")!=i:errors.append(f"concept {ident} order mismatch")
        if c.get("category") not in category_ids:errors.append(f"unknown category: {ident}")
        for f in ("title","en","definition","formula","pitfall"):
            if len(c.get(f,""))<8:
                errors.append(f"{ident}: {f} missing or too short")
        if c.get("illustrative") is not True:
            errors.append(f"{ident} must mark example data as illustrative")
        spec=c.get("diagram",{})
        kind=spec.get("kind")
        if kind not in {"balance","bridge","compare","stack","ratio","timeline","layers","tree"}:
            errors.append(f"{ident}: unexpected diagram kind")
        points=spec.get("items",[])
        if not (2<=len(points)<=5):errors.append(f"{ident}: two to five diagram items required")
        for p in points:
            if not p.get("label") or type(p.get("value")) not in (int,float) or not math.isfinite(p["value"]):
                errors.append(f"{ident}: diagram value/label missing")
        if kind=="balance" and len(points)==3 and sum(p["value"] for p in points[1:])!=points[0]["value"]:
            errors.append(f"{ident}: accounting equation is not balanced")
        if kind=="bridge" and len(points)>=3:
            if abs(points[0]["value"]+sum(p["value"] for p in points[1:-1])-points[-1]["value"])>0.000001:
                errors.append(f"{ident}: waterfall bridge is not conserved")
        if kind=="stack" and sum(p["value"] for p in points)<=0:
            errors.append(f"{ident}: non-positive stacked total")
        if kind=="stack" and any(p["value"]<0 for p in points):
            errors.append(f"{ident}: stacked segment is negative")
        if kind=="ratio" and len(points)!=2:
            errors.append(f"{ident}: ratio example needs exactly two operands")
        if kind=="ratio" and len(points)==2 and points[1]["value"]<=0:
            errors.append(f"{ident}: division by zero or negative denominator")
        if kind=="tree" and len(points)!=3:
            errors.append(f"{ident}: tree/dupont needs 3 factors")
    for cat in category_ids:
        if sum(c.get("category")==cat for c in all_items)!=10:
            errors.append(f"{cat}: expected exactly 10 concepts")
    if errors:
        raise ValueError("Glossary contract failed:\n"+"\n".join(errors))
    return True
