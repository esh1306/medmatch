from pathlib import Path
"""Whole-list reconciliation. Documents: one 'base' (patient's full existing medicines list from the GP/prescriber),
zero or more 'update' prescriber documents (discharge letter, neurology instruction), and one or more 'care' charts.
1) normalise every document (LLM via Mubit gateway + synonym table)
2) build the current prescribed list = base + updates (started / stopped / replaced / dose changed)
3) for EVERY medicine x EVERY care chart: Sapling F1 judges the pair (canonical lines + original text)
4) code rule check (labelled, not Sapling): missing from chart, extra/not prescribed, duplicated on chart."""
import json, pathlib, time
from concurrent.futures import ThreadPoolExecutor
from normalise import normalise_doc
from judge import sapling_raw, THRESHOLD, POLICY, CLAIM
ROOT = pathlib.Path(__file__).parent
ACTIVE = {"active", "started"}

def fmt(l):
    return f"{l['canonical_text']} (original text: \"{l['original'].strip()}\"{'; note: ' + l['note'] if l.get('note') else ''})"

def build_prescribed(docs_lines):
    """Returns {name: {"line":..., "history":[(doc_label, event)], "current": line|None}}"""
    meds = {}
    for d, lines in docs_lines:
        if d["role"] not in ("base", "update"): continue
        for l in lines:
            n = l["canonical_name"]; m = meds.setdefault(n, {"history": [], "current": None, "last": None})
            st = l.get("status")
            if st in ("stopped",):
                ev = "stopped"; m["current"] = None
            elif d["role"] == "base":
                ev = "on existing list" if st in ACTIVE else st; m["current"] = l if st in ACTIVE or st == "withheld" else None
            else:
                prev = m["current"]
                ev = "started" if prev is None else ("dose changed" if (prev.get("strength"), prev.get("dose"), prev.get("frequency")) != (l.get("strength"), l.get("dose"), l.get("frequency")) else "confirmed")
                m["current"] = l
            m["last"] = l; m["history"].append((d["label"], ev))
            if l.get("replaces"):
                r = meds.setdefault(l["replaces"], {"history": [], "current": None, "last": None})
                r["current"] = None; r["history"].append((d["label"], f"replaced by {n}"))
                r.setdefault("replaced_by", n)
    return meds

def compare(name, pres, care_lines, care_label):
    cur = pres.get("current") if pres else None
    active_care = [l for l in care_lines if l.get("status") in ACTIVE]
    if cur: p_text = f"{name}: CURRENT PRESCRIPTION {fmt(cur)}"
    elif pres and pres.get("last"):
        why = "; ".join(e for _, e in pres["history"])
        p_text = f"{name}: NOT CURRENTLY PRESCRIBED ({why}). Last prescriber line: {fmt(pres['last'])}"
    else: p_text = f"{name}: NOT IN ANY PRESCRIBER RECORD"
    c_text = (f"{name}: " + " | ".join(fmt(l) for l in care_lines)) if care_lines else f"{name}: NOT ON CHART"
    rule = None
    if cur and cur.get("status") in ACTIVE and not active_care and not care_lines:
        rule = "Missing: prescribed but not on this chart"
    elif not cur and active_care:
        rule = "Extra: on this chart as active but not currently prescribed" + (f" ({'; '.join(e for _, e in pres['history'])})" if pres else "")
    elif len(active_care) > 1:
        rule = "Duplicated: more than one active line on this chart"
    return {"name": name, "doc": care_label, "prescriber_line": p_text, "care_line": c_text, "rule": rule,
            "evidence": f"Prescriber record: {p_text}\nCare record: {c_text}"}

def run(case, use_live=True, workers=8, on_row=None, on_norm=None, cache_dir=None):
    t0 = time.time(); docs = case["documents"]; infos = []
    def norm(i):
        cd = Path(cache_dir) if cache_dir else ROOT / "data/extracted"
        r = normalise_doc(docs[i]["text"], docs[i]["label"], cd / f"{case['id']}__doc{i}.json", use_live)
        if on_norm: on_norm(docs[i]["label"], r[1], r[0])
        return r
    with ThreadPoolExecutor(len(docs)) as ex: res = list(ex.map(norm, range(len(docs))))
    docs_lines = [(d, r[0]) for d, r in zip(docs, res)]; infos = [dict(doc=d["label"], **r[1]) for d, r in zip(docs, res)]
    pres = build_prescribed(docs_lines)
    cares = [(d, ls) for d, ls in docs_lines if d["role"] == "care"]
    names = list(pres) + [l["canonical_name"] for _, ls in cares for l in ls if l["canonical_name"] not in pres]
    names = list(dict.fromkeys(names))
    comps = [compare(n, pres.get(n), [l for l in ls if l["canonical_name"] == n], d["label"]) for n in names for d, ls in cares]
    def judge(c):
        t1 = time.time(); s = sapling_raw(c["evidence"]); s["wall_ms"] = round((time.time() - t1) * 1000); c["sapling"] = s
        c["sapling_flag"] = s.get("violation") is not None and s["violation"] >= THRESHOLD
        c["flag"] = bool(c["sapling_flag"] or c["rule"])
        if on_row: on_row(c)
        return c
    with ThreadPoolExecutor(workers) as ex: comps = list(ex.map(judge, comps))
    meds = []
    for n in names:
        cs = [c for c in comps if c["name"] == n]
        p = pres.get(n)
        meds.append({"name": n, "prescriber_history": p["history"] if p else [], "currently_prescribed": bool(p and p["current"]),
                     "comparisons": cs, "flag": any(c["flag"] for c in cs),
                     "max_violation": max((c["sapling"].get("violation") or 0) for c in cs)})
    meds.sort(key=lambda m: (not m["flag"], -m["max_violation"]))
    return {"case": case["id"], "run_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "policy": POLICY, "claim": CLAIM,
            "threshold": THRESHOLD, "normalisation": infos, "medicines": meds, "elapsed_s": round(time.time() - t0, 1),
            "normalised_lines": {d["label"]: ls for d, ls in docs_lines}}

def save(res):
    (ROOT / f"data/results/{res['case']}.json").write_text(json.dumps(res, indent=2)); return res

def load(cid):
    p = ROOT / f"data/results/{cid}.json"; return json.loads(p.read_text()) if p.exists() else None

if __name__ == "__main__":
    import sys
    ids = sys.argv[1:] or ["fisher", "elliott", "burgess"]
    for cid in ids:
        case = json.loads((ROOT / f"data/cases/{cid}.json").read_text())
        r = save(run(case))
        print(f"== {cid} {r['elapsed_s']}s req_ids={[i.get('mubit_request_id') for i in r['normalisation']]}")
        for m in r["medicines"]:
            print(f"  {'RED ' if m['flag'] else 'grey'} {m['name']:<34} " + " || ".join(f"{c['doc'][:22]}: v={c['sapling'].get('violation') or 0:.2f} {c['sapling'].get('raw_label')} rule={c['rule']}" for c in m["comparisons"]))
