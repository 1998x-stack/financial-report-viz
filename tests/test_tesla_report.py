"""Tesla Q3 2026 primary-source transcription and SVG reconciliation checks."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.validate_data import errors_for_report
from src.tesla_charts import build_tesla_figures

T=json.loads((ROOT/"data/taxonomy.json").read_text(encoding="utf-8"))
I=json.loads((ROOT/"data/issuers/tesla.json").read_text(encoding="utf-8"))
R=json.loads((ROOT/"data/reports/tesla/2026-q3.json").read_text(encoding="utf-8"))

class TeslaReportTests(unittest.TestCase):
    def test_period_and_assurance(self):
        self.assertEqual(("2026-07-01","2026-09-30"),(R["period_start"],R["period_end"]))
        self.assertEqual("USD_million",R["unit"])
        self.assertEqual("unaudited",R["source"]["assurance"])
        self.assertEqual("2026-10-21",R["publication_date"])

    def test_transcription_and_reconciliation(self):
        self.assertEqual([],errors_for_report(R,{"tesla":I},T))
        v=R["values"]
        at=lambda k,p:v[k]["values"][p]
        self.assertEqual(28046,at("revenue","current"))
        self.assertEqual(787,at("attributable_profit","current"))
        self.assertEqual(1697,at("non_gaap_attributable_profit","current"))
        self.assertEqual(1531,at("free_cash_flow","current"))
        self.assertEqual(486532,at("total_deliveries","current"))
        self.assertEqual(1.74,at("fsd_active_subscriptions","current"))

    def test_tamper_detection(self):
        for key in ("revenue","gross_profit","operating_profit","free_cash_flow",
                    "automotive_revenue","total_assets","non_gaap_attributable_profit",
                    "total_deliveries"):
            altered=copy.deepcopy(R)
            altered["values"][key]["values"]["current"]=1
            self.assertTrue(errors_for_report(altered,{"tesla":I},T),key)

    def test_quarterly_fcf(self):
        s=R["quarterly_series"]
        for ocf,capex,fcf in zip(s["operating_cash_flow"],s["capital_expenditures"],s["free_cash_flow"]):
            self.assertEqual(ocf-capex,fcf)

    def test_ten_standalone_svgs(self):
        with tempfile.TemporaryDirectory() as temp:
            figures=build_tesla_figures(R,temp)
            self.assertEqual(10,len(figures))
            self.assertEqual(10,len(set(x["slug"] for x in figures)))
            for fig in figures:
                root=ET.parse(Path(temp)/fig["filename"]).getroot()
                self.assertIn("viewBox",root.attrib)
                self.assertTrue(any(e.tag.endswith("title") for e in root.iter()))
                self.assertTrue(any(e.tag.endswith("desc") for e in root.iter()))
                self.assertNotIn("<script",(Path(temp)/fig["filename"]).read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
