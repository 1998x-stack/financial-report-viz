"""Tesla 2026 Q3 source-anchored original SVG charts, offline and dependency-free.

Source: official Tesla Q3 2026 Update, printed pages 4/5/27-31.
Amounts in USD millions; annotations convert only for readability.
"""
from html import escape
from pathlib import Path

INK="#20303a"; MUTED="#637481"; GRID="#e5eaec"; BLUE="#295c8c"; TEAL="#178376"
AMBER="#d7a54f"; RED="#bd6858"; PAPER="#fffefa"; PALE="#edf4f1"

def h(s): return escape(str(s),quote=True)
def n(d,key,period="current"): return d["values"][key]["values"][period]
def tx(x,y,s,size=14,color=INK,anchor="start",weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{h(s)}</text>'
def rect(x,y,w,ht,color,tip="",rad=3):
    title=f'<title>{h(tip)}</title>' if tip else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(0,w):.1f}" height="{max(0,ht):.1f}" rx="{rad}" fill="{color}">{title}</rect>'
def line(x1,y1,x2,y2,color=GRID,width=1):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"/>'
def svg(title,desc,body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 426" width="1040" height="426" '
            'role="img" font-family="system-ui,Arial,sans-serif">'
            f'<title>{h(title)}</title><desc>{h(desc)}</desc>'
            +rect(0,0,1040,426,PAPER,rad=0)+body+"</svg>")
def header(label,unit):
    return tx(44,42,label,18,INK,weight=700)+tx(996,42,unit,12,MUTED,"end")
def fmt_bn(v):return f"{v/1000:,.2f}"
def source_note(page,text):
    return tx(44,410,f"Tesla Q3 2026 Update · p.{page} | {text}",11,MUTED)

def chart_quarterly(d):
    t=d["quarterly_series"]; rev=t["revenue"]; gp=t["gross_profit"]
    s=header("五季规模与毛利：规模并未持续增长","十亿美元 · 单季度")
    top=72; bottom=330; left=88; right=998
    for v in (0,8,16,24,32):
        y=bottom-v/32*(bottom-top)
        s+=line(left,y,right,y)+tx(left-12,y+4,str(v),11,MUTED,"end")
    for i,period in enumerate(t["periods"]):
        x=left+40+i*177
        for j,(value,color) in enumerate(((rev[i],BLUE),(gp[i],TEAL))):
            height=value/32000*(bottom-top)
            xpos=x+j*48
            s+=rect(xpos,bottom-height,37,height,color,f"{period}: {value:,} 百万美元")
            s+=tx(xpos+18,bottom-height-9,f"{value/1000:.1f}",11,INK,"middle",650)
        s+=tx(x+42,355,period.replace("202","'2"),12,MUTED,"middle")
    s+=rect(235,384,12,12,BLUE)+tx(255,394,"营收",12,MUTED)
    s+=rect(400,384,12,12,TEAL)+tx(420,394,"毛利",12,MUTED)
    return svg("五个季度的营收与毛利","2025 Q3 至 2026 Q3 单季度的原始披露收入和毛利润；以十亿美元作图。",s)

def chart_mix(d):
    s=header("2025 → 2026：三项业务收入的结构变化","十亿美元 · 单季度")
    keys=[("automotive_revenue","汽车",BLUE),("energy_revenue","能源",AMBER),("services_revenue","服务",TEAL)]
    scale=820/30000
    for i,p in enumerate(("prior","current")):
        y=120+i*124; x=116
        s+=tx(44,y+28,("2025 Q3","2026 Q3")[i],16,INK,weight=700)
        for key,label,color in keys:
            val=n(d,key,p); w=val*scale
            s+=rect(x,y,w,48,color,f"{label}: {val:,} 百万美元")
            if w>65: s+=tx(x+w/2,y+29,f"{val/1000:.2f}",13,"white","middle",700)
            x+=w
        s+=tx(960,y+28,f"{n(d,'revenue',p)/1000:.2f}",15,INK,"end",700)
    for i,(key,label,color) in enumerate(keys):
        x=172+i*244
        s+=rect(x,355,12,12,color)+tx(x+18,366,label,13,MUTED)
    s+=source_note(27,"业务分部之和等于营业收入")
    return svg("三大业务收入结构","两个可比季度汽车、储能和服务业务的收入堆叠，展示结构差异。",s)

def chart_revenue_bridge(d):
    prev=n(d,"revenue","prior"); now=n(d,"revenue")
    deltas=[("汽车收入",n(d,"automotive_revenue")-n(d,"automotive_revenue","prior")),
            ("能源储能",n(d,"energy_revenue")-n(d,"energy_revenue","prior")),
            ("服务及其他",n(d,"services_revenue")-n(d,"services_revenue","prior"))]
    assert prev+sum(x[1] for x in deltas)==now
    s=header("到底是谁抵消了下滑？","同比变化 · 百万美元")
    s+=tx(52,96,f"2025 Q3：{prev:,}",17,INK,weight=700)+tx(993,96,f"2026 Q3：{now:,}",17,INK,"end",700)
    x0=490
    s+=line(x0,120,x0,348,"#aebbc2",2)
    for i,(name,delta) in enumerate(deltas):
        y=133+i*70; width=abs(delta)/1300*388
        x=x0 if delta>=0 else x0-width
        s+=rect(x,y,width,30,TEAL if delta>0 else RED,f"{name}: {delta:+,} 百万美元")
        s+=tx(75,y+21,name,16,INK,weight=600)
        s+=tx(x0+width+12 if delta>=0 else x-12,y+21,f"{delta:+,}",15,TEAL if delta>=0 else RED,
              "start" if delta>=0 else "end",700)
    net=now-prev
    s+=tx(74,365,f"净变化：{net:+,} 百万美元（同比 {100*net/prev:+.2f}%）",17,INK,weight=700)
    return svg("收入变化贡献","汽车收入下降六点四五亿美元，能源收入下降五点三四亿美元，服务增加十一点三亿美元；合计收入减少四千九百万美元。",s+source_note(27,"同比贡献是金额差，不代表现金流"))

def chart_margin(d):
    s=header("毛利率改善，但经营及归母净利率走弱","按各自 GAAP 利润 / 当期营收 · %")
    margins=[("毛利率","gross_profit"),("营业利润率","operating_profit"),("归母净利率","attributable_profit")]
    for j,(name,key) in enumerate(margins):
        y=125+j*102
        a=100*n(d,key,"prior")/n(d,"revenue","prior")
        b=100*n(d,key)/n(d,"revenue")
        scale=34
        s+=tx(50,y+5,name,15,INK,weight=650)
        x0=350;x1=700
        s+=line(x0,y,x1,y,GRID,5)
        w0=a*scale;w1=b*scale
        s+=rect(x0,y-17,w0,12,BLUE,f"2025 Q3 {a:.2f}%")
        s+=rect(x0,y+10,w1,12,TEAL,f"2026 Q3 {b:.2f}%")
        s+=tx(790,y-9,f"{a:.2f}% → {b:.2f}%",17,INK,weight=650)
        s+=tx(790,y+20,f"{b-a:+.2f} pp",13,TEAL if b>a else RED)
    return svg("GAAP 利润率对比","2025 Q3 与 2026 Q3 的 GAAP 毛利率、营业利润率、归母净利率。pp 表示百分点。",s+source_note(27,"各利润率由报告值除以同一季度营收计算"))

def chart_profit(d):
    steps=[("总收入",n(d,"revenue")),("收入成本",-n(d,"cost_of_revenue")),
           ("毛利润",n(d,"gross_profit")),("研发",-n(d,"research_development")),
           ("销售及行政",-n(d,"selling_general_admin")),("营业利润",n(d,"operating_profit"))]
    assert steps[0][1]+steps[1][1]==steps[2][1]
    assert steps[2][1]+steps[3][1]+steps[4][1]==steps[5][1]
    s=header("从 280 亿美元收入，到 7.18 亿美元营业利润","2026 Q3 · 十亿美元")
    xs=[67,233,400,567,733,895]
    for i,(label,val) in enumerate(steps):
        height=abs(val)/28046*236
        y=325-height
        color=BLUE if i==0 else TEAL if i in (2,5) else RED
        s+=rect(xs[i],y,94,height,color,f"{label}：{val:+,} 百万美元")
        s+=tx(xs[i]+47,max(y-11,71),f"{val/1000:+.2f}" if val<0 else f"{val/1000:.2f}",
              13,INK,"middle",700)
        s+=tx(xs[i]+47,351,label,12,MUTED,"middle")
    s+=tx(52,390,"收入 − 成本 = 毛利；毛利 − 研发 − 销售及行政 = 营业利润（会计利润桥，非现金流向）",12,MUTED)
    return svg("营业利润拆解","收入减成本和营业费用后的营业利润，各节点满足精确金额勾稽。",s+source_note(27,"重组及其他本季披露为横线（无金额），不另作估计"))

def chart_cash(d):
    s=header("经营现金流稳定，资本开支吞噬自由现金流","十亿美元 · 2025 Q3 vs 2026 Q3")
    keys=[("经营现金流","operating_cash_flow"),("资本开支","capital_expenditures"),("自由现金流","free_cash_flow")]
    maxv=7000;bottom=315;top=90
    for val in (0,2000,4000,6000):
        y=bottom-val/maxv*(bottom-top)
        s+=line(90,y,990,y)+tx(80,y+4,f"{val/1000:g}",11,MUTED,"end")
    for i,(label,key) in enumerate(keys):
        groupx=163+i*284
        for j,(p,color) in enumerate((("prior",BLUE),("current",TEAL))):
            v=n(d,key,p);height=v/maxv*(bottom-top);x=groupx+j*69
            s+=rect(x,bottom-height,48,height,color,f"{p}: {v:,} 百万美元")
            s+=tx(x+24,bottom-height-10,f"{v/1000:.2f}",13,INK,"middle",700)
        s+=tx(groupx+60,349,label,13,INK,"middle",650)
    s+=rect(290,379,12,12,BLUE)+tx(310,390,"2025 Q3",12,MUTED)
    s+=rect(500,379,12,12,TEAL)+tx(520,390,"2026 Q3",12,MUTED)
    return svg("现金流与资本开支","两期现金流、资本开支和自由现金流。自由现金流等于经营现金流减资本开支，资本开支以正值表示支出。",s+source_note(29,"资本开支显示绝对值；FCF 是公司定义的非 GAAP 指标"))

def chart_nongaap(d):
    adjustments=[("GAAP 归母",n(d,"attributable_profit")),("+ 股权激励",n(d,"stock_comp_net_tax")),
      ("− 数字资产",-224),("+ 投资未实现损益",108),("+ 特定税项",44),("Non-GAAP",n(d,"non_gaap_attributable_profit"))]
    assert adjustments[0][1]+sum(v for _,v in adjustments[1:5])==adjustments[-1][1]
    s=header("GAAP 到 Non-GAAP：9.10 亿美元调整差额","2026 Q3 · 百万美元")
    x0=70;step=160
    cumulative=0
    for i,(label,value) in enumerate(adjustments):
        x=x0+i*step
        if i==0:cumulative=value
        elif i<5:cumulative+=value
        else:assert value==cumulative
        s+=rect(x,125,134,80,BLUE if i==0 else TEAL if i==5 else RED if value<0 else AMBER,
                f"{label}: {value:+,} 百万美元")
        s+=tx(x+67,168,f"{value:+,}" if i in (1,2,3,4) else f"{value:,}",20,"white","middle",700)
        s+=tx(x+67,239,label,12,INK,"middle",600)
        s+=tx(x+67,265,f"累计 {cumulative:,}",12,MUTED,"middle")
        if i<5:s+=line(x+134,165,x+157,165,MUTED,2)
    s+=tx(55,331,"Non-GAAP 净利润是公司定义的调整口径，并非 US GAAP 净利润。",14,INK)
    s+=tx(55,358,"股权激励、数字资产、投资估值与特定税项的税后调整均来自原始披露。",12,MUTED)
    return svg("GAAP 与 Non-GAAP 归母净利润调节","2026 Q3 归母净利润 787 百万美元加税后调整后等于 Non-GAAP 1697 百万美元。",s+source_note(30,"这些调整不等于经营现金流"))

def chart_vehicle(d):
    s=header("产量增加、交付量下降：供需两端的分化","车辆 · 单季度")
    keys=[("汽车产量","total_production"),("汽车交付量","total_deliveries")]
    for i,(label,key) in enumerate(keys):
        y=124+i*129
        prev=n(d,key,"prior");curr=n(d,key)
        s+=tx(52,y,label,17,INK,weight=700)
        s+=rect(230,y-18,prev/550000*590,26,BLUE,f"2025 Q3: {prev:,} 辆")
        s+=rect(230,y+20,curr/550000*590,26,TEAL,f"2026 Q3: {curr:,} 辆")
        s+=tx(852,y+2,f"{prev:,} / {curr:,}",13,INK,weight=650)
        s+=tx(852,y+30,f"{(curr/prev-1)*100:+.1f}%",14,TEAL if curr>prev else RED,weight=700)
    s+=rect(235,375,12,12,BLUE)+tx(255,386,"2025 Q3",12,MUTED)
    s+=rect(420,375,12,12,TEAL)+tx(440,386,"2026 Q3",12,MUTED)
    return svg("汽车生产与交付","Tesla 2026 Q3 产量增长约百分之四，交付量下降约百分之二。",s+source_note(5,"汽车生产与交付量是当期流量，不等同于已确认收入"))

def chart_adoption(d):
    s=header("FSD 订阅升温与储能部署量增长","单位分别为百万活跃订阅、GWh")
    panels=[
        (55,"活跃 FSD 订阅","fsd_active_subscriptions","百万订阅",2.1),
        (540,"储能部署","energy_deployed","GWh",16)
    ]
    for x,title,key,unit,mx in panels:
        prev=n(d,key,"prior");curr=n(d,key)
        s+=rect(x,80,440,264,PALE,rad=4)
        s+=tx(x+24,115,title,18,INK,weight=700)+tx(x+24,137,unit,12,MUTED)
        for j,(p,v,color) in enumerate((("2025 Q3",prev,BLUE),("2026 Q3",curr,TEAL))):
            by=190+j*82
            s+=tx(x+24,by,p,12,MUTED)
            s+=rect(x+120,by-18,v/mx*242,31,color,f"{p}: {v} {unit}")
            s+=tx(x+375,by+3,f"{v:.2f}" if key=="fsd_active_subscriptions" else f"{v:.1f}",15,INK,"end",700)
        s+=tx(x+24,321,f"同比 {(curr/prev-1)*100:+.1f}%",16,TEAL,weight=700)
    s+=tx(55,381,"FSD 订阅量不等于 FSD 收入；储能部署量亦不等于当期收入。",13,MUTED)
    return svg("FSD 订阅与储能部署","两个单独刻度的面板展示活跃 FSD 订阅及储能部署量的两个可比季度变化。",s+source_note(5,"FSD 为已付费订阅和一次性买断，排除免费试用"))

def chart_balance(d):
    s=header("现金储备增长，但总负债增速更快","十亿美元 · 期末时点")
    keys=[("现金和短投","cash_and_investments"),("总负债","total_liabilities"),("股东权益","total_stockholders_equity")]
    maxv=100000;left=100;bottom=327;top=100
    for i,(name,key) in enumerate(keys):
        x=left+60+i*286
        for j,(p,color) in enumerate((("prior",BLUE),("current",TEAL))):
            v=n(d,key,p); ht=v/maxv*(bottom-top)
            s+=rect(x+j*66,bottom-ht,48,ht,color,f"{name} {p}: {v:,} 百万美元")
            s+=tx(x+j*66+24,bottom-ht-10,f"{v/1000:.1f}",13,INK,"middle",650)
        s+=tx(x+50,355,name,13,INK,"middle",600)
    s+=rect(290,378,12,12,BLUE)+tx(308,390,"2025-09-30",12,MUTED)
    s+=rect(495,378,12,12,TEAL)+tx(513,390,"2026-09-30",12,MUTED)
    return svg("现金、负债与权益","季度末现金与短期投资、总负债、公司股东权益，展示资产负债面貌。",s+source_note(28,"现金及短投为资产子项；不与负债及权益相加"))

FIGURES=[
 ("quarterly","五季营收与毛利","收入停滞背景下，毛利润在本季度回升",[4,27],chart_quarterly),
 ("revenue-mix","业务收入结构","三类业务合计等于总收入；混合口径展示真实业务结构",[27],chart_mix),
 ("revenue-bridge","收入同比归因","基于披露分部金额差额而不是未经验证的产品单价分解",[27],chart_revenue_bridge),
 ("margins","三层 GAAP 利润率","变化单位为百分点（pp），不是同比百分比",[27],chart_margin),
 ("profit-bridge","营业利润桥","逐项勾稽收入、收入成本、研发和销售行政费用",[27],chart_profit),
 ("cash-flow","现金流与资本开支","经营现金流减资本开支等于 Non-GAAP 自由现金流",[29,31],chart_cash),
 ("gaap-nongaap","归母利润口径调节","非 GAAP 调整来自公司披露调节表，不能与现金利润等同",[30],chart_nongaap),
 ("vehicle","产量与交付","产量增长但交付下降，需要和业务收入分开分析",[5],chart_vehicle),
 ("adoption","FSD 订阅与储能部署","采用不同量纲分面比较，不能按规模直接相加",[5],chart_adoption),
 ("balance","资产负债弹性","现金、总负债与归属股东权益均为期末存量",[28],chart_balance),
]
def build_tesla_figures(d,out_dir):
    path=Path(out_dir);path.mkdir(parents=True,exist_ok=True);result=[]
    for slug,title,caption,pages,fn in FIGURES:
        content=fn(d)
        (path/(slug+".svg")).write_text(content,encoding="utf-8")
        result.append({"slug":slug,"title":title,"caption":caption,"pages":pages,"filename":slug+".svg"})
    return result
