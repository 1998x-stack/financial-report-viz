"""腾讯 2026 Q3 专用矢量图：源文件单位为人民币百万元，所有绘图金额显示为亿元。

与心动 H1 的千元口径及业务定义隔离，避免误用旧图。
每幅图有独立 SVG title/desc、可见精确标签及来源页码。
"""
from pathlib import Path
from src.charts import E, tx, rect, ln, cir, root_svg, INK, MUTED, GRID, BLUE, TEAL, AMBER, RED, PURPLE

COLORS=[BLUE,TEAL,AMBER,PURPLE]
def v(d,k,p="current"): return d["values"][k]["values"][p]
def yi(n): return f"{n/100:.2f}"
def nice(n): return f"{n/100:,.2f}"
def axis(left,right,top,bottom,maxval,ticks=4):
    z=tx(left-8,top-25,"亿元（人民币）",12,MUTED)
    for j in range(ticks+1):
        val=maxval*j/ticks
        yy=bottom-(bottom-top)*val/maxval
        z+=ln(left,yy,right,yy)+tx(left-14,yy+4,f"{val/100:.0f}",11,MUTED,"end")
    return z

def growth(d):
    keys=[("营收","revenue"),("毛利润","gross_profit"),("IFRS经营利润","operating_profit"),("Non-IFRS经营利润","non_ifrs_operating_profit")]
    l,r,t,b=100,1000,74,338; maximum=225000
    z=axis(l,r,t,b,maximum)
    for j,(label,key) in enumerate(keys):
        center=l+(j+.5)*(r-l)/len(keys)
        for i,p in enumerate(("prior","current")):
            value=v(d,key,p); x=center-64+i*67
            h=(b-t)*value/maximum
            z+=rect(x,b-h,57,h,[BLUE,TEAL][i],f"{label} {2025+i} Q3：{value:,} 百万元")
            z+=tx(x+28,b-h-11,yi(value),12,INK,"middle",600)
        z+=tx(center,b+31,label,12,INK,"middle",600)
    z+=rect(320,389,12,12,BLUE)+tx(339,401,"2025 Q3",12,MUTED)
    z+=rect(505,389,12,12,TEAL)+tx(524,401,"2026 Q3",12,MUTED)
    return root_svg("收入增长未转化为经营利润增长","2025与2026独立第三季度收入、毛利、IFRS和非IFRS经营利润对比；金额为人民币亿元。",z)

def segments(d):
    l,r,t,b=125,960,58,342; maximum=220000
    z=axis(l,r,t,b,maximum)
    cats=[("vas_revenue","增值服务"),("marketing_revenue","营销服务"),("fintech_revenue","金融科技及企业服务"),("other_revenue","其他")]
    for j,p in enumerate(("prior","current")):
        center=[375,730][j]; bottom=b
        for i,(key,label) in enumerate(cats):
            value=v(d,key,p); h=(b-t)*value/maximum
            z+=rect(center-85,bottom-h,170,h,COLORS[i],f"{label} {p}: {value:,} 百万元",2)
            if h>23:z+=tx(center,bottom-h/2+5,yi(value),13,"white","middle",650)
            bottom-=h
        z+=tx(center,bottom-13,yi(v(d,"revenue",p))+" 亿",17,INK,"middle",650)
        z+=tx(center,b+30,["2025 Q3","2026 Q3"][j],14,INK,"middle")
    for i,(_,label) in enumerate(cats):
        x=62+i*251
        z+=rect(x,393,11,11,COLORS[i])+tx(x+18,404,label,11,MUTED)
    return root_svg("收入结构如何变化？","两期四项独立分部收入堆叠成集团营业收入，分部之和校验通过。",z)

def drivers(d):
    z=tx(40,37,"2026 Q3 − 2025 Q3 | 正值贡献收入增长，负值抵消增长",14,MUTED)
    cats=[("vas_revenue","增值服务"),("marketing_revenue","营销服务"),("fintech_revenue","金融科技及企业服务"),("other_revenue","其他")]
    total=v(d,"revenue")-v(d,"revenue","prior")
    xzero=325; scale=7.2
    z+=ln(xzero,68,xzero,382,"#98a7b8",2)
    for i,(key,label) in enumerate(cats):
        difference=v(d,key)-v(d,key,"prior")
        y=103+i*72; width=abs(difference)/100*scale
        z+=tx(40,y+8,label,15,INK)
        if difference>=0:
            z+=rect(xzero,y-15,width,29,[BLUE,TEAL,AMBER,PURPLE][i],f"{label}增量：{difference:,}百万元",3)
            z+=tx(xzero+width+14,y+5,"+"+yi(difference)+" 亿",13,INK,weight=650)
        else:
            z+=rect(xzero-width,y-15,width,29,RED,f"{label}减少：{difference:,}百万元",3)
            z+=tx(xzero+14,y+5,"−"+yi(abs(difference))+" 亿",13,INK,weight=650)
        z+=tx(972,y+5,f"{difference/total*100:+.1f}% 增量占比",12,MUTED,"end")
    z+=tx(40,404,f"集团同比增加 {yi(total)} 亿元，分部增量之和核对一致",13,INK,weight=600)
    return root_svg("谁贡献了新增收入？","四大分部2026第三季度减2025同期的人民币亿元增量及其占集团总增量比例，负贡献独立标出。",z)

def margin(d):
    l,r=235,932
    z=tx(36,39,"毛利率 = 分部毛利 / 分部收入；箭头显示百分点变化",14,MUTED)
    for pct in (0,20,40,60,80):
        x=l+(r-l)*pct/80
        z+=ln(x,63,x,356)+tx(x,380,str(pct)+"%",12,MUTED,"middle")
    keys=[("集团","gross_profit","revenue"),("增值服务","vas_gross_profit","vas_revenue"),
          ("营销服务","marketing_gross_profit","marketing_revenue"),
          ("金融科技与企业服务","fintech_gross_profit","fintech_revenue")]
    for j,(name,g,rkey) in enumerate(keys):
        y=92+j*75
        a=100*v(d,g,"prior")/v(d,rkey,"prior")
        b=100*v(d,g)/v(d,rkey)
        xa=l+(r-l)*a/80; xb=l+(r-l)*b/80
        z+=tx(30,y+5,name,14,INK,weight=600)
        z+=ln(xa,y,xb,y,"#7d9c9a",4)
        z+=cir(xa,y,8,BLUE,f"2025 Q3 {a:.2f}%")
        z+=cir(xb,y,8,TEAL,f"2026 Q3 {b:.2f}%")
        z+=tx(xa,y-15,f"{a:.1f}%",11,BLUE,"middle",600)
        z+=tx(xb,y+24,f"{b:.1f}%",11,TEAL,"middle",600)
        z+=tx(997,y+5,f"{b-a:+.1f} pp",12,INK,"end",600)
    z+=cir(468,402,6,BLUE)+tx(483,407,"2025 Q3",11,MUTED)
    z+=cir(623,402,6,TEAL)+tx(638,407,"2026 Q3",11,MUTED)
    return root_svg("毛利率：广告业务承受更大压力","各毛利率由公司披露的收入与毛利精确值计算，单位百分比；变动使用pp。其他分部亏损未画在正数刻度内。",z)

def waterfall(d):
    keys=[("营收","revenue","+"),("成本","cost_of_revenue","-"),("毛利","gross_profit","="),
          ("营销费","selling_marketing","-"),("行政费","general_admin","-"),
          ("其他净损","other_gains_net","+"),("经营利润","operating_profit","="),
          ("投资净收益","investments_net_gains","+"),("利息收入","interest_income","+"),
          ("财务费用","finance_costs","-"),("联营合营","equity_method_result","+"),
          ("税前利润","profit_before_tax","="),("所得税","income_tax_expense","-"),
          ("期内利润","period_profit","=")]
    w,h=1560,476; left,right,top,bottom=66,1526,60,366
    high=225000
    y=lambda q:bottom-(bottom-top)*q/high
    z=tx(30,29,"2026 Q3 IFRS 利润桥 · 单位：亿元",14,MUTED)
    for j in range(5):
        amount=high*j/4
        z+=ln(left,y(amount),right,y(amount))+tx(left-13,y(amount)+4,f"{amount/100:.0f}",11,MUTED,"end")
    running=0; span=(right-left)/len(keys)
    for i,(label,key,op) in enumerate(keys):
        val=v(d,key)
        if op=="=":
            if running!=val: raise ValueError(f"IFRS利润桥校验失败: {label} {running} != {val}")
            start,end=0,val
        elif i==0: start,end=0,val;running=val
        else:
            delta=-val if op=="-" else val
            start,end=running,running+delta;running=end
        upper=max(start,end);lower=min(start,end)
        bh=y(lower)-y(upper)
        x=left+i*span+span*.16
        color=TEAL if op=="=" else BLUE if i==0 else RED if end<start else AMBER
        z+=rect(x,y(upper),span*.65,max(bh,1.5),color,f"{label}: {val:,} 百万元，累计{running:,} 百万元",2)
        lab=("+ " if end>start and i>0 and op!="=" else "− " if end<start else "")+yi(abs(val))
        z+=tx(x+span*.325,y(upper)-10,lab,10.5,INK,"middle",650)
        z+=tx(x+span*.325,bottom+25,label,11,MUTED,"middle")
    if running!=v(d,"period_profit"):raise ValueError("利润桥终点错误")
    z+=tx(69,441,"毛利、经营利润、税前利润及期内利润为校验节点；这是一张利润表桥，不是现金流向图。",13,MUTED)
    return root_svg("从收入到期内利润的14站完整桥接","所有调减和收益严格取自2026第三季度IFRS利润表，起点207336百万元，终点65139百万元。",z,w,h)

def cash(d):
    c=d["supplementary"]["quarterly_cash_flow_rounded"]
    rows=[("经营活动现金流",c["operating"]),("资本开支付款", -c["capex_payments"]),
          ("媒体内容付款",-c["media_payments"]),("租赁负债付款",-c["lease_payments"]),
          ("自由现金流",c["free_cash_flow"])]
    z=tx(35,40,"2026 Q3 | 公司按0.1十亿元披露的约数；此处转换为亿元",14,MUTED)
    xzero=814;scale=.84
    z+=ln(xzero,60,xzero,374,"#718796",2)
    for i,(label,amount) in enumerate(rows):
        y=92+i*66; val=amount/100
        z+=tx(35,y+6,label,15,INK,weight=650 if i==4 else 400)
        if val>=0:
            z+=rect(xzero,y-14,max(val*scale,2),29,TEAL,label)
            z+=tx(xzero+val*scale+12,y+5,"约 +"+f"{val:.0f}",13,INK,weight=600)
        else:
            width=abs(val)*scale
            z+=rect(xzero-width,y-14,width,29,RED if i==4 else BLUE,label)
            z+=tx(xzero-width-12,y+5,"约 −"+f"{abs(val):.0f}",13,INK,"end",600)
    if c["operating"]-c["capex_payments"]-c["media_payments"]-c["lease_payments"]!=c["free_cash_flow"]:
        raise ValueError("自由现金流等式不守恒")
    z+=tx(35,403,"注：Q3应计资本开支814.33亿元另见 p.12；此图只使用现金付现口径，避免重复计算。",12,MUTED)
    return root_svg("自由现金流为什么转为负691亿元？","经营现金流减去资本开支付款、媒体内容付款、租赁付款得到自由现金流。各金额为公司披露的约数。",z)

def liquidity(d):
    a=d["supplementary"]["liquidity"]
    cash=[a["cash_and_equivalents"][i]+a["term_deposits_and_others"][i] for i in range(2)]
    debt=[a["borrowings"][i]+a["notes_payable"][i] for i in range(2)]
    for i in range(2):
        if cash[i]-debt[i]!=a["net_cash_debt"][i]:raise ValueError("资产减债务核对失败")
    z=tx(40,40,"当期期末资金与债务：2026 Q2 → Q3 | 亿元",14,MUTED)
    maximum=570000; l,r=215,1000; scale=(r-l)/maximum
    rows=[("现金及类现金",cash),("借款及票据债务",debt)]
    for j,(name,vals) in enumerate(rows):
        ytop=80+j*125
        z+=tx(35,ytop+45,name,15,INK,weight=650)
        for i,val in enumerate(vals):
            yy=ytop+i*45; width=val*scale
            z+=rect(l,yy,width,28,[BLUE,TEAL][i],f"{name} {['Q2','Q3'][i]}：{val:,} 百万元")
            z+=tx(l+width+10,yy+19,yi(val)+" 亿",12,INK,weight=650)
    z+=rect(48,358,13,13,BLUE)+tx(69,369,"2026-06-30",12,MUTED)
    z+=rect(246,358,13,13,TEAL)+tx(267,369,"2026-09-30",12,MUTED)
    z+=tx(48,408,f"净现金/（债务）：Q2 +{yi(a['net_cash_debt'][0])} 亿 → Q3 {yi(a['net_cash_debt'][1])} 亿",16,INK,weight=700)
    return root_svg("现金储备仍大，但净现金变净负债","现金及定期存款等减借款及票据，余额从2026年6月底净现金转为9月底净债务，单位人民币亿元。",z)

def capex(d):
    yvals=[v(d,"accrual_capex","prior"),d["supplementary"]["q2_2026"]["accrual_capex"],v(d,"accrual_capex")]
    labels=["2025 Q3","2026 Q2","2026 Q3"]
    maximum=90000;l,r,t,b=120,975,71,340
    z=axis(l,r,t,b,maximum)
    for i,value in enumerate(yvals):
        x=235+i*292; bh=(b-t)*value/maximum
        z+=rect(x,b-bh,123,bh,[BLUE,AMBER,TEAL][i],f"{labels[i]}应计资本开支：{value:,} 百万元")
        z+=tx(x+61,b-bh-15,yi(value)+" 亿",17,INK,"middle",700)
        z+=tx(x+61,b+29,labels[i],14,INK,"middle",600)
    z+=tx(85,403,"应计资本开支，与当季实际资本开支付款（约651亿元）为不同统计口径。",12,MUTED)
    return root_svg("资本开支陡升：Q3同比增约527%","2025第三季、2026第二季及第三季应计资本开支：12983、52784和81433百万元，资料源于财报p.12。",z)

FIGURES=[
("growth","收入增长，经营利润为何回落？","两期独立季度主要利润指标对比；分清IFRS和Non-IFRS。",[1,5],growth,1040,426),
("segments","谁占据收入盘子？","四项分部收入堆叠；图内合计与集团收入一致。",[6],segments,1040,426),
("drivers","新增收入从哪里来？","分部增量与集团144.67亿元收入增长完整勾稽。",[6],drivers,1040,426),
("margins","不同业务利润率走向一致吗？","按分部收入与毛利计算；金额、百分比及pp分开标识。",[7],margin,1040,426),
("profit-bridge","利润表逐层扣除与加回","14节点全年口径错误被排除：本图为独立2026 Q3，起终点核对通过。",[5,18],waterfall,1560,476),
("free-cash-flow","负现金流从何而来？","约数口径的Q3付现桥；不将应计资本开支误当付现额。",[17],cash,1040,426),
("liquidity","现金负债结构发生什么改变？","Q2期末与Q3期末时点对比，不与季度流量混画。",[12,17],liquidity,1040,426),
("capex","算力投资的三个观察点","独立季度应计资本开支；2025Q3与2026Q2、Q3标明日期。",[12],capex,1040,426)
]
def build_figures(report,out_dir):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    result=[]
    for slug,title,caption,pages,fn,w,h in FIGURES:
        xml=fn(report)
        (out_dir/(slug+".svg")).write_text(xml,encoding="utf-8")
        result.append(dict(slug=slug,title=title,caption=caption,pages=pages,filename=slug+".svg",width=w,height=h))
    return result
