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

## How it works

```
 prescriber record ─┐                         ┌─> Banyan Sapling (one call per medicine, run in parallel)
 (GP / discharge)   ├─> LLM via Mubit gateway ─┤     policy + both lines -> violation probability
 care chart (MAR) ──┘   (gpt-4o-mini, JSON:    │     red if violation >= 0.4
                        name, prescriber_      └─> rule check in code (not Sapling): prescribed but
                        instruction,                missing from the care chart -> red
                        care_record_line)
                                   ──> pharmacist worklist: red "Conflict, pharmacist review"
                                       or grey "No conflict found (not verified)"
```

- **Sapling policy:** "A care medication record must match the most recent prescriber instruction: discontinued medicines must not be given, replacements must replace not add, doses must match, and every prescribed medicine must be on the administration chart."
- **Sapling evidence:** the prescriber line, then the care-record line.
- **Sapling claim:** "The care record is consistent with the prescriber instruction."
- **Extraction:** the extraction was **live through the Mubit gateway** (`https://api.mubit.ai/openai/v1`, gpt-4o-mini) for every run in this repo. A deterministic fallback in `data/extracted/*.fallback.json` is used only if the gateway fails.
- **Caching:** results are cached in `data/results/*.json` so the demo can be replayed without network calls.

## Data

All documents in `data/cases/` are **synthetic**. They were rebuilt only from facts the coroner stated, and each one carries its source report and link. The other medicines, any doses the coroner did not state, and the layout are made up for illustration. The matching medicines are deliberate controls. They are not real patient records. Note that the coroner said it was "far from clear" whether phenobarbital was actually given to Mr Fisher. The handwritten record says it was.

## Test results (honest)

**Earlier framing tests:** 24 Sapling calls on PFD-derived pairs (`sapling_pfd_tests.csv`, kept outside this repo). None came back confident: every status was `unsure`. Under framing F1, true conflicts scored violation **0.50–0.87** and matching controls scored **0.07–0.12**. The weakest case was a dropped medicine (0.50), which is why the code rule check exists.

**This build's run (24 Oct 2026, about 08:16 BST, live extraction, 21 medicine pairs, all statuses `unsure`):**

| Case | Real conflict | Violation | Flagged? | Other flags |
|---|---|---|---|---|
| Fisher step 1 (GP vs community chart) | Phenobarbital discontinued but still charted | 0.82 | Red | none. Controls 0.07–0.36 |
| Fisher step 2 (community vs agency eMAR) | Valproate missing from eMAR | 0.88 | Red, by Sapling **and** the rule check | none. Controls 0.09–0.38 |
| Elliott | Oramorph still active after replacement | 0.57 | Red | The oxycodone row itself scored 0.09, so the conflict surfaces only on the Oramorph row |
| Burgess | Brivaracetam 4ml vs 10ml | 0.65 | Red | **False positive:** cholecalciferol 800 units vs "Vit D3 800iu" scored 0.80 |

All 4 real conflicts were flagged. There was 1 false positive among 17 control pairs. The highest-scoring unflagged control was 0.38, close to the 0.4 threshold. Sapling latency was about 1.6–7 s per call when run in parallel.

## Limits

- Sapling never returned a confident verdict. MedMatch ranks by the raw violation probability. Grey means "not flagged", **not** "safe".
- Synonyms and unit spellings (Vit D3 vs cholecalciferol) can trigger false flags. A drug-name normaliser such as dm+d would help.
- The demo was tested on 4 synthetic pairs only. It has no clinical validation and is not for clinical use.
- In real life, a care home can see a GP record through GP Connect (HTML view) but cannot use the Summary Care Record. Integration is future work.

## Run

```bash
python3 -m venv --system-site-packages .venv && .venv/bin/pip install streamlit openai requests
# Mubit key: put it in /workspace/.secrets/mubit_key (gitignored, read at runtime, never logged)
.venv/bin/python extract.py   # live extraction via Mubit gateway (cached to data/extracted/*.live.json)
.venv/bin/python judge.py     # Sapling judging, cached to data/results/
.venv/bin/streamlit run app.py --server.port 8501
.venv/bin/python shoot.py cache fisher_gp_vs_community   # Playwright screenshots
```
In the app, choose a case and a mode (Live, or Replay from cache), then click **Check records**.
