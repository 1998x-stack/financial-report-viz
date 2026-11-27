#!/usr/bin/env python3
"""Validate the 100 educational terms without changing issuer-report validation."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.concepts import check_concepts

if __name__=="__main__":
    data=json.loads((ROOT/"data/concepts.json").read_text(encoding="utf-8"))
    try:
        check_concepts(data)
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            print("WARN: jsonschema not installed, semantic checks ran; schema check skipped")
        else:
            schema=json.loads((ROOT/"schemas/concepts.schema.json").read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            findings=list(Draft202012Validator(schema).iter_errors(data))
            if findings:raise ValueError("\n".join(str(x) for x in findings))
        print("PASS: 100 distinct educational concepts across ten chapters, exact diagram identities")
    except Exception as exc:
        print("FAIL: "+str(exc),file=sys.stderr)
        raise SystemExit(1)
