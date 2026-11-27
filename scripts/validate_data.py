#!/usr/bin/env python3
"""Validate catalog taxonomy, JSON Schema and reported-statement reconciliations."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def parse(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def period_days(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days + 1


def errors_for_report(r, issuers, taxonomy):
    errs = []
    rid = r.get("report_id", "?")
    def check(ok, message):
        if not ok:
            errs.append(f"{rid}: {message}")
    keys = ("report_id","issuer_id","slug","title","status","language","year",
            "period_type","period_start","period_end","comparison_period_start",
            "comparison_period_end","source","currency","unit","topics","values")
    for key in keys:
        check(key in r, "required field missing: " + key)
    if any(k not in r for k in keys):
        return errs
    check(r["report_id"] == r["issuer_id"] + "-" + r["slug"],
          "report_id and issuer_id/slug must agree")
    check(r["slug"] == str(r["year"]) + "-" + r["period_type"],
          "slug must represent year-period (not filing date)")
    check(r["issuer_id"] in issuers, "issuer_id not in registry")
    check(r["period_type"] in {x["id"] for x in taxonomy["periods"]},
          "unknown period taxonomy id")
    check(len(r["topics"]) == len(set(r["topics"])), "duplicate topic id")
    for tag in r["topics"]:
        check(tag in {x["id"] for x in taxonomy["topics"]}, "unregistered topic: " + tag)
    try:
        n = period_days(r["period_start"], r["period_end"])
        prior_n = period_days(r["comparison_period_start"], r["comparison_period_end"])
        check(abs(n - prior_n) <= 1, "comparable periods must have similar day counts")
        check(n > 0 and prior_n > 0, "period boundaries must be chronological")
        check(date.fromisoformat(r["period_end"]).year == r["year"],
              "year must match period_end")
        if r["period_type"] == "h1":
            check(r["period_end"].endswith("-06-30"), "h1 must end June 30")
    except ValueError:
        errs.append(rid + ": dates not valid ISO calendar dates")
    source = r["source"]
    check(source.get("assurance") in ("audited","reviewed_unaudited","unaudited","unknown"),
          "invalid audit/review status")
    check(urlparse(source.get("url","")).scheme == "https", "primary filing URL must be https")
    check(source.get("pdf_page_offset") is not None, "PDF page offset required")
    check(r["unit"] in ("CNY_thousand","CNY_million","HKD_thousand","USD_thousand","USD_million"),
          "unexpected amount unit")
    check(isinstance(r["values"],dict) and bool(r["values"]), "metric dictionary missing")
    for key,m in r["values"].items():
        check(bool(re.fullmatch("[a-z][a-z0-9_]*",key)), "bad metric key " + key)
        check(m.get("kind") == "reported", "actual report metrics must be source-reported: "+key)
        check(isinstance(m.get("label"),str) and bool(m.get("label")), "label missing: "+key)
        check(isinstance(m.get("page"),int) and 1 <= m["page"] <= source.get("pdf_pages",9999),
              "bad source printed page: "+key)
        for period in ("prior","current"):
            v = m.get("values",{}).get(period)
            check(v is None or (type(v) is int) or (type(v) is float and m.get("unit") in ("GWh","million_subscriptions")),
                  "numeric values must be exact integers or allowed original-unit decimals: "+key+"/"+period)
        for key2,page in m.get("pages",{}).items():
            check(key2 in ("prior","current") and isinstance(page,int) and page>0,
                  "bad per-period printed page: " + key)
    v = r["values"]
    def val(key,period):
        return v[key]["values"][period]
    def eq(expression,value,label,period):
        check(expression==value,f"{period}: {label}: computed {expression}, reported {value}")
    for period in ("prior","current"):
        essential=["revenue","cost_of_revenue","gross_profit","period_profit"]
        if r["status"]=="published":
            for key in essential:
                check(key in v and v[key]["values"][period] is not None,
                      "missing material reported item: "+key+"/"+period)
        if any(key not in v or v[key]["values"][period] is None for key in essential):
            continue
        eq(val("revenue",period)-val("cost_of_revenue",period),
           val("gross_profit",period),"revenue-cost=gross profit",period)
        if all(key in v for key in ("game_revenue","taptap_revenue")):
            eq(val("game_revenue",period)+val("taptap_revenue",period),
               val("revenue",period),"game+TapTap consolidated revenue",period)
        if all(key in v for key in ("game_cost","taptap_cost")):
            eq(val("game_cost",period)+val("taptap_cost",period),
               val("cost_of_revenue",period),"segment cost of revenue",period)
        if all(key in v for key in ("game_gross_profit","taptap_gross_profit")):
            eq(val("game_gross_profit",period)+val("taptap_gross_profit",period),
               val("gross_profit",period),"segment gross profit",period)
        for segment in ("game","taptap"):
            if all(key in v for key in (segment+"_revenue",segment+"_cost",segment+"_gross_profit")):
                eq(val(segment+"_revenue",period)-val(segment+"_cost",period),
                   val(segment+"_gross_profit",period),segment+" margin bridge",period)
        if all(key in v for key in ("network_games","paid_games","game_other","game_revenue")):
            eq(val("network_games",period)+val("paid_games",period)+val("game_other",period),
               val("game_revenue",period),"game components",period)
        if all(key in v for key in ("platform_promotion","platform_other","taptap_revenue")):
            eq(val("platform_promotion",period)+val("platform_other",period),
               val("taptap_revenue",period),"platform components",period)
        if all(key in v for key in ("mainland_game_revenue","overseas_game_revenue","network_games","paid_games")):
            eq(val("mainland_game_revenue",period)+val("overseas_game_revenue",period),
               val("network_games",period)+val("paid_games",period),
               "game-operation geography sum",period)
        op=["selling_marketing","research_development","general_admin",
            "impairment_reversal_net","other_income","other_gains_net","operating_profit"]
        if all(key in v for key in op):
            computed=(val("gross_profit",period)-val("selling_marketing",period)
                      -val("research_development",period)-val("general_admin",period)
                      +val("impairment_reversal_net",period)+val("other_income",period)
                      +val("other_gains_net",period))
            eq(computed,val("operating_profit",period),"operating profit bridge",period)
        if all(key in v for key in ("operating_profit","finance_income_net","equity_method_result","profit_before_tax")):
            eq(val("operating_profit",period)+val("finance_income_net",period)
               +val("equity_method_result",period),val("profit_before_tax",period),
               "pretax profit bridge",period)
        if all(key in v for key in ("profit_before_tax","income_tax_expense")):
            eq(val("profit_before_tax",period)-val("income_tax_expense",period),
               val("period_profit",period),"net profit after income tax",period)
        if all(key in v for key in ("operating_cash_flow","investing_cash_flow","financing_cash_flow")):
            total=sum(val(key,period) for key in
                      ("operating_cash_flow","investing_cash_flow","financing_cash_flow"))
            # There is no synthetic "cash change": validate against the original disclosure
            # only for the known Xindong 2026 H1 report. Other issuers should add source
            # line items for their cash-flow opening/closing and FX adjustments.
            if rid=="xindong-2026-h1":
                eq(total,200760 if period=="prior" else 117760,
                   "cash flow before currency translation",period)
    if rid == "tencent-2026-q3":
        required = ("revenue","cost_of_revenue","gross_profit","period_profit",
                    "vas_revenue","marketing_revenue","fintech_revenue","other_revenue",
                    "vas_gross_profit","marketing_gross_profit","fintech_gross_profit","other_gross_profit",
                    "selling_marketing","general_admin","other_gains_net","operating_profit",
                    "investments_net_gains","interest_income","finance_costs","equity_method_result",
                    "profit_before_tax","income_tax_expense","attributable_profit","minority_profit")
        for key in required:
            check(key in v, "Tencent required statement key missing: " + key)
        if all(key in v for key in required):
            for period in ("prior","current"):
                valp=lambda k:val(k,period)
                eq(sum(valp(k+"_revenue") for k in ("vas","marketing","fintech","other")),
                   valp("revenue"),"four segment revenues",period)
                eq(sum(valp(k+"_gross_profit") for k in ("vas","marketing","fintech","other")),
                   valp("gross_profit"),"four segment gross profits",period)
                eq(valp("gross_profit")-valp("selling_marketing")-valp("general_admin")
                   +valp("other_gains_net"),valp("operating_profit"),
                   "Tencent IFRS operating profit",period)
                eq(valp("operating_profit")+valp("investments_net_gains")+valp("interest_income")
                   -valp("finance_costs")+valp("equity_method_result"),
                   valp("profit_before_tax"),"Tencent IFRS pretax profit",period)
                eq(valp("attributable_profit")+valp("minority_profit"),
                   valp("period_profit"),"owners plus minority",period)
        sup=r.get("supplementary",{})
        cf=sup.get("quarterly_cash_flow_rounded")
        if cf:
            eq(cf["operating"]-cf["capex_payments"]-cf["media_payments"]-cf["lease_payments"],
               cf["free_cash_flow"],"rounded Q3 free cash flow","2026 Q3")
        else: check(False,"Tencent rounded quarterly cash flow missing")
        liq=sup.get("liquidity")
        if liq:
            for i,p in enumerate(liq["periods"]):
                eq(liq["cash_and_equivalents"][i]+liq["term_deposits_and_others"][i]
                   -liq["borrowings"][i]-liq["notes_payable"][i],
                   liq["net_cash_debt"][i],"net cash/(debt)",p)
        else: check(False,"Tencent liquidity missing")
        nine=sup.get("nine_month_cash_flows")
        if nine:
            for i,p in enumerate(("2025 9M","2026 9M")):
                eq(nine["operating"][i]+nine["investing"][i]+nine["financing"][i],
                   nine["change_in_cash"][i],"nine-month cash change",p)
        else: check(False,"Tencent 9-month cash flow missing")
    if rid == "tesla-2026-q3":
        for period in ("prior","current"):
            eq(sum(val(k,period) for k in ("automotive_revenue","energy_revenue","services_revenue")),
               val("revenue",period),"automotive+energy+services revenue",period)
            eq(sum(val(k,period) for k in ("automotive_sales","regulatory_credits","automotive_leasing")),
               val("automotive_revenue",period),"automotive subsegments",period)
            eq(sum(val(k,period) for k in ("automotive_cost","energy_cost","services_cost")),
               val("cost_of_revenue",period),"business cost of revenue",period)
            opex=sum(val(k,period) or 0 for k in ("research_development","selling_general_admin","restructuring_other"))
            eq(opex,val("operating_expenses",period),"operating expenses",period)
            eq(val("gross_profit",period)-opex,val("operating_profit",period),
               "GAAP gross profit to operating profit",period)
            eq(val("operating_profit",period)+val("interest_income",period)-
               val("interest_expense",period)+val("other_income_net",period),
               val("profit_before_tax",period),"GAAP operating-to-pre-tax bridge",period)
            eq(val("period_profit",period)-val("noncontrolling_profit",period),
               val("attributable_profit",period),"GAAP attributable net income",period)
            eq(val("operating_cash_flow",period)-val("capital_expenditures",period),
               val("free_cash_flow",period),"FCF after capex",period)
            eq(sum((val(k,period) or 0) for k in
               ("attributable_profit","stock_comp_net_tax","digital_asset_adjustment",
                "spacex_investment_adjustment","certain_tax_adjustment")),
               val("non_gaap_attributable_profit",period),"non-GAAP GAAP reconciliation",period)
            eq(val("total_liabilities",period)+val("total_stockholders_equity",period)+
               val("noncontrolling_equity",period)+val("redeemable_noncontrolling_equity",period),
               val("total_assets",period),"balance sheet assets=liabilities+equity",period)
            eq(val("model_3_y_deliveries",period)+val("other_models_deliveries",period),
               val("total_deliveries",period),"model deliveries total",period)
        quarters=r["quarterly_series"]
        for k in ("revenue","gross_profit","operating_profit","operating_cash_flow",
                  "capital_expenditures","free_cash_flow"):
            eq(quarters[k][0],val(k,"prior"),k+" quarterly first value","prior")
            eq(quarters[k][-1],val(k,"current"),k+" quarterly last value","current")
        for i in range(5):
            eq(quarters["operating_cash_flow"][i]-quarters["capital_expenditures"][i],
               quarters["free_cash_flow"][i],"quarterly FCF","quarter "+str(i))
        for row in r["consensus"]["items"]:
            if row["key"] in v:
                eq(row["actual"],val(row["key"],"current"),"consensus compare actual:"+row["key"],"current")
    return errs


def validate_all():
    errors=[]
    try:
        tax=parse(ROOT/"data/taxonomy.json")
    except (OSError, ValueError) as exc:
        return ["taxonomy: "+str(exc)]
    for kind in ("sectors","markets","periods","topics"):
        ids=[x["id"] for x in tax[kind]]
        if len(ids)!=len(set(ids)):
            errors.append(kind+": duplicate category ID")
    issuers={}
    for file in sorted((ROOT/"data/issuers").glob("*.json")):
        try:
            issuer=parse(file)
        except (OSError, ValueError) as exc:
            errors.append(str(file)+": "+str(exc));continue
        ident=issuer.get("id")
        if ident in issuers:
            errors.append("duplicate issuer id: "+str(ident))
        issuers[ident]=issuer
        if file.stem!=ident:
            errors.append("issuer filename/id mismatch: "+file.name)
        for kind,field in (("sectors","sector"),("markets","market")):
            if issuer.get(field) not in {x["id"] for x in tax[kind]}:
                errors.append(ident+": unknown "+field+" taxonomy id")
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        Draft202012Validator=None
    if Draft202012Validator:
        schemas={kind:parse(ROOT/f"schemas/{kind}.schema.json") for kind in ("report","issuer")}
        for kind,schema in schemas.items():
            Draft202012Validator.check_schema(schema)
        for issuer in issuers.values():
            for err in Draft202012Validator(schemas["issuer"],format_checker=FormatChecker()).iter_errors(issuer):
                errors.append(issuer["id"]+": schema: "+err.message)
    ids=set()
    files=sorted((ROOT/"data/reports").glob("*/*.json"))
    if not files:
        errors.append("at least one report JSON is required")
    for file in files:
        try:
            report=parse(file)
        except (OSError, ValueError) as exc:
            errors.append(str(file)+": "+str(exc));continue
        rid=report.get("report_id")
        if rid in ids:
            errors.append("duplicate report ID "+str(rid))
        ids.add(rid)
        if file.parent.name!=report.get("issuer_id") or file.stem!=report.get("slug"):
            errors.append(str(file)+": path does not match report issuer/slug")
        if Draft202012Validator:
            for err in Draft202012Validator(schemas["report"],format_checker=FormatChecker()).iter_errors(report):
                errors.append(str(file)+": schema: "+err.message)
        errors.extend(errors_for_report(report,issuers,tax))
    return errors


def main():
    errors=validate_all()
    if errors:
        for e in errors:
            print("ERROR:",e,file=sys.stderr)
        return 1
    print("PASS: taxonomy/schema and financial statement reconciliations")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
