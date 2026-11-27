"""Source regression anchors and deliberate tampering tests."""
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.validate_data import errors_for_report, validate_all
R=json.loads((ROOT/"data/reports/xindong/2026-h1.json").read_text(encoding="utf-8"))
I=json.loads((ROOT/"data/issuers/xindong.json").read_text(encoding="utf-8"))
T=json.loads((ROOT/"data/taxonomy.json").read_text(encoding="utf-8"))
class FinancialTests(unittest.TestCase):
    def test_corpus(self): self.assertEqual([],validate_all())
    def test_facts(self):
        v=R["values"]
        self.assertEqual([3081986,3312235],[v["revenue"]["values"][p] for p in ("prior","current")])
        self.assertEqual([810596,724312],[v["period_profit"]["values"][p] for p in ("prior","current")])
        self.assertEqual(2317903,v["game_revenue"]["values"]["current"])
        self.assertEqual(994332,v["taptap_revenue"]["values"]["current"])
        self.assertEqual(711934,v["operating_cash_flow"]["values"]["current"])
        self.assertEqual(39,len(v))
    def test_unaudited_review(self):
        self.assertEqual("reviewed_unaudited",R["source"]["assurance"])
        self.assertIsNone(R["publication_date"])
    def assert_corrupt(self,name,value,marker):
        d=copy.deepcopy(R);d["values"][name]["values"]["current"]=value
        self.assertTrue(any(marker in x for x in errors_for_report(d,{"xindong":I},T)))
    def test_fake_gross(self): self.assert_corrupt("gross_profit",1,"revenue-cost")
    def test_fake_segment(self): self.assert_corrupt("taptap_revenue",1,"consolidated revenue")
    def test_fake_tax(self): self.assert_corrupt("income_tax_expense",1,"net profit after income tax")
    def test_original_cash_flow(self):
        v=R["values"];n=lambda k:v[k]["values"]["current"]
        self.assertEqual(117760,n("operating_cash_flow")+n("investing_cash_flow")+n("financing_cash_flow"))
if __name__=="__main__":unittest.main()
