import unittest
from docs.evaluation.datasets.validate_dataset import validate_dataset_data, ScenarioValidator

class TestDatasetValidator(unittest.TestCase):

    def test_valid_scenario_with_q_facts(self):
        valid_scenario = {
            "scenario_id": "SCN-PILOT-001",
            "split": "pilot",
            "domain": "longitudinal_change",
            "difficulty": "medium",
            "current_consultation": {
                "text": "Patient presents with fatigue. Mentions trying to sleep earlier.",
                "fact_units": [
                    {"fact_id": "Q1", "text": "Patient presents with fatigue."},
                    {"fact_id": "Q2", "text": "Patient mentions trying to sleep earlier."}
                ]
            },
            "patient_reported_current_context": [
                {
                    "fact_id": "F1",
                    "category": "sleep",
                    "summary": "Reported sleep improved to 7 hours",
                    "value": "7 hours/night",
                    "duration": "past 1 week",
                    "source": "mental_wellness",
                    "record_type": "patient_reported"
                }
            ],
            "patient_reported_longitudinal_history": [
                {
                    "fact_id": "F2",
                    "category": "sleep",
                    "summary": "Reduced sleep associated with exam stress",
                    "value": "5 hours/night",
                    "duration": "2 weeks ago",
                    "source": "mental_wellness",
                    "record_type": "patient_reported",
                    "status": "superseded"
                },
                {
                    "fact_id": "F3",
                    "category": "habit",
                    "summary": "Prefers vegetarian meals on weekdays",
                    "source": "nutrition",
                    "record_type": "patient_reported",
                    "status": "current"
                }
            ],
            "clinician_authored_history": [
                {
                    "fact_id": "F4",
                    "note": "Fatigue symptoms were reviewed during a previous consultation.",
                    "record_type": "doctor_confirmed",
                    "timestamp": "2026-09-15T10:00:00Z"
                }
            ],
            "gold_evidence": {
                "relevant_fact_ids": ["F1", "F2", "F4"],
                "irrelevant_fact_ids": ["F3"],
                "conflict_groups": [],
                "expected_provenance": {
                    "Q1": "current_consultation",
                    "Q2": "current_consultation",
                    "F1": "patient_reported",
                    "F2": "patient_reported",
                    "F3": "patient_reported",
                    "F4": "clinician_authored"
                }
            },
            "notes_for_evaluator": "Sample test scenario with Q fact units"
        }

        is_valid, errors = validate_dataset_data(valid_scenario)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_q_fact_in_relevant_fact_ids_rejected(self):
        scenario = {
            "scenario_id": "SCN-PILOT-002",
            "split": "pilot",
            "domain": "nutrition",
            "difficulty": "easy",
            "current_consultation": {
                "text": "Skipping breakfast discussion",
                "fact_units": [
                    {"fact_id": "Q1", "text": "Patient skips breakfast"}
                ]
            },
            "patient_reported_current_context": [
                {
                    "fact_id": "F1",
                    "category": "nutrition",
                    "summary": "Skipping breakfast",
                    "source": "nutrition",
                    "record_type": "patient_reported"
                }
            ],
            "patient_reported_longitudinal_history": [],
            "clinician_authored_history": [],
            "gold_evidence": {
                "relevant_fact_ids": ["F1", "Q1"],  # Q1 forbidden in relevant_fact_ids
                "irrelevant_fact_ids": [],
                "conflict_groups": [],
                "expected_provenance": {
                    "Q1": "current_consultation",
                    "F1": "patient_reported"
                }
            }
        }

        is_valid, errors = validate_dataset_data(scenario)
        self.assertFalse(is_valid)
        self.assertTrue(any("relevant_fact_ids must contain historical 'F' facts only" in e for e in errors))

    def test_conflict_group_with_q_and_f_facts(self):
        conflict_scenario = {
            "scenario_id": "SCN-PILOT-003",
            "split": "pilot",
            "domain": "conflicting_information",
            "difficulty": "hard",
            "current_consultation": {
                "text": "Patient reports sleeping 8 hours per night regularly.",
                "fact_units": [
                    {"fact_id": "Q1", "text": "Patient reports sleeping 8 hours per night regularly."}
                ]
            },
            "patient_reported_current_context": [],
            "patient_reported_longitudinal_history": [],
            "clinician_authored_history": [
                {
                    "fact_id": "F1",
                    "note": "Documented ongoing severe insomnia with 4 hours sleep per night.",
                    "record_type": "doctor_confirmed"
                }
            ],
            "gold_evidence": {
                "relevant_fact_ids": ["F1"],
                "irrelevant_fact_ids": [],
                "conflict_groups": [
                    {
                        "conflict_id": "C1",
                        "fact_ids": ["Q1", "F1"],
                        "expected_behavior": "surface_for_verification",
                        "description": "Consultation reports 8h sleep while prior note recorded 4h insomnia."
                    }
                ],
                "expected_provenance": {
                    "Q1": "current_consultation",
                    "F1": "clinician_authored"
                }
            }
        }

        is_valid, errors = validate_dataset_data(conflict_scenario)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_invalid_overlap_and_missing_fact(self):
        invalid_scenario = {
            "scenario_id": "SCN-PILOT-004",
            "split": "pilot",
            "domain": "nutrition",
            "difficulty": "easy",
            "current_consultation": {"text": "Diet consultation"},
            "patient_reported_current_context": [
                {
                    "fact_id": "F1",
                    "category": "nutrition",
                    "summary": "Skipping breakfast",
                    "source": "nutrition",
                    "record_type": "patient_reported"
                }
            ],
            "patient_reported_longitudinal_history": [],
            "clinician_authored_history": [],
            "gold_evidence": {
                "relevant_fact_ids": ["F1", "F99"],  # F99 does not exist
                "irrelevant_fact_ids": ["F1"],        # F1 overlaps with relevant
                "conflict_groups": [],
                "expected_provenance": {
                    "F1": "clinician_authored"        # F1 declared as patient_reported
                }
            }
        }

        is_valid, errors = validate_dataset_data(invalid_scenario)
        self.assertFalse(is_valid)
        self.assertTrue(any("does not exist" in e for e in errors))
        self.assertTrue(any("both relevant and irrelevant" in e for e in errors))
        self.assertTrue(any("Mismatch with declared item origin" in e for e in errors))

    def test_forbidden_diagnostic_label(self):
        invalid_scenario = {
            "scenario_id": "SCN-PILOT-005",
            "split": "pilot",
            "domain": "mental_wellness",
            "difficulty": "hard",
            "current_consultation": {"text": "Depression screen"},
            "patient_reported_current_context": [],
            "patient_reported_longitudinal_history": [],
            "clinician_authored_history": [],
            "gold_diagnosis": "Major Depressive Disorder",  # Forbidden diagnostic ground truth
            "gold_evidence": {
                "relevant_fact_ids": [],
                "irrelevant_fact_ids": [],
                "conflict_groups": [],
                "expected_provenance": {}
            }
        }

        is_valid, errors = validate_dataset_data(invalid_scenario)
        self.assertFalse(is_valid)
        self.assertTrue(any("Forbidden diagnostic" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
