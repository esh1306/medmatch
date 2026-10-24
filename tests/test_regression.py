"""LIVE regression: synonym pairs must NOT flag; the 4 real coroner conflicts MUST flag.
Runs the full pipeline (Mubit-gateway normalisation + synonym table + Sapling + rule check).
Run: .venv/bin/python tests/test_regression.py   (writes tests/regression_results.json)"""
import json, pathlib, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from pipeline import run
def case(cid, base, care): return {"id": "test_" + cid, "documents": [dict(role="base", label="Prescriber list", text=base), dict(role="care", label="Care chart", text=care)]}
MUST_NOT_FLAG = [
 ("vitd", "Cholecalciferol 800 units tablets - 1 once daily", "Vit D3 800iu - 1 tab - OD"),
 ("paracetamol", "Paracetamol 500mg tablets - 2 four times daily", "Acetaminophen 500 mg - 2 tabs - QDS"),
 ("adcal", "Adcal-D3 chewable tablets - 1 twice daily", "Calcium carbonate + colecalciferol chewable tab - 1 - twice daily"),
 ("bd", "Amlodipine 5mg - 1 b.d.", "Amlodipine 5 mg - 1 tablet - twice daily"),
 ("gram", "Paracetamol 1g four times daily", "Paracetamol 1000mg QDS"),
]
MUST_FLAG = [
 ("fisher_phenobarbital", "Phenobarbital 30mg tablets - 1 BD - DISCONTINUED 08/04/2025 by GP\nLevetiracetam 100mg/ml 7.5ml BD",
  "Phenobarbital 30mg tab - 1 tab - 08:00 20:00 - signed 09/04-15/04/2025\nLevetiracetam liquid 7.5ml 08:00 20:00"),
 ("fisher_valproate_missing", "Sodium valproate 200mg/5ml oral solution 10ml BD\nLevetiracetam 100mg/ml 7.5ml BD",
  "Levetiracetam 100mg/ml oral soln 7.5ml Morning, Tea\n(no further medicines recorded)"),
 ("elliott_oramorph", "Oramorph 10mg/5ml - STOPPED (renal). Oxycodone 5mg/5ml 2.5ml 4-hourly PRN REPLACES Oramorph.",
  "Oramorph 10mg/5ml 2.5ml 4hrly PRN Active\nOxycodone 5mg/5ml 2.5ml 4hrly PRN Active - NEW additional"),
 ("burgess_brivaracetam", "Brivaracetam 10mg/ml oral solution 4ml twice daily", "Brivaracetam 10mg/ml soln 10ml BD"),
]
def go(t, expect):
    cid, base, care = t
    r = run(case(cid, base, care))
    meds = [{"name": m["name"], "flag": m["flag"], "violation": round(m["max_violation"], 3),
             "rule": [c["rule"] for c in m["comparisons"] if c["rule"]], "raw_label": [c["sapling"].get("raw_label") for c in m["comparisons"]]} for m in r["medicines"]]
    flagged = any(m["flag"] for m in meds)
    return {"id": cid, "expect_flag": expect, "flagged": flagged, "pass": flagged == expect, "medicines": meds,
            "mubit_request_ids": [i.get("mubit_request_id") for i in r["normalisation"]]}
if __name__ == "__main__":
    jobs = [(t, False) for t in MUST_NOT_FLAG] + [(t, True) for t in MUST_FLAG]
    with ThreadPoolExecutor(5) as ex: res = list(ex.map(lambda j: go(*j), jobs))
    out = {"run_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "passed": sum(r["pass"] for r in res), "total": len(res), "results": res}
    (pathlib.Path(__file__).parent / "regression_results.json").write_text(json.dumps(out, indent=2))
    for r in res: print(("PASS" if r["pass"] else "FAIL"), r["id"], "expect_flag=", r["expect_flag"], [(m["name"], m["violation"], m["rule"]) for m in r["medicines"]])
    print(f"{out['passed']}/{out['total']} passed"); sys.exit(0 if out["passed"] == out["total"] else 1)
