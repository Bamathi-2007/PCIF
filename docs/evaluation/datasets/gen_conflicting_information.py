"""
Final 200 Dataset - Conflicting Information Domain (25 scenarios: SCN-FINAL-121 to SCN-FINAL-145)
Distribution: 5 easy, 14 medium, 6 hard
All conflict groups adhere strictly to temporal alignment (same time period or direct contradiction)
and require expected_behavior="surface_for_verification".
"""

from .scenario_builder import make_scenario

def get_conflicting_information_scenarios():
    scenarios = []

    # SCN-FINAL-121 (easy) - Contradictory current caffeine intake report
    scenarios.append(make_scenario(
        sid="SCN-FINAL-121",
        domain="conflicting_information",
        difficulty="easy",
        consult_text="Patient states today: 'I never drink any caffeine or coffee at all, just herbal chamomile tea.' Inquires about daytime jitteriness.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient states they never consume caffeine or coffee."},
            {"fact_id": "Q2", "text": "Patient reports daytime jitteriness."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Current self-log lists drinking 3 large cold brew coffees every morning", "duration": "current", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Direct contradiction between consultation claim of zero caffeine and concurrent daily log of 3 cold brew coffees.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct contemporaneous contradiction between verbal consultation claim (zero caffeine) and patient app log (3 cold brews)."
    ))

    # SCN-FINAL-122 (easy) - Contradictory smoking status report
    scenarios.append(make_scenario(
        sid="SCN-FINAL-122",
        domain="conflicting_information",
        difficulty="easy",
        consult_text="Patient states in clinic: 'I have never smoked a cigarette in my life.' Complains of chronic morning cough.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient states they have never smoked cigarettes."},
            {"fact_id": "Q2", "text": "Patient reports chronic morning cough."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Active smoking habit of 1 pack per day for the past 5 years logged in intake form", "duration": "current", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between verbal claim of never smoking and intake log of 1 pack/day.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Contemporaneous contradiction regarding tobacco exposure relevant to chronic cough."
    ))

    # SCN-FINAL-123 (easy) - Contradictory medication adherence
    scenarios.append(make_scenario(
        sid="SCN-FINAL-123",
        domain="conflicting_information",
        difficulty="easy",
        consult_text="Patient tells doctor: 'I take my blood pressure pill every single morning without missing a single dose.'",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims 100% perfect adherence to daily blood pressure medication."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Patient context log records taking blood pressure medication only 2 or 3 days per week due to forgetting", "duration": "current", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Direct conflict between verbal claim of 100% adherence and recorded context showing frequent missed doses.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct conflict between stated perfect adherence and documented weekly missed doses."
    ))

    # SCN-FINAL-124 (easy) - Contradictory current alcohol consumption
    scenarios.append(make_scenario(
        sid="SCN-FINAL-124",
        domain="conflicting_information",
        difficulty="easy",
        consult_text="Patient states: 'I am completely sober and do not drink any alcohol.' Reports sleep disturbances.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient states they are completely sober with zero alcohol consumption."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Current food log lists 4 cans of beer nightly before bed", "duration": "current", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Direct contemporaneous conflict between verbal claim of total sobriety and current food diary showing 4 nightly beers.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Contemporaneous contradiction between patient's verbal statement and app food diary."
    ))

    # SCN-FINAL-125 (easy) - Contradictory physical activity level
    scenarios.append(make_scenario(
        sid="SCN-FINAL-125",
        domain="conflicting_information",
        difficulty="easy",
        consult_text="Patient states: 'I walk 10 miles every single day outdoors.' Inquires about persistent sedentary fatigue.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims to walk 10 miles daily outdoors."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Current wearable step tracker shows average of 1,200 steps (under 0.6 miles) daily", "duration": "current", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between claimed 10 miles/day and verified wearable tracker recording 1,200 steps/day.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct discrepancy between verbal exercise claim and synchronized objective tracker."
    ))

    # SCN-FINAL-126 (medium) - Discrepant daily sleep duration report
    scenarios.append(make_scenario(
        sid="SCN-FINAL-126",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient reports during visit: 'I get a solid 8 to 9 hours of uninterrupted restful sleep every night.' Mentions afternoon drowsiness.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient states getting 8-9 hours of uninterrupted restful sleep nightly."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Current sleep diary logs average sleep duration of 4 hours 15 minutes with frequent nocturnal awakenings", "duration": "current", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Patient attended clinic last week reporting severe insomnia and waking every hour.", "record_type": "doctor_confirmed", "timestamp": "2026-09-22T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Contemporaneous conflict between consultation statement of 8-9 hours sound sleep versus sleep diary (4h15m) and recent clinician note of insomnia.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Multi-source conflict between consultation claim, concurrent sleep log, and recent clinician note."
    ))

    # SCN-FINAL-127 (medium) - Discrepant dairy consumption in lactose intolerance
    scenarios.append(make_scenario(
        sid="SCN-FINAL-127",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient states: 'I strictly avoid all milk, cheese, and dairy products.' Reports sharp bloating after meals.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims strict avoidance of all dairy products."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Current meal photos and logs show daily whole milk cappuccino, Greek yogurt, and pizza", "duration": "current", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Diagnosed lactose intolerance; advised strict dairy elimination trial.", "record_type": "doctor_confirmed", "timestamp": "2026-08-14T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous contradiction between patient assertion of total dairy avoidance and concurrent meal logs showing heavy dairy.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Contemporaneous conflict between declared restriction and actual logged food intake."
    ))

    # SCN-FINAL-128 (medium) - Discrepant gluten intake in celiac patient
    scenarios.append(make_scenario(
        sid="SCN-FINAL-128",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient insists: 'I follow a 100% strict certified gluten-free diet without exception.' Reports persistent diarrhea.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient asserts 100% strict compliance with gluten-free diet."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Active grocery receipts show regular wheat flour bread, conventional soy sauce, and barley beer purchased weekly", "duration": "current", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Biopsy-proven Celiac Disease; patient previously instructed on hidden gluten in barley and regular soy sauce.", "record_type": "doctor_confirmed", "timestamp": "2026-05-10T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous contradiction between assertion of strict gluten-free diet and active grocery log containing wheat/barley items.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Contemporaneous conflict between claimed dietary adherence and contemporaneous grocery item logs."
    ))

    # SCN-FINAL-129 (medium) - Discrepant supplement use report
    scenarios.append(make_scenario(
        sid="SCN-FINAL-129",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient states: 'I do not take any over-the-counter vitamins, herbs, or dietary supplements.'",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient states they take no OTC vitamins or herbal supplements."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Current supplement list lists taking high-dose St. John's Wort, 5000 IU Vitamin D, and mega-dose biotin daily", "duration": "current", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Patient counseled on CYP enzyme interactions with St. John's Wort.", "record_type": "doctor_confirmed", "timestamp": "2026-07-20T09:30:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous contradiction between patient stating no supplement use and active intake listing 3 daily supplements.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct conflict between stated lack of supplement use and documented active multi-supplement regimen."
    ))

    # SCN-FINAL-130 (medium) - Contradictory pain location and timeline
    scenarios.append(make_scenario(
        sid="SCN-FINAL-130",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient tells clinician today: 'My right shoulder has never hurt before; this pain started suddenly yesterday.'",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient states right shoulder pain started suddenly yesterday with no prior history."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "App symptom journal records constant severe right shoulder pain score 8/10 for the past 6 weeks", "duration": "past 6 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Evaluated patient 3 weeks ago for chronic right subacromial bursitis; prescribed physical therapy.", "record_type": "doctor_confirmed", "timestamp": "2026-09-08T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Contemporaneous conflict between consultation statement (pain started yesterday) and documented 6-week symptom diary plus clinic visit 3 weeks ago.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct chronological conflict between verbal onset assertion and multi-source historical documentation."
    ))

    # SCN-FINAL-131 (medium) - Discrepant carbohydrate restriction claim
    scenarios.append(make_scenario(
        sid="SCN-FINAL-131",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient reports: 'I have been on a strict zero-carb ketogenic diet under 20g carbs for the entire month.' Inquires about failure to lose weight.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims strict <20g carbohydrate ketogenic adherence for the past month."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Nutritional food log records daily consumption of 250g carbohydrates (rice, bread, desserts)", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous contradiction between claimed ketogenic intake (<20g) and concurrent app log of 250g carbs/day.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct conflict between stated dietary protocol and logged macronutrient values."
    ))

    # SCN-FINAL-132 (medium) - Discrepant fluid intake in recurrent nephrolithiasis
    scenarios.append(make_scenario(
        sid="SCN-FINAL-132",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient asserts: 'I drink 4 full liters of water every single day without fail.' Inquires about dark concentrated urine.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient asserts drinking 4 liters of water daily."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "hydration", "summary": "Hydration app records average fluid intake of 650 ml per day", "duration": "current", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Urine specific gravity 1.030 today indicating marked dehydration; instructed patient on fluid targets.", "record_type": "doctor_confirmed", "timestamp": "2026-09-28T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between patient's verbal report of 4 L/day and hydration app logging only 650 ml/day.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct conflict between verbal fluid volume claim and contemporaneous app tracking."
    ))

    # SCN-FINAL-133 (medium) - Discrepant work stress level report
    scenarios.append(make_scenario(
        sid="SCN-FINAL-133",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient states: 'My life is completely stress-free; work is wonderful and relaxing.' Presents with tension headaches.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims to be completely stress-free with relaxing work environment."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Mood tracker registers peak severe stress scores (10/10) daily with notes describing toxic boss and impending layoff", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous contradiction between consultation denial of stress and app mood log recording maximum stress ratings.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Contemporaneous contradiction between verbal minimization and contemporaneous app stress scoring."
    ))

    # SCN-FINAL-134 (medium) - Contradictory allergy history report
    scenarios.append(make_scenario(
        sid="SCN-FINAL-134",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient tells doctor: 'I have never had any allergic reactions to penicillin or any antibiotics.'",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient denies any history of penicillin or antibiotic allergies."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Intake portal lists 'Severe Penicillin Allergy - Anaphylaxis with hives and bronchospasm'", "duration": "current", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Verified allergy alert in EHR: Penicillin caused anaphylaxis requiring IM epinephrine in 2021.", "record_type": "doctor_confirmed", "timestamp": "2026-01-10T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Direct conflict between verbal denial of drug allergy and active portal allergy list plus clinician EHR allergy warning.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="High-stakes conflict between verbal denial of allergy and verified EHR/portal allergy documentation."
    ))

    # SCN-FINAL-135 (medium) - Discrepant energy drink consumption
    scenarios.append(make_scenario(
        sid="SCN-FINAL-135",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient insists: 'I don't drink energy drinks or stimulants.' Presents with tachycardia.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient denies consuming any energy drinks or stimulants."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Daily nutritional log shows 4 cans of high-caffeine energy drinks consumed daily", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between verbal denial of energy drink use and concurrent nutrition log showing 4 cans daily.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct contemporaneous contradiction regarding stimulant consumption."
    ))

    # SCN-FINAL-136 (medium) - Discrepant CPAP adherence in obstructive sleep apnea
    scenarios.append(make_scenario(
        sid="SCN-FINAL-136",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient tells sleep specialist: 'I wear my CPAP mask for 8 full hours every single night.' Complains of persistent severe daytime sleepiness.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims 8 hours of nightly CPAP device usage."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "CPAP tele-monitoring report for past 30 days reveals average machine run-time of 42 minutes per night with 18 days of zero use", "duration": "past 30 days", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Diagnosed severe OSA (AHI 44/hr); prescribed AutoCPAP 8-14 cmH2O.", "record_type": "doctor_confirmed", "timestamp": "2026-06-15T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between verbal claim of 8h/night CPAP use and objective 30-day tele-monitoring showing 42 mins/night.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Objective device tele-monitoring data directly conflicting with patient's verbal self-report."
    ))

    # SCN-FINAL-137 (medium) - Discrepant salt intake in congestive heart failure
    scenarios.append(make_scenario(
        sid="SCN-FINAL-137",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient states: 'I follow a strict no-salt diet and never eat restaurant food.' Presents with 3 kg weight gain and edema.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims strict zero-salt home-cooked diet."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Credit card receipts and food diary show dining out at Chinese buffet and pizza parlors 5 nights this week", "duration": "past 1 week", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "HFrEF on carvedilol and sacubitril/valsartan; counseled on strict sodium restriction <1,500mg/day.", "record_type": "doctor_confirmed", "timestamp": "2026-04-10T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between patient verbal claim of no-salt diet and concurrent food diary showing frequent high-sodium dining.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct conflict between stated sodium abstinence and active high-sodium food logs in heart failure."
    ))

    # SCN-FINAL-138 (medium) - Discrepant fasting duration in intermittent fasting protocol
    scenarios.append(make_scenario(
        sid="SCN-FINAL-138",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient asserts: 'I complete a strict 20-hour water fast every day from 8 PM to 4 PM.' Inquires about persistent sluggishness.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims strict daily 20-hour water fasting routine."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "App fasting timer is broken repeatedly by logged mid-morning snacks of protein bars and sweet lattes", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between claimed 20-hour fast and concurrent food logs containing caloric snacks during fasting window.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct contradiction between declared fasting schedule and logged caloric consumption."
    ))

    # SCN-FINAL-139 (medium) - Discrepant antidepressant dosing schedule
    scenarios.append(make_scenario(
        sid="SCN-FINAL-139",
        domain="conflicting_information",
        difficulty="medium",
        consult_text="Patient states: 'I take my full 20mg Lexapro tablet every night at 9 PM.' Complains of sudden electric brain zaps.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims regular 20mg escitalopram intake nightly at 9 PM."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Medication tracker shows patient has missed the last 5 days of escitalopram doses", "duration": "past 5 days", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Patient warned that missing >48 hours of escitalopram can precipitate serotonin withdrawal symptoms.", "record_type": "doctor_confirmed", "timestamp": "2026-03-01T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between verbal claim of daily nightly dose and medication tracker logging 5 consecutive missed doses.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct conflict between stated nightly compliance and logged medication hiatus."
    ))

    # SCN-FINAL-140 (hard) - Multi-source conflict: Statin adherence, myalgia, and pharmacy refill gap
    scenarios.append(make_scenario(
        sid="SCN-FINAL-140",
        domain="conflicting_information",
        difficulty="hard",
        consult_text="Patient tells cardiologist: 'I take my rosuvastatin 40mg every single day without fail, but my cholesterol remains high.'",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient asserts 100% daily compliance with high-intensity rosuvastatin 40mg."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Patient self-discontinued rosuvastatin 6 weeks ago due to mild bilateral calf aching, recorded in private symptom diary", "duration": "past 6 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "EHR pharmacy claims check confirms zero statin prescription refills claimed over the past 4 months (Proportion of Days Covered = 0%).", "record_type": "doctor_confirmed", "timestamp": "2026-09-24T14:00:00Z"},
            {"fact_id": "F3", "note": "Post-PCI for STEMI 1 year ago; high-intensity statin therapy critical for secondary prevention.", "record_type": "doctor_confirmed", "timestamp": "2025-09-12T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Multi-source contemporaneous conflict between patient's verbal claim of daily statin use versus private symptom diary (self-discontinued 6 weeks ago) and objective pharmacy refill record (0% PDC over 4 months).",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Multi-source triangulation conflict comparing verbal claim, private symptom diary, and claims data."
    ))

    # SCN-FINAL-141 (hard) - Multi-source conflict: Blood glucose self-monitoring logs vs continuous CGM data
    scenarios.append(make_scenario(
        sid="SCN-FINAL-141",
        domain="conflicting_information",
        difficulty="hard",
        consult_text="Patient presents a handwritten paper logbook showing perfect fasting blood glucose readings between 90 and 110 mg/dL.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents paper logbook showing uniform fasting glucose of 90-110 mg/dL."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "CGM sensor cloud upload for the identical two-week period reveals mean glucose of 245 mg/dL with nocturnal spikes to 320 mg/dL", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Laboratory HbA1c drawn today is 10.4%, strongly contradicting the handwritten paper log.", "record_type": "doctor_confirmed", "timestamp": "2026-09-26T09:15:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Direct conflict between patient's fabricated paper logbook (90-110 mg/dL) and concurrent objective CGM upload (mean 245 mg/dL) and laboratory HbA1c 10.4%.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Direct conflict between handwritten logbook and concurrent continuous glucose telemetry and lab biomarker."
    ))

    # SCN-FINAL-142 (hard) - Multi-source conflict: Warfarin compliance, OTC herbal use, and INR volatility
    scenarios.append(make_scenario(
        sid="SCN-FINAL-142",
        domain="conflicting_information",
        difficulty="hard",
        consult_text="Patient states: 'I take my exact prescribed warfarin 5mg dose every night and take no other herbs or supplements.'",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient denies taking any other herbs, vitamins, or altering warfarin dose."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Started taking high-dose Ginkgo Biloba and St. John's Wort supplements purchased online 10 days ago", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Anticoagulation clinic visit today: INR plummeted to 1.2 (target 2.0-3.0) despite reported compliance.", "record_type": "doctor_confirmed", "timestamp": "2026-09-28T10:00:00Z"},
            {"fact_id": "F3", "note": "Warned previously that CYP3A4-inducing herbal supplements like St. John's Wort significantly accelerate warfarin metabolism.", "record_type": "doctor_confirmed", "timestamp": "2026-02-14T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1"],
                "description": "Contemporaneous conflict between verbal denial of supplement intake and contemporaneous record of high-dose St. John's Wort and Ginkgo Biloba use.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="High-risk conflict between verbal denial of supplement intake and documented concurrent herbal ingestion."
    ))

    # SCN-FINAL-143 (hard) - Multi-source conflict: Sodium intake, home blood pressure, and clinic readings
    scenarios.append(make_scenario(
        sid="SCN-FINAL-143",
        domain="conflicting_information",
        difficulty="hard",
        consult_text="Patient states: 'My home blood pressure is always perfect at 115/75, and I never consume added salt.'",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims consistent home BP of 115/75 mmHg and zero added salt."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Active dietary diary shows daily consumption of ramen noodles with bouillon packets containing 3,800mg sodium", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Automated Bluetooth blood pressure cuff transmission shows average home BP of 168/102 mmHg over the past 14 days.", "record_type": "doctor_confirmed", "timestamp": "2026-09-27T14:00:00Z"},
            {"fact_id": "F3", "note": "In-clinic BP today measured at 172/104 mmHg; bilateral pedal edema noted.", "record_type": "doctor_confirmed", "timestamp": "2026-09-27T14:20:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Contemporaneous conflict between patient verbal claim of 115/75 BP and zero salt versus actual dietary log (3800mg sodium) and automated Bluetooth cuff transmission (168/102 mmHg).",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Multi-channel conflict between verbal minimization, actual food logs, and automated telemetric BP uploads."
    ))

    # SCN-FINAL-144 (hard) - Multi-source conflict: Alcohol consumption in alcoholic liver disease
    scenarios.append(make_scenario(
        sid="SCN-FINAL-144",
        domain="conflicting_information",
        difficulty="hard",
        consult_text="Patient states: 'I have not had a single drop of alcohol in over 6 months.' Inquires about rising jaundice.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient claims complete alcohol abstinence for past 6 months."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Patient context log records purchasing 750ml vodka daily and drinking heavily in secret", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Laboratory surveillance today: Urine Ethyl Glucuronide (EtG) positive (>5,000 ng/mL); AST 280 U/L, ALT 110 U/L (AST:ALT ratio >2).", "record_type": "doctor_confirmed", "timestamp": "2026-09-28T16:00:00Z"},
            {"fact_id": "F3", "note": "Alcohol-related cirrhosis Child-Pugh Class B; absolute abstinence required for liver transplant listing.", "record_type": "doctor_confirmed", "timestamp": "2026-04-12T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Direct conflict between patient's verbal claim of 6 months abstinence versus private context log of daily vodka and positive urine EtG biomarker.",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="Triangulated conflict between verbal abstinence assertion, private intake log, and objective laboratory toxicology."
    ))

    # SCN-FINAL-145 (hard) - Multi-source conflict: Pediatric asthma controller adherence vs pharmacy data
    scenarios.append(make_scenario(
        sid="SCN-FINAL-145",
        domain="conflicting_information",
        difficulty="hard",
        consult_text="Parent states: 'We give the child their fluticasone inhaler twice daily every single day without ever missing.' Presents for frequent asthma exacerbations.",
        q_facts=[
            {"fact_id": "Q1", "text": "Parent claims perfect twice-daily adherence to inhaled corticosteroid controller."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Parent's home medication tracker shows the fluticasone canister was only used 3 times over the past 60 days", "duration": "past 60 days", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Pharmacy claims data indicates last fluticasone refill was picked up 7 months ago (6 months overdue).", "record_type": "doctor_confirmed", "timestamp": "2026-09-29T11:00:00Z"},
            {"fact_id": "F3", "note": "Child had 2 ED visits for severe bronchospasm in past 3 months; albuterol rescue canister dose counter indicates >12 puffs/day.", "record_type": "doctor_confirmed", "timestamp": "2026-09-29T11:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[
            {
                "conflict_id": "C1",
                "fact_ids": ["Q1", "F1", "F2"],
                "description": "Direct contemporaneous conflict between parent's verbal report of daily ICS use versus home tracker (3 uses in 60 days) and pharmacy claims (refill 7 months overdue).",
                "expected_behavior": "surface_for_verification"
            }
        ],
        evaluator_notes="High-impact multi-source pediatric adherence conflict between parent report, home tracker, and pharmacy records."
    ))

    return scenarios
