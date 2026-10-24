"""MedMatch live server: serves docs/ and streams a real pipeline run (Mubit gateway + Sapling).
The Mubit key is loaded server-side by normalise.py from /workspace/.secrets/mubit_key; it is never sent or logged."""
import json, queue, threading, uuid, tempfile, time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pipeline

ROOT = Path(__file__).parent
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
LOCK = threading.Semaphore(3)

@app.get("/api/health")
def health(): return {"ok": True}

@app.post("/api/check")
async def check(req: Request):
    body = await req.json()
    cid = body.get("case_id", "fisher")
    case = json.loads((ROOT / f"data/cases/{cid}.json").read_text())
    if body.get("documents"):
        docs = body["documents"][:4]
        case["documents"] = [{"role": d.get("role", case["documents"][i]["role"] if i < len(case["documents"]) else "care"),
                              "label": d.get("label", case["documents"][i]["label"] if i < len(case["documents"]) else f"Document {i+1}"),
                              "text": str(d.get("text", ""))[:6000]} for i, d in enumerate(docs)]
    case["id"] = "live_" + uuid.uuid4().hex[:8]
    q = queue.Queue()
    def work():
        if not LOCK.acquire(timeout=60):
            q.put({"type": "error", "message": "server busy"}); q.put(None); return
        try:
            q.put({"type": "start", "documents": [d["label"] for d in case["documents"]]})
            def on_norm(label, info, lines):
                q.put({"type": "llm", "doc": label, "gateway": info.get("gateway"), "model": info.get("model"),
                       "mubit_request_id": info.get("mubit_request_id"), "latency_ms": info.get("latency_ms"),
                       "lines": [{k: l.get(k) for k in ("original", "canonical_name", "canonical_text", "status")} for l in lines]})
            def on_row(c):
                q.put({"type": "sapling", "name": c["name"], "doc": c["doc"], "violation": c["sapling"].get("violation"),
                       "status": c["sapling"].get("status"), "wall_ms": c["sapling"].get("wall_ms"), "rule": c["rule"],
                       "flag": c["flag"], "prescriber_line": c["prescriber_line"], "care_line": c["care_line"]})
            with tempfile.TemporaryDirectory() as td:
                res = pipeline.run(case, use_live=True, workers=8, on_row=on_row, on_norm=on_norm, cache_dir=td)
            for m in res["medicines"]:
                for c in m["comparisons"]: c.pop("evidence", None)
            res.pop("policy", None)
            q.put({"type": "done", "result": res})
        except Exception as e:
            q.put({"type": "error", "message": f"{type(e).__name__}"})
        finally:
            LOCK.release(); q.put(None)
    threading.Thread(target=work, daemon=True).start()
    def gen():
        while True:
            try: ev = q.get(timeout=15)
            except queue.Empty:
                yield "\n"; continue
            if ev is None: break
            yield json.dumps(ev) + "\n"
    return StreamingResponse(gen(), media_type="application/x-ndjson", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

app.mount("/", StaticFiles(directory=ROOT / "docs", html=True), name="docs")
