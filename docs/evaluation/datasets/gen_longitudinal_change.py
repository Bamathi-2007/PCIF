"""
Final 200 Dataset - Longitudinal Change Domain (30 scenarios: SCN-FINAL-091 to SCN-FINAL-120)
Distribution: 7 easy, 16 medium, 7 hard
"""

from .scenario_builder import make_scenario

def get_longitudinal_change_scenarios():
    scenarios = []

    # SCN-FINAL-091 (easy) - Stepped reduction in daily coffee intake
    scenarios.append(make_scenario(
        sid="SCN-FINAL-091",
        domain="longitudinal_change",
        difficulty="easy",
        consult_text="Patient presents reporting mild afternoon drowsiness but acknowledges complete resolution of morning heart palpitations.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has mild afternoon drowsiness but palpitations have fully resolved."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Reduced coffee intake to 1 single cup daily after breakfast", "value": "1 cup/day", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "habit", "summary": "Previously drank 6 cups of espresso daily causing frequent tremors and palpitations", "duration": "3 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal step-down in caffeine volume tracking symptom resolution (palpitations resolved) with minor expected tiredness."
    ))

    # SCN-FINAL-092 (easy) - Gradual increase in walking steps
    scenarios.append(make_scenario(
        sid="SCN-FINAL-092",
        domain="longitudinal_change",
        difficulty="easy",
        consult_text="Patient reports improved mood and deeper sleep after gradually increasing physical activity over the past two months.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports improved mood and better sleep quality with increased walking."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Averages 9,000 steps daily through structured morning and evening walks", "value": "9000 steps/day", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "activity", "summary": "Sedentary baseline of under 2,000 steps per day following ankle sprain", "duration": "2 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Positive longitudinal progression from sedentary post-injury baseline to 9k daily steps."
    ))

    # SCN-FINAL-093 (easy) - Sleep duration improvement after bedroom screen ban
    scenarios.append(make_scenario(
        sid="SCN-FINAL-093",
        domain="longitudinal_change",
        difficulty="easy",
        consult_text="Patient presents noting easier sleep onset and feeling well-rested after changing nighttime phone habits.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports faster sleep onset and feeling refreshed in the morning."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Sleeps 7.5 continuous hours per night with phone kept in another room", "value": "7.5 hours", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "sleep", "summary": "Previously suffered from 2-hour sleep latency while using phone in bed", "duration": "3 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal habit change (device removal) resulting in documented sleep latency reduction."
    ))

    # SCN-FINAL-094 (easy) - Sugar-sweetened beverage elimination and weight trajectory
    scenarios.append(make_scenario(
        sid="SCN-FINAL-094",
        domain="longitudinal_change",
        difficulty="easy",
        consult_text="Patient reports feeling lighter, noticing less abdominal bloating, and having steady afternoon energy.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports reduced abdominal bloating and steady afternoon energy."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Replaced all soda with sparkling water and herbal teas, consuming 0g added liquid sugar", "duration": "past 6 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "nutrition", "summary": "Previously drank 3 cans of regular cola daily with frequent energy crashes", "duration": "3 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal dietary substitution eliminating liquid sugar resulting in improved metabolic stability."
    ))

    # SCN-FINAL-095 (easy) - Tapering alcohol consumption
    scenarios.append(make_scenario(
        sid="SCN-FINAL-095",
        domain="longitudinal_change",
        difficulty="easy",
        consult_text="Patient notes clearer thinking and no more morning acid reflux after reducing evening alcohol.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports clearer morning cognition and complete resolution of nocturnal acid reflux."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Consumes maximum 1 glass of wine on weekend nights only", "value": "1 drink/week", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "habit", "summary": "Previously drank 3-4 beers every weeknight to fall asleep", "duration": "4 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal reduction in alcohol volume leading to resolution of gastroesophageal reflux."
    ))

    # SCN-FINAL-096 (easy) - Increased hydration and resolution of constipation
    scenarios.append(make_scenario(
        sid="SCN-FINAL-096",
        domain="longitudinal_change",
        difficulty="easy",
        consult_text="Patient presents pleased that daily bowel movements have become soft and regular without straining.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports regular, soft daily bowel movements without straining."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "hydration", "summary": "Drinks 2.5 liters of water daily carrying a refillable insulated bottle", "value": "2.5 L/day", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "hydration", "summary": "Chronic dehydration with intake under 700ml per day and painful hard stools", "duration": "3 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal hydration ramp from <700ml to 2.5L tracking bowel normalization."
    ))

    # SCN-FINAL-097 (easy) - Meditation habit and reduced workplace stress reactivity
    scenarios.append(make_scenario(
        sid="SCN-FINAL-097",
        domain="longitudinal_change",
        difficulty="easy",
        consult_text="Patient reports feeling calmer during executive meetings and not losing patience during delays.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports increased emotional composure during high-pressure meetings."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Practices 15 minutes of mindfulness breathwork every morning before opening email", "duration": "past 6 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "stress", "summary": "Frequent anger outbursts and chest tightness during morning work meetings", "duration": "4 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal habit adoption (mindfulness) linked to improved affective regulation."
    ))

    # SCN-FINAL-098 (medium) - Mediterranean diet adoption and lipid profile improvement
    scenarios.append(make_scenario(
        sid="SCN-FINAL-098",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents for routine follow-up following a complete overhaul of dietary patterns, reporting sustained high energy.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents for dietary review reporting sustained energy throughout the day."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Adheres strictly to Mediterranean diet rich in extra virgin olive oil, wild salmon, and legumes", "duration": "past 4 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "nutrition", "summary": "Standard western diet high in processed meats, refined grains, and trans fats", "duration": "8 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Baseline fasting lipid panel 8 months ago showed elevated LDL 165 mg/dL, triglycerides 220 mg/dL; counseled on Mediterranean pattern.", "record_type": "doctor_confirmed", "timestamp": "2026-01-20T11:00:00Z"},
            {"fact_id": "F4", "note": "Repeat fasting lipids today show marked improvement: LDL 118 mg/dL, triglycerides 135 mg/dL.", "record_type": "doctor_confirmed", "timestamp": "2026-09-18T10:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal multi-source documentation tracking dietary change from western to Mediterranean and subsequent biomarker response."
    ))

    # SCN-FINAL-099 (medium) - Structured CBT for insomnia (CBT-I) sleep consolidation
    scenarios.append(make_scenario(
        sid="SCN-FINAL-099",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient reports sleep efficiency has reached 88% with sleep onset latency under 20 minutes.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports sleep efficiency of 88% and sleep latency under 20 minutes."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Sleep window compressed to 11:30 PM - 6:30 AM with strict stimulus control; falls asleep in 15 mins", "value": "7 hours sleep window", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "sleep", "summary": "Spent 10 hours in bed tossing and turning with 90-minute sleep latency and sleep efficiency <55%", "duration": "3 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient initiated 6-week structured CBT-I program for chronic psychophysiological insomnia.", "record_type": "doctor_confirmed", "timestamp": "2026-07-10T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal progression through CBT-I sleep restriction therapy resulting in documented consolidation."
    ))

    # SCN-FINAL-100 (medium) - Weight-loss plateau after initial rapid drop
    scenarios.append(make_scenario(
        sid="SCN-FINAL-100",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents concerned that weight has remained unchanged at 82 kg for 5 weeks despite continuing initial diet.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports a 5-week weight plateau at 82 kg following earlier rapid loss."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Maintains 1,600 kcal/day diet; weight stable at 82 kg for past 5 weeks", "duration": "past 5 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "lifestyle_change", "summary": "Lost 10 kg rapidly over initial 8 weeks starting from 92 kg on 1,600 kcal diet", "duration": "3 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient counseled on adaptive thermogenesis and reduction in total daily energy expenditure after 10kg mass loss.", "record_type": "doctor_confirmed", "timestamp": "2026-08-15T15:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal metabolic adaptation where same caloric intake produces rapid early loss then weight plateau."
    ))

    # SCN-FINAL-101 (medium) - Progressive knee osteoarthritis symptom worsening with weight gain
    scenarios.append(make_scenario(
        sid="SCN-FINAL-101",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents reporting increased right knee aching and difficulty walking down stairs over the past 6 months.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports progressive worsening of right knee pain especially descending stairs."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Right knee pain score 7/10 after walking 2 blocks; requires handrail on stairs", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "lifestyle_change", "summary": "Body weight increased from 75 kg to 88 kg over past 6 months following job change", "duration": "past 6 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "symptom", "summary": "Mild occasional knee stiffness only after vigorous hiking (pain 2/10)", "duration": "1 year ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Right knee radiograph confirmed mild medial compartment joint space narrowing 1 year ago.", "record_type": "doctor_confirmed", "timestamp": "2025-09-10T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal escalation of joint symptoms correlating with 13kg mechanical weight gain."
    ))

    # SCN-FINAL-102 (medium) - Gradual SSRI dose titration and anxiety symptom course
    scenarios.append(make_scenario(
        sid="SCN-FINAL-102",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient reports significant reduction in daily panic episodes and improved work concentration at 12-week follow-up.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports panic attacks have dropped to zero and work focus is restored."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "mood", "summary": "Reports feeling emotionally balanced with no panic episodes in past 4 weeks", "duration": "past 4 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "stress", "summary": "Experienced 3-4 disabling panic attacks weekly with agoraphobia", "duration": "3 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Initiated sertraline 25mg daily for Panic Disorder 12 weeks ago; titrated to 50mg at week 4 and 100mg at week 8.", "record_type": "doctor_confirmed", "timestamp": "2026-06-25T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal pharmacological titration trajectory demonstrating progressive clinical remission."
    ))

    # SCN-FINAL-103 (medium) - Progressive increase in training volume leading to overtraining syndrome
    scenarios.append(make_scenario(
        sid="SCN-FINAL-103",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents complaining of heavy legs, elevated resting heart rate, insomnia, and declining race performance.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports elevated resting HR, insomnia, heavy limbs, and performance decline."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Training 14 sessions/week with 110 miles running, zero rest days", "duration": "past 4 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Resting heart rate surged from 48 bpm to 65 bpm; fragmented sleep", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "activity", "summary": "Maintained balanced 50 miles/week training with 2 rest days and strong race times", "duration": "4 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal volume ramp exceeding physiological recovery capacity, matching overtraining phenotype."
    ))

    # SCN-FINAL-104 (medium) - Stepwise dietary sodium reduction and blood pressure response
    scenarios.append(make_scenario(
        sid="SCN-FINAL-104",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents for hypertension check; home blood pressure log shows sustained reduction to 124/80 mmHg.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents with home blood pressure logs demonstrating sustained 124/80 mmHg control."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Strictly cooking at home using fresh herbs and no added salt (<1,500mg Na/day)", "duration": "past 2 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "nutrition", "summary": "Frequent restaurant dining and canned foods with sodium >4,500mg/day and clinic BP 148/94", "duration": "5 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Stage 1 HTN diagnosed 5 months ago; patient elected 3-month trial of strict DASH dietary lifestyle changes before medications.", "record_type": "doctor_confirmed", "timestamp": "2026-04-15T09:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal therapeutic lifestyle trial tracking dietary adherence and subsequent normative blood pressure response."
    ))

    # SCN-FINAL-105 (medium) - Transition from acute grief to integrated mourning
    scenarios.append(make_scenario(
        sid="SCN-FINAL-105",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents for 6-month check-in, noting ability to smile at memories and return to community volunteer work.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports returning to social volunteering and experiencing fond memories with less acute distress."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "mood", "summary": "Engaging in daily routines, volunteering at animal shelter, sleeping 7 hours", "duration": "past 6 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "mood", "summary": "Acute profound grief with daily crying, inability to leave home, and severe insomnia following sibling's death", "duration": "6 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Supportive counseling provided at 1 month post-loss; encouraged gradual social re-engagement.", "record_type": "doctor_confirmed", "timestamp": "2026-03-20T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal progression from acute disabling grief to integrated functioning over 6 months."
    ))

    # SCN-FINAL-106 (medium) - Plant-based transition: initial bloating resolving into regular motility
    scenarios.append(make_scenario(
        sid="SCN-FINAL-106",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient reports that early digestive gas has completely settled and bowel habits are smooth and predictable.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports that digestive gas has settled and bowel motility is smooth."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes 45g fiber daily from varied beans, lentils, and vegetables with zero bloating", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Severe bloating, cramping, and flatulence during initial 2 weeks of high-fiber vegan diet", "duration": "2 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Reassured patient that early microbial fermentation changes with sudden fiber ramp typically adapt within 4-6 weeks.", "record_type": "doctor_confirmed", "timestamp": "2026-07-15T16:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal microbiome adaptation to high-fiber intake progressing from acute dysbiosis symptoms to tolerance."
    ))

    # SCN-FINAL-107 (medium) - Gradual smoking cessation and lung capacity improvement
    scenarios.append(make_scenario(
        sid="SCN-FINAL-107",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents noting significant reduction in morning cough and ability to jog without wheezing.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports resolution of morning cough and improved exertional breathing while jogging."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Completely smoke-free for 90 days using nicotine lozenges as needed", "duration": "past 3 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "habit", "summary": "1 pack-per-day cigarette smoker for 15 years with chronic morning productive cough", "duration": "6 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Enrolled in tobacco cessation protocol; spirometry showed mild FEV1 reduction.", "record_type": "doctor_confirmed", "timestamp": "2026-03-10T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal smoking cessation timeline with progressive clearance of bronchial mucus and cough."
    ))

    # SCN-FINAL-108 (medium) - Stepwise hydration ramp in chronic kidney stone former
    scenarios.append(make_scenario(
        sid="SCN-FINAL-108",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents for 6-month renal clinic follow-up; 24-hour urine collection volume measured at 2.8 liters.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents for renal follow-up with 24-hour urine volume of 2.8 liters."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "hydration", "summary": "Consistently drinks 3.2 liters of fluid daily including lemon water", "duration": "past 4 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "hydration", "summary": "Prior 24-hour urine volume was 1.1 liters with recurrent calcium oxalate stones", "duration": "6 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Target 24h urine volume >2.5 L to prevent recurrent nephrolithiasis; commended patient on compliance.", "record_type": "doctor_confirmed", "timestamp": "2026-09-15T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal fluid titration achieving clinical therapeutic volume targets in recurrent stone disease."
    ))

    # SCN-FINAL-109 (medium) - Progressive strength recovery after rotator cuff repair
    scenarios.append(make_scenario(
        sid="SCN-FINAL-109",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents for 6-month orthopedic follow-up demonstrating full active shoulder abduction without pain.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient demonstrates full painless active shoulder abduction at 6-month post-op check."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Performs resistance band rotator cuff strengthening 4 days/week; swims laps weekly", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Immobilized in sling with severe pain (8/10) and 0 active abduction immediately post-surgery", "duration": "6 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Right arthroscopic supraspinatus repair performed 6 months ago; physical therapy protocol progressed through phases I-IV.", "record_type": "doctor_confirmed", "timestamp": "2026-03-12T08:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal surgical rehabilitation trajectory from acute post-op immobilization to full functional range."
    ))

    # SCN-FINAL-110 (medium) - Progressive glycemic control with lifestyle and metformin titration
    scenarios.append(make_scenario(
        sid="SCN-FINAL-110",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents for diabetes review; latest HbA1c has dropped to 6.2% from an initial 8.9%.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents with repeat HbA1c reduced to 6.2%."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Maintains low-glycemic Mediterranean meal plan and walks 30 minutes after dinner", "duration": "past 3 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "nutrition", "summary": "Sedentary lifestyle with daily fast food and soda at initial diagnosis", "duration": "6 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Newly diagnosed Type 2 Diabetes (HbA1c 8.9%) 6 months ago; started Metformin 500mg BID titrated to 1000mg BID with lifestyle counseling.", "record_type": "doctor_confirmed", "timestamp": "2026-03-18T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal diabetes management demonstrating sustained glycemic normalization over 6-month window."
    ))

    # SCN-FINAL-111 (medium) - Gradual reduction in migraines after trigger identification
    scenarios.append(make_scenario(
        sid="SCN-FINAL-111",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient reports headache days have decreased from 12 days per month down to 2 days per month.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports headache frequency reduced from 12 days/month to 2 days/month."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Eliminated aged cheeses, maintained consistent 10 PM sleep schedule, and eliminated artificial sweeteners", "duration": "past 2 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Suffered 12-14 debilitating migraine episodes monthly requiring frequent urgent care visits", "duration": "6 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Migraine headache diary review identified dietary tyramine and erratic sleep as primary triggers; started low-dose topiramate.", "record_type": "doctor_confirmed", "timestamp": "2026-04-01T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal reduction in chronic episodic migraine frequency following multimodal trigger elimination."
    ))

    # SCN-FINAL-112 (medium) - Post-concussion symptom recovery trajectory
    scenarios.append(make_scenario(
        sid="SCN-FINAL-112",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient presents for 3-month post-concussion review reporting full tolerance to school screens and light.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports full tolerance of school screens, reading, and ambient light."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Attending full school days with 6 hours of computer use without headache or dizziness", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Severe photophobia, vestibular dizziness, and nausea provoked by 10 minutes of screen time after sports concussion", "duration": "3 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Sport-related concussion sustained in soccer match; prescribed graded return-to-learn and return-to-play protocol.", "record_type": "doctor_confirmed", "timestamp": "2026-06-15T09:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal graded recovery through post-concussive return-to-learn protocol."
    ))

    # SCN-FINAL-113 (medium) - Progressive improvement in GERD after weight loss and head-of-bed elevation
    scenarios.append(make_scenario(
        sid="SCN-FINAL-113",
        domain="longitudinal_change",
        difficulty="medium",
        consult_text="Patient reports nocturnal heartburn and chronic cough have resolved completely, allowing discontinuation of antacids.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports nocturnal heartburn and cough resolved; stopped OTC antacid use."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Elevated head of bed 6 inches on wood blocks, stops eating 3 hours before sleep, lost 8 kg", "duration": "past 2 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Woke choking on stomach acid nightly, took calcium carbonate chews 4 times daily", "duration": "5 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Endoscopy showed Grade B reflux esophagitis; advised mechanical head elevation and weight reduction.", "record_type": "doctor_confirmed", "timestamp": "2026-04-10T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal mechanical and lifestyle intervention resolving documented reflux esophagitis."
    ))

    # SCN-FINAL-114 (hard) - Heart failure recovery trajectory: EF improvement and NYHA functional downstaging
    scenarios.append(make_scenario(
        sid="SCN-FINAL-114",
        domain="longitudinal_change",
        difficulty="hard",
        consult_text="Patient presents for 1-year heart failure review; walks 2 miles daily with zero dyspnea or ankle swelling.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient walks 2 miles daily without dyspnea or peripheral edema at 1-year follow-up."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Walks 2 miles daily at brisk pace; strict <1,800mg sodium diet with daily weight logging", "duration": "past 3 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Severely limited by NYHA Class III dyspnea on walking 20 feet with 3-pillow orthopnea and gross lower limb edema", "duration": "1 year ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Initial diagnosis of HFrEF with Left Ventricular Ejection Fraction (LVEF) 25% post-viral myocarditis 1 year ago.", "record_type": "doctor_confirmed", "timestamp": "2025-09-20T10:00:00Z"},
            {"fact_id": "F4", "note": "Optimized on quadruple guideline-directed medical therapy (GDMT: ARNI, beta-blocker, MRA, SGLT2i). Repeat echocardiogram today demonstrates recovered LVEF 52% (HFrecEF).", "record_type": "doctor_confirmed", "timestamp": "2026-09-22T14:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal myocardial recovery (heart failure with recovered ejection fraction) under GDMT and dietary adherence."
    ))

    # SCN-FINAL-115 (hard) - Crohn's disease disease activity progression: endoscopic remission to clinical flare
    scenarios.append(make_scenario(
        sid="SCN-FINAL-115",
        domain="longitudinal_change",
        difficulty="hard",
        consult_text="Patient presents reporting return of right lower quadrant cramping, 6 liquid bowel movements daily, and low-grade fevers.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports RLQ abdominal pain, 6 loose stools daily, and low-grade fevers."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Developed sharp RLQ pain post-prandially and nocturnal diarrhea", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Missed last 2 monthly infliximab infusion appointments due to insurance transition", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "symptom", "summary": "Maintained complete deep clinical and biochemical remission with 1 formed bowel movement daily", "duration": "past 18 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Colonoscopy 6 months ago showed complete mucosal healing (SES-CD score 0) on maintenance infliximab 5mg/kg every 8 weeks.", "record_type": "doctor_confirmed", "timestamp": "2026-03-15T11:00:00Z"},
            {"fact_id": "F5", "note": "Fecal calprotectin surged to 850 ug/g today; secondary loss of response secondary to missed doses suspected.", "record_type": "doctor_confirmed", "timestamp": "2026-09-25T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4", "F5"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal loss of remission in inflammatory bowel disease following medication lapse tracking biochemical biomarker surge."
    ))

    # SCN-FINAL-116 (hard) - Chronic kidney disease progression: Stage 2 to Stage 4 transition over years
    scenarios.append(make_scenario(
        sid="SCN-FINAL-116",
        domain="longitudinal_change",
        difficulty="hard",
        consult_text="Patient presents with increasing fatigue, metallic taste in mouth, and generalized skin pruritus over past 3 months.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports progressive fatigue, metallic dysgeusia, and pruritus."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Severe daytime lethargy, nausea with high-protein meals, and persistent skin itching", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Completely asymptomatic with normal energy and baseline creatinine 1.1 mg/dL", "duration": "3 years ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Longitudinal laboratory tracking: 2023 eGFR 78 mL/min; 2025 eGFR 45 mL/min; current eGFR 22 mL/min (creatinine 2.9 mg/dL).", "record_type": "doctor_confirmed", "timestamp": "2026-09-20T09:00:00Z"},
            {"fact_id": "F4", "note": "Diabetic nephropathy with heavy proteinuria (UACR 2,200 mg/g); initiated vascular access planning and renal replacement education.", "record_type": "doctor_confirmed", "timestamp": "2026-09-20T09:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal multi-year trajectory of diabetic kidney disease showing progressive nephron loss and uremic symptom emergence."
    ))

    # SCN-FINAL-117 (hard) - Rheumatoid arthritis treatment escalation and disease activity score (DAS28) response
    scenarios.append(make_scenario(
        sid="SCN-FINAL-117",
        domain="longitudinal_change",
        difficulty="hard",
        consult_text="Patient presents for rheumatology review; reports morning joint stiffness has decreased from 3 hours to 10 minutes.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports morning joint stiffness duration has decreased from 3 hours to 10 minutes."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Zero swollen joints, minor stiffness in MCP joints resolving in 10 minutes", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Severe polyarticular synovitis with 14 swollen tender joints and inability to button shirt", "duration": "8 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Seropositive RA with high disease activity (DAS28-CRP 5.8) refractory to methotrexate monotherapy 8 months ago.", "record_type": "doctor_confirmed", "timestamp": "2026-01-15T14:00:00Z"},
            {"fact_id": "F4", "note": "Added TNF inhibitor (adalimumab 40mg biweekly); current DAS28-CRP 1.9 confirming clinical remission.", "record_type": "doctor_confirmed", "timestamp": "2026-09-15T14:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal biological disease-modifying therapy escalation leading to documented clinical remission."
    ))

    # SCN-FINAL-118 (hard) - Bariatric surgery multi-year metabolic and nutritional trajectory
    scenarios.append(make_scenario(
        sid="SCN-FINAL-118",
        domain="longitudinal_change",
        difficulty="hard",
        consult_text="Patient presents for 3-year post-gastric bypass annual surveillance; reports feeling energetic with stable BMI 24.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents for 3-year post-bariatric annual surveillance with stable normal weight."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consistently takes specialized bariatric multivitamin, calcium citrate, and B12 injections", "duration": "past 1 year", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "lifestyle_change", "summary": "Pre-operative baseline BMI 46 kg/m2 with severe sleep apnea and uncontrolled Type 2 Diabetes", "duration": "3 years ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Roux-en-Y gastric bypass performed in 2023; total weight loss 52 kg with complete T2D resolution off all antidiabetic agents.", "record_type": "doctor_confirmed", "timestamp": "2024-09-10T10:00:00Z"},
            {"fact_id": "F4", "note": "Annual lab panel today confirms normal ferritin, B12, vitamin D, and intact PTH on current supplementation.", "record_type": "doctor_confirmed", "timestamp": "2026-09-20T11:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Multi-year longitudinal metabolic post-bariatric trajectory demonstrating sustained diabetes remission and nutritional adequacy."
    ))

    # SCN-FINAL-119 (hard) - Parkinson's disease motor fluctuation emergence: honeymoon phase to 'wearing-off'
    scenarios.append(make_scenario(
        sid="SCN-FINAL-119",
        domain="longitudinal_change",
        difficulty="hard",
        consult_text="Patient presents noting that tremor and muscle stiffness return predictably 3 hours after each carbidopa/levodopa tablet.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports predictable return of resting tremor and stiffness 3 hours post-levodopa dose."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Experiences 'wearing-off' phenomenon with severe bradykinesia occurring 60 minutes before scheduled next dose", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Maintained smooth, continuous 24-hour symptom control on TID levodopa dosing without motor fluctuations", "duration": "2 years ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Idiopathic Parkinson's Disease diagnosed 4 years ago; initial excellent sustained response to levodopa 100/25mg TID.", "record_type": "doctor_confirmed", "timestamp": "2024-05-10T10:00:00Z"},
            {"fact_id": "F4", "note": "Motor fluctuations documented; discussed dose fractionation or COMT inhibitor / dopamine agonist adjunctive therapy.", "record_type": "doctor_confirmed", "timestamp": "2026-09-22T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal neurodegenerative progression from smooth therapeutic window to motor wearing-off fluctuations in Parkinson's."
    ))

    # SCN-FINAL-120 (hard) - Post-traumatic stress disorder (PTSD) trajectory through prolonged exposure therapy
    scenarios.append(make_scenario(
        sid="SCN-FINAL-120",
        domain="longitudinal_change",
        difficulty="hard",
        consult_text="Patient reports significant reduction in startle response, ability to drive on highways, and cessation of recurring nightmares.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports normalized startle reactivity, successful highway driving, and resolution of nightmares."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "mood", "summary": "Drives daily on highway without panic; sleeps 7 hours without nightmares; PCL-5 score 14", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "stress", "summary": "Severe vehicle-related PTSD with PCL-5 score 62, complete driving avoidance, and nightly panic awakenings", "duration": "9 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Severe PTSD secondary to major motor vehicle collision; completed 16-session manualized Prolonged Exposure (PE) therapy.", "record_type": "doctor_confirmed", "timestamp": "2026-02-10T14:00:00Z"},
            {"fact_id": "F4", "note": "Post-treatment psychometrics confirm sustained loss of PTSD diagnosis at 6-month follow-up.", "record_type": "doctor_confirmed", "timestamp": "2026-09-18T16:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal trauma recovery trajectory following evidence-based trauma-focused cognitive behavioral therapy."
    ))

    return scenarios
