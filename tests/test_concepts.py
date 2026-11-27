"""Glossary quality regressions: 100 terms + index = 101 independent HTML outputs."""
import importlib.util
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.concepts import check_concepts, render_svg, ratio_result
DATA=json.loads((ROOT/"data/concepts.json").read_text(encoding="utf-8"))
CAT={x["id"]:x for x in DATA["categories"]}
CONCEPTS=DATA["concepts"]
BY_ID={c["id"]:c for c in CONCEPTS}


class ConceptTests(unittest.TestCase):
    def test_100_unique_ordered(self):
        self.assertTrue(check_concepts(DATA))
        self.assertEqual(100,len(CONCEPTS))
        self.assertEqual(100,len(BY_ID))
        self.assertEqual(list(range(1,101)),[x["order"] for x in CONCEPTS])

    def test_ten_chapters(self):
        self.assertEqual(10,len(CAT))
        for key in CAT:
            self.assertEqual(10,sum(x["category"]==key for x in CONCEPTS))

    def test_bridge_and_equation_are_not_faked(self):
        c=BY_ID["accounting-equation"]
        self.assertEqual(120,70+50)
        self.assertEqual("balance",c["diagram"]["kind"])
        w=BY_ID["net-profit"]["diagram"]["items"]
        self.assertEqual(w[0]["value"]+sum(i["value"] for i in w[1:-1]),w[-1]["value"])
        self.assertEqual("24.0%",ratio_result(BY_ID["operating-margin"]))
        self.assertEqual("60.8 天",ratio_result(BY_ID["dso"]))
        self.assertEqual("300（单位按示例说明）",ratio_result(BY_ID["market-cap"]))

    def test_each_svg_is_independent_and_accessible(self):
        for c in CONCEPTS:
            xml=render_svg(c,CAT[c["category"]])
            root=ET.fromstring(xml)
            self.assertTrue(root.tag.endswith("svg"),c["id"])
            self.assertIn("viewBox",root.attrib)
            self.assertTrue(any(t.tag.endswith("title") for t in root.iter()))
            self.assertTrue(any(t.tag.endswith("desc") for t in root.iter()))
            self.assertNotIn("foreignObject",xml)
            self.assertNotIn("<script",xml)
            self.assertIn(c["title"],xml)

    def test_separate_site_from_education(self):
        for c in CONCEPTS:
            self.assertTrue(c["illustrative"])
            self.assertIn(c["category"],CAT)
        self.assertNotIn("source_url",DATA)
        self.assertNotIn("HKEX",json.dumps(DATA))


if __name__=="__main__":unittest.main()
