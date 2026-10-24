"""Restructure into whole-list cases: base = full existing medicines list, then updates, then care charts."""
import json, pathlib
D = pathlib.Path("data/cases"); L = lambda i: json.loads((D / f"{i}.json").read_text())
f1, f2, el, bu = L("fisher_gp_vs_community"), L("fisher_community_vs_agency"), L("elliott"), L("burgess")
NOTE = f1["synthetic_note"]
el_gp = f"""[{NOTE}]
Source: PFD 2025-0515  {el['source_url']}

GP PRACTICE - REPEAT MEDICATION LIST (before admission, Dec 2024)
Pt: T.E.
- Oramorph 10mg/5ml oral solution - 2.5ml every 4 hours when required for pain
- Paracetamol 500mg tablets - 2 four times a day
- Amlodipine 5mg - 1 daily
- Laxido sachets - 1 twice daily
- Atorvastatin 20mg - 1 at night
"""
cases = [
 dict(id="fisher", title="Fisher (PFD 2026-0166): GP list vs community team chart vs care agency eMAR", ref=f1["ref"], source_url=f1["source_url"],
      coroner_fact=f1["coroner_fact"] + " Also: " + f2["coroner_fact"],
      documents=[dict(role="base", label="GP medicines list (existing)", text=f1["left"]),
                 dict(role="care", label="Community team handwritten MAR", text=f1["right"]),
                 dict(role="care", label="Care agency eMAR", text=f2["right"])]),
 dict(id="elliott", title="Elliott (PFD 2025-0515): GP list + discharge letter vs care home eMAR", ref=el["ref"], source_url=el["source_url"],
      coroner_fact=el["coroner_fact"],
      documents=[dict(role="base", label="GP medicines list (existing)", text=el_gp),
                 dict(role="update", label="Hospital discharge letter", text=el["left"]),
                 dict(role="care", label="Care home eMAR", text=el["right"])]),
 dict(id="burgess", title="Burgess (PFD 2024-0077): neurology/GP list vs care home MAR", ref=bu["ref"], source_url=bu["source_url"],
      coroner_fact=bu["coroner_fact"],
      documents=[dict(role="base", label="Neurology / GP medicines list", text=bu["left"]),
                 dict(role="care", label="Care home MAR", text=bu["right"])]),
]
for c in cases:
    c["synthetic_note"] = NOTE; (D / f"{c['id']}.json").write_text(json.dumps(c, indent=2, ensure_ascii=False))
import os
for old in ["fisher_gp_vs_community", "fisher_community_vs_agency"]:
    os.makedirs("data/cases/v1_pairs", exist_ok=True); os.rename(D / f"{old}.json", f"data/cases/v1_pairs/{old}.json")
os.rename(D / "burgess.json", D / "burgess.json")
print("ok")
