"""
Final 200 Dataset - Sparse and No-History Control Domains (20 scenarios: SCN-FINAL-166 to SCN-FINAL-185)
Distribution:
- sparse_history (12 scenarios: SCN-FINAL-166 to 177; 4 easy, 5 medium, 3 hard)
- no_history (8 scenarios: SCN-FINAL-178 to 185; 4 easy, 4 medium, 0 hard)
Total: 8 easy, 9 medium, 3 hard
"""

from .scenario_builder import make_scenario

def get_sparse_and_no_history_scenarios():
    scenarios = []

    # =========================================================================
    # SPARSE HISTORY (12 scenarios: SCN-FINAL-166 to 177)
    # =========================================================================

    # SCN-FINAL-166 (easy, sparse_history) - Single brief hydration fact
    scenarios.append(make_scenario(
        sid="SCN-FINAL-166",
        domain="sparse_history",
        difficulty="easy",
        consult_text="Patient presents complaining of dry lips, mild lightheadedness upon standing, and infrequent urination.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports dry lips, orthostatic lightheadedness, and oliguria."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "hydration", "summary": "Drinks approximately 500 ml of fluid per day", "value": "500 ml/day", "duration": "past 1 week", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history control containing a single clear hydration fact relevant to dehydration symptoms."
    ))

    # SCN-FINAL-167 (easy, sparse_history) - Single brief stress fact
    scenarios.append(make_scenario(
        sid="SCN-FINAL-167",
        domain="sparse_history",
        difficulty="easy",
        consult_text="Patient reports tight band-like sensations around forehead occurring every afternoon.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has afternoon band-like tension headaches."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "High occupational stress preparing for annual tax audit", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history control containing a single occupational stress fact."
    ))

    # SCN-FINAL-168 (easy, sparse_history) - Single brief caffeine fact
    scenarios.append(make_scenario(
        sid="SCN-FINAL-168",
        domain="sparse_history",
        difficulty="easy",
        consult_text="Patient presents reporting hand tremors and rapid heartbeat before noon.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports hand tremors and rapid heart rate in mornings."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Drinks 4 large cups of black coffee on empty stomach before 10 AM", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history control with single high morning caffeine fact."
    ))

    # SCN-FINAL-169 (easy, sparse_history) - Single brief sleep restriction fact
    scenarios.append(make_scenario(
        sid="SCN-FINAL-169",
        domain="sparse_history",
        difficulty="easy",
        consult_text="Patient complains of heavy eyelids, poor focus, and nodding off during afternoon work meetings.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports severe afternoon somnolence and impaired concentration."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Sleep curtailed to 4 hours per night due to new work shift", "duration": "past 10 days", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history control with a single sleep curtailment fact."
    ))

    # SCN-FINAL-170 (medium, sparse_history) - Single brief clinician note on penicillin allergy
    scenarios.append(make_scenario(
        sid="SCN-FINAL-170",
        domain="sparse_history",
        difficulty="medium",
        consult_text="Patient presents with acute bacterial tonsillitis requiring antibiotic therapy. Inquires about medication options.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents with bacterial tonsillitis requiring antibiotic selection."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F1", "note": "Patient has severe IgE-mediated anaphylaxis to penicillin documented in chart.", "record_type": "doctor_confirmed", "timestamp": "2024-05-12T10:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history consisting solely of one vital clinician-documented drug allergy note."
    ))

    # SCN-FINAL-171 (medium, sparse_history) - Single brief clinician note on ACE inhibitor cough
    scenarios.append(make_scenario(
        sid="SCN-FINAL-171",
        domain="sparse_history",
        difficulty="medium",
        consult_text="Patient presents complaining of a dry, hacking, non-productive cough persistent for 3 weeks.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports a persistent non-productive dry cough for 3 weeks."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F1", "note": "Initiated lisinopril 10mg daily for essential hypertension 4 weeks ago.", "record_type": "doctor_confirmed", "timestamp": "2026-08-30T14:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history with single clinician note on ACE inhibitor initiation explaining dry cough."
    ))

    # SCN-FINAL-172 (medium, sparse_history) - Single patient fact on sudden unramped fiber
    scenarios.append(make_scenario(
        sid="SCN-FINAL-172",
        domain="sparse_history",
        difficulty="medium",
        consult_text="Patient reports sudden onset of abdominal distension, excessive flatulence, and lower belly discomfort.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has acute abdominal bloating, cramping, and gas."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Began taking 3 daily tablespoons of raw inulin fiber supplement without ramping", "duration": "past 3 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history with a single unramped prebiotic fiber fact explaining acute bloating."
    ))

    # SCN-FINAL-173 (medium, sparse_history) - Single clinician note on chronic kidney disease
    scenarios.append(make_scenario(
        sid="SCN-FINAL-173",
        domain="sparse_history",
        difficulty="medium",
        consult_text="Patient presents for severe knee sprain and asks if high-dose over-the-counter naproxen is safe to take.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient inquires about using OTC naproxen for acute knee pain."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F1", "note": "Stage 3b Chronic Kidney Disease (eGFR 35 mL/min); NSAIDs strictly contraindicated.", "record_type": "doctor_confirmed", "timestamp": "2026-05-18T11:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history with single vital clinician note contraindicating NSAID therapy."
    ))

    # SCN-FINAL-174 (medium, sparse_history) - Single patient fact on midnight binge eating
    scenarios.append(make_scenario(
        sid="SCN-FINAL-174",
        domain="sparse_history",
        difficulty="medium",
        consult_text="Patient reports severe post-dinner heartburn and sour fluid regurgitation while sleeping.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences severe nocturnal heartburn and sour regurgitation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Eats heavy fried snacks in bed at 11:30 PM immediately before sleeping", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history with single late-night meal habit fact explaining nocturnal GERD."
    ))

    # SCN-FINAL-175 (hard, sparse_history) - Single clinician note on mechanical heart valve and anticoagulation
    scenarios.append(make_scenario(
        sid="SCN-FINAL-175",
        domain="sparse_history",
        difficulty="hard",
        consult_text="Patient presents with acute right shoulder rotator cuff tendinitis and asks if they can start high-dose oral herbal turmeric and fish oil.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient inquires about starting high-dose turmeric and omega-3 fish oil supplements."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F1", "note": "Mechanical St. Jude aortic valve prosthesis on Warfarin; target INR 2.5-3.5. Warned regarding antiplatelet/anticoagulant supplement interactions.", "record_type": "doctor_confirmed", "timestamp": "2026-02-14T09:30:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history with critical clinician note on mechanical valve and warfarin anticoagulation sensitivity."
    ))

    # SCN-FINAL-176 (hard, sparse_history) - Single clinician note on gastric bypass and NSAID ulcer risk
    scenarios.append(make_scenario(
        sid="SCN-FINAL-176",
        domain="sparse_history",
        difficulty="hard",
        consult_text="Patient presents complaining of acute lower back spasm and asks if they can take prescription oral ketorolac.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient inquires about taking oral ketorolac for acute back spasm."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F1", "note": "History of Roux-en-Y gastric bypass; lifelong avoidance of all systemic NSAIDs required due to high risk of marginal anastomotic ulceration and perforation.", "record_type": "doctor_confirmed", "timestamp": "2025-10-10T14:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse history with critical surgical note warning against NSAID-induced anastomotic marginal ulceration."
    ))

    # SCN-FINAL-177 (hard, sparse_history) - Single patient fact on high lithium dietary sodium restriction
    scenarios.append(make_scenario(
        sid="SCN-FINAL-177",
        domain="sparse_history",
        difficulty="hard",
        consult_text="Patient presents complaining of worsening hand tremors, coarse ataxia, nausea, and slurred speech over past 3 days.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports acute coarse tremors, ataxia, nausea, and dysarthria."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Started extreme zero-sodium diet and rigorous sweating sauna regimen 4 days ago", "duration": "past 4 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Maintained on Lithium carbonate 900mg daily for Bipolar I; counseled on strict maintenance of dietary sodium and hydration to avoid lithium toxicity.", "record_type": "doctor_confirmed", "timestamp": "2026-04-15T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sparse multi-channel context where acute sodium restriction and dehydration in lithium patient precipitates neurotoxicity."
    ))

    # =========================================================================
    # NO HISTORY CONTROLS (8 scenarios: SCN-FINAL-178 to 185)
    # Completely empty historical context to test baseline and PCIF handling
    # of consultation-only input.
    # =========================================================================

    # SCN-FINAL-178 (easy, no_history) - Acute ankle sprain
    scenarios.append(make_scenario(
        sid="SCN-FINAL-178",
        domain="no_history",
        difficulty="easy",
        consult_text="Patient twisted right ankle while stepping off sidewalk curb 2 hours ago. Reports lateral malleolar swelling, bruising, and inability to bear weight.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient twisted right ankle 2 hours ago."},
            {"fact_id": "Q2", "text": "Patient has lateral malleolar swelling, ecchymosis, and inability to bear weight."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating self-contained acute mechanical ankle inversion trauma."
    ))

    # SCN-FINAL-179 (easy, no_history) - Acute sore throat and fever
    scenarios.append(make_scenario(
        sid="SCN-FINAL-179",
        domain="no_history",
        difficulty="easy",
        consult_text="Patient presents with 2 days of severe painful swallowing, fever to 38.5 C, tender anterior cervical lymph nodes, and absence of cough.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports 2 days of odynophagia and fever to 38.5 C."},
            {"fact_id": "Q2", "text": "Patient has tender anterior cervical adenopathy and no cough."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating acute infectious pharyngitis presentation."
    ))

    # SCN-FINAL-180 (easy, no_history) - Acute seasonal eye itching
    scenarios.append(make_scenario(
        sid="SCN-FINAL-180",
        domain="no_history",
        difficulty="easy",
        consult_text="Patient presents with bilateral watery eyes, severe conjunctival itching, and sneezing after mowing the lawn this morning.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has bilateral itchy, watery eyes and sneezing after mowing lawn."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating acute allergic conjunctivitis from lawn mowing."
    ))

    # SCN-FINAL-181 (easy, no_history) - Acute superficial burn
    scenarios.append(make_scenario(
        sid="SCN-FINAL-181",
        domain="no_history",
        difficulty="easy",
        consult_text="Patient accidentally touched hot frying pan handle 30 minutes ago. Presents with 2cm erythematous, painful, non-blistering burn on right palm.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient sustained 2cm painful erythematous non-blistering burn to right palm 30 minutes ago."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating acute first-degree contact thermal burn."
    ))

    # SCN-FINAL-182 (medium, no_history) - Acute viral gastroenteritis
    scenarios.append(make_scenario(
        sid="SCN-FINAL-182",
        domain="no_history",
        difficulty="medium",
        consult_text="Patient reports sudden onset of watery non-bloody diarrhea, nausea, low-grade fever, and diffuse abdominal cramping starting 12 hours ago after attending a catered banquet.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient developed acute watery diarrhea, nausea, fever, and cramping 12 hours post-banquet."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating acute foodborne/viral gastroenteritis outbreak context."
    ))

    # SCN-FINAL-183 (medium, no_history) - Acute uncomplicated cystitis
    scenarios.append(make_scenario(
        sid="SCN-FINAL-183",
        domain="no_history",
        difficulty="medium",
        consult_text="Patient presents with 24 hours of burning on urination (dysuria), urinary frequency every 30 minutes, and suprapubic pressure with no fevers or flank pain.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports 24 hours of acute dysuria, frequency, and suprapubic ache with no fevers or flank tenderness."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating acute uncomplicated lower urinary tract symptoms."
    ))

    # SCN-FINAL-184 (medium, no_history) - Acute contact dermatitis from poison ivy
    scenarios.append(make_scenario(
        sid="SCN-FINAL-184",
        domain="no_history",
        difficulty="medium",
        consult_text="Patient presents with intensely itchy linear streaks of vesicles and redness on bilateral forearms 2 days after clearing brush in woods.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has pruritic linear vesicular rash on forearms 2 days post-woodland brush clearing."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating classic linear phytodermatitis (urushiol-induced contact dermatitis)."
    ))

    # SCN-FINAL-185 (medium, no_history) - Acute external ear canal otitis (swimmer's ear)
    scenarios.append(make_scenario(
        sid="SCN-FINAL-185",
        domain="no_history",
        difficulty="medium",
        consult_text="Patient reports severe right ear canal pain, itching, and tenderness on tugging the pinna/tragus following daily swimming in a lake 3 days ago.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has acute right otalgia, tragal tenderness, and canal pruritus after lake swimming."}
        ],
        patient_current=[],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=[],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="No-history control evaluating acute otitis externa with classic tragal sign."
    ))

    return scenarios
