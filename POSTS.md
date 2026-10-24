# DRAFTS ONLY. Nothing here has been posted.

## X (under 280 chars)
A care agency left epilepsy medicine off a chart for 6 days. Coroner: no cross-check system.

MedMatch checks a patient's whole medicines list against every care chart. Banyan Sapling flags stopped, missing & wrong-dose meds. Built at @MubitLabs x Night Shift [video]

## LinkedIn (tag Mubit)
In April 2025, a man with epilepsy was moved between care providers. One chart still listed a medicine his GP had stopped. Another left out his sodium valproate completely, so he missed 6 days of it. He died in May. The coroner wrote that there was "no system in place to cross check" (Prevention of Future Deaths report 2026-0166).

This isn't a one-off. PFD Monitor counts 273 coroner reports about unreliable hospital discharge.

At the Mubit x Night Shift hackathon today we built MedMatch:
• You give it the patient's whole existing medicines list from the GP, any updates (discharge letter, specialist), and every care chart.
• An LLM through the Mubit gateway normalises every line (brand to generic, Vit D3 = colecalciferol, b.d. = twice daily, 1g = 1000mg).
• Banyan Sapling checks every medicine against every chart under one policy: stopped means stopped, a replacement replaces, doses match, nothing goes missing. Code flags anything missing, extra or duplicated.
• Contradictions go onto a pharmacist's worklist.

On synthetic records rebuilt from three coroner reports, it flagged all four real conflicts. After adding normalisation, synonym pairs (Vit D3/colecalciferol, acetaminophen/paracetamol, Adcal-D3) no longer flag: 9/9 live regression tests pass. Rows it doesn't flag are labelled "not verified", never "all clear".

Synthetic data only. Not for clinical use.
[video link] [repo link]
@Mubit #hackathon #patientsafety

## 90-second recording script (https://esh1306.github.io/medmatch/, browser at 1440x900 or 1280x800, full screen)
1. **0-12s, Journey (Fisher).** Page opens on step 01. The timeline draws GP surgery, then community team, then care agency; the two red stops pulse. Say: "John Fisher moved between three care settings in a week. Each one wrote its own medicines record."
2. **12-22s, Documents.** Click **Next**. Three records slide in: printed GP list, handwritten chart, eMAR. Say: "Phenobarbital was stopped by the GP but is still on the handwritten chart. Valproate is missing from the eMAR."
3. **22-34s, Extract.** **Next**. Lines highlight and drop into the structured list. Point at the badge: "LLM via Mubit gateway" with the real Mubit request ID.
4. **34-44s, Normalise.** **Next**. Abbreviations and brand names map to one canonical form, so different words for the same medicine never flag (regression results under the list).
5. **44-62s, Check.** **Next**. The grid fills cell by cell: 12 real Sapling calls. Two cells turn red: valproate 0.87 on the eMAR, phenobarbital 0.61 on the handwritten chart. Everything else stays grey, 0.06-0.29.
6. **62-70s, Rule check.** **Next**. Amber "Code rule: Missing / Extra" tags appear, labelled as code, not Sapling.
7. **70-85s, Worklist.** **Next**. Red cards drop in with the two conflicting lines side by side, the tally, and the coroner quote: "no system in place to cross check."
8. **85-90s.** Click **Elliott** or **Burgess** and jump to **07 Worklist** to show it works on other cases. Say: "Grey means not verified, not safe. A pharmacist makes the call."

Tip: **Play** auto-advances through all steps; arrow keys also work.

## Side-quests channel message (template)
Team: [TEAM NAME]
Side quest: Banyan Sapling Policy Challenge
What we built: MedMatch checks a patient's whole medicines list against every care chart and flags medicine contradictions between a GP record or discharge letter and a care home's medicines chart. It uses Banyan Sapling with one reconciliation policy, and extraction runs through the Mubit gateway.
X post: [X LINK]
LinkedIn post: [LINKEDIN LINK]
Repo: [GITHUB LINK]
