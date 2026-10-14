import json
T = {}
T["Immunexis Overview"] = """Immunexis Overview slide. Therapeutic area: Immunology.
Product: Immunexis (immuneximab). Tagline: Targeted Immune Modulation for Lasting Disease Control.

Mechanism of Action: Immunexis is a fully human monoclonal antibody that selectively targets and modulates the IL-23 pathway, reducing pathogenic Th17-driven inflammation while preserving protective immune function.

Image: smiling middle-aged woman (patient) with abstract molecular graphics.
Footer: For healthcare professional use only."""
T["Immunexis Efficacy"] = """Immunexis Clinical Efficacy slide. Trial: IMMUNEX-1 Phase III Trial, N=1,247, 52 weeks.

Key results:
- 78% Clinical Response at Week 16 (vs 32% placebo).
- 62% Clinical Remission at Week 52 (vs 19% placebo).
- 3.2 weeks Median Time to Response (rapid onset of action).

Primary Endpoint: Clinical Remission at Week 52. Bar chart: Immunexis 62%, Placebo 19%, p<0.001.
Footer: Sample data for demonstration purposes only."""
T["Immunexis Safety"] = """Immunexis Safety Profile slide. Well-tolerated with a consistent safety profile through 52 weeks. Comparable discontinuation rates to placebo.

Adverse events table, Immunexis (n=623) vs Placebo (n=624):
- Upper respiratory tract infection: 8.4% vs 7.9%
- Injection site reaction: 5.2% vs 2.1%
- Headache: 4.1% vs 3.8%
- Fatigue: 3.0% vs 2.7%
- Serious adverse events: 2.9% vs 3.1%
- Discontinuation due to AE: 1.8% vs 2.0%

Callouts: No New Safety Signals. Low Immunogenicity (<2% anti-drug antibodies). No Dose-Limiting Toxicity.
Footer: For information only. Not a real product or brand logo."""
T["Immunexis Dosing"] = """Immunexis Dosing & Administration slide. Simple dosing regimen designed for patient convenience.

Dosing schedule (subcutaneous, SC):
- Week 0: Loading Dose, 300 mg SC
- Week 4: Second Dose, 300 mg SC
- Week 8: Third Dose, 300 mg SC
- Every 8 Weeks: Maintenance, 150 mg SC

Induction: 300 mg subcutaneous injection at Weeks 0, 4 and 8.
Maintenance: 150 mg subcutaneous injection every 8 weeks.
Self-Administration: Prefilled Pen, at-home administration after training.
Storage: Refrigerate at 2-8°C.
Administration Sites: Upper arm, thigh, or abdomen. Rotate injection sites.
Footer: For information only. Not a real product or brand logo."""
T["Immunexis Resources"] = """Immunexis Patient Support & Resources slide. Comprehensive support programs to help patients start and stay on therapy.

Patient Support Program: nurse educators; injection training; appointment reminders; 24/7 hotline.
Financial Assistance: co-pay savings card; patient assistance; benefits investigation; prior auth assistance.
HCP Resources: prescribing information; peer education; clinical reprints; dosing guides.
Patient Education: disease awareness materials; self-injection videos; treatment diary; caregiver resources.

Getting Started with Immunexis: 1. Prescribe & submit enrollment. 2. Benefits verification & prior auth. 3. Patient receives first dose."""
json.dump(T, open("extracted_text.json","w"), indent=1, ensure_ascii=False)
