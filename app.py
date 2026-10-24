import json, pathlib, time, html, threading, queue
import streamlit as st
from pipeline import run, save, load
from judge import THRESHOLD, POLICY, CLAIM
ROOT = pathlib.Path(__file__).parent
st.set_page_config(page_title="MedMatch", page_icon="💊", layout="wide")
ORDER = ["fisher", "elliott", "burgess"]
CASES = {k: json.loads((ROOT / f"data/cases/{k}.json").read_text()) for k in ORDER}
st.markdown("""<style>.row{border-radius:8px;padding:10px 14px;margin:6px 0;border-left:8px solid}
.red{background:#fdecea;border-color:#d93025}.grey{background:#f1f3f4;border-color:#9aa0a6}
.bar{height:9px;background:#e0e0e0;border-radius:5px;overflow:hidden;margin:3px 0}.fill{height:9px}
.small{font-size:0.82em;color:#333}.cell{border-top:1px dashed #ccc;margin-top:6px;padding-top:4px}</style>""", unsafe_allow_html=True)
st.title("💊 MedMatch")
st.caption("Checks a patient's WHOLE existing medicines list against every other document (discharge letters, care charts): started, stopped, "
           "replaced, dose changed, missing, extra, duplicated. Normalisation: LLM via Mubit gateway + synonym table. Judging: Banyan Sapling, one call per medicine per chart.")
with st.sidebar:
    cid = st.selectbox("Case", ORDER, format_func=lambda k: CASES[k]["title"])
    live = st.radio("Mode", ["Live (Mubit gateway + Sapling)", "Replay from cache"], index=1).startswith("Live")
    st.markdown(f"**Red if** Sapling violation ≥ {THRESHOLD}, or the code rule check fires (missing / extra / duplicated).")
    with st.expander("Sapling policy and claim"): st.write(POLICY); st.write("Claim: " + CLAIM)
case = CASES[cid]
st.subheader(case["title"]); st.markdown(f"**Coroner-stated facts:** {case['coroner_fact']}")
cols = st.columns(len(case["documents"]))
for c, d in zip(cols, case["documents"]):
    with c:
        st.markdown(f"**{'📄' if d['role'] != 'care' else '📋'} {d['label']}** · _{ {'base':'existing list','update':'prescriber update','care':'care chart'}[d['role']] }_")
        st.code(d["text"], language=None, wrap_lines=True)

def cell(c):
    s = c["sapling"]; v = s.get("violation") or 0; col = "#d93025" if v >= THRESHOLD else "#9aa0a6"
    rule = f"<br>⚙️ <b>Rule check (code, not Sapling):</b> {html.escape(c['rule'])}" if c["rule"] else ""
    return (f"<div class='cell small'><b>{html.escape(c['doc'])}</b>: {'🔴 conflict' if c['flag'] else 'no conflict found (not verified)'}<br>"
            f"Care: {html.escape(c['care_line'])}<div class='bar'><div class='fill' style='width:{v*100:.0f}%;background:{col}'></div></div>"
            f"Sapling violation <b>{v:.2f}</b> · raw label <code>{s.get('raw_label')}</code> · status <code>{s.get('status')}</code> · {s.get('wall_ms')} ms{rule}</div>")
def render(m):
    hist = "; ".join(f"{d}: {e}" for d, e in m["prescriber_history"]) or "not in any prescriber record"
    head = "🔴 Conflict, pharmacist review" if m["flag"] else "No conflict found (not verified)"
    return (f"<div class='row {'red' if m['flag'] else 'grey'}'><b>{head}</b> — <b>{html.escape(m['name'])}</b>"
            f"<div class='small'>Prescriber history: {html.escape(hist)} · currently prescribed: {'yes' if m['currently_prescribed'] else 'no'}<br>"
            f"{html.escape(m['comparisons'][0]['prescriber_line'])}</div>" + "".join(cell(c) for c in m["comparisons"]) + "</div>")

if st.button("🔍 Check records", type="primary"):
    tally = st.empty(); info = st.empty(); stream = st.empty()
    if live:
        q = queue.Queue(); box = {}
        th = threading.Thread(target=lambda: box.update(r=run(case, use_live=True, on_row=q.put)), daemon=True); th.start()
        done = []; info.info("Normalising every document via the Mubit gateway, then Sapling judges each medicine × chart…")
        while th.is_alive() or not q.empty():
            try: c = q.get(timeout=0.2)
            except queue.Empty: continue
            done.append(c); tally.markdown(f"### {len(done)} comparisons judged by Sapling, {sum(x['flag'] for x in done)} flagged ⏳")
            stream.markdown("".join(f"<div class='small'>{'🔴' if x['flag'] else '⚪'} {html.escape(x['name'])} vs {html.escape(x['doc'])}: violation {(x['sapling'].get('violation') or 0):.2f}</div>" for x in done), unsafe_allow_html=True)
        res = save(box["r"])
    else:
        res = load(cid)
        if not res: st.error("No cached result; use Live."); st.stop()
        allc = [c for m in res["medicines"] for c in m["comparisons"]]
        for i in range(1, len(allc) + 1):
            time.sleep(0.25); tally.markdown(f"### {i} comparisons judged by Sapling, {sum(x['flag'] for x in allc[:i])} flagged ⏳")
            stream.markdown("".join(f"<div class='small'>{'🔴' if x['flag'] else '⚪'} {html.escape(x['name'])} vs {html.escape(x['doc'])}: violation {(x['sapling'].get('violation') or 0):.2f}</div>" for x in allc[:i]), unsafe_allow_html=True)
    stream.empty()
    nm = res["normalisation"]
    info.info(("Replaying cached run from " + res["run_at"] + " · " if not live else "") +
              f"Normalisation: {nm[0].get('mode')} via {nm[0].get('gateway')} ({nm[0].get('model')}) · Mubit request ids: " + ", ".join(str(n.get('mubit_request_id')) for n in nm))
    ncomp = sum(len(m["comparisons"]) for m in res["medicines"])
    tally.markdown(f"### {len(res['medicines'])} medicines checked across {len(case['documents'])} documents ({ncomp} Sapling calls), **{sum(m['flag'] for m in res['medicines'])} flagged**")
    st.markdown("#### Pharmacist worklist (one row per medicine, flagged first)")
    for m in res["medicines"]: st.markdown(render(m), unsafe_allow_html=True)
    with st.expander("Normalised lines (canonical name + strength + dose + frequency)"):
        for d, ls in res["normalised_lines"].items():
            st.markdown(f"**{d}**"); st.table([{"original": l["original"], "canonical": l["canonical_text"]} for l in ls])
    st.caption("Sapling returned status 'unsure' on every call; MedMatch ranks by the raw violation probability. Grey = not flagged, NOT confirmed safe.")
st.divider()
st.caption(f"Synthetic records reconstructed from public coroner report {case['ref']} {case['source_url']}. Not for clinical use.")
