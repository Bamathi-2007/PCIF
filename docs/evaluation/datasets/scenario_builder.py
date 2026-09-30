"""
PCIF Final 200 Scenarios Generator
==================================
Assembles exactly 200 locked evaluation scenarios across 9 domains with strict difficulty quotas.
"""

import json
from pathlib import Path

def make_scenario(
    sid: str,
    domain: str,
    difficulty: str,
    consult_text: str,
    q_facts: list,
    patient_current: list,
    patient_longitudinal: list,
    clinician_notes: list,
    relevant_ids: list,
    irrelevant_ids: list,
    conflict_groups: list,
    evaluator_notes: str
) -> dict:
    expected_prov = {}
    for q in q_facts:
        expected_prov[q["fact_id"]] = "current_consultation"
    for f in patient_current:
        expected_prov[f["fact_id"]] = "patient_reported"
    for f in patient_longitudinal:
        expected_prov[f["fact_id"]] = "patient_reported"
    for f in clinician_notes:
        expected_prov[f["fact_id"]] = "clinician_authored"

    return {
        "scenario_id": sid,
        "split": "final",
        "domain": domain,
        "difficulty": difficulty,
        "current_consultation": {
            "text": consult_text,
            "fact_units": q_facts
        },
        "patient_reported_current_context": patient_current,
        "patient_reported_longitudinal_history": patient_longitudinal,
        "clinician_authored_history": clinician_notes,
        "gold_evidence": {
            "relevant_fact_ids": relevant_ids,
            "irrelevant_fact_ids": irrelevant_ids,
            "conflict_groups": conflict_groups,
            "expected_provenance": expected_prov
        },
        "notes_for_evaluator": evaluator_notes
    }

# We will write separate domain generator files and import them to keep code clean and maintainable.
