"""Step 3: judge each medicine pair with Banyan Sapling (framing F1) + a plain code rule check."""
import json, pathlib, re, time, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT = pathlib.Path(__file__).parent
SAPLING_URL = "https://6adbee0669a00298cd4774c9.endpoints.huggingface.cloud"
POLICY = ("A care medication record must match the most recent prescriber instruction: discontinued medicines "
          "must not be given, replacements must replace not add, doses must match, and every prescribed medicine "
          "must be on the administration chart.")
CLAIM = "The care record is consistent with the prescriber instruction."
THRESHOLD = 0.4
MISSING = re.compile(r"not on chart|not recorded|absent|missing|^\s*$|^none", re.I)
NOT_PRESCRIBED = re.compile(r"not in prescriber record", re.I)

def rule_check(m):
    """Deterministic rule: prescribed medicine with no line on the care chart."""
    if MISSING.search(m["care_record_line"]) and not NOT_PRESCRIBED.search(m["prescriber_instruction"]) \
       and not re.search(r"discontinued|stop", m["prescriber_instruction"], re.I):
        return "On the prescriber list but missing from the care chart"
    return None

def evidence(m):
    return (f"Prescriber record: {m['name']}: {m['prescriber_instruction']}\n"
            f"Care record: {m['name']}: {m['care_record_line']}")

def sapling(m):
    return sapling_raw(evidence(m))

def sapling_raw(ev):
    payload = {"inputs": {"policy": POLICY, "evidence": ev, "claim": CLAIM}}
    t = time.time()
    try:
        r = requests.post(SAPLING_URL, json=payload, timeout=120)
        d = r.json()
        if isinstance(d, list): d = d[0]
        p = d.get("probabilities", {})
        return {"status": d.get("status"), "raw_label": d.get("raw_label"), "prediction_set": d.get("prediction_set"),
                "probabilities": p, "violation": float(p.get("violation", 0.0)),
                "model_ms": (d.get("timing_ms") or {}).get("model"), "wall_ms": int((time.time() - t) * 1000),
                "http": r.status_code, "evidence": payload["inputs"]["evidence"]}
    except Exception as e:
        return {"error": type(e).__name__, "violation": None, "wall_ms": int((time.time() - t) * 1000),
                "evidence": payload["inputs"]["evidence"]}

def row(m, s):
    rule = rule_check(m)
    sap_flag = s.get("violation") is not None and s["violation"] >= THRESHOLD
    return {**m, "sapling": s, "rule": rule, "sapling_flag": sap_flag, "flag": bool(sap_flag or rule)}

def judge_stream(meds, workers=8):
    """Yields result rows as Sapling calls finish (parallel)."""
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(sapling, m): m for m in meds}
        for f in as_completed(futs):
            yield row(futs[f], f.result())

def save(case_id, rows, extract_info):
    out = {"case": case_id, "run_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "policy": POLICY, "claim": CLAIM,
           "threshold": THRESHOLD, "extraction": extract_info, "rows": rows}
    (ROOT / f"data/results/{case_id}.json").write_text(json.dumps(out, indent=2))
    return out

def load(case_id):
    p = ROOT / f"data/results/{case_id}.json"
    return json.loads(p.read_text()) if p.exists() else None

if __name__ == "__main__":
    from extract import extract
    for f in sorted((ROOT / "data/cases").glob("*.json")):
        c = json.loads(f.read_text())
        meds, info = extract(c, use_live=False)  # cached live extraction
        if info.get("model"): info["mode"] = "live"
        rows = list(judge_stream(meds))
        save(c["id"], rows, info)
        print(f"== {c['id']} (extraction: {info['mode']})")
        for r in sorted(rows, key=lambda r: -(r['sapling']['violation'] or 0)):
            s = r["sapling"]
            print(f"  {'RED ' if r['flag'] else 'grey'} {r['name']:<28} viol={s.get('violation')} {s.get('raw_label')} {s.get('status')} {s.get('wall_ms')}ms rule={r['rule']}")
