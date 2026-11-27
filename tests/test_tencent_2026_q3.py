"""腾讯2026 Q3财报回归测试：金额单位人民币百万元。"""
import copy
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.validate_data import errors_for_report, validate_all
from src.charts import build_figures

D=json.loads((ROOT/"data/reports/tencent/2026-q3.json").read_text(encoding="utf-8"))
T=json.loads((ROOT/"data/taxonomy.json").read_text(encoding="utf-8"))
I=json.loads((ROOT/"data/issuers/tencent.json").read_text(encoding="utf-8"))

def v(k,p="current"):return D["values"][k]["values"][p]

class TencentQ3Tests(unittest.TestCase):
    def test_corpus_and_source(self):
        self.assertEqual([],validate_all())
        self.assertEqual("CNY_million",D["unit"])
        self.assertEqual("reviewed_unaudited",D["source"]["assurance"])
        self.assertEqual(0,D["source"]["pdf_page_offset"])
        self.assertEqual("2026-07-01",D["period_start"])
        self.assertEqual("2026-09-30",D["period_end"])
        self.assertEqual(32,len(D["values"]))
    def test_primary_statement_anchors(self):
        self.assertEqual([192869,207336],[v("revenue",x) for x in ("prior","current")])
        self.assertEqual([63554,59147],[v("operating_profit",x) for x in ("prior","current")])
        self.assertEqual([70551,66519],[v("non_ifrs_attributable_profit",x) for x in ("prior","current")])
        self.assertEqual([12983,81433],[v("accrual_capex",x) for x in ("prior","current")])
        self.assertEqual(-1235,v("other_gross_profit"))
    def test_segment_and_profit_bridge(self):
        for p in ("prior","current"):
            self.assertEqual(v("revenue",p),sum(v(k+"_revenue",p) for k in ("vas","marketing","fintech","other")))
            self.assertEqual(v("gross_profit",p),sum(v(k+"_gross_profit",p) for k in ("vas","marketing","fintech","other")))
            self.assertEqual(v("operating_profit",p),v("gross_profit",p)-v("selling_marketing",p)-v("general_admin",p)+v("other_gains_net",p))
            self.assertEqual(v("profit_before_tax",p),v("operating_profit",p)+v("investments_net_gains",p)+v("interest_income",p)-v("finance_costs",p)+v("equity_method_result",p))
            self.assertEqual(v("period_profit",p),v("profit_before_tax",p)-v("income_tax_expense",p))
    def test_cash_scope_and_liquidity(self):
        c=D["supplementary"]["quarterly_cash_flow_rounded"]
        self.assertEqual(-69100,c["operating"]-c["capex_payments"]-c["media_payments"]-c["lease_payments"])
        l=D["supplementary"]["liquidity"]
        self.assertEqual([58191,-13702],l["net_cash_debt"])
        self.assertEqual(-13702,l["cash_and_equivalents"][1]+l["term_deposits_and_others"][1]-l["borrowings"][1]-l["notes_payable"][1])
        nine=D["supplementary"]["nine_month_cash_flows"]
        self.assertEqual(95266,nine["operating"][1]+nine["investing"][1]+nine["financing"][1])
    def test_deliberately_bad_segment_rejected(self):
        bad=copy.deepcopy(D)
        bad["values"]["marketing_revenue"]["values"]["current"]+=1
        errors=errors_for_report(bad,{"tencent":I},T)
        self.assertTrue(any("four segment revenues" in x for x in errors),errors)
    def test_standalone_svg_xml_and_figure_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            figures=build_figures(D,tmp)
            self.assertEqual(8,len(figures))
            for fig in figures:
                path=Path(tmp)/fig["filename"]
                root=ET.parse(path).getroot()
                self.assertIn("viewBox",root.attrib)
                self.assertGreaterEqual(len([x for x in root.iter() if x.tag.endswith("title")]),1)
                self.assertGreaterEqual(len([x for x in root.iter() if x.tag.endswith("desc")]),1)
                xml=path.read_text(encoding="utf-8")
                self.assertNotIn("<foreignObject",xml)
                self.assertNotIn("<script",xml)

if __name__=="__main__":
    unittest.main()
