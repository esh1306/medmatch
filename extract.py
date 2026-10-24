"""Step 2: extract medicine pairs from the two documents via the Mubit gateway (OpenAI-compatible).
The API key is read from /workspace/.secrets/mubit_key into an env var at runtime. It is never printed,
logged or written anywhere. Error messages are reduced to class name + HTTP status so a key fragment
can never leak into logs. If the gateway fails, the deterministic pre-extracted JSON is used."""
import json, os, pathlib, time
ROOT = pathlib.Path(__file__).parent
KEY_FILE = pathlib.Path("/workspace/.secrets/mubit_key")
BASE_URL = "https://api.mubit.ai/openai/v1"
MODELS = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"]

PROMPT = """You reconcile medicines between two records for a pharmacist.
PRESCRIBER RECORD:
<<<{left}>>>
CARE RECORD:
<<<{right}>>>
List every medicine that appears in EITHER record (merge brand/generic/abbreviated names of the same drug).
Return JSON: {{"medicines":[{{"name": str, "prescriber_instruction": str, "care_record_line": str}}]}}
- prescriber_instruction: the latest prescriber instruction incl. dose/frequency and any STOP/discontinued/replaces wording, verbatim facts only. "NOT IN PRESCRIBER RECORD" if absent.
- care_record_line: what the care record says incl. status/notes. "NOT ON CHART" if absent.
Copy each line in FULL, close to verbatim: drug name, strength, dose, route, frequency/times, and any status, dates or notes (e.g. Active, NEW, additional, STOP, replaces, withheld, started after...). Expand abbreviations (OD=once daily, BD=twice daily, TDS=three times daily, QDS=four times daily, ON=at night, PRN=when required).
Do not judge; just extract."""

def _load_key():
    if not os.environ.get("MUBIT_API_KEY") and KEY_FILE.exists():
        os.environ["MUBIT_API_KEY"] = KEY_FILE.read_text().strip()
    return bool(os.environ.get("MUBIT_API_KEY"))

def _safe_err(e):
    return f"{type(e).__name__}(status={getattr(e, 'status_code', None)})"

def fallback(case_id):
    return json.loads((ROOT / f"data/extracted/{case_id}.fallback.json").read_text())

def extract(case, use_live=True, timeout=60):
    """Returns (medicines, info). info = {mode: live|cache|fallback, model, latency_ms, error}."""
    cid = case["id"]; cache = ROOT / f"data/extracted/{cid}.live.json"
    if not use_live:
        if cache.exists():
            d = json.loads(cache.read_text()); return d["medicines"], {**d["info"], "mode": "cache"}
        return fallback(cid), {"mode": "fallback", "error": "no cached live extraction"}
    if not _load_key():
        return fallback(cid), {"mode": "fallback", "error": "no key file"}
    from openai import OpenAI
    client = OpenAI(base_url=BASE_URL, api_key=os.environ["MUBIT_API_KEY"], timeout=timeout, max_retries=1)
    errs = []
    for m in MODELS:
        t = time.time()
        try:
            r = client.chat.completions.create(model=m, temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": PROMPT.format(left=case["left"], right=case["right"])}])
            meds = json.loads(r.choices[0].message.content)["medicines"]
            meds = [{k: str(x.get(k, "")) for k in ("name", "prescriber_instruction", "care_record_line")} for x in meds]
            info = {"mode": "live", "model": m, "latency_ms": int((time.time() - t) * 1000), "gateway": BASE_URL}
            cache.write_text(json.dumps({"medicines": meds, "info": info}, indent=2))
            return meds, info
        except Exception as e:
            errs.append(f"{m}: {_safe_err(e)}")
    return fallback(cid), {"mode": "fallback", "error": "; ".join(errs)}

if __name__ == "__main__":
    import sys
    for f in sorted((ROOT / "data/cases").glob("*.json")):
        c = json.loads(f.read_text())
        meds, info = extract(c)
        print(c["id"], info, len(meds))
        for x in meds: print("   ", x["name"], "|", x["prescriber_instruction"][:60], "|", x["care_record_line"][:60])
