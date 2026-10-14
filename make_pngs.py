import textwrap, json
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Helvetica.ttc"
docs = {
 "01_elranatamab_bcma": ("Elranatamab: BCMA-Directed Bispecific Antibody in Multiple Myeloma",
  "Elranatamab is a humanized bispecific antibody that binds B-cell maturation antigen (BCMA) on myeloma cells and CD3 on T cells. Simultaneous engagement redirects cytotoxic T cells to lyse plasma cells. In the phase 2 MagnetisMM-3 study of relapsed or refractory multiple myeloma, patients who had received an immunomodulatory agent, a proteasome inhibitor and an anti-CD38 antibody achieved an objective response rate of 61 percent. Cytokine release syndrome was the most common adverse event and was mostly grade 1 or 2. Step-up priming doses mitigate its severity."),
 "02_mrna_vaccine_lnp": ("Lipid Nanoparticle Delivery of Nucleoside-Modified mRNA Vaccines",
  "Nucleoside-modified messenger RNA encoding the SARS-CoV-2 spike glycoprotein is encapsulated in lipid nanoparticles containing an ionizable cationic lipid, cholesterol, a phospholipid and PEG-lipid. After intramuscular injection, the particles are endocytosed by antigen-presenting cells. Endosomal escape releases mRNA into the cytosol where ribosomes translate the spike protein, triggering neutralizing antibody and CD8 T-cell responses. Substituting pseudouridine reduces innate sensing through toll-like receptors."),
 "03_amyloid_alzheimers": ("Amyloid Beta and Tau Pathology in Alzheimer's Disease",
  "Alzheimer's disease is characterized by extracellular amyloid beta plaques derived from sequential cleavage of amyloid precursor protein by beta-secretase and gamma-secretase, and by intraneuronal neurofibrillary tangles of hyperphosphorylated tau. Monoclonal antibodies that clear aggregated amyloid, such as lecanemab, slow cognitive decline in early disease. Amyloid-related imaging abnormalities, including cerebral edema and microhemorrhage, require MRI monitoring, especially in APOE e4 homozygotes."),
 "04_metformin_ampk": ("Metformin Mechanism of Action in Type 2 Diabetes Mellitus",
  "Metformin lowers fasting plasma glucose primarily by suppressing hepatic gluconeogenesis. It inhibits mitochondrial complex I, raising the AMP to ATP ratio and activating AMP-activated protein kinase (AMPK). Activated AMPK reduces expression of gluconeogenic enzymes and improves peripheral insulin sensitivity. Common adverse effects are gastrointestinal. Lactic acidosis is rare but is a contraindication-related concern in severe renal impairment with eGFR below 30."),
 "05_crispr_sickle_cell": ("CRISPR-Cas9 Gene Editing for Sickle Cell Disease",
  "Sickle cell disease results from a single nucleotide substitution in the HBB gene producing hemoglobin S, which polymerizes under deoxygenation. Exagamglogene autotemcel uses CRISPR-Cas9 to disrupt the erythroid-specific enhancer of BCL11A in autologous CD34-positive hematopoietic stem cells, de-repressing fetal hemoglobin gamma-globin expression. After myeloablative busulfan conditioning and infusion, most patients were free of vaso-occlusive crises."),
 "06_beta_lactam_resistance": ("Mechanisms of Beta-Lactam Antibiotic Resistance in Gram-Negative Bacteria",
  "Gram-negative pathogens resist beta-lactam antibiotics through production of beta-lactamases such as extended-spectrum beta-lactamases (ESBL) and carbapenemases like KPC and NDM-1, which hydrolyze the beta-lactam ring. Additional mechanisms include porin loss that reduces outer membrane permeability, efflux pump overexpression, and altered penicillin-binding proteins. Combination agents such as ceftazidime-avibactam pair a cephalosporin with a beta-lactamase inhibitor."),
 "07_pd1_checkpoint": ("PD-1 Immune Checkpoint Blockade with Pembrolizumab",
  "Programmed cell death protein 1 (PD-1) on activated T cells binds PD-L1 and PD-L2 on tumor cells, delivering an inhibitory signal that causes T-cell exhaustion. Pembrolizumab is a monoclonal IgG4 antibody that blocks this interaction and restores antitumor immunity. Immune-related adverse events include pneumonitis, colitis, hepatitis and thyroiditis, and are managed with corticosteroids. PD-L1 combined positive score guides patient selection in non-small cell lung cancer."),
 "08_statin_ldl": ("Statins and LDL Cholesterol Reduction in Atherosclerotic Cardiovascular Disease",
  "Statins competitively inhibit HMG-CoA reductase, the rate-limiting enzyme of hepatic cholesterol biosynthesis. Reduced intracellular cholesterol upregulates LDL receptors on hepatocytes, increasing clearance of circulating LDL cholesterol by thirty to fifty percent. High-intensity atorvastatin lowers the risk of myocardial infarction and stroke. Myopathy and rhabdomyolysis are rare dose-related adverse effects, and creatine kinase should be checked when muscle symptoms occur."),
}
W=1400
tf=ImageFont.truetype(FONT,44); bf=ImageFont.truetype(FONT,32)
for key,(title,body) in docs.items():
    tl=textwrap.wrap(title,55); bl=textwrap.wrap(body,78)
    H=60+len(tl)*58+30+len(bl)*46+60
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im); y=40
    for l in tl: d.text((50,y),l,font=tf,fill="black"); y+=58
    y+=30
    for l in bl: d.text((50,y),l,font=bf,fill="black"); y+=46
    im.save(f"pngs/{key}.png")
json.dump({k:v[0] for k,v in docs.items()},open("pngs/manifest.json","w"),indent=1)
print(len(docs),"written")
