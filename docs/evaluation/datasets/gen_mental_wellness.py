"""
Final 200 Dataset - Mental Wellness Domain (30 scenarios: SCN-FINAL-031 to SCN-FINAL-060)
Distribution: 8 easy, 15 medium, 7 hard
"""

from .scenario_builder import make_scenario

def get_mental_wellness_scenarios():
    scenarios = []

    # SCN-FINAL-031 (easy) - Sleep deprivation and irritability
    scenarios.append(make_scenario(
        sid="SCN-FINAL-031",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient reports feeling irritable with family members and struggling with low energy throughout the morning.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports morning low energy and irritability with family."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Averages 4.5 hours of fragmented sleep per night", "value": "4.5 hours", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Reports elevated workplace stress from staff shortages", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Direct correlation between chronic acute sleep deficit, workplace stress, and reported irritability."
    ))

    # SCN-FINAL-032 (easy) - Academic stress and tension headaches
    scenarios.append(make_scenario(
        sid="SCN-FINAL-032",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient presents with tight band-like sensations around the forehead during exam study sessions.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has band-like forehead tension during study sessions."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Severe anxiety regarding qualifying board exams in two weeks", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Straightforward context linking acute high-stakes exam anxiety to tension headaches."
    ))

    # SCN-FINAL-033 (easy) - Screen time before bed and sleep-onset insomnia
    scenarios.append(make_scenario(
        sid="SCN-FINAL-033",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient reports tossing and turning for over 90 minutes before falling asleep every night.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports severe sleep-onset latency of over 90 minutes."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Browses social media and watches videos in bed on phone with maximum brightness until 1 AM", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="High blue-light screen exposure directly in bed explains delayed melatonin onset and sleep latency."
    ))

    # SCN-FINAL-034 (easy) - Social isolation following relocation and low mood
    scenarios.append(make_scenario(
        sid="SCN-FINAL-034",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient mentions feeling lonely, disconnected, and lacking enthusiasm for weekend hobbies.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient feels lonely, disconnected, and lacks interest in weekend activities."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Relocated to new city alone for work 6 weeks ago; works 100% remotely with no local social circle", "duration": "past 6 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "mood", "summary": "Describes persistent sadness and diminished motivation", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Remote work isolation following relocation directly contextualizes low mood and loss of interest."
    ))

    # SCN-FINAL-035 (easy) - Overwork burnout and mental exhaustion
    scenarios.append(make_scenario(
        sid="SCN-FINAL-035",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient presents feeling emotionally drained, cynical about their career, and struggling to start tasks.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports emotional exhaustion, cynicism, and severe task procrastination."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Working 75 hours per week without weekend breaks for consecutive quarters", "duration": "past 4 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Chronic severe work overload context matches burnout symptomatology."
    ))

    # SCN-FINAL-036 (easy) - Restlessness and evening rumination
    scenarios.append(make_scenario(
        sid="SCN-FINAL-036",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient complains of racing thoughts about daily finances when trying to wind down at night.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences racing financial worries during evening wind-down."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Recent unexpected vehicle and home repair expenses causing acute financial worry", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Difficulty switching off mind at bedtime", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Acute financial stress triggering nocturnal cognitive hyperarousal."
    ))

    # SCN-FINAL-037 (easy) - Lack of physical activity and lethargic mood
    scenarios.append(make_scenario(
        sid="SCN-FINAL-037",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient feels sluggish, unmotivated, and physically heavy throughout the day.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient feels sluggish, unmotivated, and physically heavy."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Sedentary lifestyle with under 2,000 steps per day and zero structured exercise", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Marked physical inactivity providing context for persistent sluggishness."
    ))

    # SCN-FINAL-038 (easy) - Post-viral fatigue and temporary brain fog
    scenarios.append(make_scenario(
        sid="SCN-FINAL-038",
        domain="mental_wellness",
        difficulty="easy",
        consult_text="Patient notes lingering mental haziness and reduced stamina two weeks after recovering from a seasonal flu.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has lingering mental haziness and reduced stamina after viral infection."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Had acute influenza with high fevers resolved 14 days ago", "duration": "2 weeks ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Post-viral convalescent phase explaining mild residual cognitive fogginess."
    ))

    # SCN-FINAL-039 (medium) - Caregiver burden and compassion fatigue
    scenarios.append(make_scenario(
        sid="SCN-FINAL-039",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient presents feeling chronically overwhelmed, numb, and tearful while managing family duties.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports chronic overwhelm, emotional numbness, and tearfulness."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Primary 24/7 caregiver for elderly parent with advanced dementia with no respite care", "duration": "past 6 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Woken 3-4 times nightly by parent wandering", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient expressed growing strain from caregiving duties; recommended community respite resources.", "record_type": "doctor_confirmed", "timestamp": "2026-06-15T14:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Continuous unassisted caregiver burden with sleep fragmentation matches clinical picture of caregiver burnout."
    ))

    # SCN-FINAL-040 (medium) - Shift-work sleep disorder and circadian misalignment
    scenarios.append(make_scenario(
        sid="SCN-FINAL-040",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports severe daytime sleepiness, memory slips at work, and inability to sleep during daytime sleep opportunities.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports severe workplace sleepiness and inability to sleep during daytime rest periods."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Rotating between day, evening, and night shifts on a 3-day rapid rotation", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Sleep environment has no blackout curtains and significant street noise", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Reviewed circadian hygiene principles and light therapy strategies for rotating shift schedule.", "record_type": "doctor_confirmed", "timestamp": "2026-08-01T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Rapidly rotating shift work combined with suboptimal sleep environment explains severe circadian misalignment."
    ))

    # SCN-FINAL-041 (medium) - Performance anxiety and somatic hyperarousal
    scenarios.append(make_scenario(
        sid="SCN-FINAL-041",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient describes sweating, hand tremors, and dry mouth immediately before public presentations at work.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has acute tremors, diaphoresis, and dry mouth prior to public speaking."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Promoted to executive role requiring weekly company-wide town hall presentations", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Drinks 2 double espressos 30 minutes before presentations to calm nerves", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Situational performance demand combined with pre-talk caffeine surge exacerbates sympathetic autonomic discharge."
    ))

    # SCN-FINAL-042 (medium) - Seasonal affective pattern and reduced daylight exposure
    scenarios.append(make_scenario(
        sid="SCN-FINAL-042",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports hypersomnia (sleeping 10+ hours), carbohydrate cravings, and heavy low mood returning each late autumn.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences autumn-onset hypersomnia, carb cravings, and low mood."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "mood", "summary": "Noticed sharp drop in energy and mood coinciding with daylight saving time end", "duration": "past 4 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "activity", "summary": "Spends entire day indoors in windowless basement office", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "mood", "summary": "Reported identical winter depressive symptoms last year that resolved in spring", "duration": "1 year ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Classic seasonal pattern with recurring autumn exacerbation and low daylight exposure."
    ))

    # SCN-FINAL-043 (medium) - Grief reaction and intermittent pangs of sadness
    scenarios.append(make_scenario(
        sid="SCN-FINAL-043",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient presents discussing waves of grief, crying spells, and difficulty engaging in usual routines.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports waves of grief, crying spells, and disrupted daily routine."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Loss of spouse 2 months ago following a brief illness", "duration": "2 months ago", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "appetite", "summary": "Reduced appetite with 3 kg unintended weight loss since loss", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient attended bereavement support group; grieving process progressing normally.", "record_type": "doctor_confirmed", "timestamp": "2026-08-25T11:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Recent spousal bereavement and participation in bereavement support provides clear contextual foundation."
    ))

    # SCN-FINAL-044 (medium) - Sleep hygiene deterioration following home renovation
    scenarios.append(make_scenario(
        sid="SCN-FINAL-044",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient presents complaining of broken sleep, waking at 4 AM unable to return to sleep, and daytime fatigue.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports frequent awakenings, early morning insomnia at 4 AM, and daytime tiredness."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Temporary bedroom setup in living room during major home renovation; exposed to outdoor streetlight and drafts", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Checks work email on tablet during middle-of-the-night awakenings", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Environmental sleep disruption from renovation paired with conditioned arousal from checking email in bed."
    ))

    # SCN-FINAL-045 (medium) - Postpartum sleep fragmentation and mood fluctuations
    scenarios.append(make_scenario(
        sid="SCN-FINAL-045",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports feeling anxious about infant care, tearful in the evenings, and exhausted during the day.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports maternal anxiety, evening tearfulness, and profound fatigue."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Delivered healthy infant 5 weeks ago; exclusively breastfeeding on demand every 2 hours", "duration": "5 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Sleep broken into 90-minute increments, total 4 hours in 24-hour period", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Postpartum 2-week check was normal; EPDS score 6. Advised prioritizing maternal sleep intervals.", "record_type": "doctor_confirmed", "timestamp": "2026-09-02T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Postpartum transition with extreme sleep fragmentation informs emotional vulnerability."
    ))

    # SCN-FINAL-046 (medium) - Medical illness anxiety following family health scare
    scenarios.append(make_scenario(
        sid="SCN-FINAL-046",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient presents reporting constant checking of pulse, frequent blood pressure monitoring, and worry over bodily sensations.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports compulsive pulse checking and somatic hypervigilance."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Sibling suffered sudden non-fatal cardiac event 3 weeks ago", "duration": "3 weeks ago", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Checks pulse on smartwatch 40+ times per day and searches symptoms online", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Recent vicarious health trauma triggering acute somatic checking rituals and health anxiety."
    ))

    # SCN-FINAL-047 (medium) - Social anxiety and avoidance of workplace interactions
    scenarios.append(make_scenario(
        sid="SCN-FINAL-047",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports intense discomfort eating in the company cafeteria and avoiding hallway conversations with colleagues.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences distress eating in public cafeteria and avoids casual coworker interactions."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Fears being judged or scrutinized while eating or talking in groups", "duration": "past 3 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Eats lunch alone in car to avoid interpersonal contact", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Social evaluation fears and behavioral avoidance patterns contextualize workplace distress."
    ))

    # SCN-FINAL-048 (medium) - Digital media overconsumption and doomscrolling anxiety
    scenarios.append(make_scenario(
        sid="SCN-FINAL-048",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient describes constant dread, muscle tension in neck and shoulders, and difficulty focusing on reading books.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports constant sense of dread, neck muscle tension, and shortened attention span."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Spends 5+ hours daily doomscrolling breaking news and geopolitical crisis feeds", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Reports feeling overwhelmed by global events beyond personal control", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Excessive continuous consumption of distressful media fuels sustained sympathetic hyperarousal."
    ))

    # SCN-FINAL-049 (medium) - Retirement adjustment and loss of role structure
    scenarios.append(make_scenario(
        sid="SCN-FINAL-049",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports feeling aimless, sleeping late, and losing a sense of daily purpose.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient feels aimless, lacks daily structure, and reports loss of purpose."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Retired 3 months ago after a 40-year career in management with no planned routine", "duration": "past 3 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "mood", "summary": "Expresses emptiness and missing daily social interactions with former team", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Major life role transition from full-time career to unstructured retirement explaining purposelessness."
    ))

    # SCN-FINAL-050 (medium) - Chronic pain and secondary mood distress
    scenarios.append(make_scenario(
        sid="SCN-FINAL-050",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient presents expressing frustration, discouragement, and low mood related to persistent lower back ache.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports frustration, discouragement, and low mood secondary to back discomfort."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "symptom", "summary": "Chronic mechanical low back pain limiting ability to garden or walk dogs", "duration": "past 5 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "mood", "summary": "Feels demoralized by physical limitations", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient engaged with physical therapy for lumbar strain; noted psychological burden of pain.", "record_type": "doctor_confirmed", "timestamp": "2026-07-20T15:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Secondary emotional demoralization stemming directly from functional limitations of chronic musculoskeletal pain."
    ))

    # SCN-FINAL-051 (medium) - Perfectionism and procrastination paralysis
    scenarios.append(make_scenario(
        sid="SCN-FINAL-051",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports overwhelming anxiety when starting new creative projects, leading to last-minute panic.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports acute project initiation paralysis followed by severe deadline panic."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Holds belief that any submitted work must be flawless; fears negative peer critique", "duration": "past 6 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Avoids opening design files until 12 hours before client presentations", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Maladaptive perfectionistic standard driving task avoidance and acute anticipatory panic cycles."
    ))

    # SCN-FINAL-052 (medium) - Anticipatory anxiety regarding dental procedures
    scenarios.append(make_scenario(
        sid="SCN-FINAL-052",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports heart pounding, sleepless nights, and stomach knots ahead of an upcoming dental root canal.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports insomnia, tachycardia, and gastrointestinal distress ahead of dental visit."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Upcoming complex endodontic dental procedure scheduled in 5 days", "duration": "past 1 week", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "symptom", "summary": "Had a traumatic dental experience with inadequate local anesthesia during childhood", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Conditioned dental phobia and childhood medical trauma triggering acute anticipatory somatic anxiety."
    ))

    # SCN-FINAL-053 (medium) - Environmental noise sensitivity and home sleep disruption
    scenarios.append(make_scenario(
        sid="SCN-FINAL-053",
        domain="mental_wellness",
        difficulty="medium",
        consult_text="Patient reports feeling jumpy, fatigued, and angry due to persistent neighbor construction noise early in the morning.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports hyperarousal, anger, and fatigue from early morning neighbor noise."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Adjacent apartment building demolition starting daily at 6:30 AM with heavy drilling", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "sleep", "summary": "Sleep prematurely curtailed by 2 hours daily due to acoustic disturbance", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1", "F2"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Chronic involuntary acoustic intrusion causing involuntary early arousal and daytime affective irritability."
    ))

    # SCN-FINAL-054 (hard) - Antidepressant discontinuation syndrome vs somatic anxiety
    scenarios.append(make_scenario(
        sid="SCN-FINAL-054",
        domain="mental_wellness",
        difficulty="hard",
        consult_text="Patient presents with electric shock-like sensations in the head ('brain zaps'), dizziness, vivid nightmares, and crying spells.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports electric shock sensations in head, dizziness, vivid nightmares, and emotional lability."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Abruptly stopped taking daily escitalopram 20mg 4 days ago after running out of medication", "duration": "past 4 days", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "symptom", "summary": "Symptoms began within 48 hours of missing doses", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "mood", "summary": "Mood was stable on continuous SSRI therapy for past 18 months", "duration": "past 18 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Patient maintained on Escitalopram 20mg daily for generalized anxiety; warned against abrupt cessation.", "record_type": "doctor_confirmed", "timestamp": "2026-03-10T10:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Classic SSRI discontinuation syndrome following abrupt un-tapered cessation of long-term escitalopram."
    ))

    # SCN-FINAL-055 (hard) - Complex trauma trigger and dissociation context
    scenarios.append(make_scenario(
        sid="SCN-FINAL-055",
        domain="mental_wellness",
        difficulty="hard",
        consult_text="Patient presents reporting episodes of feeling 'outside their body', sudden panic, and hypervigilance after a workplace incident.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient experiences depersonalization, sudden panic attacks, and intense hypervigilance."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Witnessed severe physical altercation between two clients at workplace 1 week ago", "duration": "past 1 week", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "symptom", "summary": "Experiences intrusive flashbacks and avoidant behavior around workplace entrance", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Past history of PTSD related to motor vehicle collision 5 years ago, previously well-compensated with EMDR therapy.", "record_type": "doctor_confirmed", "timestamp": "2025-09-14T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Acute traumatic trigger reactivating trauma-spectrum dissociative and hyperarousal physiology in patient with prior PTSD."
    ))

    # SCN-FINAL-056 (hard) - Bipolar mood charting and hypomanic sleep reduction
    scenarios.append(make_scenario(
        sid="SCN-FINAL-056",
        domain="mental_wellness",
        difficulty="hard",
        consult_text="Patient reports sleeping only 2 hours a night while feeling extremely energized, starting 4 new business ideas, and talking rapidly.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports decreased need for sleep (2 hrs/night), surged energy, pressured speech, and rapid ideation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Averages 2 hours of sleep per night for past 6 days without daytime fatigue", "value": "2 hours/night", "duration": "past 6 days", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "mood", "summary": "Reports euphoric mood, elevated self-confidence, and spending large sums on equipment", "duration": "past 6 days", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "mood", "summary": "Experienced 3-month depressive episode with psychomotor slowing last winter", "duration": "8 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Diagnosed Bipolar II Disorder; prescribed lamotrigine maintenance. Advised early contact if sleep requirement drops below 4 hours.", "record_type": "doctor_confirmed", "timestamp": "2026-02-18T16:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Decreased need for sleep with elevated mood and pressured behavior in known Bipolar II patient represents cardinal hypomanic episode context."
    ))

    # SCN-FINAL-057 (hard) - Obstructive sleep apnea vs depression overlap
    scenarios.append(make_scenario(
        sid="SCN-FINAL-057",
        domain="mental_wellness",
        difficulty="hard",
        consult_text="Patient presents reporting unremitting morning headaches, daytime somnolence, low mood, and memory lapses.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has morning headaches, severe daytime sleepiness, low mood, and memory lapses."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "sleep", "summary": "Bed partner reports loud choking and gasping episodes during sleep with heavy snoring", "duration": "past 6 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Stops breathing repeatedly during the night according to spouse", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "lifestyle_change", "summary": "Gained 12 kg over the past year following knee injury", "duration": "past 1 year", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Prior trial of sertraline 50mg showed no improvement in daytime fatigue or cognitive fog.", "record_type": "doctor_confirmed", "timestamp": "2026-05-10T11:00:00Z"},
            {"fact_id": "F5", "note": "Physical exam noted BMI 34 kg/m2, crowded oropharynx (Mallampati IV). Recommended diagnostic polysomnography.", "record_type": "doctor_confirmed", "timestamp": "2026-05-10T11:20:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4", "F5"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Nocturnal airway obstruction symptoms and physical airway features explain refractory fatigue and cognitive symptoms unassisted by antidepressants."
    ))

    # SCN-FINAL-058 (hard) - ADHD executive dysfunction vs anxiety paralysis
    scenarios.append(make_scenario(
        sid="SCN-FINAL-058",
        domain="mental_wellness",
        difficulty="hard",
        consult_text="Patient presents complaining of lost paperwork, missed appointments, and chronic task paralysis leading to severe work distress.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports severe executive dysfunction, missed deadlines, and disorganization."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Placed on formal workplace performance improvement plan due to late reports", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Works simultaneously on 6 open browser tabs, constantly jumping between unfinished tasks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "symptom", "summary": "Lifelong history of losing items, careless mistakes in school, and difficulty sustaining attention since elementary school", "duration": "since childhood", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Comprehensive adult neuropsychological testing confirmed ADHD-Combined presentation; discussed multimodal management.", "record_type": "doctor_confirmed", "timestamp": "2026-01-15T15:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Longitudinal lifelong executive deficits contextualized by formal adult ADHD diagnosis informing acute occupational impairment."
    ))

    # SCN-FINAL-059 (hard) - Chronic insomnia conditioned arousal and sleep effort paradox
    scenarios.append(make_scenario(
        sid="SCN-FINAL-059",
        domain="mental_wellness",
        difficulty="hard",
        consult_text="Patient complains that the harder they try to sleep, the more awake they feel, spending 8 hours in bed while sleeping only 3.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports paradoxical arousal in bed, excessive sleep effort, and severe sleep inefficiency."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Goes to bed at 9 PM to 'force sleep', checks clock every 15 minutes, stays in bed until 7 AM tossing", "duration": "past 3 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Experiences intense dread and elevated heart rate as soon as bedroom lights are turned off", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "sleep", "summary": "Able to sleep easily on living room couch or during long train commutes", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Patient exhibits classic conditioned psychophysiological insomnia; recommended CBT-I with stimulus control and sleep restriction.", "record_type": "doctor_confirmed", "timestamp": "2026-07-08T09:45:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Psychophysiological insomnia with conditioned bedroom arousal, clock watching, and excessive time in bed."
    ))

    # SCN-FINAL-060 (hard) - Obsessive-compulsive contamination rituals and skin breakdown
    scenarios.append(make_scenario(
        sid="SCN-FINAL-060",
        domain="mental_wellness",
        difficulty="hard",
        consult_text="Patient presents with severely cracked, bleeding, and raw hands accompanied by intense distress regarding environmental germs.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents with severe irritant hand dermatitis and intense contamination anxiety."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Washes hands with harsh industrial antibacterial soap 50+ times daily, 3 minutes per wash with scalding water", "duration": "past 2 months", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "stress", "summary": "Experiences intense anxiety that touching household doorknobs will cause fatal illness to family", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "symptom", "summary": "History of checking rituals in adolescence, which worsened after birth of first child", "duration": "past 4 years", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "OCD with contamination subtype documented; patient referred for Exposure and Response Prevention (ERP) therapy and prescribed topical barrier emollients.", "record_type": "doctor_confirmed", "timestamp": "2026-06-22T13:15:00Z"}
        ],
        relevant_ids=["F1", "F2", "F3", "F4"],
        irrelevant_ids=[],
        conflict_groups=[],
        evaluator_notes="Compulsive repetitive hand-washing rituals driving severe physical skin barrier breakdown in documented OCD."
    ))

    return scenarios
