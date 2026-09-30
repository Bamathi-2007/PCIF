"""
Final 200 Dataset - Nutrition Domain (30 scenarios: SCN-FINAL-001 to SCN-FINAL-030)
Distribution: 8 easy, 15 medium, 7 hard
"""

from .scenario_builder import make_scenario

def get_nutrition_scenarios():
    scenarios = []

    # 1. SCN-FINAL-001 (easy) - Skipping meals and afternoon fatigue
    scenarios.append(make_scenario(
        sid="SCN-FINAL-001",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient presents with recurring afternoon energy slumps and mild dizzy spells. Inquires if adjustments to daily eating schedules could help.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences recurring afternoon energy slumps."},
            {"fact_id": "Q2", "text": "Patient reports mild dizzy spells."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Skips midday meal 4 days per week during work", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Consumes only one cup of water before 2 PM", "value": "250 ml", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Direct nutrition scenario testing recognition of irregular meal timing and low daytime hydration relevant to afternoon fatigue."
    ))

    # 2. SCN-FINAL-002 (easy) - High sodium intake and evening ankle puffiness
    scenarios.append(make_scenario(
        sid="SCN-FINAL-002",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient notices mild tightness and puffiness around the ankles by late evening. Wonders if recent dietary habits are contributing.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient notices mild evening ankle puffiness and tightness."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Increased consumption of prepared frozen dinners and canned soups high in sodium", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Straightforward context connecting sudden increase in prepared high-sodium foods with evening fluid retention."
    ))

    # 3. SCN-FINAL-003 (easy) - Excessive caffeine and palpitations/jitters
    scenarios.append(make_scenario(
        sid="SCN-FINAL-003",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient reports feeling jittery and noticing a fast heart rate in the late mornings during office hours.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports late morning jitteriness and fast heart rate."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Drinks 4 large dark roast coffees before 11 AM on an empty stomach", "value": "4 cups", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Clear pattern of high morning caffeine on empty stomach relevant to reported jitteriness."
    ))

    # 4. SCN-FINAL-004 (easy) - Sudden fiber spike and bloating
    scenarios.append(make_scenario(
        sid="SCN-FINAL-004",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient complains of significant abdominal bloating and flatulence starting a few days ago after adopting a new wellness plan.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient complains of new abdominal bloating and flatulence."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Added 3 scoops of raw psyllium husk fiber and raw lentils daily without gradual ramp-up", "duration": "past 4 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Daily fluid intake remains unchanged at approximately 1 liter per day", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sudden high unramped fiber intake paired with low fluid volume directly informs bloating symptom context."
    ))

    # 5. SCN-FINAL-005 (easy) - Nighttime snacking and acid reflux
    scenarios.append(make_scenario(
        sid="SCN-FINAL-005",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient reports waking up with a sour, burning taste in the back of the throat and throat clearing.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient wakes with sour burning sensation and throat clearing."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Eats spicy chips and dark chocolate immediately prior to lying down in bed", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Eating reflux-trigger foods right before bed provides contextual background for morning reflux symptoms."
    ))

    # 6. SCN-FINAL-006 (easy) - Strict carbohydrate restriction and athletic fatigue
    scenarios.append(make_scenario(
        sid="SCN-FINAL-006",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient reports heavy leg sensations and inability to sustain pace during afternoon 5k runs.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports heavy legs and premature fatigue during running sessions."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Restricted carbohydrate intake to under 20g/day while maintaining high training volume", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Very low carbohydrate intake under heavy cardiovascular training explains athletic stamina drop."
    ))

    # 7. SCN-FINAL-007 (easy) - Lactose re-exposure and digestive discomfort
    scenarios.append(make_scenario(
        sid="SCN-FINAL-007",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient reports intermittent lower abdominal cramping and loose stools occurring after breakfast.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has post-breakfast lower abdominal cramping and loose stools."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Switched from oat milk to whole cow's milk in morning cereal bowls", "duration": "past 1 week", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Switch to dairy milk in breakfast aligns temporally with post-breakfast digestive distress."
    ))

    # 8. SCN-FINAL-008 (easy) - Inadequate caloric intake during intense desk shifts
    scenarios.append(make_scenario(
        sid="SCN-FINAL-008",
        domain="nutrition",
        difficulty="easy",
        consult_text="Patient reports feeling spacey, irritable, and shaky around 5 PM while finishing work reports.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports shakiness, irritability, and lightheadedness at end of workday."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes only an energy drink and small bag of crackers throughout the entire 9-hour shift", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Severe daytime caloric restriction with high stimulant intake provides direct context for late-day shakiness."
    ))

    # 9. SCN-FINAL-009 (medium) - High protein powder intake, constipation, and low fluid intake
    scenarios.append(make_scenario(
        sid="SCN-FINAL-009",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient presents with persistent constipation, hard stools, and fullness over the past two weeks. Mentions starting a new strength program.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports two weeks of constipation and hard stools."},
            {"fact_id": "Q2", "text": "Patient recently started a strength training routine."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Added 3 whey protein isolate shakes daily without increasing dietary fiber", "value": "75g supplemental protein", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Fluid intake remains low at around 1.2 liters per day", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient counseled previously regarding maintaining hydration during high-protein diet trials.", "record_type": "doctor_confirmed", "timestamp": "2026-07-15T10:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Combines patient reported high protein/low hydration with prior clinician documentation of dietary counseling."
    ))

    # 10. SCN-FINAL-010 (medium) - Intermittent fasting with evening bingeing
    scenarios.append(make_scenario(
        sid="SCN-FINAL-010",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient reports severe post-dinner lethargy and uncomfortable epigastric fullness making it hard to relax in the evenings.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports severe post-dinner lethargy and epigastric fullness."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Follows 20:4 intermittent fasting schedule with a compressed 4-hour eating window", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Consumes 2,200 calories in a single 90-minute evening sitting", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "nutrition", "summary": "Previously maintained 3 balanced meals without postprandial distress", "duration": "6 months ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Extreme meal volume concentration during evening window explains heavy postprandial fullness compared to prior baseline."
    ))

    # 11. SCN-FINAL-011 (medium) - Iron supplement timing with calcium and tannins
    scenarios.append(make_scenario(
        sid="SCN-FINAL-011",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient inquires why their energy levels remain sluggish despite diligently taking oral iron supplements daily with breakfast.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports persistent low energy despite daily morning iron supplementation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Takes ferrous sulfate tablet together with a large latte and calcium-fortified orange juice", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Prescribed oral iron; advised taking with vitamin C and avoiding concurrent dairy or tea.", "record_type": "doctor_confirmed", "timestamp": "2026-08-20T14:15:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Co-administration of iron with calcium and coffee impairs absorption, contrasting with previous clinician instruction."
    ))

    # 12. SCN-FINAL-012 (medium) - High sugar-sweetened beverage intake and dental/thirst symptoms
    scenarios.append(make_scenario(
        sid="SCN-FINAL-012",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient mentions constant unquenchable thirst and frequent urination throughout the day, especially mid-afternoon.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports constant daytime thirst and frequent urination."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Drinks 4 cans of regular sweet tea and fruit punch daily to stay hydrated", "value": "150g added sugar/day", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Rarely drinks plain unflavored water", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High osmotic sugar load from beverages explains persistent thirst and frequent micturition."
    ))

    # 13. SCN-FINAL-013 (medium) - Plant-based transition without vitamin B12 / zinc planning
    scenarios.append(make_scenario(
        sid="SCN-FINAL-013",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient reports mild tingling in fingertips, lower endurance, and mouth ulcers after switching to a strict vegan diet 4 months ago.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports fingertip tingling, decreased endurance, and mouth ulcers after diet change."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Strict vegan diet consisting mainly of pasta, bread, and salads without fortified foods or supplements", "duration": "past 4 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Patient discussed transitioning to plant-based diet; recommended B12 supplement and varied legumes.", "record_type": "doctor_confirmed", "timestamp": "2026-05-12T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Unsupplemented restrictive vegan intake without planned micronutrient sources provides context for neurological and mucosal symptoms."
    ))

    # 14. SCN-FINAL-014 (medium) - Alcohol-associated nocturnal awakenings and morning dehydration
    scenarios.append(make_scenario(
        sid="SCN-FINAL-014",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient presents complaining of fragmented sleep with 3 AM awakenings and a dry, sticky mouth every morning.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports fragmented sleep with 3 AM awakenings and dry mouth."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Drinks 3 glasses of red wine nightly between 8 PM and 10 PM as a sleep aid", "duration": "past 6 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Does not drink water before sleeping to avoid nighttime bathroom visits", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Nocturnal rebound and diuretic effects of late alcohol consumption explain mid-sleep awakenings and dehydration."
    ))

    # 15. SCN-FINAL-015 (medium) - Ketogenic diet transition and 'keto flu' electrolyte context
    scenarios.append(make_scenario(
        sid="SCN-FINAL-015",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient reports dull bilateral headache, mental fogginess, and muscle cramps during the first week of a strict ketogenic protocol.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences dull headache, mental fog, and muscle cramps during new diet protocol."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Began strict ketogenic diet with under 15g net carbs per day 5 days ago", "duration": "past 5 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Has not used supplemental electrolytes (sodium, potassium, magnesium)", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Acute carbohydrate restriction inducing natriuresis without electrolyte replacement context."
    ))

    # 16. SCN-FINAL-016 (medium) - Extreme caloric restriction and cold intolerance
    scenarios.append(make_scenario(
        sid="SCN-FINAL-016",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient reports constant sensitivity to cold indoor temperatures, wearing sweaters in heated rooms, and brittle fingernails.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports constant cold intolerance, wearing sweaters indoors, and brittle fingernails."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Restricting total daily calories to 800 kcal/day for rapid weight loss", "duration": "past 6 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "appetite", "summary": "Suppresses hunger cues with black coffee and sparkling water", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Severe hypocaloric intake provides metabolic context for thermoregulatory suppression and nutrient insufficiency."
    ))

    # 17. SCN-FINAL-017 (medium) - High FODMAP dietary change triggering IBS symptoms
    scenarios.append(make_scenario(
        sid="SCN-FINAL-017",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient reports sharp post-meal abdominal cramps and alternating bowel habits after starting a 'gut health' smoothie routine.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports post-meal cramping and altered bowel habits with new smoothie routine."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Daily smoothies include raw garlic, inulin powder, apples, blackberries, and honey", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "nutrition", "summary": "Historically tolerated low-FODMAP cooked meals without digestive issues", "duration": "past 1 year", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Concentrated high-FODMAP ingredients (inulin, apples, honey, garlic) provide direct context for fermentative GI distress."
    ))

    # 18. SCN-FINAL-018 (medium) - Excessive dietary oxalate intake and flank discomfort inquiry
    scenarios.append(make_scenario(
        sid="SCN-FINAL-018",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient asks about dietary factors relating to mild intermittent right flank ache after increasing green juice consumption.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient inquires about dietary factors relating to intermittent flank ache."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes 2 large raw spinach, almond butter, and beet green smoothies daily", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Low water intake, approximately 800 ml per day", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient has family history of calcium oxalate nephrolithiasis; advised adequate hydration.", "record_type": "doctor_confirmed", "timestamp": "2026-04-10T16:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High oxalate load combined with low hydration provides context for patient's inquiry."
    ))

    # 19. SCN-FINAL-019 (medium) - High glycemic load snacking and mood swings
    scenarios.append(make_scenario(
        sid="SCN-FINAL-019",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient describes noticeable mood irritability and sudden mental fog exactly 60 to 90 minutes after lunchtime meals.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports irritability and mental fog 60-90 minutes post-lunch."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Lunches consist of refined white bagel with fruit jam, followed by gummy candy and soda", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Rapidly absorbable high glycemic lunch causing reactive glycemic oscillations matches timing of symptoms."
    ))

    # 20. SCN-FINAL-020 (medium) - Excessive grapefruit consumption with statin context
    scenarios.append(make_scenario(
        sid="SCN-FINAL-020",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient reports new generalized calf soreness and thigh aching after starting a citrus breakfast routine.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports calf soreness and thigh aching after new breakfast routine."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Eats 2 whole fresh grapefruits and drinks fresh grapefruit juice daily", "duration": "past 12 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Patient takes atorvastatin 20mg daily for hyperlipidemia; counseled on CYP3A4 dietary interactions.", "record_type": "doctor_confirmed", "timestamp": "2026-06-01T09:30:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High grapefruit consumption interacting with documented statin therapy provides crucial pharmacological-dietary context."
    ))

    # 21. SCN-FINAL-021 (medium) - Very low dietary fat intake and fat-soluble vitamin absorption
    scenarios.append(make_scenario(
        sid="SCN-FINAL-021",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient presents reporting dry flaky skin, night vision glare, and joint stiffness despite taking multivitamin supplements.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports dry flaky skin, night glare, and joint stiffness despite multivitamin use."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Strict non-fat diet with zero dietary oils, nuts, or butter", "duration": "past 3 months", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Takes fat-soluble vitamins (A, D, E, K) on an empty stomach with plain black coffee", "duration": "past 2 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Absence of dietary lipids severely compromises absorption of fat-soluble vitamin supplements."
    ))

    # 22. SCN-FINAL-022 (medium) - Salt substitute overuse and potassium context
    scenarios.append(make_scenario(
        sid="SCN-FINAL-022",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient presents complaining of unusual muscle weakness, tingling around the lips, and dull chest discomfort.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports muscle weakness, perioral tingling, and dull chest discomfort."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Liberally seasons all meals with potassium chloride salt substitute to avoid sodium", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Patient takes lisinopril 20mg daily for hypertension; instructed to monitor potassium intake.", "record_type": "doctor_confirmed", "timestamp": "2026-05-18T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Potassium chloride substitute combined with ACE inhibitor therapy provides vital contextual background."
    ))

    # 23. SCN-FINAL-023 (medium) - Night-shift eating dysregulation and metabolic fatigue
    scenarios.append(make_scenario(
        sid="SCN-FINAL-023",
        domain="nutrition",
        difficulty="medium",
        consult_text="Patient reports erratic hunger, persistent indigestion, and difficulty staying alert during 11 PM - 7 AM hospital shifts.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports erratic hunger, indigestion, and fatigue during overnight work shifts."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Eats heavy fried takeout meals at 3 AM and grazes continuously until sunrise", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Relies exclusively on cold sugary canned energy drinks throughout the shift", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Circadian mismatch with high-fat nocturnal eating and high-sugar energy drinks informs indigestion and alertness issues."
    ))

    # 24. SCN-FINAL-024 (hard) - Multi-phase elimination diet reintroduction with cross-reactive symptoms
    scenarios.append(make_scenario(
        sid="SCN-FINAL-024",
        domain="nutrition",
        difficulty="hard",
        consult_text="Patient presents reviewing complex digestive reactions, skin flare-ups, and headache patterns after attempting multi-food reintroduction.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports digestive reactions, facial rash, and headaches during food reintroduction protocol."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Reintroduced soy, aged cheddar cheese, and fermented kimchi simultaneously on the same day", "duration": "past 3 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "symptom", "summary": "Noticed facial flushing and throbbing headache 45 minutes after eating aged cheese and kimchi", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "nutrition", "summary": "Maintained strict 6-week hypoallergenic elimination diet with complete symptom clearance", "duration": "past 2 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Instructed patient on single-food staggered reintroduction protocol with 72-hour observation intervals.", "record_type": "doctor_confirmed", "timestamp": "2026-08-10T10:00:00Z"},
            {"fact_id": "F5", "note": "Patient noted historical sensitivity to high-histamine fermented foods.", "record_type": "doctor_confirmed", "timestamp": "2026-03-14T11:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4", "F5"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Complex multi-source history tracking protocol deviation (simultaneous reintroduction) and histamine sensitivity context."
    ))

    # 25. SCN-FINAL-025 (hard) - Bariatric surgery history, reactive hypoglycemia, and dumping syndrome
    scenarios.append(make_scenario(
        sid="SCN-FINAL-025",
        domain="nutrition",
        difficulty="hard",
        consult_text="Patient presents with severe episodes of sweating, lightheadedness, shakiness, and nausea occurring 2 hours after breakfast.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports sweating, lightheadedness, nausea, and shakiness 2 hours post-breakfast."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Breakfast consists of a large blended mango-banana smoothie with sweetened almond milk consumed in under 5 minutes", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Drinks 500ml of iced water simultaneously while drinking the smoothie", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "History of Roux-en-Y gastric bypass 3 years ago; maintained stable weight.", "record_type": "doctor_confirmed", "timestamp": "2026-01-20T14:00:00Z"},
            {"fact_id": "F4", "note": "Post-bariatric dietary guidelines provided: separate solids and liquids by 30 minutes, limit simple sugars to avoid dumping syndrome.", "record_type": "doctor_confirmed", "timestamp": "2026-01-20T14:20:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Rapid consumption of high-glycemic liquid with concurrent fluid ingestion post-bariatric surgery perfectly explains dumping syndrome mechanics."
    ))

    # 26. SCN-FINAL-026 (hard) - Chronic kidney disease dietary non-compliance and hyperphosphatemia context
    scenarios.append(make_scenario(
        sid="SCN-FINAL-026",
        domain="nutrition",
        difficulty="hard",
        consult_text="Patient complains of generalized skin itching (pruritus), bone aches, and red eyes developing over the past month.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports severe generalized skin itching, bone aches, and red conjunctival irritation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes dark colas, processed processed deli meats with inorganic phosphate additives, and high-dairy snacks daily", "duration": "past 4 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Consistently forgets to take prescribed calcium acetate phosphate binders with meals", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Stage 3b Chronic Kidney Disease documented; baseline eGFR 38 mL/min.", "record_type": "doctor_confirmed", "timestamp": "2026-04-05T09:00:00Z"},
            {"fact_id": "F4", "note": "Prescribed calcium acetate 667mg with meals; emphasized strict dietary phosphorus restriction.", "record_type": "doctor_confirmed", "timestamp": "2026-04-05T09:20:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High inorganic phosphorus intake combined with missed phosphate binders in CKD patient provides complete context for uremic pruritus."
    ))

    # 27. SCN-FINAL-027 (hard) - Celiac disease occult gluten exposure and recurrent aphthous stomatitis
    scenarios.append(make_scenario(
        sid="SCN-FINAL-027",
        domain="nutrition",
        difficulty="hard",
        consult_text="Patient presents with recurring fatigue, painful mouth ulcers, and loose stools despite believing they are on a 100% gluten-free diet.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports recurrent mouth ulcers, fatigue, and loose stools on supposedly strict gluten-free diet."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Switched to using shared household toaster and eating restaurant soups containing modified food starch and soy sauce", "duration": "past 6 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "lifestyle_change", "summary": "Began purchasing bulk bin oat flour without certified gluten-free seal", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "symptom", "summary": "Experienced complete remission of GI symptoms and mouth ulcers during strict certified gluten-free period", "duration": "past 1 year", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Biopsy-confirmed Celiac Disease documented 2 years ago; serology normalized on strict GFD.", "record_type": "doctor_confirmed", "timestamp": "2025-11-12T13:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Unintentional cross-contamination and hidden gluten sources in documented celiac patient explains symptom recurrence."
    ))

    # 28. SCN-FINAL-028 (hard) - Gout flare triggers: high purine, high fructose corn syrup, and dehydration
    scenarios.append(make_scenario(
        sid="SCN-FINAL-028",
        domain="nutrition",
        difficulty="hard",
        consult_text="Patient presents with acute severe pain, swelling, and redness in the first metatarsophalangeal joint of the left foot.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has acute severe pain, erythema, and swelling in the left great toe."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Attended seafood festival: consumed large portions of mussels, anchovies, and beer over the weekend", "duration": "past 3 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Drinks 1 liter of high-fructose corn syrup sweetened lemonade daily", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F3", "category": "hydration", "summary": "Sweated heavily during outdoor work with minimal water intake", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F4", "note": "Documented history of hyperuricemia and prior podagra flare 2 years ago; counseled on purine triggers.", "record_type": "doctor_confirmed", "timestamp": "2025-08-14T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Classic convergence of high purine seafood, beer, high fructose, and dehydration precipitating acute gouty arthritis."
    ))

    # 29. SCN-FINAL-029 (hard) - Warfarin dietary vitamin K instability and INR fluctuations
    scenarios.append(make_scenario(
        sid="SCN-FINAL-029",
        domain="nutrition",
        difficulty="hard",
        consult_text="Patient presents for routine review following recent laboratory notification of subtherapeutic INR (1.4). Patient feels well.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents following notification of subtherapeutic INR 1.4."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Started consuming large daily kale and collard green salads to lower cholesterol", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "lifestyle_change", "summary": "Started taking an over-the-counter green superfood powder rich in vitamin K1", "duration": "past 1 week", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "nutrition", "summary": "Previously maintained steady low vitamin K intake with stable target INR 2.0-3.0", "duration": "past 6 months", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Patient on Warfarin 5mg daily for mechanical aortic valve; target INR 2.5-3.5. Emphasized consistent vitamin K intake.", "record_type": "doctor_confirmed", "timestamp": "2026-02-10T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Sharp increase in dietary vitamin K from kale and green powder directly antagonizes warfarin mechanism."
    ))

    # 30. SCN-FINAL-030 (hard) - Post-cholecystectomy high-fat intolerance and bile acid diarrhea
    scenarios.append(make_scenario(
        sid="SCN-FINAL-030",
        domain="nutrition",
        difficulty="hard",
        consult_text="Patient complains of urgent, explosive watery diarrhea and abdominal cramping occurring within 30 minutes of eating meals.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports urgent postprandial watery diarrhea and cramping within 30 minutes of meals."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Diet consists heavily of deep-fried chicken wings, creamy cheese sauces, and bacon", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Consumes large high-fat meals in a single bolus after fasting all day", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Laparoscopic cholecystectomy completed 6 months ago uneventfully.", "record_type": "doctor_confirmed", "timestamp": "2026-03-22T08:00:00Z"},
            {"fact_id": "F4", "note": "Discharge instructions emphasized gradual reintroduction of fats and low-fat small frequent meals to prevent bile acid diarrhea.", "record_type": "doctor_confirmed", "timestamp": "2026-03-23T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Large bolus high-fat meals in post-cholecystectomy state overwhelms unbuffered continuous biliary flow."
    ))

    return scenarios
