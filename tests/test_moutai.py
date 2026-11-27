import json, unittest
from pathlib import Path
from src.moutai import reconciliation_errors
R=Path(__file__).resolve().parents[1]
class MoutaiTests(unittest.TestCase):
    def test_exact(self):
        d=json.loads((R/"data/reports/moutai/2026-q3.json").read_text())
        self.assertEqual([],reconciliation_errors(d))
        self.assertEqual(13097074364904,d["values"]["revenue"]["values"]["current"])
