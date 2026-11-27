"""Yuncong 2026 Q3: regression checks on primary-report transcriptions."""
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from src.yuncong import figures, reconciliation_errors

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/reports/yuncong/2026-q3.json"


class YuncongQ3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(DATA.read_text(encoding="utf-8"))

    def val(self, key, p="current"):
        return self.r["values"][key]["values"][p]

    def test_source_exact_fen(self):
        self.assertEqual(self.r["unit"], "CNY_fen")
        self.assertEqual(self.val("revenue"), 13_052_377_429)
        self.assertEqual(self.val("parent_profit"), -10_214_715_864)
        self.assertEqual(self.val("operating_cash_flow"), -11_888_905_848)
        self.assertEqual(self.val("quarter_revenue"), 3_026_015_401)

    def test_all_reconciliations(self):
        self.assertEqual(reconciliation_errors(self.r), [])

    def test_time_bases_and_no_inferred_quarter_prior(self):
        self.assertEqual(self.r["values"]["balance_inventory"]["period_basis"], "balance")
        self.assertEqual(self.r["values"]["revenue"]["period_basis"], "nine_month")
        self.assertEqual(self.r["values"]["quarter_revenue"]["period_basis"], "quarter")
        self.assertIsNone(self.r["values"]["quarter_revenue"]["values"]["prior"])

    def test_all_generated_vector_charts_are_standalone(self):
        with tempfile.TemporaryDirectory() as tmp:
            generated=figures(self.r,Path(tmp))
            self.assertGreaterEqual(len(generated),6)
            for fig in generated:
                path=Path(tmp)/fig["filename"]
                self.assertTrue(path.exists(),fig["filename"])
                root=ET.parse(path).getroot()
                self.assertIn("viewBox",root.attrib)
                self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}title"))
                self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}desc"))
                xml=path.read_text(encoding="utf-8")
                self.assertNotIn("<foreignObject",xml)
                self.assertNotIn("http://www.w3.org/1999/xhtml",xml)


if __name__=="__main__":
    unittest.main()
