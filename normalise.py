"""Normalisation BEFORE Sapling: the LLM (via the Mubit gateway) maps every medicine line in a document to
generic name + strength + unit + dose + frequency + status; then code applies data/synonyms.json so names,
units and frequencies are canonical. The Mubit key is read from file at runtime and never printed/logged."""
import json, os, pathlib, re, time
ROOT = pathlib.Path(__file__).parent
KEY_FILE = pathlib.Path("/workspace/.secrets/mubit_key")
BASE_URL = "https://api.mubit.ai/openai/v1"   # docs.mubit.ai quickstart, OpenAI SDK
MODEL = "gpt-4o-mini"
SYN = json.loads((ROOT / "data/synonyms.json").read_text())
SYN["names"].update({v: v for v in list(SYN["names"].values())})  # canonical names map to themselves

PROMPT = """Extract EVERY medicine line from this {kind} document. Return JSON:
{{"lines":[{{"original": exact text of the line,
 "generic_name": lowercase generic (INN) name, never a brand (Vit D3 -> colecalciferol, acetaminophen -> paracetamol, Oramorph -> morphine sulfate, Adcal-D3 -> calcium carbonate + colecalciferol),
 "strength": number or null, "strength_unit": "mg"|"micrograms"|"units"|"mg/5ml"|"mg/ml"|null (convert g to mg: 1g -> 1000 mg; iu/IU -> units),
 "dose": amount per administration as text with unit e.g. "10 ml", "1 tablet", "2 tablets",
 "frequency": one of "once daily","twice daily","three times daily","four times daily","at night","every 4 hours" plus " when required" if PRN,
 "status": "active"|"stopped"|"started"|"withheld"|"not given",
 "replaces": generic name of the medicine it replaces, or null,
 "note": dates, NEW/additional, reasons, other notes}}]}}
Treat lines marked STOP/DISCONTINUED as status "stopped". Include withheld lines. Do not invent medicines.
DOCUMENT:
<<<{text}>>>"""

def _key():
    if not os.environ.get("MUBIT_API_KEY") and KEY_FILE.exists():
        os.environ["MUBIT_API_KEY"] = KEY_FILE.read_text().strip()
    return bool(os.environ.get("MUBIT_API_KEY"))

def canon_name(n):
    n = (n or "").lower().strip()
    n = re.sub(r"\s+", " ", n.replace("cholecalciferol", "colecalciferol").replace("sulphate", "sulfate"))
    if n in SYN["names"]: return SYN["names"][n]
    for k in sorted(SYN["names"], key=len, reverse=True):
        if re.search(rf"\b{re.escape(k)}\b", n): return SYN["names"][k]
    return n

def canon_freq(f):
    f = (f or "").lower().strip(); prn = "when required" in f or "prn" in f
    base = f.replace("when required", "").replace("prn", "").strip(" ,")
    base = SYN["frequency"].get(base, base)
    return (base + " when required").strip() if prn else base

def canon_line(l):
    l = dict(l); l["canonical_name"] = canon_name(l.get("generic_name") or l.get("original"))
    u = (l.get("strength_unit") or ""); u = SYN["units"].get(u.lower(), u)
    s = l.get("strength")
    try:
        if u == "g" and s is not None: s, u = float(s) * 1000, "mg"
        if s is not None: s = float(s); s = int(s) if s == int(s) else s
    except Exception: pass
    l["strength"], l["strength_unit"] = s, u
    l["frequency"] = canon_freq(l.get("frequency"))
    if l.get("replaces"): l["replaces"] = canon_name(l["replaces"])
    l["canonical_text"] = " ".join(str(x) for x in [l["canonical_name"], s if s is not None else "", u, "-", l.get("dose") or "", l["frequency"], f"[{l.get('status')}]"] if x != "").replace("  ", " ")
    return l

def normalise_doc(text, kind, cache_path=None, use_live=True):
    if not use_live and cache_path and pathlib.Path(cache_path).exists():
        d = json.loads(pathlib.Path(cache_path).read_text()); return d["lines"], {**d["info"], "replayed": True}
    if not _key(): raise RuntimeError("no Mubit key file")
    from openai import OpenAI
    client = OpenAI(base_url=BASE_URL, api_key=os.environ["MUBIT_API_KEY"], timeout=60, max_retries=1)
    t = time.time()
    raw = client.chat.completions.with_raw_response.create(model=MODEL, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": PROMPT.format(kind=kind, text=text)}])
    r = raw.parse()
    lines = [canon_line(x) for x in json.loads(r.choices[0].message.content)["lines"]]
    info = {"mode": "live", "gateway": BASE_URL, "model": MODEL, "latency_ms": int((time.time() - t) * 1000),
            "mubit_request_id": raw.headers.get("x-middleware-request-id")}
    if cache_path: pathlib.Path(cache_path).write_text(json.dumps({"lines": lines, "info": info}, indent=2))
    return lines, info
