"""
Final 200 Dataset - Provenance Sensitive Domain (15 scenarios: SCN-FINAL-186 to SCN-FINAL-200)
Distribution: 2 easy, 5 medium, 8 hard
Features intricate multi-tier provenance across:
- current_consultation (Q facts)
- patient_reported (F facts)
- clinician_authored (F facts)
"""

from .scenario_builder import make_scenario

def get_provenance_sensitive_scenarios():
    scenarios = []

    # SCN-FINAL-186 (easy) - Clear patient-reported fatigue vs clinician-confirmed iron deficiency
    scenarios.append(make_scenario(
        sid="SCN-FINAL-186",
        domain="provenance_sensitive",
        difficulty="easy",
        consult_text="Patient presents inquiring about their recent blood tests and reports feeling fatigued during afternoon walks.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports afternoon fatigue during walks."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Avoids red meat and eats mostly salads", "duration": "past 6 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Serum ferritin 12 ng/mL and hemoglobin 10.8 g/dL confirming iron deficiency anemia.", "record_type": "doctor_confirmed", "timestamp": "2026-09-20T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Tests distinct attribution: Q1 (current consultation), F1 (patient-reported diet), F2 (clinician-confirmed lab result)."
    ))

    # SCN-FINAL-187 (easy) - Patient-reported stress vs clinician-confirmed hypertension
    scenarios.append(make_scenario(
        sid="SCN-FINAL-187",
        domain="provenance_sensitive",
        difficulty="easy",
        consult_text="Patient presents complaining of occipital morning headaches and asks if blood pressure is contributing.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports occipital morning headaches."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Reports intense workplace burnout and sleeping poorly", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Stage 2 Essential Hypertension documented; in-clinic BP 158/98 mmHg.", "record_type": "doctor_confirmed", "timestamp": "2026-09-15T14:30:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Tests attribution across patient-reported stress (F1) and clinician-confirmed hypertension diagnosis (F2)."
    ))

    # SCN-FINAL-188 (medium) - Multi-channel asthma: patient trigger vs clinician spirometry
    scenarios.append(make_scenario(
        sid="SCN-FINAL-188",
        domain="provenance_sensitive",
        difficulty="medium",
        consult_text="Patient presents with nighttime wheezing and asks for prescription refill for rescue inhaler.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports nocturnal wheezing and requests rescue inhaler refill."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Adopted a long-haired rescue cat that sleeps in patient's bedroom", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Post-bronchodilator spirometry demonstrated 18% improvement in FEV1 confirming reversible airway obstruction.", "record_type": "doctor_confirmed", "timestamp": "2026-04-10T11:00:00Z"},
            {"fact_id": "F3", "note": "Skin prick testing positive (4+) for Fel d 1 cat dander allergy.", "record_type": "doctor_confirmed", "timestamp": "2024-06-12T09:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Tests attribution: Q1 (consult), F1 (patient-reported pet exposure), F2 (clinician spirometry), F3 (clinician allergy testing)."
    ))

    # SCN-FINAL-189 (medium) - Patient symptom report vs clinician endoscopy findings
    scenarios.append(make_scenario(
        sid="SCN-FINAL-189",
        domain="provenance_sensitive",
        difficulty="medium",
        consult_text="Patient presents complaining of retrosternal burning pain after coffee and difficulty swallowing large pills.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports postprandial retrosternal burning and pill dysphagia."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes 4 cups of acidic dark roast coffee and hot tomato dishes daily", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Upper endoscopy (EGD) revealed Los Angeles Grade C reflux esophagitis with distal esophageal peptic stricture.", "record_type": "doctor_confirmed", "timestamp": "2026-05-18T13:30:00Z"},
            {"fact_id": "F3", "note": "Histopathology biopsies negative for Barrett's esophagus or dysplasia.", "record_type": "doctor_confirmed", "timestamp": "2026-05-20T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Differentiates patient self-reported dietary habits (F1) from formal clinician endoscopic (F2) and histopathologic (F3) findings."
    ))

    # SCN-FINAL-190 (medium) - Patient sleep diary vs clinician polysomnography
    scenarios.append(make_scenario(
        sid="SCN-FINAL-190",
        domain="provenance_sensitive",
        difficulty="medium",
        consult_text="Patient presents complaining of waking up choking, gasping for air, and having morning headaches.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports nocturnal choking/gasping awakenings and morning headaches."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Sleep diary logs 6 nocturnal awakenings per night and snoring loud enough to disturb partner", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Diagnostic in-lab Polysomnography (PSG) showed Apnea-Hypopnea Index (AHI) of 38 events/hour (severe OSA) with oxygen nadir 79%.", "record_type": "doctor_confirmed", "timestamp": "2026-08-10T08:00:00Z"},
            {"fact_id": "F3", "note": "Prescribed CPAP at 10 cmH2O with heated humidifier.", "record_type": "doctor_confirmed", "timestamp": "2026-08-12T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Differentiates subjective sleep diary (F1) from objective PSG telemetry (F2) and clinician order (F3)."
    ))

    # SCN-FINAL-191 (medium) - Patient migraine diary vs clinician neurological workup
    scenarios.append(make_scenario(
        sid="SCN-FINAL-191",
        domain="provenance_sensitive",
        difficulty="medium",
        consult_text="Patient presents reporting severe unilateral pulsating headaches with visual aura occurring twice weekly.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports twice-weekly unilateral pulsating headaches with scintillating scotoma."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Identified red wine, aged cheese, and erratic sleep as headache triggers in app log", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Brain MRI with and without contrast revealed normal intracranial architecture with no vascular malformation or aneurysm.", "record_type": "doctor_confirmed", "timestamp": "2026-06-05T15:00:00Z"},
            {"fact_id": "F3", "note": "Formal diagnosis of Migraine with Aura; initiated sumatriptan 50mg for acute abortive therapy.", "record_type": "doctor_confirmed", "timestamp": "2026-06-08T11:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Separates patient-logged triggers (F1) from neuroimaging clearance (F2) and clinician prescription (F3)."
    ))

    # SCN-FINAL-192 (medium) - Patient joint stiffness report vs clinician radiography
    scenarios.append(make_scenario(
        sid="SCN-FINAL-192",
        domain="provenance_sensitive",
        difficulty="medium",
        consult_text="Patient reports persistent bilateral knee aching and stiffness when standing up after sitting for 30 minutes.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports bilateral knee gelling and pain after prolonged sitting."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Walks 15,000 steps daily on hard concrete warehouse floors", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Weight-bearing bilateral knee X-rays showed Kellgren-Lawrence Grade 3 medial joint space narrowing and marginal osteophytes.", "record_type": "doctor_confirmed", "timestamp": "2026-07-22T09:45:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Attribution separates patient occupational activity (F1) from clinician radiographic staging (F2)."
    ))

    # SCN-FINAL-193 (hard) - Multi-tier diabetic kidney disease: patient diet log, home glucometer, and clinician laboratory panel
    scenarios.append(make_scenario(
        sid="SCN-FINAL-193",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents for chronic disease review; reports feeling mild lower extremity heaviness and asking about dietary protein.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports lower extremity heaviness and inquires about protein intake."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes 120g protein daily with protein shakes and red meat", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Home fingerstick blood glucose diary averages 160-210 mg/dL postprandially", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "lifestyle_change", "summary": "Maintained low-carb diet 1 year ago with stable weight", "duration": "1 year ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Comprehensive Metabolic Panel: Serum creatinine 1.8 mg/dL, eGFR 42 mL/min/1.73m2 (CKD Stage 3b).", "record_type": "doctor_confirmed", "timestamp": "2026-09-22T09:00:00Z"},
            {"fact_id": "F5", "note": "Urinalysis: Urine Albumin-to-Creatinine Ratio (UACR) 450 mg/g (severely increased albuminuria).", "record_type": "doctor_confirmed", "timestamp": "2026-09-22T09:20:00Z"}
        ],
        relevant_ids=["F1", "F2", "F4", "F5"],
        irrelevant_ids=["F3"],
        conflict_groups=[],
        evaluator_notes="High-precision provenance distinction: Q1 (consult), F1/F2 (patient-reported diet/glucometer), F4/F5 (clinician-confirmed laboratory panels)."
    ))

    # SCN-FINAL-194 (hard) - Multi-tier cardiology: patient palpitations log, wearable ECG, and cardiologist Holter report
    scenarios.append(make_scenario(
        sid="SCN-FINAL-194",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents reporting sudden fluttering sensations in the chest lasting 5-10 minutes with mild shortness of breath.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports paroxysmal chest fluttering and exertional dyspnea."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Smartwatch ECG export flagged 'Possible Atrial Fibrillation' during 3 separate exercise episodes", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Drinks 3 energy drinks (600mg caffeine) prior to gym workouts", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "14-day continuous ambulatory patch monitor confirmed Paroxysmal Atrial Fibrillation with maximum ventricular rate 142 bpm.", "record_type": "doctor_confirmed", "timestamp": "2026-09-20T14:00:00Z"},
            {"fact_id": "F4", "note": "Transthoracic Echocardiogram showed left atrial volume index (LAVI) mildly enlarged at 38 mL/m2 with preserved EF 60%.", "record_type": "doctor_confirmed", "timestamp": "2026-09-21T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Attribution separates patient wearable alert (F1), patient caffeine habit (F2), cardiologist patch monitor (F3), and echocardiography report (F4)."
    ))

    # SCN-FINAL-195 (hard) - Multi-tier celiac disease: patient food log, serology, and duodenal histology
    scenarios.append(make_scenario(
        sid="SCN-FINAL-195",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents reviewing gastrointestinal workup results and reporting persistent post-meal bloating and fatigue.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports postprandial bloating, abdominal discomfort, and chronic fatigue."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Dietary diary shows continued consumption of regular wheat pasta and barley soup", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Reported iron deficiency anemia resistant to oral iron 1 year ago", "duration": "1 year ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Serology: Tissue Transglutaminase IgA (tTG-IgA) strongly elevated at >100 U/mL (normal <10).", "record_type": "doctor_confirmed", "timestamp": "2026-09-10T10:00:00Z"},
            {"fact_id": "F4", "note": "Esophagogastroduodenoscopy with duodenal bulb biopsies revealed Marsh 3c subtotal villous atrophy with intraepithelial lymphocytosis.", "record_type": "doctor_confirmed", "timestamp": "2026-09-18T13:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Differentiates patient current gluten intake (F1), historical refractory anemia (F2), clinician serology (F3), and biopsy histology (F4)."
    ))

    # SCN-FINAL-196 (hard) - Multi-tier inflammatory bowel disease: patient symptom diary, fecal calprotectin, and colonoscopy
    scenarios.append(make_scenario(
        sid="SCN-FINAL-196",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents reporting 6 bloody loose stools daily, tenesmus, and lower abdominal cramping.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports 6 bloody bowel movements daily, rectal tenesmus, and cramping."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Severe psychological stress related to family legal dispute", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Took OTC ibuprofen 600mg TID for 10 days for tension headaches", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Stool Fecal Calprotectin measured at 1,150 ug/g indicating severe mucosal inflammation.", "record_type": "doctor_confirmed", "timestamp": "2026-09-22T11:00:00Z"},
            {"fact_id": "F4", "note": "Colonoscopy demonstrated continuous mucosal erythema, loss of vascular pattern, and spontaneous bleeding from rectum to splenic flexure (Ulcerative Colitis, Mayo Endoscopic Score 2).", "record_type": "doctor_confirmed", "timestamp": "2026-09-25T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Multi-source provenance distinguishing patient reported stress/NSAID use (F1/F2) from biomarker (F3) and endoscopic visualization (F4)."
    ))

    # SCN-FINAL-197 (hard) - Multi-tier rheumatology: patient morning stiffness log, autoantibody panel, and hand MRI
    scenarios.append(make_scenario(
        sid="SCN-FINAL-197",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents complaining of symmetric swelling and pain in both hands making it impossible to turn doorknobs in the morning.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports symmetric bilateral hand swelling and severe morning functional limitation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Morning hand joint stiffness lasts over 2.5 hours every morning in patient diary", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Rheumatology serology: Anti-Cyclic Citrullinated Peptide (anti-CCP) >250 U/mL (high positive), Rheumatoid Factor (RF) 88 IU/mL.", "record_type": "doctor_confirmed", "timestamp": "2026-09-14T09:30:00Z"},
            {"fact_id": "F3", "note": "Contrast MRI bilateral wrists/hands demonstrated extensive active tenosynovitis and early cortical bone erosions at the 2nd and 3rd MCP joints.", "record_type": "doctor_confirmed", "timestamp": "2026-09-22T16:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Separates patient stiffness duration diary (F1) from clinician serological antibody titer (F2) and MRI imaging (F3)."
    ))

    # SCN-FINAL-198 (hard) - Multi-tier endocrine: patient weight/mood logs, thyroid serology, and radioactive iodine uptake scan
    scenarios.append(make_scenario(
        sid="SCN-FINAL-198",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents with hand tremors, heat intolerance, loose stools, and 6 kg unintentional weight loss over 6 weeks.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports tremors, heat intolerance, frequent loose stools, and 6 kg weight loss."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "mood", "summary": "App mood tracker records continuous anxiety, irritability, and insomnia", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Increased daily caloric intake to 3,500 kcal/day due to ravenous constant hunger", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Endocrine serology: TSH <0.01 uIU/mL, Free T4 3.8 ng/dL (elevated), Thyroid-Stimulating Immunoglobulin (TSI) 420% (positive).", "record_type": "doctor_confirmed", "timestamp": "2026-09-18T10:30:00Z"},
            {"fact_id": "F4", "note": "Radioactive Iodine Uptake (RAIU) scan showed homogeneous diffuse elevated uptake of 62% at 24 hours confirming Graves' Disease.", "record_type": "doctor_confirmed", "timestamp": "2026-09-24T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Differentiates patient psychobehavioral/nutritional logs (F1/F2) from clinician serology (F3) and RAIU nuclear scintigraphy (F4)."
    ))

    # SCN-FINAL-199 (hard) - Multi-tier neurology: patient aura log, continuous video-EEG telemetry, and 3T brain MRI
    scenarios.append(make_scenario(
        sid="SCN-FINAL-199",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents with recurring episodes of rising epigastric sensation, olfactory hallucinations of burning rubber, and 2-minute memory blank outs.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports stereotypic rising epigastric aura, olfactory hallucinations, and transient amnesia."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Symptom journal logs 4 stereotypic focal episodes weekly, occurring mostly during sleep deprivation", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "72-hour Epilepsy Monitoring Unit (EMU) video-EEG captured 3 focal electrographic seizures originating from the left anterior-mesial temporal lobe.", "record_type": "doctor_confirmed", "timestamp": "2026-09-15T12:00:00Z"},
            {"fact_id": "F3", "note": "High-resolution 3T epilepsy-protocol Brain MRI revealed left hippocampal sclerosis with volume loss and hyperintense T2/FLAIR signal.", "record_type": "doctor_confirmed", "timestamp": "2026-09-20T15:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Separates patient subjective aura diary (F1) from objective inpatient video-EEG telemetry (F2) and structural MRI neuroimaging (F3)."
    ))

    # SCN-FINAL-200 (hard) - Multi-tier oncology surveillance: patient symptom diary, serum tumor markers, and contrast CT scan
    scenarios.append(make_scenario(
        sid="SCN-FINAL-200",
        domain="provenance_sensitive",
        difficulty="hard",
        consult_text="Patient presents for 2-year post-colectomy oncological surveillance; reports feeling well with normal appetite and energy.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents for 2-year post-resection oncological surveillance reporting good energy."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Walks 5 miles daily, maintains healthy Mediterranean nutrition, and denies abdominal pain or bowel changes", "duration": "past 6 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "other_clinically_relevant_context", "summary": "Underwent laparoscopic sigmoid colectomy for Stage IIA colon adenocarcinoma 2 years ago", "duration": "2 years ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Serial Carcinoembryonic Antigen (CEA) surveillance: Baseline post-op CEA was 1.4 ng/mL; steady rise over last 6 months to 3.2, 6.8, and currently 14.5 ng/mL today.", "record_type": "doctor_confirmed", "timestamp": "2026-09-25T09:00:00Z"},
            {"fact_id": "F4", "note": "Contrast-enhanced Chest/Abdomen/Pelvis CT scan revealed new 2.2 cm solitary hypervascular lesion in hepatic segment VII suspicious for metastatic recurrence; colon anastomosis normal.", "record_type": "doctor_confirmed", "timestamp": "2026-09-28T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Comprehensive multi-tier provenance distinguishing patient reported well-being (F1), remote surgical history (F2), serial biomarker CEA trajectory (F3), and CT imaging finding (F4)."
    ))

    return scenarios
