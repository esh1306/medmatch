import json, pathlib, time, html
import streamlit as st
from extract import extract
from judge import judge_stream, save, load, THRESHOLD, POLICY, CLAIM

ROOT = pathlib.Path(__file__).parent
st.set_page_config(page_title="MedMatch", page_icon="💊", layout="wide")
CASES = {json.loads(f.read_text())["id"]: json.loads(f.read_text()) for f in sorted((ROOT / "data/cases").glob("*.json"))}
ORDER = ["fisher_gp_vs_community", "fisher_community_vs_agency", "elliott", "burgess"]

st.markdown("""<style>
.row{border-radius:8px;padding:10px 14px;margin:6px 0;border-left:8px solid}
.red{background:#fdecea;border-color:#d93025}.grey{background:#f1f3f4;border-color:#9aa0a6}
.bar{height:10px;background:#e0e0e0;border-radius:5px;overflow:hidden;margin:4px 0}
.fill{height:10px}.small{font-size:0.82em;color:#444}.status{font-weight:700}
</style>""", unsafe_allow_html=True)

st.title("💊 MedMatch")
st.caption("Catches medicine mismatches between the prescriber's record and the care home / agency medicines chart, "
           "and puts contradictions on a pharmacist's worklist. Extraction: LLM via Mubit gateway. Judging: Banyan Sapling.")

with st.sidebar:
    cid = st.selectbox("Case", ORDER, format_func=lambda k: CASES[k]["title"])
    mode = st.radio("Mode", ["Live (Mubit gateway + Sapling)", "Replay from cache"], index=1)
    live = mode.startswith("Live")
    st.markdown(f"**Flag rule:** Sapling violation ≥ {THRESHOLD}, or the code rule check (prescribed but missing from chart).")
    with st.expander("Sapling policy and claim"):
        st.write(POLICY); st.write("Claim: " + CLAIM)

case = CASES[cid]
st.subheader(case["title"])
st.markdown(f"**Coroner-stated fact:** {case['coroner_fact']}")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**📄 {case['left_label']}**"); st.code(case["left"], language=None, wrap_lines=True)
with c2:
    st.markdown(f"**📋 {case['right_label']}**"); st.code(case["right"], language=None, wrap_lines=True)

def render(r):
    s = r["sapling"]; v = s.get("violation")
    red = r["flag"]
    head = "🔴 Conflict, pharmacist review" if red else "No conflict found (not verified)"
    pct = 0 if v is None else v * 100
    colour = "#d93025" if (v or 0) >= THRESHOLD else "#9aa0a6"
    rule = f"<div class='small'>⚙️ <b>Rule check (code, not Sapling):</b> {html.escape(r['rule'])}</div>" if r["rule"] else ""
    sap = (f"Sapling violation probability <b>{v:.2f}</b> · raw label <code>{s.get('raw_label')}</code> · "
           f"status <code>{s.get('status')}</code> · latency {s.get('wall_ms')} ms") if v is not None else \
          f"Sapling call failed ({s.get('error')})"
    return f"""<div class='row {"red" if red else "grey"}'>
<span class='status'>{head}</span> — <b>{html.escape(r['name'])}</b>
<div class='small'>Prescriber: {html.escape(r['prescriber_instruction'])}<br>Care record: {html.escape(r['care_record_line'])}</div>
<div class='bar'><div class='fill' style='width:{pct:.0f}%;background:{colour}'></div></div>
<div class='small'>{sap}</div>{rule}</div>"""

def tally(rows, total, done):
    f = sum(r["flag"] for r in rows)
    return f"### {len(rows)} of {total} medicines checked, **{f} flagged** {'' if done else '⏳'}"

if st.button("🔍 Check records", type="primary"):
    tally_ph = st.empty(); info_ph = st.empty(); list_ph = st.empty()
    rows = []
    if live:
        with st.spinner("Extracting medicines via Mubit gateway…"):
            meds, info = extract(case, use_live=True)
        info_ph.info(f"Extraction: **{info['mode']}**" + (f" · model {info.get('model')} · {info.get('latency_ms')} ms via {info.get('gateway')}" if info["mode"] == "live" else f" · {info.get('error')}"))
        tally_ph.markdown(tally(rows, len(meds), False))
        for r in judge_stream(meds):
            rows.append(r); list_ph.markdown(''.join(render(x) for x in rows), unsafe_allow_html=True)
            tally_ph.markdown(tally(rows, len(meds), False))
        save(cid, rows, info)
    else:
        res = load(cid)
        if not res:
            st.error("No cached result for this case yet. Switch to Live mode."); st.stop()
        info = res["extraction"]
        info_ph.info(f"Replaying cached run from {res['run_at']} · extraction was **{info.get("mode")}**" + (f" ({info.get('model')} via Mubit gateway)" if info.get("model") else ""))
        for r in res["rows"]:
            time.sleep(0.35); rows.append(r); list_ph.markdown(''.join(render(x) for x in rows), unsafe_allow_html=True)
            tally_ph.markdown(tally(rows, len(res["rows"]), False))
    tally_ph.markdown(tally(rows, len(rows), True)); list_ph.empty()
    st.markdown("#### Pharmacist worklist (flagged first)")
    for r in sorted(rows, key=lambda r: (not r["flag"], -(r["sapling"].get("violation") or 0))):
        st.markdown(render(r), unsafe_allow_html=True)
    st.caption("Sapling returned status 'unsure' on every call; MedMatch uses the raw violation probability to rank. "
               "Grey rows are NOT confirmed safe, only not flagged.")

st.divider()
st.caption(f"Synthetic records reconstructed from public coroner report {case['ref']} {case['source_url']}. Not for clinical use.")
