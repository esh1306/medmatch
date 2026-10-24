# DRAFTS ONLY. Nothing here has been posted.

## X (under 280 chars)
A care agency left epilepsy medicine off a chart for 6 days. Coroner: "no system in place to cross check."

We built MedMatch at the @MubitLabs x Night Shift hackathon: LLM extraction via Mubit + Banyan Sapling flag med mismatches for a pharmacist. [video link]

## LinkedIn (tag Mubit)
In April 2025, a man with epilepsy was moved between care providers. One chart still listed a medicine his GP had stopped. Another left out his sodium valproate completely, so he missed 6 days of it. He died in May. The coroner wrote that there was "no system in place to cross check" (Prevention of Future Deaths report 2026-0166).

This isn't a one-off. PFD Monitor counts 273 coroner reports about unreliable hospital discharge.

At the Mubit x Night Shift hackathon today we built MedMatch:
• You give it the prescriber's record (GP record or discharge letter) and the care home's medicines chart.
• An LLM through the Mubit gateway pulls out each medicine pair.
• Banyan Sapling checks each pair against one policy: stopped means stopped, a replacement replaces, doses match, and nothing goes missing.
• Contradictions go onto a pharmacist's worklist.

On synthetic records rebuilt from three coroner reports, it flagged all four real conflicts. It also flagged one false positive (vitamin D written two different ways). Rows it doesn't flag are labelled "not verified", never "all clear".

Synthetic data only. Not for clinical use.
[video link] [repo link]
@Mubit #hackathon #patientsafety

## 90-second recording script
1. **0–10s.** Show the app title. Say: "When people move between care providers, their medicines charts drift. Coroners keep writing about it."
2. **10–30s.** In the sidebar, pick **Fisher (step 1)**. Point at the coroner quote and at the two documents side by side. Say: "The GP stopped phenobarbital on 8 April. The community team's chart still gives it twice a day."
3. **30–45s.** Set the mode to **Live (Mubit gateway + Sapling)**. Click **Check records**. Point at the extraction banner showing gpt-4o-mini via the Mubit gateway. The rows stream in, and phenobarbital goes red at about 0.8.
4. **45–60s.** Pick **Fisher (step 2)** and click **Check records**. Valproate goes red, flagged by both Sapling and the rule check. Say: "Valproate never made it onto the agency's chart. That's 6 days of missed doses in the real case."
5. **60–75s.** Pick **Elliott**. Switch to **Replay from cache** for speed and click **Check records**. Oramorph goes red: it should have been replaced by oxycodone, not given alongside it.
6. **75–90s.** Point at the grey rows. Say: "Grey means not verified, not safe. Sapling is always 'unsure', so we rank by violation probability, and a person makes the call." Show the footer: synthetic data, not for clinical use.

## Side-quests channel message (template)
Team: [TEAM NAME]
Side quest: Banyan Sapling Policy Challenge
What we built: MedMatch flags medicine contradictions between a GP record or discharge letter and a care home's medicines chart. It uses Banyan Sapling with one reconciliation policy, and extraction runs through the Mubit gateway.
X post: [X LINK]
LinkedIn post: [LINKEDIN LINK]
Repo: [GITHUB LINK]
