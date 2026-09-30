"""
Final 200 Dataset - Mixed Context Domain (30 scenarios: SCN-FINAL-061 to SCN-FINAL-090)
Distribution: 7 easy, 16 medium, 7 hard
"""

from .scenario_builder import make_scenario

def get_mixed_context_scenarios():
    scenarios = []

    # SCN-FINAL-061 (easy) - Stress eating and weight gain
    scenarios.append(make_scenario(
        sid="SCN-FINAL-061",
        domain="mixed_context",
        difficulty="easy",
        consult_text="Patient presents noticing rapid weight gain and tight clothing over the last month during a tense corporate restructuring.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports rapid weight gain and tight clothing during corporate restructuring."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "High job insecurity and workplace restructuring anxiety", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Eats nightly tubs of ice cream and pastries to cope with stress", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Straightforward mixed scenario linking acute occupational stress with nocturnal hyperpalatable bingeing and weight gain."
    ))

    # SCN-FINAL-062 (easy) - Poor sleep and high caffeine consumption causing tremors
    scenarios.append(make_scenario(
        sid="SCN-FINAL-062",
        domain="mixed_context",
        difficulty="easy",
        consult_text="Patient reports mild bilateral hand tremors and heart racing during early afternoon meetings.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences hand tremors and heart racing in the early afternoon."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Sleep curtailed to 4 hours per night due to new infant", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Drinks 5 energy drinks and 3 cold brews across the morning to compensate for exhaustion", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sleep deprivation driving extreme caffeine intake, precipitating tremor and tachycardia."
    ))

    # SCN-FINAL-063 (easy) - Dehydration and cognitive fogginess at desk
    scenarios.append(make_scenario(
        sid="SCN-FINAL-063",
        domain="mixed_context",
        difficulty="easy",
        consult_text="Patient reports mid-afternoon headaches, dry mouth, and difficulty concentrating on spreadsheets.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports afternoon headaches, dry mouth, and poor concentration."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "hydration", "summary": "Drinks zero water throughout 8-hour workday, only diet sodas", "value": "0 ml water", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "High workload intensity preventing bathroom breaks", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Workplace stress suppressing hydration behavior leading to tension/dehydration headaches."
    ))

    # SCN-FINAL-064 (easy) - Skipping breakfast and morning panic-like shakiness
    scenarios.append(make_scenario(
        sid="SCN-FINAL-064",
        domain="mixed_context",
        difficulty="easy",
        consult_text="Patient describes sudden episodes of sweating, shaky hands, and intense panic sensations at 10:30 AM daily.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has recurrent episodes of shakiness, diaphoresis, and panic sensations mid-morning."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Skips breakfast entirely while drinking 2 large black coffees", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Experiences high anxiety when facilitating morning team standup calls", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Fasting caffeine surge interacting with situational public speaking anxiety."
    ))

    # SCN-FINAL-065 (easy) - Late night bingeing and insomnia
    scenarios.append(make_scenario(
        sid="SCN-FINAL-065",
        domain="mixed_context",
        difficulty="easy",
        consult_text="Patient complains of tossing and turning with indigestion and uncomfortable heartburn after midnight.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports nocturnal indigestion, heartburn, and sleep disruption."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Orders fast food delivery (burgers, fries) and eats at 11:30 PM in bed", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Uses midnight eating to decompress after high-stress evening study sessions", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Stress-driven late-night high-fat meals provoking mechanical reflux and insomnia."
    ))

    # SCN-FINAL-066 (easy) - Exercise avoidance and low mood/sluggish digestion
    scenarios.append(make_scenario(
        sid="SCN-FINAL-066",
        domain="mixed_context",
        difficulty="easy",
        consult_text="Patient presents complaining of sluggish bowel movements, low energy, and feeling down on weekends.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports sluggish bowel transit, low energy, and low weekend mood."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Stopped all gym workouts and daily walking; completely sedentary", "duration": "past 6 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Decreased intake of whole grains and fresh produce in favor of processed snacks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sedentary shift combined with low-fiber dietary pattern explaining both bowel sluggishness and lethargy."
    ))

    # SCN-FINAL-067 (easy) - Alcohol use as stress management and morning hangover fatigue
    scenarios.append(make_scenario(
        sid="SCN-FINAL-067",
        domain="mixed_context",
        difficulty="easy",
        consult_text="Patient reports waking with dull headaches, dry mouth, and grogginess affecting morning work output.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports morning headaches, xerostomia, and grogginess impairing work."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Consumes 4 cocktails nightly between 9 PM and midnight", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Drinks to numb anxiety over pending divorce proceedings", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Marital stress prompting nightly alcohol consumption, generating morning withdrawal/hangover symptoms."
    ))

    # SCN-FINAL-068 (medium) - Marathon training, underfueling (RED-S), and amenorrhea/mood decline
    scenarios.append(make_scenario(
        sid="SCN-FINAL-068",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents with missed menstrual periods for 3 months, persistent bone soreness in shins, and mood irritability.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports 3 months of secondary amenorrhea, shin pain, and mood irritability."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Increased running mileage to 80 miles per week for marathon training", "duration": "past 3 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Restricting total calorie intake to 1,400 kcal/day while cutting dietary fats", "duration": "past 3 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient had normal regular menstrual cycles previously; advised on adequate energy availability during endurance training.", "record_type": "doctor_confirmed", "timestamp": "2026-04-12T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Relative Energy Deficiency in Sport (RED-S) context linking high training volume, hypocaloric diet, and hypothalamic amenorrhea."
    ))

    # SCN-FINAL-069 (medium) - High-sugar crash cycles mimicking panic attacks
    scenarios.append(make_scenario(
        sid="SCN-FINAL-069",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents concerned about 'sudden anxiety attacks' featuring racing pulse, dizziness, and cold sweats at 3 PM.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports mid-afternoon tachycardia, dizziness, and diaphoresis described as anxiety attacks."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Eats lunch consisting of large cinnamon roll and sweetened mocha frappuccino daily at 1:30 PM", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Under moderate stress managing new retail store opening", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Cardiology workup (ECG, Holter) 2 months ago was unremarkable for arrhythmia.", "record_type": "doctor_confirmed", "timestamp": "2026-07-15T11:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Reactive postprandial adrenergic surge from refined high-sugar lunch producing somatic sensations indistinguishable from panic."
    ))

    # SCN-FINAL-070 (medium) - Chronic insomnia, excessive daytime energy drink use, and nocturnal palpitations
    scenarios.append(make_scenario(
        sid="SCN-FINAL-070",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents complaining of bedtime heart pounding, restlessness in legs, and getting only 3 hours of sleep.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports nocturnal heart pounding, restless legs, and severe sleep curtailment."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes 3 high-stimulant 300mg caffeine workout drinks throughout the afternoon until 7 PM", "value": "900mg caffeine", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Takes 2 hours to fall asleep, wakes repeatedly with racing thoughts", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Reviewed sleep hygiene and recommended tapering caffeine intake past 12 PM.", "record_type": "doctor_confirmed", "timestamp": "2026-08-10T09:15:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Extreme afternoon caffeine intake generating sustained nocturnal adrenergic stimulation and insomnia."
    ))

    # SCN-FINAL-071 (medium) - Irritable Bowel Syndrome flare linked to work deadline anxiety and spicy takeout
    scenarios.append(make_scenario(
        sid="SCN-FINAL-071",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient reports frequent lower abdominal cramping, urgent watery diarrhea, and bloating during project sprint weeks.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports abdominal cramping, urgent diarrhea, and bloating during work sprint weeks."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "High anxiety regarding impending software release milestone", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Eats spicy takeout curry and fried appetizers while working late at desk", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Diagnosed IBS-Diarrhea predominant; counseled on gut-brain axis and dietary trigger management.", "record_type": "doctor_confirmed", "timestamp": "2025-10-05T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Gut-brain axis interaction: acute cognitive stress combined with spicy high-fat dietary triggers provoking IBS-D flare."
    ))

    # SCN-FINAL-072 (medium) - Migraine attack frequency surge with irregular sleep and skipping meals
    scenarios.append(make_scenario(
        sid="SCN-FINAL-072",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents reporting a surge in unilateral throbbing headaches with photophobia from once a month to 3 times weekly.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports increased frequency of throbbing unilateral headaches with photophobia."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Frequently skips lunch and goes 8+ hours without eating during busy workdays", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Erratic sleep schedule varying from 4 hours on weekdays to 11 hours on weekends", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Established migraine without aura; identified fasting and sleep variability as potent personal triggers.", "record_type": "doctor_confirmed", "timestamp": "2026-03-01T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Classic synergistic migraine triggers: prolonged fasting and circadian irregularity."
    ))

    # SCN-FINAL-073 (medium) - Restless legs syndrome exacerbated by evening wine and iron-poor diet
    scenarios.append(make_scenario(
        sid="SCN-FINAL-073",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient complains of irresistible urge to move legs accompanied by crawling sensations when lying down at 10 PM.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has nocturnal creeping dysesthesias in legs and motor restlessness at bedtime."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Drinks 2-3 glasses of wine nightly after dinner", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Consumes strictly plant-based meals with low bioavailable iron intake", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Serum ferritin borderline low at 22 ng/mL 4 months ago; discussed iron-rich nutrition.", "record_type": "doctor_confirmed", "timestamp": "2026-05-20T10:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Low ferritin background coupled with nocturnal alcohol trigger provoking restless legs syndrome."
    ))

    # SCN-FINAL-074 (medium) - Chronic fatigue and sedentary deconditioning following depressive episode
    scenarios.append(make_scenario(
        sid="SCN-FINAL-074",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents complaining of persistent muscle fatigue and shortness of breath when climbing one flight of stairs.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports exertional muscle fatigue and dyspnea on minor stair climbing."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Bed- and couch-bound for majority of day with under 1,500 steps/day", "duration": "past 3 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Diet consists of ultra-processed convenience foods with low protein", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "mood", "summary": "Treated for major depressive episode 4 months ago; mood has improved but physical stamina remains low", "duration": "past 4 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Physical deconditioning following prolonged depressive inactivity interacting with poor nutritional density."
    ))

    # SCN-FINAL-075 (medium) - Orthostatic dizziness, low sodium intake, and chronic anxiety hyperventilation
    scenarios.append(make_scenario(
        sid="SCN-FINAL-075",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient reports lightheadedness and feeling faint upon standing from office chair, with tingling around mouth.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences orthostatic dizziness and perioral tingling upon standing."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Strict very low sodium diet (under 1,000 mg/day) and drinks only distilled water", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Frequent shallow chest breathing and hyperventilation during workday anxiety", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Hypovolemia from severe sodium restriction combined with anxiety-induced respiratory alkalosis."
    ))

    # SCN-FINAL-076 (medium) - Weight plateau, metabolic adaptation, and mood frustration
    scenarios.append(make_scenario(
        sid="SCN-FINAL-076",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient expresses deep discouragement and anxiety after weight loss stalled completely for 4 weeks despite eating 1,000 kcal/day.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports emotional distress over a 4-week weight loss stall on 1000 kcal diet."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Strict 1,000 kcal restriction maintained for 16 consecutive weeks", "duration": "past 16 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Constantly weighs self 4 times daily; high anxiety over 100g fluctuations", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient counseled on metabolic adaptation and benefits of diet breaks/refeeding phases.", "record_type": "doctor_confirmed", "timestamp": "2026-07-28T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Metabolic adaptation from protracted severe caloric restriction accompanied by maladaptive scale fixation."
    ))

    # SCN-FINAL-077 (medium) - Shift-worker metabolic dysregulation, nighttime sweet cravings, and mood dip
    scenarios.append(make_scenario(
        sid="SCN-FINAL-077",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents discussing unmanageable 3 AM sugar cravings, brain fog, and low daytime mood on night shifts.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has intense 3 AM sugar cravings, cognitive fogginess, and low daytime mood."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Eats 4 donuts and sweetened iced coffee at 3:30 AM during overnight shift", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "mood", "summary": "Feels depressed and disconnected from daylight social life", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Circadian desynchronization interacting with nocturnal refined carbohydrate intake and social isolation."
    ))

    # SCN-FINAL-078 (medium) - Pre-workout supplement use, agitation, and gastrointestinal cramps
    scenarios.append(make_scenario(
        sid="SCN-FINAL-078",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient reports intense agitation, nausea, stomach cramps, and prickly skin sensations before gym sessions.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences agitation, nausea, abdominal cramps, and skin paresthesias before workouts."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Takes 2 heaping scoops of concentrated pre-workout powder containing 400mg caffeine, beta-alanine, and niacin on empty stomach", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Pressures self heavily to achieve personal record lifts every workout", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High-dose stimulant and beta-alanine pre-workout formula on empty stomach interacting with performance pressure."
    ))

    # SCN-FINAL-079 (medium) - Severe emotional distress, appetite loss, and electrolyte depletion
    scenarios.append(make_scenario(
        sid="SCN-FINAL-079",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents complaining of general weakness, muscle twitching, and crying spells following a sudden relationship breakup.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports muscle twitching, generalized weakness, and severe emotional distress."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Acute grief and emotional shock after sudden termination of 5-year relationship", "duration": "past 10 days", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "appetite", "summary": "Severe appetite suppression; consumed only plain iced tea and crackers for 10 days", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Acute situational grief leading to near-total food refusal and secondary micronutrient/electrolyte depletion."
    ))

    # SCN-FINAL-080 (medium) - High-fat comfort eating during seasonal depression
    scenarios.append(make_scenario(
        sid="SCN-FINAL-080",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents with worsening sluggishness, 6 kg weight gain, and lack of motivation to leave the house during winter.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports winter lethargy, 6 kg weight gain, and low motivation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "mood", "summary": "Low energy, prolonged sleep of 11 hours/night, and sadness beginning in November", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Consumes heavy pasta dishes, cheese, and pastries daily for emotional comfort", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Seasonal affective symptoms driving hyperphagic comfort eating and physical hibernation patterns."
    ))

    # SCN-FINAL-081 (medium) - Heavy work travel, fast food, and sleep disruption causing hypertension spike
    scenarios.append(make_scenario(
        sid="SCN-FINAL-081",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient reports elevated home blood pressure readings (155/95 mmHg), occipital tightness, and fatigue during business travel.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports home BP elevation to 155/95 mmHg, occipital tightness, and fatigue during business travel."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Eats airport fast food and steakhouse client dinners with heavy sodium every day", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Sleeping 4-5 hours per night in unfamiliar hotels across multiple time zones", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Well-controlled essential hypertension on amlodipine 5mg; baseline BP 122/78 mmHg at last clinic visit.", "record_type": "doctor_confirmed", "timestamp": "2026-06-10T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High dietary sodium, jetlag, and hotel sleep fragmentation destabilizing baseline blood pressure control."
    ))

    # SCN-FINAL-082 (medium) - Post-viral recovery, low appetite, and anxiety about health recovery
    scenarios.append(make_scenario(
        sid="SCN-FINAL-082",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents anxious about slow recovery from COVID-19, reporting persistent fatigue, poor appetite, and weight loss.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports health anxiety, persistent post-COVID fatigue, anorexia, and weight loss."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "appetite", "summary": "Loss of smell and taste leading to minimal food intake of under 800 kcal/day", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Constant anxiety searching online forums about long COVID and permanent disability", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Anosmia-induced nutritional deficit combined with health anxiety forum doomscrolling."
    ))

    # SCN-FINAL-083 (medium) - Chronic back pain, sedentary lifestyle, and comfort grazing
    scenarios.append(make_scenario(
        sid="SCN-FINAL-083",
        domain="mixed_context",
        difficulty="medium",
        consult_text="Patient presents complaining of knee joint stiffness, weight gain, and feelings of discouragement over physical limitations.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports knee stiffness, weight gain, and emotional discouragement."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Continuous grazing on chips and cookies while watching television all afternoon", "duration": "past 2 months", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "mood", "summary": "Feels isolated and discouraged by chronic knee osteoarthritis", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Knee OA diagnosed; recommended low-impact aquatic therapy and nutrition consult.", "record_type": "doctor_confirmed", "timestamp": "2026-04-18T13:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Osteoarthritis immobility paired with sedentary boredom snacking and affective demoralization."
    ))

    # SCN-FINAL-084 (hard) - Type 1 Diabetes: high-stress exams, irregular eating, and glycemic lability
    scenarios.append(make_scenario(
        sid="SCN-FINAL-084",
        domain="mixed_context",
        difficulty="hard",
        consult_text="Patient presents with wild swings in continuous glucose monitor readings (ranging from 45 to 320 mg/dL) over the past two weeks.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports severe glycemic volatility (45-320 mg/dL) on CGM over past two weeks."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Extreme stress preparing for medical school board examinations with high cortisol arousal", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Skips meals randomly then eats massive carbohydrate meals at midnight without counting carbs accurately", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "lifestyle_change", "summary": "Maintained 85% time-in-range (TIR) on basal-bolus insulin pump during structured semester", "duration": "6 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Established Type 1 Diabetes Mellitus for 8 years on Tandem Control-IQ pump; baseline HbA1c 6.8%.", "record_type": "doctor_confirmed", "timestamp": "2026-03-15T09:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Stress neuroendocrine counter-regulatory surges combined with erratic uncounted meal boluses in Type 1 Diabetes."
    ))

    # SCN-FINAL-085 (hard) - Anorexia nervosa history, orthostatic bradycardia, and obsessive exercise tracking
    scenarios.append(make_scenario(
        sid="SCN-FINAL-085",
        domain="mixed_context",
        difficulty="hard",
        consult_text="Patient presents with lightheadedness upon standing, resting pulse in the 40s, and intense fear of weight gain.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has orthostatic lightheadedness, resting bradycardia (40s bpm), and intense weight gain terror."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Restricting intake to 600 kcal/day of cucumber and egg whites", "duration": "past 6 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "activity", "summary": "Walks 30,000 steps daily pacing bedroom; experiences severe panic if step goal is not met", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Past hospitalization for Anorexia Nervosa restricting subtype 2 years ago; weight was restored to BMI 20.", "record_type": "doctor_confirmed", "timestamp": "2025-04-10T14:00:00Z"},
            {"fact_id": "F4", "note": "Warned regarding cardiovascular risks of relapse including sinus bradycardia and QTc prolongation.", "record_type": "doctor_confirmed", "timestamp": "2025-04-10T14:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Relapse of severe restrictive eating disorder with compulsive pacing resulting in marked cardiovascular adaptation/bradycardia."
    ))

    # SCN-FINAL-086 (hard) - Chronic kidney disease, unmanaged anxiety, and NSAID self-medication
    scenarios.append(make_scenario(
        sid="SCN-FINAL-086",
        domain="mixed_context",
        difficulty="hard",
        consult_text="Patient presents reporting worsening bilateral lower extremity edema, fatigue, and foamy urine.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports bilateral lower extremity edema, fatigue, and frothy urine."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Takes 800mg over-the-counter ibuprofen 3 times daily for tension headaches", "value": "2400mg/day", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Severe anxiety attacks and muscle tension headaches from caregiving stress", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Stage 3a CKD (baseline creatinine 1.6 mg/dL); strict avoidance of NSAIDs documented and emphasized to patient.", "record_type": "doctor_confirmed", "timestamp": "2026-02-12T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High-dose NSAID ingestion for tension headaches in patient with pre-existing CKD precipitating renal decompensation."
    ))

    # SCN-FINAL-087 (hard) - Binge Eating Disorder, depressive isolation, and rapid metabolic decline
    scenarios.append(make_scenario(
        sid="SCN-FINAL-087",
        domain="mixed_context",
        difficulty="hard",
        consult_text="Patient presents feeling overwhelmed by uncontrollable episodes of rapid secret eating followed by intense guilt and disgust.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports uncontrollable secret binge eating episodes with severe post-binge remorse."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes 5,000+ calories in secret nocturnal binges 4-5 nights per week without purging", "duration": "past 2 months", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "mood", "summary": "Experiences intense shame, self-disgust, and social withdrawal; avoids family gatherings", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "lifestyle_change", "summary": "History of chronic weight cycling through restrictive commercial diets over past decade", "duration": "past 10 years", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Screened positive for Binge Eating Disorder on BED-7; referred for specialized CBT-E psychotherapy.", "record_type": "doctor_confirmed", "timestamp": "2026-05-14T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Classic Binge Eating Disorder cycle: severe dietary restriction leading to nocturnal loss-of-control binges and depressive shame."
    ))

    # SCN-FINAL-088 (hard) - Heart failure with preserved ejection fraction (HFpEF), sodium binging, and panic attacks
    scenarios.append(make_scenario(
        sid="SCN-FINAL-088",
        domain="mixed_context",
        difficulty="hard",
        consult_text="Patient presents with acute orthopnea, paroxysmal nocturnal dyspnea waking in panic gasping for breath, and 4 kg rapid weight gain.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has acute orthopnea, nocturnal gasping episodes with panic, and 4 kg fluid weight gain."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Ate multiple bags of heavily salted potato chips and pickled snacks over holiday weekend", "duration": "past 4 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Experiences intense panic sensations when feeling short of breath lying flat", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "HFpEF (EF 55%, diastolic dysfunction grade II) on torsemide 10mg daily. Strict <2,000mg sodium diet mandated.", "record_type": "doctor_confirmed", "timestamp": "2026-03-20T10:30:00Z"},
            {"fact_id": "F4", "note": "Patient counseled that sudden weight gain >1.5 kg in 48h indicates volume overload requiring clinic notification.", "record_type": "doctor_confirmed", "timestamp": "2026-03-20T10:50:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Acute dietary sodium indiscretion precipitating decompensated HFpEF volume overload and secondary nocturnal respiratory panic."
    ))

    # SCN-FINAL-089 (hard) - Fibromyalgia flare: sleep disruption, dietary excitotoxins, and central sensitization
    scenarios.append(make_scenario(
        sid="SCN-FINAL-089",
        domain="mixed_context",
        difficulty="hard",
        consult_text="Patient presents with widespread body aches, tender points, allodynia, brain fog, and non-restorative sleep.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports widespread musculoskeletal pain, cutaneous allodynia, brain fog, and unrefreshing sleep."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Unrefreshing sleep with alpha-wave intrusion symptoms, waking every hour", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Increased consumption of artificial sweeteners (aspartame) and monosodium glutamate (MSG) in processed meals", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "symptom", "summary": "Diagnosed with Fibromyalgia 3 years ago; previously well-controlled with low-dose naltrexone and gentle yoga", "duration": "past 3 years", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Fibromyalgia management plan reviewed: optimize sleep continuity, avoid dietary excitotoxin triggers, maintain paced activity.", "record_type": "doctor_confirmed", "timestamp": "2025-11-05T14:15:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Synergistic exacerbation of central sensitization from non-restorative sleep and high dietary excitotoxin exposure in fibromyalgia."
    ))

    # SCN-FINAL-090 (hard) - Post-bariatric reactive hypoglycemia, anxiety attacks, and food avoidance
    scenarios.append(make_scenario(
        sid="SCN-FINAL-090",
        domain="mixed_context",
        difficulty="hard",
        consult_text="Patient presents with severe anxiety about eating, shaking episodes after meals, and progressive fear of leaving home.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has postprandial tremor/sweating episodes and developed agoraphobia from fear of collapsing."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Eats sweet pastries and high-carb bagels, triggering severe postprandial neuroglycopenic shakiness at 90 minutes", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Developed severe fear of experiencing a hypoglycemic collapse in public places", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "lifestyle_change", "summary": "Underwent sleeve gastrectomy 2 years ago with 45 kg weight loss", "duration": "2 years ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Post-bariatric late dumping / hyperinsulinemic hypoglycemia documented on mixed meal tolerance test; prescribed low-glycemic, high-protein diet.", "record_type": "doctor_confirmed", "timestamp": "2026-04-02T16:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Post-bariatric hyperinsulinemic hypoglycemia from simple carbs driving conditioned panic and agoraphobic avoidance."
    ))

    return scenarios
