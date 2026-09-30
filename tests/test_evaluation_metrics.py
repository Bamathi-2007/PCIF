"""
Unit Tests for PCIF Evaluation Scoring & Metrics (Final Frozen Specification)
=============================================================================
Verifies:
1. PCIF perfect/partial recall & distractor inclusion
2. Baseline condition-aware historical metrics -> N/A (None)
3. Zero-denominator handling -> None (N/A)
4. Condition-aware conflict surfacing: Baseline evaluates only Q-conflicts (returns None if no evaluable conflicts)
5. 4-way provenance breakdown, channel-specific accuracies, and explicitness rate
6. Condition-specific unsupported claim scoring
"""

import unittest
from evaluation.scoring import (
    score_scenario_response,
    match_fact_semantically,
    is_conflict_evaluable,
    evaluate_conflict_surfacing,
    evaluate_claim_provenance
)

class TestEvaluationMetrics(unittest.TestCase):

    def setUp(self):
        self.sample_scenario = {
            "scenario_id": "SCN-TEST-001",
            "domain": "nutrition",
            "difficulty": "medium",
            "current_consultation": {
                "text": "Patient reports afternoon fatigue.",
                "fact_units": [
                    {"fact_id": "Q1", "text": "Patient reports afternoon fatigue."}
                ]
            },
            "patient_reported_current_context": [
                {
                    "fact_id": "F1",
                    "category": "nutrition",
                    "summary": "Skips lunch on workdays",
                    "source": "nutrition",
                    "record_type": "patient_reported"
                },
                {
                    "fact_id": "F2",
                    "category": "hydration",
                    "summary": "Low fluid intake of 500 mL daily",
                    "value": "500 mL/day",
                    "source": "nutrition",
                    "record_type": "patient_reported"
                }
            ],
            "patient_reported_longitudinal_history": [
                {
                    "fact_id": "F3",
                    "category": "habit",
                    "summary": "Likes reading sci-fi books",
                    "source": "mental_wellness",
                    "record_type": "patient_reported",
                    "status": "current"
                }
            ],
            "clinician_authored_history": [
                {
                    "fact_id": "F4",
                    "note": "Documented prior fatigue discussion.",
                    "record_type": "doctor_confirmed",
                    "timestamp": "2026-08-01T10:00:00Z"
                }
            ],
            "gold_evidence": {
                "relevant_fact_ids": ["F1", "F2", "F4"],
                "irrelevant_fact_ids": ["F3"],
                "conflict_groups": [],
                "expected_provenance": {
                    "Q1": "current_consultation",
                    "F1": "patient_reported",
                    "F2": "patient_reported",
                    "F3": "patient_reported",
                    "F4": "clinician_authored"
                }
            }
        }

    def test_pcif_perfect_recall_and_zero_irrelevant_inclusion(self):
        pcif_response = {
            "context_summary": "Patient presents with fatigue. Background shows skipping lunch and low hydration.",
            "relevant_current_context": [
                "Patient reported frequently skips lunch during workdays.",
                "Low fluid intake averaging 500 mL per day."
            ],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [
                "Prior clinician documentation noted earlier fatigue symptoms review."
            ],
            "items_to_verify": []
        }

        res = score_scenario_response(self.sample_scenario, "pcif", pcif_response)
        metrics = res["metrics"]

        self.assertEqual(metrics["relevant_historical_recall"], 1.0)
        self.assertEqual(metrics["omission_rate"], 0.0)
        self.assertEqual(metrics["irrelevant_inclusion_rate"], 0.0)
        self.assertEqual(metrics["unsupported_inference_rate"], 0.0)
        self.assertIsNotNone(metrics["provenance_accuracy"])
        self.assertGreaterEqual(metrics["provenance_accuracy"], 0.8)
        self.assertIsNotNone(metrics["provenance_explicitness_rate"])

    def test_pcif_partial_recall_and_irrelevant_inclusion(self):
        pcif_response = {
            "context_summary": "Patient skips lunch and reads sci-fi books.",
            "relevant_current_context": [
                "Patient reported skips lunch during workdays.",
                "Patient likes reading sci-fi books."
            ],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": []
        }

        res = score_scenario_response(self.sample_scenario, "pcif", pcif_response)
        metrics = res["metrics"]

        self.assertAlmostEqual(metrics["relevant_historical_recall"], 1/3, places=2)
        self.assertAlmostEqual(metrics["omission_rate"], 2/3, places=2)
        self.assertEqual(metrics["irrelevant_inclusion_rate"], 1.0)

    def test_baseline_condition_aware_na_metrics(self):
        baseline_response = {
            "context_summary": "Patient presents reporting afternoon fatigue.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": []
        }

        res = score_scenario_response(self.sample_scenario, "baseline", baseline_response)
        metrics = res["metrics"]

        # Baseline was given 0 historical context -> historical metrics are N/A (None)
        self.assertIsNone(metrics["relevant_historical_recall"])
        self.assertIsNone(metrics["omission_rate"])
        self.assertIsNone(metrics["irrelevant_inclusion_rate"])
        self.assertIsNone(metrics["conflict_surfacing_rate"])
        self.assertEqual(metrics["unsupported_inference_rate"], 0.0)
        self.assertEqual(metrics["provenance_accuracy"], 1.0)

    def test_zero_denominator_na_handling(self):
        no_hist_scenario = {
            "scenario_id": "SCN-TEST-NOHIST",
            "domain": "no_history",
            "difficulty": "medium",
            "current_consultation": {
                "text": "New patient with fatigue.",
                "fact_units": [{"fact_id": "Q1", "text": "Patient with fatigue."}]
            },
            "patient_reported_current_context": [],
            "patient_reported_longitudinal_history": [],
            "clinician_authored_history": [],
            "gold_evidence": {
                "relevant_fact_ids": [],
                "irrelevant_fact_ids": [],
                "conflict_groups": [],
                "expected_provenance": {"Q1": "current_consultation"}
            }
        }

        response = {
            "context_summary": "New patient presents with fatigue. No prior structured records available.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": []
        }

        res = score_scenario_response(no_hist_scenario, "pcif", response)
        metrics = res["metrics"]

        self.assertIsNone(metrics["relevant_historical_recall"])
        self.assertIsNone(metrics["omission_rate"])
        self.assertIsNone(metrics["irrelevant_inclusion_rate"])
        self.assertIsNone(metrics["conflict_surfacing_rate"])
        self.assertEqual(metrics["unsupported_inference_rate"], 0.0)

    def test_condition_aware_conflict_surfacing_scoring(self):
        # Conflict requiring historical F2 (insomnia note) vs patient F1 (8h sleep)
        conflict_scenario = {
            "scenario_id": "SCN-TEST-CONFLICT",
            "domain": "conflicting_information",
            "difficulty": "hard",
            "current_consultation": {
                "text": "Patient states sleeping 8 hours every night.",
                "fact_units": [{"fact_id": "Q1", "text": "Patient states sleeping 8 hours."}]
            },
            "patient_reported_current_context": [
                {
                    "fact_id": "F1",
                    "category": "sleep",
                    "summary": "Sleeps 8 hours per night",
                    "source": "mental_wellness",
                    "record_type": "patient_reported"
                }
            ],
            "patient_reported_longitudinal_history": [],
            "clinician_authored_history": [
                {
                    "fact_id": "F2",
                    "note": "Documented severe persistent insomnia under 4 hours.",
                    "record_type": "doctor_confirmed",
                    "timestamp": "2026-09-20T10:00:00Z"
                }
            ],
            "gold_evidence": {
                "relevant_fact_ids": ["F1", "F2"],
                "irrelevant_fact_ids": [],
                "conflict_groups": [
                    {
                        "conflict_id": "C1",
                        "fact_ids": ["F1", "F2"],
                        "expected_behavior": "surface_for_verification",
                        "description": "Contemporaneous conflict between 8h report and clinician insomnia note."
                    }
                ],
                "expected_provenance": {
                    "Q1": "current_consultation",
                    "F1": "patient_reported",
                    "F2": "clinician_authored"
                }
            }
        }

        # PCIF: evaluable and successfully surfaced
        pcif_good_response = {
            "context_summary": "Discrepancy noted regarding sleep duration.",
            "relevant_current_context": ["Patient reported sleeping 8 hours."],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": ["Clinician note documented severe persistent insomnia under 4 hours."],
            "items_to_verify": [
                "Verify sleep duration: patient reports 8 hours sleep versus clinician documentation of severe insomnia under 4 hours."
            ]
        }
        res_pcif = score_scenario_response(conflict_scenario, "pcif", pcif_good_response)
        self.assertEqual(res_pcif["metrics"]["conflict_surfacing_rate"], 1.0)

        # Baseline: F1/F2 were NOT supplied to Baseline -> 0 evaluable conflicts -> returns None (N/A)
        base_response = {
            "context_summary": "Patient states sleeping 8 hours.",
            "relevant_current_context": [],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": ["Verify sleep patterns."]
        }
        res_base = score_scenario_response(conflict_scenario, "baseline", base_response)
        self.assertIsNone(res_base["metrics"]["conflict_surfacing_rate"])

    def test_condition_specific_unsupported_claims_for_baseline(self):
        hallucinating_baseline = {
            "context_summary": "Patient presents with fatigue.",
            "relevant_current_context": [
                "Patient has a long history of skipping meals on weekdays."
            ],
            "relevant_longitudinal_changes": [],
            "relevant_clinician_notes": [],
            "items_to_verify": []
        }

        res = score_scenario_response(self.sample_scenario, "baseline", hallucinating_baseline)
        metrics = res["metrics"]
        self.assertGreater(metrics["unsupported_inference_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
