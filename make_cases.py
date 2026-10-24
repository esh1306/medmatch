"""Builds the synthetic case files. Every document is SYNTHETIC, reconstructed only from facts
stated in public coroner Prevention of Future Deaths (PFD) reports. Names of other medicines,
doses not stated by the coroner, and all formatting are illustrative."""
import json, pathlib
D=pathlib.Path("data/cases")
NOTE="SYNTHETIC record reconstructed from facts stated in a public coroner report. Other medicines, unstated doses and layout are illustrative. Not a real patient record. Not for clinical use."
cases=[
dict(id="fisher_gp_vs_community", title="Fisher (step 1): GP record vs community team handwritten chart",
 ref="PFD 2026-0166 (John Fisher, report dated 19 Mar 2026)",
 source_url="https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/",
 news_url="",
 coroner_fact="'According to the UCR records this apparently included phenobarbital tablets twice a day even though Mr Fisher's GP had discontinued the phenobarbital on 8 April 2025.'",
 left_label="GP practice medication record (prescriber)",
 left=f"""[{NOTE}]
Source: PFD 2026-0166  https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/

TRINITY MEDICAL CENTRE - MEDICATION SUMMARY (printed 08/04/2025)
Pt: J.F.  DOB: xx/xx/1950  NHS No: xxx xxx xxxx
Problems: Epilepsy (dx Dec 2020). Chest infection Apr 2025.

ACUTE / REPEAT MEDS
- Sodium valproate 200mg/5ml oral soln - 10ml BD  [repeat]
- Levetiracetam 100mg/ml oral soln - 7.5ml BD  [repeat]
- Phenobarbital 30mg tabs - 1 BD  ** DISCONTINUED 08/04/2025 by GP **
- Lansoprazole 15mg orodisp tab - 1 OD  [repeat]
- Senna 7.5mg tabs - 2 ON prn  [repeat]
- Amoxicillin 125mg/5ml susp - 20ml TDS x 5 days (started 07/04/25)  [acute]

Note: phenobarbital supplied by community pharmacy in a SEPARATE BOX, not in blister pack.
""",
 right_label="Community response team handwritten MAR, 9-15 Apr 2025 (care record)",
 right=f"""[{NOTE}]
Source: PFD 2026-0166  https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/

URGENT COMMUNITY RESPONSE - MEDICATION ADMINISTRATION RECORD (handwritten, transcribed)
Client: J Fisher   Period: 09/04/25 - 15/04/25   Allergies: NKDA

Medicine                      | Dose / route   | Times      | Signed
Na valproate liquid 200/5     | 10 ml PO       | 08:00 20:00| ✓✓✓✓✓✓✓
Levetiracetam liquid          | 7.5 ml PO      | 08:00 20:00| ✓✓✓✓✓✓✓
Phenobarbital 30mg tab        | 1 tab PO       | 08:00 20:00| ✓✓✓✓✓✓✓  (from blister? box?)
Lansoprazole 15mg             | 1 PO           | 08:00      | ✓✓✓✓✓✓✓
Amoxicillin liquid            | 20 ml PO       | TDS        | ✓✓✓✓✓ (course end?)
Senna                         | 2 tabs PO      | night PRN  | -
"""),
dict(id="fisher_community_vs_agency", title="Fisher (step 2): community team chart vs care agency electronic chart",
 ref="PFD 2026-0166 (John Fisher, report dated 19 Mar 2026)",
 source_url="https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/",
 news_url="",
 coroner_fact="'although the UCR handwritten forms included sodium valproate oral solution, this was not added at all into the Coastal Homecare electronic MAR chart' ... 'there is no system in place to cross check'.",
 left_label="Community response team handwritten MAR (handover source)",
 left=f"""[{NOTE}]
Source: PFD 2026-0166  https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/

URGENT COMMUNITY RESPONSE - MAR handed over to care agency 15/04/25
Na valproate oral soln 200mg/5ml   10 ml   BD (08:00, 20:00)
Levetiracetam oral soln 100mg/ml   7.5 ml  BD
Lansoprazole 15mg                  1       OD mane
Senna 7.5mg                        2       ON PRN
Amoxicillin susp (chest inf.)      20 ml   TDS - stop date not written
""",
 right_label="Care agency electronic MAR, from 15 Apr 2025 (care record)",
 right=f"""[{NOTE}]
Source: PFD 2026-0166  https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/

HOMECARE eMAR  - Client JF  - Visits: 3x daily  - Created 15/04/2025 by supervisor
ID  Medication                         Dose     Schedule        Form
01  Levetiracetam 100mg/ml oral soln   7.5ml    Morning, Tea    liquid
02  Lansoprazole 15mg orodisp          1 tab    Morning         blister
03  Senna 7.5mg                        2 tabs   Bed PRN         blister
04  Amoxicillin 125mg/5ml              20ml     Mor/Lunch/Tea   liquid
(no further medicines recorded)
"""),
dict(id="elliott", title="Elliott: hospital discharge letter vs care home electronic MAR",
 ref="PFD 2025-0515 (Thompson Elliott, report dated 14 Oct 2025)",
 source_url="https://www.judiciary.uk/prevention-of-future-death-reports/thompson-elliott-prevention-of-future-deaths-report/",
 news_url="",
 coroner_fact="Oramorph was switched to oxycodone because of its impact on his kidneys; oxycodone was then 'incorrectly added to the record as new and additional medication - not replacement medication'.",
 left_label="Hospital discharge letter, 18 Dec 2024 (prescriber)",
 left=f"""[{NOTE}]
Source: PFD 2025-0515  https://www.judiciary.uk/prevention-of-future-death-reports/thompson-elliott-prevention-of-future-deaths-report/

DISCHARGE SUMMARY - Ward 7   Date of discharge: 18/12/2024   Destination: residential care home
Pt: T.E.   Reason for admission: pain / reduced kidney function

MEDICATION CHANGES
STOPPED:  Oramorph (morphine sulfate oral soln 10mg/5ml) - STOP. Reason: impact on renal function.
STARTED:  Oxycodone oral soln 5mg/5ml 2.5ml 4-hourly PRN - REPLACES Oramorph (renal).
UNCHANGED:
  Paracetamol 500mg 2 tabs QDS
  Amlodipine 5mg OD
  Laxido 1 sachet BD
  Atorvastatin 20mg ON
""",
 right_label="Care home electronic MAR, 20 Dec 2024 (care record)",
 right=f"""[{NOTE}]
Source: PFD 2025-0515  https://www.judiciary.uk/prevention-of-future-death-reports/thompson-elliott-prevention-of-future-deaths-report/

eMAR - Resident T.E. - Room 12 - printed 20/12/2024 21:00
Medicine                          Instruction           Status   Notes
Paracetamol 500mg tab             2 QDS                 Active
Amlodipine 5mg tab                1 OD                  Active
Laxido sachet                     1 BD                  Active
Atorvastatin 20mg                 1 night               Active
Oramorph 10mg/5ml                 2.5ml 4hrly PRN       Active   given 18/12, 19/12, 20/12
Oxycodone 5mg/5ml liquid          2.5ml 4hrly PRN       Active   NEW - added 20/12 (additional)
Discharge letter: not located
"""),
dict(id="burgess", title="Burgess: neurology / family instruction vs care home administration record",
 ref="PFD 2024-0077 (Burgess; response from Godfrey Care dated 27 Mar 2024; events July 2022)",
 source_url="https://www.judiciary.uk/wp-content/uploads/2024/02/2024-0077-Response-from-Godfrey-Care.pdf",
 news_url="",
 coroner_fact="'informed by Mr Burgess' mother and the Neurology department ... that the appropriate dose of Brivaracetam was 4ml twice daily' ... '10ml twice daily was commenced on 26 July 2022 following a call to the 111 service'.",
 left_label="Neurology department / family instruction (prescriber)",
 left=f"""[{NOTE}]
Source: PFD 2024-0077  https://www.judiciary.uk/wp-content/uploads/2024/02/2024-0077-Response-from-Godfrey-Care.pdf

Telephone record - Neurology dept (confirmed by mother), July 2022
Brivaracetam 10mg/ml oral solution: 4 ml twice daily (morning & evening)
Continue other regular medicines unchanged:
  Omeprazole 20mg caps OD
  Macrogol sachet 1 OD
  Cholecalciferol 800 units OD
""",
 right_label="Care home administration record from 26 Jul 2022 (care record)",
 right=f"""[{NOTE}]
Source: PFD 2024-0077  https://www.judiciary.uk/wp-content/uploads/2024/02/2024-0077-Response-from-Godfrey-Care.pdf

MAR CHART  Resident: Mr B   Week commencing 25/07/2022
22-25/07: brivaracetam WITHHELD - awaiting written instruction from prescriber
Brivaracetam 10mg/ml soln   10 ml   BD  (started 26/07 after NHS 111 call)
Omeprazole 20mg             1 cap   OD
Macrogol                    1 sach  OD
Vit D3 800iu                1 tab   OD
"""),
]
fallback={
"fisher_gp_vs_community":[
 ("Sodium valproate","Sodium valproate 200mg/5ml oral solution 10ml twice daily (repeat)","Na valproate liquid 200/5 10ml PO 08:00 20:00, signed daily"),
 ("Levetiracetam","Levetiracetam 100mg/ml oral solution 7.5ml twice daily (repeat)","Levetiracetam liquid 7.5ml PO 08:00 20:00, signed daily"),
 ("Phenobarbital","Phenobarbital 30mg tablets: DISCONTINUED by GP on 08/04/2025","Phenobarbital 30mg tab 1 tab PO 08:00 20:00, signed daily 09/04-15/04/2025"),
 ("Lansoprazole","Lansoprazole 15mg once daily (repeat)","Lansoprazole 15mg 1 PO 08:00, signed daily"),
 ("Senna","Senna 7.5mg 2 tablets at night when required (repeat)","Senna 2 tabs PO at night PRN, not given"),
 ("Amoxicillin","Amoxicillin 125mg/5ml 20ml three times daily for 5 days from 07/04/2025","Amoxicillin liquid 20ml PO three times daily, stop date not written")],
"fisher_community_vs_agency":[
 ("Sodium valproate","Sodium valproate oral solution 200mg/5ml 10ml twice daily","NOT ON CHART"),
 ("Levetiracetam","Levetiracetam oral solution 100mg/ml 7.5ml twice daily","Levetiracetam 100mg/ml oral solution 7.5ml morning and tea"),
 ("Lansoprazole","Lansoprazole 15mg once daily in the morning","Lansoprazole 15mg orodispersible 1 tab morning"),
 ("Senna","Senna 7.5mg 2 at night when required","Senna 7.5mg 2 tabs bedtime PRN"),
 ("Amoxicillin","Amoxicillin suspension 20ml three times daily, stop date not written","Amoxicillin 125mg/5ml 20ml morning/lunch/tea")],
"elliott":[
 ("Oramorph (morphine oral solution)","Oramorph STOPPED on discharge 18/12/2024 because of impact on renal function; replaced by oxycodone","Oramorph 10mg/5ml 2.5ml 4-hourly PRN, status Active, given 18/12, 19/12 and 20/12"),
 ("Oxycodone","Oxycodone oral solution 5mg/5ml 2.5ml 4-hourly PRN, REPLACES Oramorph","Oxycodone 5mg/5ml 2.5ml 4-hourly PRN, Active, added 20/12 as new additional medicine alongside Oramorph"),
 ("Paracetamol","Paracetamol 500mg 2 tablets four times daily (unchanged)","Paracetamol 500mg 2 four times daily, Active"),
 ("Amlodipine","Amlodipine 5mg once daily (unchanged)","Amlodipine 5mg 1 once daily, Active"),
 ("Laxido","Laxido 1 sachet twice daily (unchanged)","Laxido 1 sachet twice daily, Active"),
 ("Atorvastatin","Atorvastatin 20mg at night (unchanged)","Atorvastatin 20mg 1 at night, Active")],
"burgess":[
 ("Brivaracetam","Brivaracetam 10mg/ml oral solution 4ml twice daily (neurology, confirmed by mother)","Brivaracetam 10mg/ml solution 10ml twice daily, started 26/07/2022 after NHS 111 call"),
 ("Omeprazole","Omeprazole 20mg once daily (unchanged)","Omeprazole 20mg 1 cap once daily"),
 ("Macrogol","Macrogol 1 sachet once daily (unchanged)","Macrogol 1 sachet once daily"),
 ("Cholecalciferol (vitamin D)","Cholecalciferol 800 units once daily (unchanged)","Vit D3 800iu 1 tab once daily")],
}
for c in cases:
    c["synthetic_note"]=NOTE
    (D/f"{c['id']}.json").write_text(json.dumps(c,indent=2,ensure_ascii=False))
    (D/f"{c['id']}_prescriber.txt").write_text(c["left"]); (D/f"{c['id']}_care.txt").write_text(c["right"])
    fb=[dict(name=n,prescriber_instruction=p,care_record_line=r) for n,p,r in fallback[c["id"]]]
    pathlib.Path(f"data/extracted/{c['id']}.fallback.json").write_text(json.dumps(fb,indent=2))
print("ok",len(cases))
