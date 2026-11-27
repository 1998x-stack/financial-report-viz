"""Moutai-specific exact-integer reconciliation and standalone vector charts."""
from .charts import root_svg, rect, tx, ln, BLUE, TEAL, RED, INK, MUTED
from decimal import Decimal
def reconciliation_errors(r):
    v=r["values"]
    errors=[]
    def n(k,p): return v[k]["values"][p]
    def eq(a,b,label):
        if a!=b: errors.append(label)
    for k,m in v.items():
        for p in ("prior","current"):
            raw=m["source_values"][p]
            if raw is not None:
                factor=1000000 if m["source_unit"]=="CNY_10000" else 100
                eq(int(Decimal(raw)*factor),n(k,p),"source unit "+k+"/"+p)
    for p in ("prior","current"):
        eq(n("profit_before_tax",p)-n("income_tax_expense",p),n("period_profit",p),"income tax bridge "+p)
        eq(n("parent_profit",p)+n("minority_profit",p),n("period_profit",p),"profit ownership "+p)
        eq(n("assets",p),n("liabilities",p)+n("equity",p),"balance sheet "+p)
        eq(sum(n(k,p) for k in ("operating_cash_flow","investing_cash_flow","financing_cash_flow","cash_fx")),n("cash_change",p),"cash flow bridge "+p)
        eq(n("cash_open",p)+n("cash_change",p),n("cash_close",p),"cash balance "+p)
    c=lambda k:n(k,"current")
    eq(c("moutai_liquor")+c("series_liquor"),c("direct_sales")+c("wholesale"),"product/channel totals")
    eq(c("domestic")+c("overseas"),c("direct_sales")+c("wholesale"),"geography/channel totals")
    if c("i_moutai")>c("direct_sales"): errors.append("platform exceeds direct sales")
    return errors

def charts(r, folder):
    folder.mkdir(parents=True,exist_ok=True)
    v=r["values"]
    result=[]
    def amount(k,p):
        x=v[k]["values"][p]
        return None if x is None else x/1e10
    def add(slug,title,caption,pages,body):
        name=slug+".svg"
        (folder/name).write_text(root_svg(title,caption,body),encoding="utf-8")
        result.append(dict(slug=slug,filename=name,title=title,caption=caption,pages=pages))
    def bars(slug,title,caption,keys,pages,derived=None,current_only=False,point=False):
        entries=[]
        for k in keys:
            for p in (("current",) if current_only else ("prior","current")):
                a=amount(k,p)
                if a is not None: entries.append((v[k]["label"],p,a))
        if derived: entries=derived
        lo=min(0,min(a for _,_,a in entries)); hi=max(0,max(a for _,_,a in entries))
        span=max(hi-lo,1); lo-=span*.08 if lo<0 else 0; hi+=span*.12
        x=lambda a: 300+(a-lo)/(hi-lo)*650
        s=tx(300,26,"人民币亿元" if not derived else "百分比（%）",14,MUTED)
        s+=ln(x(0),42,x(0),380,MUTED)
        dy=min(54,320/len(entries))
        for i,(label,p,a) in enumerate(entries):
            y=48+i*dy
            period=("2025年末" if point else "2025年1–9月") if p=="prior" else ("2026年9月末" if point else "2026年1–9月")
            s+=tx(12,y+15,label+" · "+period,12,INK)
            s+=rect(min(x(0),x(a)),y,abs(x(a)-x(0)),max(12,dy-7),BLUE if p=="prior" else TEAL,title=f"{label} {period}: {a:.2f}")
            s+=tx(x(a)+(8 if a>=0 else -8),y+15,f"{a:.2f}",12,INK,"start" if a>=0 else "end")
        add(slug,title,caption,pages,s)
    bars("growth","收入增长是否带来利润增长？","营业收入与归母净利润，同期九个月比较。",[ "revenue","parent_profit"],[8,9])
    bars("margin","毛利率下降了多少？","计算值：营业毛利率=(营业收入-营业成本)/营业收入；归母利润率=归母净利润/营业收入。",[],[8,9],[(label,p,(1-amount("cost_of_revenue",p)/amount("revenue",p))*100 if label=="营业毛利率" else amount("parent_profit",p)/amount("revenue",p)*100) for label in ("营业毛利率","归母利润率") for p in ("prior","current")])
    bars("cost","哪些成本费用变化值得追踪？","营业成本、销售及管理费用、税金及附加。",["cost_of_revenue","selling_marketing","general_admin","tax_surcharge"],[8])
    bars("product","酒类收入由什么构成？","2026年前三季度主营业务收入，分产品；未披露上年同期值。",["moutai_liquor","series_liquor"],[3],current_only=True)
    bars("channel","直销和批发各占多少？","主营业务按渠道拆分；i茅台是平台指标，不与渠道合计重复相加。",["direct_sales","wholesale","i_moutai"],[3],current_only=True)
    bars("geography","海外收入规模有多大？","主营收入按地区拆分；非终端消费地推断。",["domestic","overseas"],[3],current_only=True)
    bars("cash","现金流来自哪类活动？","合并现金流包含财务公司，经营现金流不等于白酒回款。",["operating_cash_flow","investing_cash_flow","financing_cash_flow"],[3,11,12])
    bars("balance","资产负债结构如何变化？","时点比较：2025年末与2026年9月末，不是同比。",["assets","liabilities","equity","contract_liabilities"],[2,7,8],point=True)
    return result
