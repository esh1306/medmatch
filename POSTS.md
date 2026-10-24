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

## 90-second recording script
1. **0–10s.** Show the app title. Say: "When people move between care providers, their medicines charts drift. Coroners keep writing about it."
2. **10–30s.** Pick **Fisher**. Point at the three documents: the GP's whole existing medicines list, the community team's handwritten chart, the agency eMAR. Say: "MedMatch checks every medicine on the list against every chart."
3. **30–50s.** Choose **Live (Mubit gateway + Sapling)**, click **Check records**. Point at the banner (gpt-4o-mini via api.mubit.ai, Mubit request IDs). Rows stream in: 6 medicines x 2 charts = 12 Sapling calls. Phenobarbital red on the community chart (stopped but still given, 0.61); valproate red on the agency eMAR (missing, 0.87).
4. **50–65s.** Pick **Elliott** (Replay from cache). Oramorph red: replaced by oxycodone on the discharge letter, still on the care eMAR.
5. **65–80s.** Pick **Burgess**. Brivaracetam red at 0.84: 4 ml on the chart vs 10 ml prescribed, caught by Sapling alone. Point at colecalciferol vs "Vit D3 800iu": grey, because names are normalised first.
6. **80–90s.** Say: "Grey means not verified, not safe; a pharmacist makes the call." Show the footer: synthetic data, not for clinical use.

## Side-quests channel message (template)
Team: [TEAM NAME]
Side quest: Banyan Sapling Policy Challenge
What we built: MedMatch checks a patient's whole medicines list against every care chart and flags medicine contradictions between a GP record or discharge letter and a care home's medicines chart. It uses Banyan Sapling with one reconciliation policy, and extraction runs through the Mubit gateway.
X post: [X LINK]
LinkedIn post: [LINKEDIN LINK]
Repo: [GITHUB LINK]
