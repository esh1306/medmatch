# MedMatch

MedMatch catches medicine mismatches between the **prescriber's record** (GP record or hospital discharge letter) and the **care home or home-care agency medicines chart**. Each contradiction goes onto a pharmacist's worklist.

Built at the Mubit x Night Shift hackathon (London, 24 Oct 2026) for the Banyan Sapling Policy Challenge.

## The problem (sourced)

- **John Fisher, died 4 May 2025. Coroner's report PFD 2026-0166, dated 19 Mar 2026.** The community team's records show "phenobarbital tablets twice a day even though Mr Fisher's GP had discontinued the phenobarbital on 8 April 2025". Sodium valproate "was not added at all into the Coastal Homecare electronic MAR chart", and doses were missed for 6 days. The coroner said there was no system in place to cross-check. https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/
- **Thompson Elliott. PFD 2025-0515, dated 14 Oct 2025.** The hospital switched him from Oramorph to oxycodone because of the effect on his kidneys. The care home added oxycodone "as new and additional medication – not replacement medication", and an opioid overdose followed. https://www.judiciary.uk/prevention-of-future-death-reports/thompson-elliott-prevention-of-future-deaths-report/
- **Burgess. PFD 2024-0077, response from Godfrey Care.** Neurology and his mother said brivaracetam **4ml** twice daily. **10ml** twice daily was started on 26 Jul 2022 after a call to NHS 111. https://www.judiciary.uk/wp-content/uploads/2024/02/2024-0077-Response-from-Godfrey-Care.pdf
- **This keeps happening.** PFD Monitor groups **273** coroner reports under "Unreliable hospital discharge processes". https://pfdmonitor.org/concerns/recurring-concern-ba5e203f1b24ff50a1bd80b9/
- **The safety net is incomplete.** In August 2026, only **66%** of NHS Discharge Medicines Service claims were complete (16,783 of 25,328). https://www.nhsbsa.nhs.uk/prescription-data/dispensing-data/nhs-discharge-medicines-service
- **HSSIB (14 Aug 2025)** found medication harm linked to "conflicting information in his patient records". https://www.hssib.org.uk/patient-safety-investigations/medication-related-harm/third-investigation-report/

## How it works (v2: whole existing medicines list)

```
 GP / prescriber FULL existing medicines list (base) ─┐
 prescriber updates (discharge letter, neurology)  ───┼─> 1. NORMALISE every line of every document
 every care chart (handwritten MAR, eMAR, ...)  ──────┘      LLM via Mubit gateway (gpt-4o-mini, JSON) -> generic name,
                                                             strength, unit, dose, frequency, status, replaces
                                                             + data/synonyms.json (brand->generic, Vit D3, iu->units,
                                                               b.d./b.i.d.->twice daily, 1g->1000 mg)
  2. CURRENT PRESCRIBED LIST (code): base, then updates applied: started / stopped / replaced / dose changed
  3. EVERY medicine x EVERY care chart -> Banyan Sapling (F1): policy + "Prescriber record: <canonical line + original>"
     + "Care record: <canonical line + original>" ; red if violation >= 0.4
  4. RULE CHECK in code (labelled, not Sapling): missing from chart / extra (on chart, not currently prescribed) / duplicated
  5. WORKLIST: one row per medicine, per-document status, red "Conflict, pharmacist review" or grey "No conflict found (not verified)"
```

- Sapling endpoint: exactly the official quickstart HF endpoint `https://6adbee0669a00298cd4774c9.endpoints.huggingface.cloud` (no auth).
- Policy: "A care medication record must match the most recent prescriber instruction: discontinued medicines must not be given, replacements must replace not add, doses must match, and every prescribed medicine must be on the administration chart." Claim: "The care record is consistent with the prescriber instruction."
- Gateway: OpenAI SDK with `base_url="https://api.mubit.ai/openai/v1"` and the Mubit key as `api_key` (per docs.mubit.ai quickstart). Every call's `x-middleware-request-id` response header (`mreq_...`, Mubit's call ID) is stored in `data/results/*.json` and shown in the app as proof the call went through Mubit. Key is read from `/workspace/.secrets/mubit_key` at runtime, never printed, logged or committed.
- Synonym table `data/synonyms.json`: small hand-compiled table, generic names per RxNorm/openFDA and NHS dm+d (links in file). Illustrative, not complete.
- v1 (pairwise) cases/results kept in `data/cases/v1_pairs/`, `data/results/v1_pairs/` for comparison.

## Data

All documents in `data/cases/` are **synthetic**, rebuilt only from coroner-stated facts, each labelled with its source report and link. Other medicines, unstated doses and layout are illustrative; matching medicines are deliberate controls. The Elliott GP pre-admission list is illustrative (the coroner states the Oramorph->oxycodone switch). The coroner said it was "far from clear" whether phenobarbital was actually given to Mr Fisher; the handwritten record says it was.

## Results (honest)

**Earlier framing tests:** 24 Sapling calls, 0 confident (all `unsure`); F1 true conflicts 0.50-0.87 vs controls 0.07-0.12.

**v1 (pairwise, before normalisation):** 4/4 real conflicts flagged, but a false positive: cholecalciferol 800 units vs "Vit D3 800iu" = 0.80.

**v2 whole-list run (24 Oct 2026, ~08:35 BST, live normalisation via Mubit, 22 Sapling calls, all status `unsure`):**

| Case | Documents | Flagged | Numbers |
|---|---|---|---|
| Fisher | GP list + community MAR + agency eMAR (12 calls) | sodium valproate, phenobarbital | Valproate vs agency eMAR 0.87 + rule "Missing"; phenobarbital vs community MAR 0.61 + rule "Extra (stopped)". All other pairs 0.06-0.29 |
| Elliott | GP list + discharge letter + care eMAR (6 calls) | morphine sulfate (Oramorph) | 0.62 + rule "Extra (stopped; replaced by oxycodone)". Others 0.06-0.07 |
| Burgess | neurology/GP list + care MAR (4 calls) | brivaracetam | 0.84 (4 ml vs 10 ml, Sapling only). Colecalciferol now 0.06 (was 0.80 in v1) |

All 4 real conflicts flagged, 0 false positives across 18 control comparisons (highest control 0.29).

**Live regression test (`tests/test_regression.py`, results in `tests/regression_results.json`): 9/9 passed.**
Must NOT flag: Vit D3 vs cholecalciferol 0.09; acetaminophen vs paracetamol 0.13; Adcal-D3 vs calcium carbonate + colecalciferol 0.07; b.d. vs twice daily 0.07; 1g vs 1000mg 0.10.
Must flag: Fisher phenobarbital 0.76 + rule; Fisher valproate missing 0.88 + rule; Elliott Oramorph 0.69-0.75 + rule; Burgess brivaracetam 0.83.
Caveat: in the valproate-missing test, the matching levetiracetam line also scored 0.90 (a false positive inside a must-flag test).

## Limits

- Sapling never returned a confident verdict; we rank by raw violation probability. Grey = not flagged, NOT safe.
- Oxycodone's own row scores low (0.07); the Elliott conflict surfaces on the Oramorph row (Sapling + rule).
- Sapling still produced a stray false positive in one test (levetiracetam 0.90 when another drug was missing from the same chart). Synonym table is small and hand-made; not dm+d-complete.
- LLM normalisation can mis-read messy lines; the canonical and original text are both shown so a pharmacist can check.
- Synthetic data only, 3 cases + 9 regression pairs. Not clinically validated. Not for clinical use.
- Real access: care homes can view GP records via GP Connect (HTML); Summary Care Record not approved for care homes. Integration is future work.

## Run

```bash
python3 -m venv --system-site-packages .venv && .venv/bin/pip install streamlit openai requests playwright
# Mubit key in /workspace/.secrets/mubit_key (gitignored; read at runtime, never logged)
.venv/bin/python pipeline.py                 # live: normalise via Mubit + Sapling, caches data/results/*.json
.venv/bin/python tests/test_regression.py    # live regression (synonyms must not flag, 4 conflicts must flag)
.venv/bin/streamlit run app.py --server.port 8501
.venv/bin/python shoot.py cache fisher elliott burgess   # Playwright screenshots
```
In the app pick a case, choose Live or Replay from cache, click **Check records**.
