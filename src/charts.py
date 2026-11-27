"""Original, source-driven, standalone SVG figure renderers.

Amounts use original CNY thousand inputs. Only the SVG annotation layer converts
to 亿元: CNY_100M = CNY_thousand / 100000.
"""
from html import escape
from pathlib import Path


INK, MUTED, GRID = "#263449", "#6b7889", "#e6e9ed"
BLUE, TEAL, AMBER, RED, PURPLE = "#3465b4", "#158780", "#d5a04a", "#ce6d5c", "#7565a3"
PAPER = "#fffefa"


def E(s):
    return escape(str(s), quote=True)


def yuan(v):
    return f"{v / 100000:.2f}"


def fmt(v, digits=1):
    return f"{v:.{digits}f}"


def tx(x, y, label, size=13, color=INK, anchor="start", weight=400):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}">{E(label)}</text>')


def rect(x, y, w, h, color, title="", radius=4, opacity=1):
    child = f'<title>{E(title)}</title>' if title else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(0,w):.1f}" '
            f'height="{max(0,h):.1f}" rx="{radius}" fill="{color}" opacity="{opacity}">{child}</rect>')


def ln(x1, y1, x2, y2, color=GRID, width=1, dash=""):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')


def cir(x, y, r, color, title=""):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"><title>{E(title)}</title></circle>'


def root_svg(title, desc, body, width=1040, height=426):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
            f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'font-family="system-ui,-apple-system,Arial,sans-serif">'
            f'<title>{E(title)}</title><desc>{E(desc)}</desc>'
            f'{rect(0,0,width,height,PAPER,radius=0)}{body}</svg>')


def get(d, key, p="current"):
    return d["values"][key]["values"][p]


def base_axes(top, bottom, left, right, tick_max, grid=4, precision=0):
    parts = []
    for k in range(grid + 1):
        value = tick_max * k / grid
        y = bottom - (bottom - top) * k / grid
        parts.append(ln(left, y, right, y))
        parts.append(tx(left - 12, y + 5, f"{value / 100000:.{precision}f}", 11, MUTED, "end"))
    parts.append(tx(left - 13, top - 23, "亿元", 11, MUTED))
    return "".join(parts)


def grouped(d, title, keys, colors, maximum=None):
    left, right, top, bottom = 92, 986, 65, 337
    mx = maximum or max(get(d, k, p) for k in keys for p in ("prior", "current")) * 1.18
    s = base_axes(top,bottom,left,right,mx,4,0)
    count = len(keys)
    step = (right - left) / count
    for j,k in enumerate(keys):
        x0 = left + j * step + step * .12
        for i,p in enumerate(("prior","current")):
            v = get(d,k,p)
            bh = (bottom-top) * v/mx
            x = x0 + i * step*.34
            s += rect(x,bottom-bh,step*.25,bh,[BLUE,TEAL][i],
                      f'{d["values"][k]["label"]} {2025+i} H1：{v:,} 人民币千元')
            s += tx(x+step*.125,bottom-bh-9,yuan(v),13,INK,"middle",600)
        s += tx(left+j*step+step*.42,bottom+29,d["values"][k]["label"].replace("期内",""),12,INK,"middle")
    s += rect(110,385,13,13,BLUE)+tx(131,397,"2025 H1",12,MUTED)
    s += rect(260,385,13,13,TEAL)+tx(281,397,"2026 H1",12,MUTED)
    return root_svg(title,"分组柱状图，同口径 2025 与 2026 上半年人民币亿元金额。",s)


def segments(d):
    left,right,top,bottom = 98,972,60,336
    totalmax=3600000
    s=base_axes(top,bottom,left,right,totalmax)
    for i,p in enumerate(("prior","current")):
        cx=340+i*380
        width=174
        base=bottom
        for key,col in (("game_revenue",BLUE),("taptap_revenue",TEAL)):
            v=get(d,key,p)
            h=(bottom-top)*v/totalmax
            s+=rect(cx-width/2,base-h,width,h,col,f'{d["values"][key]["label"]} {p}：{v:,} 人民币千元',2)
            if h>40:s+=tx(cx,base-h/2+5,yuan(v)+" 亿",16,"#fff","middle",650)
            base-=h
        s+=tx(cx,base-12,yuan(get(d,"revenue",p))+" 亿",19,INK,"middle",700)
        s+=tx(cx,bottom+28,("2025 H1","2026 H1")[i],14,MUTED,"middle",600)
    s+=rect(220,387,13,13,BLUE)+tx(240,399,"游戏分部",12,MUTED)
    s+=rect(440,387,13,13,TEAL)+tx(460,399,"TapTap 平台",12,MUTED)
    return root_svg("分部收入结构","游戏和 TapTap 平台占合并收入比例，分部之和等于总营收。",s)


def margins(d):
    left,right,top,bottom=150,910,70,340
    s=""
    for k in range(0,81,20):
        x=left+k/80*(right-left)
        s+=ln(x,top,x,bottom)+tx(x,bottom+28,f"{k}%",11,MUTED,"middle")
    rows=[("毛利率","gross_profit"),("经营利润率","operating_profit"),("净利率","period_profit")]
    for j,(label,numerator) in enumerate(rows):
        y=105+j*104
        values=[100*get(d,numerator,p)/get(d,"revenue",p) for p in ("prior","current")]
        xx=[left+v/80*(right-left) for v in values]
        s+=tx(left-24,y+5,label,15,INK,"end",650)
        s+=ln(xx[0],y,xx[1],y,"#aab8c7",4)
        for i,x in enumerate(xx):
            s+=cir(x,y,9,[BLUE,TEAL][i],f"{label}: {values[i]:.2f}%")
            s+=tx(x,y-19,f"{values[i]:.1f}%",13,[BLUE,TEAL][i],"middle",650)
    s+=cir(690,393,7,BLUE)+tx(709,398,"2025 H1",12,MUTED)
    s+=cir(822,393,7,TEAL)+tx(842,398,"2026 H1",12,MUTED)
    return root_svg("盈利能力：毛利率、经营利润率与净利率",
                    "三组利润率均按对应期间利润项目除以对应期间收入计算；两个期间的差为百分点。",s)


def expenses(d):
    return grouped(d,"主要费用与税费",["selling_marketing","research_development","income_tax_expense"],[BLUE,TEAL],maximum=1050000)


def waterfall(d):
    steps=[
        ("营业收入",get(d,"revenue"),"total"),
        ("收入成本",-get(d,"cost_of_revenue"),"change"),
        ("销售营销",-get(d,"selling_marketing"),"change"),
        ("研发",-get(d,"research_development"),"change"),
        ("行政",-get(d,"general_admin"),"change"),
        ("减值拨回",get(d,"impairment_reversal_net"),"change"),
        ("其他收入",get(d,"other_income"),"change"),
        ("其他收益",get(d,"other_gains_net"),"change"),
        ("经营利润",get(d,"operating_profit"),"total"),
        ("财务收入净额",get(d,"finance_income_net"),"change"),
        ("权益法份额",get(d,"equity_method_result"),"change"),
        ("税前利润",get(d,"profit_before_tax"),"total"),
        ("所得税",-get(d,"income_tax_expense"),"change"),
        ("期内利润",get(d,"period_profit"),"total"),
    ]
    W,H=1530,490
    left, right, top,bottom=68,W-34,74,374
    high=3650000
    yy=lambda v:bottom-(bottom-top)*v/high
    s=""
    for k in range(0,4):
        v=1000000*k
        y=yy(v)
        s+=ln(left,y,right,y)+tx(left-10,y+4,str(k*10),11,MUTED,"end")
    s+=tx(20,44,"人民币亿元",13,MUTED)
    span=(right-left)/len(steps)
    running=0
    for i,(label,value,kind) in enumerate(steps):
        old=running
        if kind=="total":
            if i not in (0,): 
                # A total checkpoint must agree with the current running balance.
                if abs(running-value)>0:raise ValueError(f"waterfall checkpoint {label}: {running} != {value}")
            start,end=0,value
            running=value
        else:
            start,end=running,running+value
            running=end
        hi,lo=max(start,end),min(start,end)
        bh=yy(lo)-yy(hi)
        x=left+i*span+span*.22
        color=BLUE if i==0 else TEAL if kind=="total" else RED if value<0 else AMBER
        s+=rect(x,yy(hi),span*.58,max(1,bh),color,
                f"{label}：{value/100000:+.3f} 亿元，累计：{running/100000:.3f} 亿元",2)
        s+=tx(x+span*.29,yy(hi)-8,
              ("" if kind=="total" else "+" if value>=0 else "−")+f"{abs(value)/100000:.2f}",
              11,INK,"middle",650)
        s+=tx(x+span*.29,bottom+25,label,11,MUTED,"middle")
        if i+1<len(steps) and kind!="total":
            s+=ln(x+span*.58,yy(running),left+(i+1)*span+span*.22,yy(running),"#adbbc8",1,"3 3")
    if running!=get(d,"period_profit"):raise ValueError("waterfall final profit does not match net profit")
    s+=tx(75,459,"经营利润、税前利润、期内利润为校验节点；正负号展示该项目对利润的影响。",13,MUTED)
    return root_svg("2026 H1 全口径利润桥",
                    "从营业收入到期内利润的全量可核验瀑布图，费用为减项、收益为加项。",s,W,H)


def cashflow(d):
    top,bottom,left,right=67,335,116,975
    y=lambda v:bottom-(v+600000)/1500000*(bottom-top)
    zero=y(0)
    s=""
    for v in (-600000,-300000,0,300000,600000,900000):
        yy=y(v)
        s+=ln(left,yy,right,yy,"#b5bfcb" if v==0 else GRID,2 if v==0 else 1)
        s+=tx(left-15,yy+5,fmt(v/100000,0),11,MUTED,"end")
    s+=tx(22,42,"人民币亿元",12,MUTED)
    keys=[("经营活动","operating_cash_flow"),("投资活动","investing_cash_flow"),("融资活动","financing_cash_flow")]
    gap=(right-left)/len(keys)
    for j,(label,k) in enumerate(keys):
        for i,p in enumerate(("prior","current")):
            v=get(d,k,p)
            x=left+j*gap+(0.2+i*.33)*gap
            bar_top=min(zero,y(v));bh=abs(y(v)-zero)
            s+=rect(x,bar_top,gap*.24,bh,[BLUE,TEAL][i],f"{label} {p}：{v:,} 人民币千元")
            s+=tx(x+gap*.12,bar_top-9 if v>0 else bar_top+bh+17,("+" if v>0 else "")+yuan(v),12,INK,"middle",650)
        s+=tx(left+j*gap+gap*.48,382,label,13,INK,"middle")
    return root_svg("现金流三分法","2025和2026上半年经营、投资、融资活动现金净额；负值代表现金流出。",s)


def usermetrics(d):
    keys=["network_games_mau","network_games_mpu","taptap_cn_mau","taptap_global_mau"]
    s=tx(56,40,"平均每月用户 · 单位：万人（源报告为千人）",14,MUTED)
    for i,key in enumerate(keys):
        prev,now=get(d,key,"prior"),get(d,key,"current")
        y=91+i*83
        pct=100*(now/prev-1)
        s+=tx(56,y,d["values"][key]["label"],15,INK,weight=600)
        s+=tx(56,y+26,f"2025 H1  {prev/10:,.1f} 万",12,MUTED)
        s+=tx(404,y+26,f"2026 H1  {now/10:,.1f} 万",12,TEAL,weight=600)
        s+=tx(872,y+22,("+" if pct>=0 else "")+f"{pct:.1f}%",20,TEAL if pct>=0 else RED,"end",700)
        s+=ln(56,y+38,955,y+38)
    return root_svg("用户指标：四项运营温度计",
                    "网络游戏平均月活跃/付费用户及TapTap中国版和国际版平均月活跃用户，同比变化。",s)


def geography(d):
    top,bottom,left,right=58,333,100,980
    maxv=2800000
    s=base_axes(top,bottom,left,right,maxv)
    for i,p in enumerate(("prior","current")):
        cx=350+350*i
        baseline=bottom
        for key,color in (("mainland_game_revenue",BLUE),("overseas_game_revenue",TEAL)):
            v=get(d,key,p)
            ht=(bottom-top)*v/maxv
            s+=rect(cx-100,baseline-ht,200,ht,color,f"{key}: {v:,} 人民币千元",2)
            s+=tx(cx,baseline-ht/2+6,yuan(v)+" 亿",18,"white","middle",650)
            baseline-=ht
        s+=tx(cx,baseline-14,yuan(get(d,"network_games",p)+get(d,"paid_games",p))+" 亿",17,INK,"middle",700)
        s+=tx(cx,371,("2025 H1","2026 H1")[i],14,MUTED,"middle")
    s+=rect(115,395,12,12,BLUE)+tx(133,406,"中国内地",12,MUTED)
    s+=rect(265,395,12,12,TEAL)+tx(283,406,"其他地区",12,MUTED)
    return root_svg("游戏运营收入：内地与其他地区",
                    "网络游戏加付费游戏的运营收入按地理位置拆分；不是整个公司地理收入。",s)


FIGURES=[
    ("growth","增长由谁贡献？","收入、毛利与期内利润的两期对照",[49],lambda d:grouped(d,"收入、毛利润、期内利润",["revenue","gross_profit","period_profit"],[BLUE,TEAL])),
    ("segments","增长背后的业务结构","游戏与 TapTap 两个分部总计等于合并收入",[9,68,69],segments),
    ("margins","规模扩大，利润率为何回落？","根据同期间合并财务数值计算，非独立披露数据",[49],margins),
    ("profit-bridge","利润究竟流向哪里？","逐项展示 2026 H1 披露的收入、费用、其他收益与所得税",[49],waterfall),
    ("expenses","费用强度变化","销售营销、研发和所得税费用对比；费用已正数化呈现",[49],expenses),
    ("cash-flow","现金流的另一面","经营、投资、融资现金流，现金流与利润不是同一概念",[58],cashflow),
    ("users","用户侧发生了什么？","网络游戏与 TapTap 国内、国际版使用不同人口基数，不可相加",[5],usermetrics),
    ("geography","游戏运营收入的区域重心","仅限游戏运营收入，不等于所有游戏分部收入",[70],geography),
]


def build_figures(report, out_dir):
    out_dir=Path(out_dir)
    out_dir.mkdir(parents=True,exist_ok=True)
    created=[]
    for slug,title,caption,pages,fn in FIGURES:
        xml=fn(report)
        (out_dir/f"{slug}.svg").write_text(xml,encoding="utf-8")
        created.append(dict(slug=slug,title=title,caption=caption,pages=pages,filename=f"{slug}.svg"))
    return created
