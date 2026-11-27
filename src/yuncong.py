"""Yuncong/CloudWalk 2026 Q3: cent-exact reconciliations and accessible standalone SVGs.

'prior' is 2025 Jan-Sep for flows and 2025-12-31 for balance-sheet stocks.
'current' is 2026 Jan-Sep for flows and 2026-09-30 for stocks.
All stored monetary figures are integer CNY fen (cents); 1 亿元 = 10^10 fen.
"""
from decimal import Decimal
from html import escape
from pathlib import Path
from .charts import root_svg, rect, tx, ln, BLUE, TEAL, RED, AMBER, INK, MUTED, GRID

HUNDRED_MILLION = 10_000_000_000


def amount(r, name, period="current"):
    return r["values"][name]["values"][period]


def yi(v):
    return v / HUNDRED_MILLION


def fenyuan(v):
    if v is None:
        return "—"
    sign = "-" if v < 0 else ""
    a = abs(v)
    return f"{sign}{a // 100:,}.{a % 100:02d}"


def pct_delta(before, after):
    if before is None or after is None or before <= 0:
        return "不适用"
    return f"{(after / before - 1) * 100:+.2f}%"


def reconciliation_errors(r):
    """Hard-fail on inaccurate source transcriptions, statement and time-base identities."""
    v, errs = r["values"], []
    def n(k, p):
        return v[k]["values"][p]
    def eq(a, b, label):
        if a != b:
            errs.append(f"{label}: expected {b}; got {a}")
    for key, m in v.items():
        for p in ("prior", "current"):
            source = m.get("source_values", {}).get(p)
            if source is not None:
                eq(int(Decimal(source) * 100), n(key, p), f"raw cent conversion {key}/{p}")
        if m["kind"] == "derived" and key != "gross_profit":
            errs.append("Unexpected derived entry: " + key)
        if m["kind"] == "reported" and not m.get("source_values"):
            errs.append("Missing original source amount: " + key)
        if m.get("period_basis") not in ("nine_month", "quarter", "balance"):
            errs.append("Missing period_basis for " + key)
    for p in ("prior", "current"):
        eq(n("revenue", p) - n("cost_of_revenue", p), n("gross_profit", p),
           "gross profit calculated from two disclosed items " + p)
        eq(n("revenue", p)-n("total_operating_cost", p)+
           sum(n(k,p) for k in ("other_income","investment_income","fair_value_income",
                                "credit_impairment","asset_impairment","asset_disposal_income")),
           n("operating_profit",p), "operating-profit bridge " + p)
        eq(n("operating_profit",p)+n("nonoperating_income",p)-n("nonoperating_expense",p),
           n("profit_before_tax",p),"pre-tax bridge " + p)
        eq(n("profit_before_tax",p)-n("income_tax_expense",p),n("period_profit",p),
           "tax bridge " + p)
        eq(n("parent_profit",p)+n("minority_profit",p),n("period_profit",p),
           "parent/minority profit " + p)
        eq(n("operating_cash_inflows",p)-n("operating_cash_outflows",p),
           n("operating_cash_flow",p),"cash from operations " + p)
        fx = n("cash_fx",p) if n("cash_fx",p) is not None else 0
        eq(sum(n(k,p) for k in ("operating_cash_flow","investing_cash_flow","financing_cash_flow"))+fx,
           n("cash_change",p),"cash-flow categories plus FX " + p)
        eq(n("cash_open",p)+n("cash_change",p),n("cash_close",p),
           "cash opening + change = closing " + p)
        eq(n("balance_total_assets",p),
           n("balance_liabilities",p)+n("balance_equity",p),
           "assets = total liabilities + total equity " + p)
        eq(n("balance_parent_equity",p)+n("balance_minority_equity",p),
           n("balance_equity",p),"equity attribution " + p)
    delta_operating = n("operating_profit","current") - n("operating_profit","prior")
    deltas = [n("revenue","current")-n("revenue","prior"),
              n("total_operating_cost","prior")-n("total_operating_cost","current")]
    deltas += [n(k,"current")-n(k,"prior") for k in
               ("other_income","investment_income","fair_value_income",
                "credit_impairment","asset_impairment","asset_disposal_income")]
    eq(sum(deltas),delta_operating,"year-on-year operating profit change bridge")
    return errs


def bars(r, title, question, keys, pages, *, basis="nine_month", percent=False, width=1120):
    """Two-period horizontal bars: zero-baseline, safe for positive and negative values."""
    rows=[]
    for key in keys:
        m=r["values"][key]
        if m["period_basis"] != basis:
            raise ValueError(f"Wrong time basis for {key}")
        a,b=amount(r,key,"prior"),amount(r,key,"current")
        if percent:
            if key=="gross_profit":
                a=100*a/amount(r,"revenue","prior")
                b=100*b/amount(r,"revenue","current")
            elif key=="period_profit":
                a=100*a/amount(r,"revenue","prior")
                b=100*b/amount(r,"revenue","current")
            elif key=="parent_profit":
                a=100*a/amount(r,"revenue","prior")
                b=100*b/amount(r,"revenue","current")
            else:
                a=100*a/amount(r,"revenue","prior")
                b=100*b/amount(r,"revenue","current")
        else:
            a,b=yi(a),yi(b)
        rows.append((m["label"],a,b))
    vals=[x for _label,a,b in rows for x in (a,b)]
    left,right=358,width-76
    lo=min(0,min(vals));hi=max(0,max(vals))
    padding=max(.18,(hi-lo)*.12)
    lo-=padding if lo<0 else 0
    hi+=padding
    if hi==lo:hi=lo+1
    xx=lambda v: left+(v-lo)/(hi-lo)*(right-left)
    height=145+len(rows)*94
    ybase=72
    s=tx(27,36,"百分比 %（计算值）" if percent else "人民币亿元",13,MUTED)
    for k in range(6):
        v=lo+(hi-lo)*k/5
        x=xx(v)
        s+=ln(x,54,x,height-75,GRID if abs(v)>.001 else "#9ea8b5",1 if abs(v)>.001 else 2)
        s+=tx(x,height-50,f"{v:.0f}" if percent else f"{v:.1f}",11,MUTED,"middle")
    for idx,(label,a,b) in enumerate(rows):
        y=ybase+idx*94
        s+=tx(25,y+28,label[:23],14,INK,weight=650)
        for j,(value,period,color) in enumerate(((a,"2025年1—9月" if basis=="nine_month" else "2025年末",BLUE),
                                                (b,"2026年1—9月" if basis=="nine_month" else "2026年9月末",TEAL))):
            yy=y+j*32
            start,end=xx(0),xx(value)
            s+=rect(min(start,end),yy,abs(end-start),22,color,
                    f"{label} {period}: {value:.2f}"+("%" if percent else "亿元"),3)
            anchor="start" if value>=0 else "end"
            s+=tx(end+(6 if value>=0 else -6),yy+16,
                  f"{value:+.2f}" if value<0 else f"{value:.2f}",
                  12,INK,anchor,650)
    s+=rect(25,height-29,12,12,BLUE)+tx(45,height-18,"2025同期/年末",12,MUTED)
    s+=rect(215,height-29,12,12,TEAL)+tx(235,height-18,"2026同期/9月末",12,MUTED)
    return root_svg(title,question+"。所有柱形以零为基线；标签注明比较期。",s,width,height),height


def impact_figure(r):
    labels=[("营业收入减少","revenue",-1),
            ("营业总成本减少","total_operating_cost",1),
            ("其他收益变化","other_income",-1),
            ("投资收益变化","investment_income",-1),
            ("公允价值变化","fair_value_income",-1),
            ("信用减值变化","credit_impairment",-1),
            ("资产减值变化","asset_impairment",-1),
            ("资产处置收益变化","asset_disposal_income",-1)]
    contributions=[]
    for label,key,reverse in labels:
        # Revenue and all income/impairment result lines: new - old.
        # Total operating costs: old - new.
        delta=(amount(r,key,"prior")-amount(r,key,"current")) if reverse==1 else (
                amount(r,key,"current")-amount(r,key,"prior"))
        contributions.append((label,yi(delta)))
    change=yi(amount(r,"operating_profit")-amount(r,"operating_profit","prior"))
    if abs(sum(v for _,v in contributions)-change)>1e-9:
        raise ValueError("non-reconciling operating profit impact bridge")
    W,H=1180,565;left,right,top,bottom=370,1110,75,460
    lo=min(-2.8,min(v for _,v in contributions)*1.15)
    hi=max(3.9,max(v for _,v in contributions)*1.15)
    xx=lambda v:left+(v-lo)/(hi-lo)*(right-left)
    s=tx(30,36,"对2026年前三季度营业利润同比变化的影响 · 亿元",13,MUTED)
    for i in range(8):
        tick=lo+(hi-lo)*i/7
        x=xx(tick)
        s+=ln(x,top-12,x,bottom,GRID)
        s+=tx(x,bottom+23,f"{tick:.1f}",11,MUTED,"middle")
    s+=ln(xx(0),top-20,xx(0),bottom,"#81919d",2)
    for i,(label,v) in enumerate(contributions):
        y=top+i*45
        s+=tx(24,y+17,label,13,INK,weight=550)
        x0,xv=xx(0),xx(v)
        s+=rect(min(x0,xv),y,abs(xv-x0),26,TEAL if v>=0 else RED,
                f"{label} 对营业利润的影响 {v:+.4f}亿元",3)
        s+=tx(xv+(8 if v>=0 else -8),y+18,f"{v:+.2f}",12,INK,"start" if v>=0 else "end",650)
    s+=tx(28,526,f"经勾稽：上述变化合计 {change:+.3f} 亿元，营业亏损从 -3.157 亿元收窄至 -1.018 亿元。",14,INK,weight=650)
    s+=tx(28,549,"此图为利润表项目的同比影响，不是现金流；减值变化亦不表示实际收款。",11,MUTED)
    return root_svg("营业亏损为何收窄？8项同比影响逐项相加",
                    "2025年1—9月至2026年1—9月营业利润改善额逐项可勾稽：收入、营业总成本及6类其他收益/减值。",s,W,H),W,H


def figures(r, folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    items=[]
    def add(slug,title,question,keys,pages,**kwargs):
        xml,h=bars(r,title,question,keys,pages,**kwargs)
        (folder/(slug+".svg")).write_text(xml,encoding="utf-8")
        items.append(dict(slug=slug,title=title,caption=question,pages=pages,
                          filename=slug+".svg",width=1120,height=h))
    add("growth","收入大幅下滑，毛利额也在下降","2025/2026年同期九个月：收入、计算毛利和归母净利润；归母仍为负数。",
        ["revenue","gross_profit","parent_profit"],[9,10])
    add("quality","毛利率改善，但销售管理研发三费率偏高","毛利率=毛利润/收入；费用率=单项费用/收入；比例为计算值。",
        ["gross_profit","selling_expense","administrative_expense","rd_expense"],[9],percent=True)
    add("expenses","三项期间费用怎样下降？","销售、管理、研发费用由2025同期水平大幅收缩，注意不是全部现金支出。",
        ["selling_expense","administrative_expense","rd_expense"],[9])
    svg,w,h=impact_figure(r)
    (folder/"profit-impact.svg").write_text(svg,encoding="utf-8")
    items.append(dict(slug="profit-impact",title="营业利润同比改善到底来自哪里？",
                      caption="8个利润表项目同比变化精确相加，按金额影响展示正负；不是收入流向图。",
                      pages=[9,10],filename="profit-impact.svg",width=w,height=h))
    add("cash-flow","现金流三分法：经营为负、筹资为正",
        "2025/2026年前三季度经营、投资、筹资现金净额；现金流与利润不同。",
        ["operating_cash_flow","investing_cash_flow","financing_cash_flow"],[12,13])
    add("collections","回款减少，采购现金支出增加",
        "现金流量表的销售商品及提供劳务收到的现金、采购商品及接受劳务支付的现金；不等同于同期开票营收和成本。",
        ["sales_cash_received","goods_cash_paid","employee_cash_paid"],[12])
    add("balance","存货、短期借款与合同负债怎样变化？",
        "资产负债表时点比较：2025年12月末与2026年9月末，绝非九个月同比。",
        ["balance_inventory","balance_short_debt","balance_contract_liabilities","balance_cash","balance_contract_assets"],
        [6,7],basis="balance")
    return items


def kpi_cards(report):
    v=lambda k,p="current":amount(report,k,p)
    margin=lambda p:(v("gross_profit",p)/v("revenue",p))*100
    delta_margin=margin("current")-margin("prior")
    loss_improve=(abs(v("parent_profit","prior"))-abs(v("parent_profit")))/abs(v("parent_profit","prior"))*100
    rows=[
        ("营业收入",f"{yi(v('revenue')):.3f}","亿元","同比 -63.25%","2026年1—9月"),
        ("归母净利润",f"{yi(v('parent_profit')):.3f}","亿元",f"亏损收窄 {loss_improve:.1f}%","不等于扭亏"),
        ("经营现金流",f"{yi(v('operating_cash_flow')):.3f}","亿元","由正转负","2025同期 +0.313亿元"),
        ("毛利率（计算）",f"{margin('current'):.2f}","%",f"同比 {delta_margin:+.2f} pp","毛利额反而下降")
    ]
    return "".join(
        '<div class="kpi-card"><span class="label">'+escape(name)+'</span><strong>'+
        escape(value)+'<small style="display:inline;font-size:13px;margin-left:5px">'+escape(unit)+'</small></strong>'+
        '<span class="change '+("neg" if ("-" in change or value.startswith("-")) else "")+'">'+escape(change)+'</span>'+
        '<small>'+escape(note)+'</small></div>'
        for name,value,unit,change,note in rows
    )


def metric_tables(report, source_link):
    parts=[]
    for basis, heading, prior, current in (
        ("nine_month","前三季度合并利润表及现金流量表 · 原始人民币元","2025年1—9月","2026年1—9月"),
        ("quarter","第三季度单季 · 报告仅披露本期精确额","2025年7—9月","2026年7—9月"),
        ("balance","资产负债表 · 两个时点比较（非同比）","2025年12月31日","2026年9月30日")):
        rows=[]
        for key,m in report["values"].items():
            if m["period_basis"] != basis:
                continue
            prev,cur=m["values"]["prior"],m["values"]["current"]
            def raw(p,v):
                if m["kind"]=="derived":
                    return fenyuan(v)+"（计算）"
                return m["source_values"][p] if m["source_values"][p] is not None else "—"
            change="—" if prev is None else pct_delta(prev,cur)
            if basis=="balance" and prev is not None:
                change += "（较2025年末）"
            if prev is not None and prev < 0:
                change="N/M（前期为负值）"
            if key=="quarter_revenue":
                change="披露同比 -83.75%（不反推基数）"
            page=m["page"]
            rows.append('<tr data-metric-row="'+escape(m["label"]+" "+key)+'"><th scope="row">'+escape(m["label"])+
                        '</th><td>'+escape(raw("prior",prev))+'</td><td>'+escape(raw("current",cur))+
                        '</td><td>'+escape(change)+'</td><td><a target="_blank" rel="noopener noreferrer" href="'+
                        source_link(report,page)+'">p.'+str(page)+'</a></td></tr>')
        parts.append('<div class="table-wrap"><table><caption>'+escape(heading)+
          '</caption><thead><tr><th scope="col">指标</th><th scope="col">'+escape(prior)+
          '</th><th scope="col">'+escape(current)+
          '</th><th scope="col">同比／变动说明</th><th scope="col">财报页码</th></tr></thead><tbody>'+
          "".join(rows)+'</tbody></table></div>')
    return "".join(parts)


def cross_filing_block(r):
    if not r.get("cross_filings"):
        return ""
    a=['<section class="block" id="cross-filings"><div class="section-head"><div>'+
       '<p class="kicker">CONTEXT / OTHER PRIMARY DISCLOSURES</p>'+
       '<h2>跨期证据：年度报告、半年报与经营策略</h2>'+
       '<p>下列是另外期间披露的背景，不属于2026年9月末数据；不能与第三季度直接拼成同比。</p>'+
       '</div></div><div class="method-grid">']
    for item in r["cross_filings"]:
        a.append('<div><h3><a href="'+escape(item["url"],quote=True)+
                 '" target="_blank" rel="noopener noreferrer">'+escape(item["title"])+
                 '</a></h3><p>'+escape(item["date"])+'</p><p>'+escape(item["note"])+'</p></div>')
    a.append('</div></section>')
    return "".join(a)
