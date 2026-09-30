"""
Final 200 Dataset - Irrelevant History Domain (20 scenarios: SCN-FINAL-146 to SCN-FINAL-165)
Distribution: 5 easy, 10 medium, 5 hard
Includes realistic, plausible historical distractors in irrelevant_fact_ids to test relevance filtering.
"""

from .scenario_builder import make_scenario

def get_irrelevant_history_scenarios():
    scenarios = []

    # SCN-FINAL-146 (easy) - Tension headache with distractor of resolved childhood wrist sprain
    scenarios.append(make_scenario(
        sid="SCN-FINAL-146",
        domain="irrelevant_history",
        difficulty="easy",
        consult_text="Patient presents reporting severe bilateral tension headaches and neck stiffness after long hours working on computer monitors.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports bilateral tension headaches and neck tightness from prolonged screen time."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Working 12-hour continuous shifts at desktop computer without ergonomic breaks", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Mild left wrist sprain after rollerblading fall during high school with complete recovery", "duration": "10 years ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 is directly relevant to computer screen tension headaches; F2 (resolved wrist sprain 10 years ago) is a clear distractor."
    ))

    # SCN-FINAL-147 (easy) - Lactose intolerance with distractor of favorite movie genre
    scenarios.append(make_scenario(
        sid="SCN-FINAL-147",
        domain="irrelevant_history",
        difficulty="easy",
        consult_text="Patient presents complaining of abdominal cramps and loose stools after drinking milkshakes.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has cramps and loose stools after milkshakes."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Recently added large dairy ice cream milkshakes daily", "duration": "past 1 week", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Enjoys watching documentary films on Sunday evenings", "duration": "past 2 years", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 directly explains dairy intolerance; F2 (watching documentaries) is an irrelevant personal preference distractor."
    ))

    # SCN-FINAL-148 (easy) - Sleep latency with distractor of owning a pet turtle
    scenarios.append(make_scenario(
        sid="SCN-FINAL-148",
        domain="irrelevant_history",
        difficulty="easy",
        consult_text="Patient reports taking 2 hours to fall asleep due to racing thoughts about bills.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient takes 2 hours to fall asleep due to racing thoughts about bills."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Acute financial stress over overdue mortgage payments", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "other_clinically_relevant_context", "summary": "Owns an aquatic pet turtle in a glass tank in the study", "duration": "past 4 years", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains cognitive hyperarousal at bedtime; F2 (pet turtle) is irrelevant."
    ))

    # SCN-FINAL-149 (easy) - Dehydration headache with distractor of preference for blue shirts
    scenarios.append(make_scenario(
        sid="SCN-FINAL-149",
        domain="irrelevant_history",
        difficulty="easy",
        consult_text="Patient presents with dry mouth, dark urine, and dull headache on hot summer days.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has dry mouth, dark urine, and headache on hot days."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "hydration", "summary": "Drinks only 400ml water daily while working in un-airconditioned warehouse", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "habit", "summary": "Prefers wearing cotton blue shirts over synthetic athletic wear", "duration": "past 5 years", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains dehydration; F2 (shirt color/fabric preference) is an irrelevant distractor."
    ))

    # SCN-FINAL-150 (easy) - Caffeine jitteriness with distractor of past dental filling
    scenarios.append(make_scenario(
        sid="SCN-FINAL-150",
        domain="irrelevant_history",
        difficulty="easy",
        consult_text="Patient reports heart pounding and hand tremors after morning coffee.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has palpitations and tremors after morning coffee."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Drinks 5 shots of espresso within 30 minutes of waking", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Routine composite resin filling on tooth #19 performed uneventfully 3 years ago.", "record_type": "doctor_confirmed", "timestamp": "2023-08-10T10:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 is directly relevant to caffeine sensitivity; F2 (old dental filling) is an irrelevant clinical note."
    ))

    # SCN-FINAL-151 (medium) - Plantar fasciitis with distractor of mild seasonal pollen rhinitis
    scenarios.append(make_scenario(
        sid="SCN-FINAL-151",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient presents complaining of stabbing right heel pain during the first morning steps out of bed.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports stabbing morning heel pain on first standing."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Started working a 10-hour retail shift walking on concrete floors in worn-out flat sneakers", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "symptom", "summary": "Occasional mild nasal sneezing in spring from tree pollen, completely resolved", "duration": "spring only", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patient counseled on plantar fascia stretching and supportive arch orthotics.", "record_type": "doctor_confirmed", "timestamp": "2026-09-12T14:00:00Z"}
        ],
        relevant_ids=["F1", "F3"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 (footwear/standing) and F3 (stretching) are relevant to plantar fasciitis; F2 (spring allergic rhinitis) is an irrelevant distractor."
    ))

    # SCN-FINAL-152 (medium) - High-sugar diet crash with distractor of mild myopia prescription
    scenarios.append(make_scenario(
        sid="SCN-FINAL-152",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient reports afternoon brain fog and shakiness 1 hour after eating sweet snacks.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports postprandial shakiness and cognitive fog 1 hour after sweet foods."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Lunches consist of glazed pastries and sweetened boba tea", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "other_clinically_relevant_context", "summary": "Wears prescription eyeglasses for mild myopia (-1.50 diopters) for distance driving", "duration": "past 5 years", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains reactive hypoglycemia; F2 (mild myopia glasses) is an irrelevant ocular distractor."
    ))

    # SCN-FINAL-153 (medium) - Acute situational bereavement with distractor of childhood chickenpox
    scenarios.append(make_scenario(
        sid="SCN-FINAL-153",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient reports acute grief, tearfulness, and appetite loss after losing their spouse last week.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports acute grief, crying spells, and poor appetite after spousal loss."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Spouse passed away unexpectedly 7 days ago", "duration": "7 days ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Childhood varicella (chickenpox) infection at age 6 documented in historical record.", "record_type": "doctor_confirmed", "timestamp": "2020-01-15T09:00:00Z"},
            {"fact_id": "F3", "note": "Supportive grief counseling resources provided.", "record_type": "doctor_confirmed", "timestamp": "2026-09-24T11:00:00Z"}
        ],
        relevant_ids=["F1", "F3"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 (loss) and F3 (grief support) are relevant; F2 (childhood varicella) is an irrelevant historical note."
    ))

    # SCN-FINAL-154 (medium) - Acid reflux with distractor of benign childhood clavicle fracture
    scenarios.append(make_scenario(
        sid="SCN-FINAL-154",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient complains of burning chest discomfort and acid taste upon lying down after late-night pizza.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has postprandial nocturnal retrosternal burning and regurgitation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Eats pepperoni pizza and hot sauce at 11 PM and immediately lies flat to sleep", "duration": "past 2 weeks", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Healed non-displaced right clavicle fracture sustained while playing soccer at age 12", "duration": "15 years ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 directly contextualizes gastroesophageal reflux; F2 (healed childhood clavicle fracture) is an irrelevant distractor."
    ))

    # SCN-FINAL-155 (medium) - Marathon training sore calf with distractor of mild earwax buildup
    scenarios.append(make_scenario(
        sid="SCN-FINAL-155",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient presents with bilateral gastrocnemius muscle tightness following sudden increase in hill sprint workouts.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports bilateral calf soreness following hill sprints."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Added 10 steep hill sprint repetitions twice weekly without adequate calf stretching", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Ear canal cerumen impaction cleared with gentle warm water lavage 1 year ago.", "record_type": "doctor_confirmed", "timestamp": "2025-08-15T10:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains exercise-induced muscular strain; F2 (past ear lavage) is an irrelevant clinical note."
    ))

    # SCN-FINAL-156 (medium) - Constipation from low fiber with distractor of childhood tonsillectomy
    scenarios.append(make_scenario(
        sid="SCN-FINAL-156",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient presents complaining of hard, infrequent bowel movements over the past month.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports constipation and hard stools."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumes less than 8g dietary fiber per day, eating mainly meat and cheese", "duration": "past 1 month", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Elective tonsillectomy for recurrent tonsillitis in childhood at age 8.", "record_type": "doctor_confirmed", "timestamp": "2018-04-12T09:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains dietary constipation; F2 (childhood tonsillectomy) is an irrelevant surgical history distractor."
    ))

    # SCN-FINAL-157 (medium) - Screen time sleep latency with distractor of preference for spicy Thai food
    scenarios.append(make_scenario(
        sid="SCN-FINAL-157",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient complains of lying awake for 2 hours looking at ceiling before falling asleep.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has 2-hour sleep latency."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Uses iPad with bright blue light in bed for reading until 1 AM", "duration": "past 1 month", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "nutrition", "summary": "Enjoys spicy Thai green curry occasionally for lunch on Fridays without GI upset", "duration": "past 1 year", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains sleep latency; F2 (well-tolerated Friday Thai lunch) is an irrelevant dietary preference distractor."
    ))

    # SCN-FINAL-158 (medium) - Overuse thumb tendinitis with distractor of past superficial knee scrape
    scenarios.append(make_scenario(
        sid="SCN-FINAL-158",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient presents with pain and clicking at the base of the right thumb after prolonged smartphone texting.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports pain and tenderness at radial base of thumb from texting."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "activity", "summary": "Spends 6+ hours daily typing with right thumb on large smartphone for social media management", "duration": "past 3 weeks", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "symptom", "summary": "Superficial skin abrasion on left knee from garden stumble 6 months ago, healed completely", "duration": "6 months ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains De Quervain-type thumb tendinitis; F2 (resolved knee abrasion) is an irrelevant distractor."
    ))

    # SCN-FINAL-159 (medium) - Gout flare after shellfish feast with distractor of past mild dandruff
    scenarios.append(make_scenario(
        sid="SCN-FINAL-159",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient presents with acute severe pain, erythema, and swelling in the right big toe.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient has acute severe first MTP joint inflammation."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Ate 2 dozen oysters, crab cakes, and drank 4 dark beers 2 nights ago", "duration": "2 days ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[
            {"fact_id": "F2", "note": "Mild scalp seborrheic dermatitis noted during routine exam 2 years ago; responded to OTC ketoconazole shampoo.", "record_type": "doctor_confirmed", "timestamp": "2024-07-10T10:00:00Z"}
        ],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 (high purine load) is relevant to acute gout flare; F2 (past dandruff) is an irrelevant dermatological note."
    ))

    # SCN-FINAL-160 (medium) - Fasting energy crash with distractor of playing acoustic guitar
    scenarios.append(make_scenario(
        sid="SCN-FINAL-160",
        domain="irrelevant_history",
        difficulty="medium",
        consult_text="Patient presents complaining of shaky hands and brain fog when working past 2 PM without lunch.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports afternoon shaky hands and brain fog when skipping lunch."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Skips midday meals 4 days a week due to back-to-back meetings", "duration": "past 3 weeks", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Plays acoustic guitar for 20 minutes on weekend afternoons as a relaxing hobby", "duration": "past 5 years", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[],
        clinician_notes=[],
        relevant_ids=["F1"],
        irrelevant_ids=["F2"],
        conflict_groups=[],
        evaluator_notes="F1 explains fasting hypoglycemic symptoms; F2 (guitar playing) is an irrelevant leisure hobby distractor."
    ))

    # SCN-FINAL-161 (hard) - Multi-system presentation: Gout vs Pseudogout with multiple surgical and cosmetic distractors
    scenarios.append(make_scenario(
        sid="SCN-FINAL-161",
        domain="irrelevant_history",
        difficulty="hard",
        consult_text="Patient presents with acute severe pain, swelling, and heat in the right knee joint developing overnight.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient presents with acute right knee monoarthritis with joint effusion."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Consumed 6 beers and large barbecue meat platter at wedding reception yesterday", "duration": "yesterday", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "hydration", "summary": "Severe dehydration after dancing in outdoor heat without drinking water", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "other_clinically_relevant_context", "summary": "Elective cosmetic laser tattoo removal on left upper arm completed without complication", "duration": "2 years ago", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F4", "category": "symptom", "summary": "Mild benign non-pigmented skin tag removed from neck", "duration": "4 years ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F5", "note": "Hyperuricemia documented (serum uric acid 9.2 mg/dL) with prior podagra flare 3 years ago.", "record_type": "doctor_confirmed", "timestamp": "2023-09-14T11:00:00Z"},
            {"fact_id": "F6", "note": "Routine screening colonoscopy 5 years ago was completely normal with zero polyps.", "record_type": "doctor_confirmed", "timestamp": "2021-04-10T08:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F5"],
        irrelevant_ids=["F3", "F4", "F6"],
        conflict_groups=[],
        evaluator_notes="F1 (purine/alcohol), F2 (dehydration), and F5 (hyperuricemia) are relevant to acute gouty monoarthritis; F3, F4, and F6 are distinct clinical distractors."
    ))

    # SCN-FINAL-162 (hard) - Heart failure exacerbation with extensive irrelevant remote surgical and dental history
    scenarios.append(make_scenario(
        sid="SCN-FINAL-162",
        domain="irrelevant_history",
        difficulty="hard",
        consult_text="Patient presents with worsening dyspnea on exertion, bilateral 2+ pitting pedal edema, and 3 kg weight gain over 4 days.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports exertional dyspnea, bilateral pedal edema, and acute 3 kg fluid gain."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "nutrition", "summary": "Ate heavy canned ham, salted soups, and pickled relishes containing >5,000mg sodium daily", "duration": "past 4 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Stopped taking prescribed furosemide 40mg due to running out of medication", "duration": "past 3 days", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "other_clinically_relevant_context", "summary": "Routine dental crown replacement on upper right molar", "duration": "18 months ago", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F4", "category": "symptom", "summary": "Mild benign sebaceous cyst on scalp observed with no infection", "duration": "3 years ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F5", "note": "HFrEF (EF 30%) secondary to ischemic cardiomyopathy; strict sodium restriction and loop diuretic adherence required.", "record_type": "doctor_confirmed", "timestamp": "2025-11-10T14:00:00Z"},
            {"fact_id": "F6", "note": "Right inguinal hernia repaired with synthetic mesh in 2015 without recurrence.", "record_type": "doctor_confirmed", "timestamp": "2015-06-12T09:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F5"],
        irrelevant_ids=["F3", "F4", "F6"],
        conflict_groups=[],
        evaluator_notes="F1 (sodium binge), F2 (diuretic non-adherence), and F5 (HFrEF) explain volume overload; F3, F4, and F6 are distractors."
    ))

    # SCN-FINAL-163 (hard) - Panic Disorder flare with distractors of old scar and eye drop prescription
    scenarios.append(make_scenario(
        sid="SCN-FINAL-163",
        domain="irrelevant_history",
        difficulty="hard",
        consult_text="Patient presents with sudden-onset palpitations, lightheadedness, chest tightness, and fear of impending doom during office meetings.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports paroxysmal panic attacks with tachycardia, chest tightness, and fear of dying."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "stress", "summary": "Facing intense audit and job termination threat at work", "duration": "past 2 weeks", "source": "mental_wellness", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Consumes 6 double espressos daily to stay awake during late audit prep", "duration": "past 10 days", "source": "nutrition", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "symptom", "summary": "Linear superficial scar on left index finger from kitchen knife cut in childhood", "duration": "20 years ago", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Panic Disorder diagnosed 2 years ago; full cardiology evaluation (ECG, 24h Holter, echo) was completely normal.", "record_type": "doctor_confirmed", "timestamp": "2024-10-18T10:00:00Z"},
            {"fact_id": "F5", "note": "Prescribed lubricating artificial tear eye drops for dry eyes in air-conditioned office.", "record_type": "doctor_confirmed", "timestamp": "2025-05-12T15:30:00Z"}
        ],
        relevant_ids=["F1", "F2", "F4"],
        irrelevant_ids=["F3", "F5"],
        conflict_groups=[],
        evaluator_notes="F1, F2, and F4 directly contextualize panic disorder recurrence; F3 (finger scar) and F5 (lubricating eye drops) are distractors."
    ))

    # SCN-FINAL-164 (hard) - Anticoagulated patient epistaxis with distractors of mild myopia and remote appendectomy
    scenarios.append(make_scenario(
        sid="SCN-FINAL-164",
        domain="irrelevant_history",
        difficulty="hard",
        consult_text="Patient presents with recurrent spontaneous anterior epistaxis (nosebleeds) lasting 20 minutes each over past 3 days.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports recurrent spontaneous epistaxis lasting 20 minutes."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "habit", "summary": "Self-medicated with high-dose aspirin 650mg TID and ibuprofen 800mg TID for knee ache", "duration": "past 5 days", "source": "nutrition", "record_type": "patient_reported"},
            {"fact_id": "F2", "category": "habit", "summary": "Uses dry un-humidified indoor electric heater running 24/7 causing severe nasal crusting", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F3", "category": "other_clinically_relevant_context", "summary": "Underwent uncomplicated laparoscopic appendectomy at age 16", "duration": "14 years ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F4", "note": "Patient on Apixaban (Eliquis) 5mg BID for non-valvular atrial fibrillation; warned against NSAID/aspirin co-medication.", "record_type": "doctor_confirmed", "timestamp": "2026-01-20T11:00:00Z"},
            {"fact_id": "F5", "note": "Corrective lenses prescribed for mild presbyopia.", "record_type": "doctor_confirmed", "timestamp": "2025-03-10T14:00:00Z"}
        ],
        relevant_ids=["F1", "F2", "F4"],
        irrelevant_ids=["F3", "F5"],
        conflict_groups=[],
        evaluator_notes="F1 (dual NSAID/aspirin), F2 (mucosal desiccation), and F4 (DOAC anticoagulation) explain epistaxis; F3 (remote appendectomy) and F5 (presbyopia glasses) are distractors."
    ))

    # SCN-FINAL-165 (hard) - Allergic contact dermatitis with distractors of childhood ear piercing and remote wisdom teeth extraction
    scenarios.append(make_scenario(
        sid="SCN-FINAL-165",
        domain="irrelevant_history",
        difficulty="hard",
        consult_text="Patient presents with intensely pruritic, erythematous, vesicular rash on both earlobes and periumbilical abdomen.",
        q_facts=[
            {"fact_id": "Q1", "text": "Patient reports pruritic vesicular dermatitis on earlobes and periumbilical skin."}
        ],
        patient_current=[
            {"fact_id": "F1", "category": "lifestyle_change", "summary": "Started wearing cheap costume jewelry earrings and a new metal belt buckle containing un-plated nickel", "duration": "past 1 week", "source": "mental_wellness", "record_type": "patient_reported"}
        ],
        patient_longitudinal=[
            {"fact_id": "F2", "category": "other_clinically_relevant_context", "summary": "Surgical extraction of 4 impacted third molars (wisdom teeth) under local anesthesia", "duration": "8 years ago", "source": "nutrition", "record_type": "patient_reported"}
        ],
        clinician_notes=[
            {"fact_id": "F3", "note": "Patch testing 3 years ago confirmed Type IV hypersensitivity to Nickel Sulfate (+++) and Cobalt.", "record_type": "doctor_confirmed", "timestamp": "2023-05-18T10:00:00Z"},
            {"fact_id": "F4", "note": "Annual dermatological full-body skin check showed no atypical melanocytic nevi.", "record_type": "doctor_confirmed", "timestamp": "2026-02-15T16:00:00Z"}
        ],
        relevant_ids=["F1", "F3"],
        irrelevant_ids=["F2", "F4"],
        conflict_groups=[],
        evaluator_notes="F1 (nickel jewelry/belt buckle) and F3 (proven nickel allergy) explain contact dermatitis; F2 (wisdom teeth removal) and F4 (routine skin check) are distractors."
    ))

    return scenarios
