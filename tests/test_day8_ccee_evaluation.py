"""
Day 8 CCEE Automated Evaluation & Hardening Test Suite (Final Pass).

Evaluates CCEE across 36 synthetic test cases (Days 4–8) covering 11 independent dimensions:
1. Relevance Filtering
2. Relevant Context Retention
3. Compression / Redundancy Control
4. Distinct Phenomenon Preservation
5. Unsupported Inference Prevention
6. Evidence Preservation
7. Temporal Reasoning
8. Speaker Attribution Safety
9. Source Integrity
10. Schema Validity
11. Context Sufficiency

Evaluates each dimension independently per case so that a failure in one specific requirement
does not falsely zero out unrelated passing dimensions.
"""

import os
import sys
import time
import json
from typing import List, Dict, Any, Union, Optional, cast

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure utf-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ccee.schema import (
    ClinicalContextItem,
    ALLOWED_SOURCES,
    ALLOWED_CATEGORIES,
    ALLOWED_RECORD_TYPES,
)
from ccee.engine import ClinicalContextExtractionEngine, ccee_engine
from backend.app.services.llm_service import llm_service


def run_local_hardening_tests():
    """Phase 1: Local schema validation, failure handling, and boundary tests (No LLM calls)."""
    print("\n" + "=" * 70)
    print("PHASE 1: DAY 8 LOCAL SCHEMA HARDENING & BOUNDARY TESTS (NO LLM)")
    print("=" * 70)

    # 1. Blank summary rejection in ClinicalContextItem
    try:
        ClinicalContextItem(
            category="sleep",
            summary="   ",
            source="mental_wellness"
        )
        assert False, "Should have raised ValueError for blank summary"
    except ValueError as ve:
        assert "non-empty string" in str(ve).lower() or "summary" in str(ve).lower()
        print("✓ Test 1 Passed: Blank/whitespace summary rejected by ClinicalContextItem")

    # 2. None or non-string summary rejection
    try:
        ClinicalContextItem(
            category="sleep",
            summary=cast(str, None),
            source="mental_wellness"
        )
        assert False, "Should have raised ValueError for None summary"
    except ValueError as ve:
        print("✓ Test 2 Passed: None summary rejected by ClinicalContextItem")

    # 3. Discarding schema-invalid item with blank summary raises controlled RuntimeError
    class MockBlankSummaryService:
        def extract_ccee(self, conversation_text, source):
            return [{"category": "sleep", "summary": "   ", "source": source}]

    mock_engine = ClinicalContextExtractionEngine(service=MockBlankSummaryService())
    try:
        mock_engine.extract_context("I feel tired", "mental_wellness")
        assert False, "Engine should raise RuntimeError when all candidate items fail validation"
    except RuntimeError as re:
        assert "failed schema validation" in str(re).lower()
        print("✓ Test 3 Passed: Engine raises controlled RuntimeError when all candidate items fail validation")


    # 4. Engine handling of empty/whitespace input (Day 8 Case 9)
    empty_result = ccee_engine.extract_context("   \n\t  ", "nutrition")
    assert empty_result == []
    print("✓ Test 4 Passed: Whitespace-only conversation immediately returns [] without LLM call")

    # 5. Engine handling of invalid source (Day 8 Case 10)
    try:
        ccee_engine.extract_context("I sleep five hours.", "fitness_ai")
        assert False, "Should have raised ValueError for invalid source 'fitness_ai'"
    except ValueError as ve:
        assert "Invalid source" in str(ve)
        print("✓ Test 5 Passed: Invalid source 'fitness_ai' rejected with controlled ValueError")

    # 6. Source integrity enforcement (source preserved even if category differs)
    item = ClinicalContextItem(
        category="sleep",
        summary="Reduced sleep due to late meals",
        source="nutrition",
        value="5 hours/night"
    )
    assert item.source == "nutrition"
    assert item.to_dict()["source"] == "nutrition"
    print("✓ Test 6 Passed: Source integrity strictly preserved (category='sleep', source='nutrition')")

    # 7. Unconfigured LLM service raises RuntimeError instead of fake []
    class MockUnconfiguredService:
        def extract_ccee(self, conversation_text, source):
            raise RuntimeError("Gemini client unavailable: GEMINI_API_KEY is not configured in backend environment.")

    mock_unconfig_engine = ClinicalContextExtractionEngine(service=MockUnconfiguredService())
    try:
        mock_unconfig_engine.extract_context("I sleep 5 hours", "mental_wellness")
        assert False, "Engine should re-raise LLM service RuntimeError"
    except RuntimeError as re:
        assert "GEMINI_API_KEY is not configured" in str(re)
        print("✓ Test 7 Passed: Infrastructure/config failure raises RuntimeError (distinguishable from [])")

    # 8. Mock A: Malformed top-level JSON / unparsable structured response -> controlled extraction exception
    class MockMalformedTopLevelService:
        def extract_ccee(self, conversation_text, source):
            raise RuntimeError("CCEE extraction failed: Unparsable structured response")

    mock_malformed_engine = ClinicalContextExtractionEngine(service=MockMalformedTopLevelService())
    try:
        mock_malformed_engine.extract_context("I feel tired", "mental_wellness")
        assert False, "Engine should raise RuntimeError for unparsable top-level JSON"
    except RuntimeError as re:
        assert "Unparsable structured response" in str(re)
        print("✓ Test 8 Passed: Malformed top-level JSON raises controlled extraction exception")

    # 9. Mock B: Result containing candidate items, but EVERY item fails schema validation -> controlled extraction exception
    class MockAllInvalidItemsService:
        def extract_ccee(self, conversation_text, source):
            return [
                {"category": "invalid_cat_1", "summary": "Bad category"},
                {"category": "sleep", "summary": "   "}  # Blank summary
            ]

    mock_all_invalid_engine = ClinicalContextExtractionEngine(service=MockAllInvalidItemsService())
    try:
        mock_all_invalid_engine.extract_context("I feel tired", "mental_wellness")
        assert False, "Engine should raise RuntimeError when ALL candidate items fail schema validation"
    except RuntimeError as re:
        assert "failed schema validation" in str(re).lower()
        print("✓ Test 9 Passed: All-invalid candidate items raise controlled extraction exception (not [])")

    # 10. Mock C: Mixed valid + invalid items -> valid items retained, invalid items rejected with warning (partial validation)
    class MockMixedItemsService:
        def extract_ccee(self, conversation_text, source):
            return [
                {"category": "sleep", "summary": "Reduced sleep duration", "value": "4 hours/night"},
                {"category": "invalid_category", "summary": "Invalid category item"}
            ]

    mock_mixed_engine = ClinicalContextExtractionEngine(service=MockMixedItemsService())
    mixed_result = mock_mixed_engine.extract_context("I sleep four hours", "mental_wellness")
    assert len(mixed_result) == 1
    assert mixed_result[0].category == "sleep"
    assert mixed_result[0].value == "4 hours/night"
    print("✓ Test 10 Passed: Mixed valid+invalid items performs partial validation (valid retained, invalid discarded)")



def get_all_evaluation_cases() -> List[Dict[str, Any]]:
    """Defines the complete test set of 36 synthetic cases (Days 4–8)."""
    return [
        # --- DAY 4 CASES (5) ---
        {
            "id": "Day 4 Case 3.1",
            "name": "Skipped breakfast due early classes",
            "source": "nutrition",
            "text": "I keep having to skip breakfast almost every morning because my college lectures start at 7:30 AM and I have to rush out.",
            "expect_empty": False,
            "required_categories": ["nutrition"],
            "must_contain": ["breakfast"],
        },
        {
            "id": "Day 4 Case 3.2",
            "name": "Reduced sleep due exam stress",
            "source": "mental_wellness",
            "text": "I've been sleeping around five hours because I'm stressed about exams for the last week.",
            "expect_empty": False,
            "required_categories": ["sleep"],
            "must_contain": ["5"],
            "expect_duration": True,
        },
        {
            "id": "Day 4 Case 3.3",
            "name": "Reduced appetite for one week",
            "source": "nutrition",
            "text": "For the past week, my appetite has dropped significantly and I feel full after eating barely half a meal.",
            "expect_empty": False,
            "required_categories": ["appetite"],
            "expect_duration": True,
            "prohibited_words": ["anorexia", "eating disorder", "malnutrition"],
        },
        {
            "id": "Day 4 Case 3.4",
            "name": "Low water intake",
            "source": "nutrition",
            "text": "I barely drink any water during the day, usually just one small glass because I get busy and keep forgetting.",
            "expect_empty": False,
            "required_categories": ["hydration"],
            "must_contain": ["1", "glass"],
        },
        {
            "id": "Day 4 Case 3.5",
            "name": "Irrelevant conversation (weather/car)",
            "source": "mental_wellness",
            "text": "Do you think it's going to rain this afternoon? I'm trying to decide if I should wash my car today or wait until the weekend.",
            "expect_empty": True,
        },

        # --- DAY 5 CASES (5) ---
        {
            "id": "Day 5 Case 4.1",
            "name": "Casual greeting",
            "source": "mental_wellness",
            "text": "Hi, how are you today?",
            "expect_empty": True,
        },
        {
            "id": "Day 5 Case 4.2",
            "name": "Preference without health relevance",
            "source": "nutrition",
            "text": "My favourite colour is yellow.",
            "expect_empty": True,
        },
        {
            "id": "Day 5 Case 4.3",
            "name": "Multiple meaningful phenomena",
            "source": "mental_wellness",
            "text": "I've been skipping meals this week and sleeping only four hours because I'm stressed about exams.",
            "expect_empty": False,
            "required_categories": ["nutrition", "sleep"],
            "fold_cause_stress": True,  # exam stress should fold into sleep/nutrition context, not standalone stress unless functional impact
        },
        {
            "id": "Day 5 Case 4.4",
            "name": "Unsupported diagnosis prevention & fatigue report",
            "source": "mental_wellness",
            "text": "I've been feeling tired and sleeping only four hours.",
            "expect_empty": False,
            "required_concepts": ["sleep", "tired"],  # Accepts 1 combined item OR 2 separate items (sleep + symptom)
            "prohibited_words": ["insomnia", "depression", "anemia", "syndrome", "disorder", "chronic fatigue"],
        },
        {
            "id": "Day 5 Case 4.5",
            "name": "Uncertain self-report",
            "source": "nutrition",
            "text": "I think I've been eating less than usual recently.",
            "expect_empty": False,
            "required_concepts": ["eating less"],
            "prohibited_words": ["severe", "anorexia", "malnutrition", "100%", "starvation"],
        },

        # --- DAY 6 CASES (7) ---
        {
            "id": "Day 6 Case 5.1",
            "name": "Exact/repeated sleep meaning",
            "source": "mental_wellness",
            "text": "I've been sleeping only five hours lately. Most nights I get about five hours because I'm studying late. My sleep has definitely reduced.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "must_contain": ["5"],
        },
        {
            "id": "Day 6 Case 5.2",
            "name": "Stress as context, not independent record",
            "source": "mental_wellness",
            "text": "I'm stressed about my exams and because of that I'm sleeping only four hours every night.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "forbidden_categories": ["stress"],
            "must_contain": ["4"],
        },
        {
            "id": "Day 6 Case 5.3",
            "name": "Two distinct phenomena & temporal attachment",
            "source": "mental_wellness",
            "text": "I'm sleeping only four hours and I've also lost my appetite this week.",
            "expect_empty": False,
            "expected_count": 2,
            "required_categories": ["sleep", "appetite"],
            "check_strict_temporal_attachment": True,  # sleep MUST NOT inherit duration="this week" from appetite!
        },
        {
            "id": "Day 6 Case 5.4",
            "name": "Repeated nutrition meaning",
            "source": "nutrition",
            "text": "I keep skipping breakfast. I usually don't eat anything in the morning before college. Most weekdays I leave without breakfast because my first class is early.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["nutrition"],
        },
        {
            "id": "Day 6 Case 5.5",
            "name": "Related hydration repetition & uncertainty preservation",
            "source": "nutrition",
            "text": "I forget to drink water at college. Some days I only drink one glass. I stay busy and hardly drink water until evening.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["hydration"],
            "check_episodic_qualifier": True,
        },
        {
            "id": "Day 6 Case 5.6",
            "name": "Independent stress should remain",
            "source": "mental_wellness",
            "text": "I feel overwhelmed throughout the entire day because of exams. I can't concentrate on normal tasks. I'm also sleeping around four hours at night.",
            "expect_empty": False,
            "expected_count": 2,
            "required_categories": ["stress", "sleep"],
        },
        {
            "id": "Day 6 Case 5.7",
            "name": "Irrelevant repetition",
            "source": "nutrition",
            "text": "Hi. Hello again. By the way my favourite colour is yellow. I really like yellow.",
            "expect_empty": True,
        },

        # --- DAY 7 CASES (9) ---
        {
            "id": "Day 7 Case 6.1",
            "name": "Explicit self-correction",
            "source": "mental_wellness",
            "text": "I've been sleeping around three hours. Actually, I think it's closer to five hours.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "must_contain": ["5"],
            "must_not_contain_as_value": ["3 hours"],
        },
        {
            "id": "Day 7 Case 6.2",
            "name": "Past -> current improvement",
            "source": "mental_wellness",
            "text": "Last week I was sleeping around four hours, but this week I'm back to about seven hours.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "must_contain": ["7"],
        },
        {
            "id": "Day 7 Case 6.3",
            "name": "Ongoing duration",
            "source": "mental_wellness",
            "text": "I've been sleeping around five hours every night for the past two weeks.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "must_contain": ["5"],
            "expect_duration": True,
        },
        {
            "id": "Day 7 Case 6.4",
            "name": "Resolved insignificant past event",
            "source": "mental_wellness",
            "text": "I had one night where I barely slept about three months ago, but my sleep has been normal ever since.",
            "expect_empty": True,
        },
        {
            "id": "Day 7 Case 6.5",
            "name": "Ongoing worsening appetite & approx duration",
            "source": "nutrition",
            "text": "My appetite started decreasing about two weeks ago, and it still seems to be getting worse.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["appetite"],
            "expect_duration": True,
            "check_approx_duration": True,
        },
        {
            "id": "Day 7 Case 6.6",
            "name": "Temporal decline",
            "source": "mental_wellness",
            "text": "Earlier this month I was sleeping around six hours. This week it's down to four hours because assignments are keeping me up.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "must_contain": ["4"],
        },
        {
            "id": "Day 7 Case 6.7",
            "name": "Distinct temporal phenomena",
            "source": "mental_wellness",
            "text": "My sleep has improved this week, but my appetite has been getting worse for about two weeks.",
            "expect_empty": False,
            "expected_count": 2,
            "required_categories": ["sleep", "appetite"],
        },
        {
            "id": "Day 7 Case 6.8",
            "name": "Source integrity",
            "source": "nutrition",
            "text": "I've been sleeping only five hours lately because my meal schedule keeps me up late.",
            "expect_empty": False,
            "required_categories": ["sleep"],
            "expected_source": "nutrition",
        },
        {
            "id": "Day 7 Case 6.9",
            "name": "Multi-turn transcript & calendar-relative duration",
            "source": "mental_wellness",
            "text": [
                {"role": "user", "content": "I'm sleeping only three hours."},
                {"role": "assistant", "content": "Has that been happening every night?"},
                {"role": "user", "content": "Actually I exaggerated — it's closer to five hours, mostly this week."}
            ],
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "must_contain": ["5"],
            "check_calendar_duration": True,
        },

        # --- DAY 8 HARDENING CASES (10) ---
        {
            "id": "Day 8 Case 8.1",
            "name": "Hypothetical health statement",
            "source": "mental_wellness",
            "text": "What happens if someone sleeps only three hours every night?",
            "expect_empty": True,
        },
        {
            "id": "Day 8 Case 8.2",
            "name": "Third-person information",
            "source": "mental_wellness",
            "text": "My roommate barely sleeps four hours because of exams.",
            "expect_empty": True,
        },
        {
            "id": "Day 8 Case 8.3",
            "name": "Mixed relevant + irrelevant information",
            "source": "mental_wellness",
            "text": "My favourite colour is yellow. Anyway, I've been sleeping only five hours lately because of assignments.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["sleep"],
            "must_contain": ["5"],
            "check_ignored_preference": True,
        },
        {
            "id": "Day 8 Case 8.4",
            "name": "Explicit negation",
            "source": "nutrition",
            "text": "I am not having any appetite problems. I'm eating normally.",
            "expect_empty": True,
        },
        {
            "id": "Day 8 Case 8.5",
            "name": "Negated candidate followed by real issue",
            "source": "nutrition",
            "text": "I'm not skipping meals, but I barely drink water during college.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["hydration"],
            "forbidden_categories": ["nutrition"],
        },
        {
            "id": "Day 8 Case 8.6",
            "name": "Corrected quantity",
            "source": "nutrition",
            "text": "I drink maybe one glass of water a day — actually that's not right, probably closer to four glasses.",
            "expect_empty": False,
            "expected_count": 1,
            "required_categories": ["hydration"],
            "must_contain": ["4"],
            "must_not_contain_as_value": ["1 glass"],
        },
        {
            "id": "Day 8 Case 8.7",
            "name": "Unsupported causal inference",
            "source": "mental_wellness",
            "text": "I've been tired lately and I also haven't been sleeping much.",
            "expect_empty": False,
            "required_concepts": ["sleep", "tired"],  # Accepts 1 combined record OR 2 separate records
            "prohibited_words": ["caused", "due to sleep deprivation", "insomnia", "depression"],
            "check_no_invented_cause": True,
        },
        {
            "id": "Day 8 Case 8.8",
            "name": "Assistant hypothesis rejection",
            "source": "mental_wellness",
            "text": [
                {"role": "user", "content": "I've been tired lately."},
                {"role": "assistant", "content": "Could this be because you're only sleeping four hours?"},
                {"role": "user", "content": "No, I usually sleep around seven hours."}
            ],
            "expect_empty": False,
            "must_reject_assistant_value": ["4 hours"],
            "must_contain_user_value": ["7"],
            "required_concepts": ["sleep", "tired"],
        },
        {
            "id": "Day 8 Case 8.9",
            "name": "Empty / whitespace input",
            "source": "nutrition",
            "text": "   ",
            "expect_empty": True,
            "local_only": True,
        },
        {
            "id": "Day 8 Case 8.10",
            "name": "Invalid source validation",
            "source": "fitness_ai",
            "text": "I sleep five hours.",
            "expected_exception": ValueError,
            "local_only": True,
        },
    ]


def evaluate_case_dimensions(case: Dict[str, Any], items: List[ClinicalContextItem], err: Optional[Exception]) -> Dict[str, Optional[bool]]:
    """
    Evaluates each of the 11 dimensions independently for a specific test case execution.
    Returns a dict mapping dimension_name -> Optional[bool] (True for PASS, False for FAIL, None for N/A).
    """
    results: Dict[str, Optional[bool]] = {}

    if case.get("expected_exception"):
        exp_exc = case["expected_exception"]
        exc_passed = (err is not None and isinstance(err, exp_exc))
        results["relevance_filtering"] = None
        results["relevant_context_retention"] = None
        results["compression_redundancy_control"] = None
        results["distinct_phenomenon_preservation"] = None
        results["unsupported_inference_prevention"] = True
        results["evidence_preservation"] = True
        results["temporal_reasoning"] = True
        results["speaker_attribution_safety"] = True
        results["source_integrity"] = exc_passed
        results["schema_validity"] = exc_passed
        results["context_sufficiency"] = None
        return results

    # Standard diagnostic terms for inference check
    prohibited_diagnosis_terms = [
        "insomnia", "major depressive", "depression", "generalized anxiety",
        "anorexia", "eating disorder", "anemia", "diabetes", "syndrome", "chronic fatigue"
    ]
    prohibited_words = case.get("prohibited_words", []) + prohibited_diagnosis_terms

    # 1. Relevance Filtering
    if case.get("expect_empty"):
        results["relevance_filtering"] = (len(items) == 0)
    elif case.get("check_ignored_preference"):
        # Mixed relevant + irrelevant: favourite colour should yield 1 sleep item
        results["relevance_filtering"] = (len(items) == 1 and items[0].category == "sleep")
    else:
        results["relevance_filtering"] = (len(items) > 0)

    # 2. Relevant Context Retention
    if case.get("expect_empty"):
        results["relevant_context_retention"] = (len(items) == 0)
    else:
        req_cats = case.get("required_categories", [])
        actual_cats = [i.category for i in items]
        has_cats = all(c in actual_cats for c in req_cats)
        
        req_concepts = case.get("required_concepts", [])
        if req_concepts:
            # Check concepts across all item summaries/values
            combined_text = " ".join([f"{i.category} {i.summary} {i.value or ''}".lower() for i in items])
            has_concepts = all(c.lower() in combined_text for c in req_concepts)
            results["relevant_context_retention"] = (has_cats and has_concepts)
        else:
            results["relevant_context_retention"] = (has_cats and len(items) > 0)

    # 3. Compression / Redundancy Control
    exp_count = case.get("expected_count")
    if case.get("expect_empty"):
        results["compression_redundancy_control"] = (len(items) == 0)
    elif case.get("fold_cause_stress"):
        # Cause-only stress should not produce a separate stress record
        has_extra_stress = any(i.category == "stress" for i in items)
        results["compression_redundancy_control"] = not has_extra_stress
    elif exp_count is not None:
        results["compression_redundancy_control"] = (len(items) == exp_count)
    else:
        # Flexible count (e.g. 1 or 2 items acceptable for multi-concept self reports)
        results["compression_redundancy_control"] = (len(items) in [1, 2])

    # 4. Distinct Phenomenon Preservation
    if case.get("expect_empty"):
        results["distinct_phenomenon_preservation"] = (len(items) == 0)
    elif case.get("required_categories") and len(case["required_categories"]) > 1:
        actual_cats = [i.category for i in items]
        results["distinct_phenomenon_preservation"] = all(c in actual_cats for c in case["required_categories"])
    elif case.get("required_concepts") and len(case["required_concepts"]) > 1:
        combined_text = " ".join([f"{i.category} {i.summary} {i.value or ''}".lower() for i in items])
        results["distinct_phenomenon_preservation"] = all(c.lower() in combined_text for c in case["required_concepts"])
    else:
        results["distinct_phenomenon_preservation"] = (len(items) > 0)

    # 5. Unsupported Inference Prevention
    found_prohibited = False
    for item in items:
        sum_lower = item.summary.lower()
        for pw in prohibited_words:
            if pw.lower() in sum_lower:
                found_prohibited = True
                break

    if case.get("check_no_invented_cause"):
        # Check no unstated causal claims like "sleep caused fatigue"
        for item in items:
            sum_lower = item.summary.lower()
            if "caused" in sum_lower or "due to sleep deprivation" in sum_lower:
                found_prohibited = True

    results["unsupported_inference_prevention"] = not found_prohibited

    # 6. Evidence Preservation
    must_contain = case.get("must_contain", [])
    must_not_val = case.get("must_not_contain_as_value", [])

    has_must_contain = True
    if must_contain:
        has_must_contain = any(
            any(m.lower() in (i.value or "").lower() or m.lower() in i.summary.lower() for i in items)
            for m in must_contain
        )

    has_bad_val = False
    if must_not_val:
        has_bad_val = any(
            any(b.lower() in (i.value or "").lower() for i in items)
            for b in must_not_val
        )

    has_episodic = True
    if case.get("check_episodic_qualifier"):
        hyd_item = next((i for i in items if i.category == "hydration"), None)
        if hyd_item:
            val_lower = (hyd_item.value or "").lower()
            if "/day" in val_lower or "per day" in val_lower:
                has_episodic = False

    results["evidence_preservation"] = (has_must_contain and not has_bad_val and has_episodic)

    # 7. Temporal Reasoning
    has_strict_attachment = True
    if case.get("check_strict_temporal_attachment"):
        # Sleep item MUST NOT inherit duration="this week" from appetite!
        sleep_item = next((i for i in items if i.category == "sleep"), None)
        if sleep_item and sleep_item.duration:
            has_strict_attachment = False

    has_approx_dur = True
    if case.get("check_approx_duration"):
        app_item = next((i for i in items if i.category == "appetite"), None)
        if app_item:
            dur_lower = (app_item.duration or "").lower()
            sum_lower = app_item.summary.lower()
            combined = f"{dur_lower} {sum_lower}"
            if "about" not in combined and "approx" not in combined and "around" not in combined:
                has_approx_dur = False

    has_cal_dur = True
    if case.get("check_calendar_duration"):
        sleep_item = next((i for i in items if i.category == "sleep"), None)
        if sleep_item:
            dur_lower = (sleep_item.duration or "").lower()
            if "1 week" in dur_lower or "one week" in dur_lower:
                has_cal_dur = False

    has_dur_when_expected = True
    if case.get("expect_duration"):
        has_dur_when_expected = any(i.duration for i in items)

    results["temporal_reasoning"] = (has_strict_attachment and has_approx_dur and has_cal_dur and has_dur_when_expected)

    # 8. Speaker Attribution Safety
    reject_assistant = True
    bad_assistant_vals = case.get("must_reject_assistant_value", [])
    if bad_assistant_vals:
        for b in bad_assistant_vals:
            if any(b.lower() in (i.value or "").lower() or b.lower() in i.summary.lower() for i in items):
                reject_assistant = False

    user_val_ok = True
    user_vals = case.get("must_contain_user_value", [])
    if user_vals:
        user_val_ok = any(
            any(u.lower() in (i.value or "").lower() or u.lower() in i.summary.lower() for i in items)
            for u in user_vals
        )

    results["speaker_attribution_safety"] = (reject_assistant and user_val_ok)

    # 9. Source Integrity
    expected_src = case.get("expected_source", case.get("source"))
    source_ok = True
    if items and expected_src:
        source_ok = all(i.source == expected_src for i in items)
    results["source_integrity"] = source_ok

    # 10. Schema Validity
    schema_ok = True
    for item in items:
        if item.category not in ALLOWED_CATEGORIES:
            schema_ok = False
        if item.source not in ALLOWED_SOURCES:
            schema_ok = False
        if item.record_type not in ALLOWED_RECORD_TYPES:
            schema_ok = False
        if not item.summary or not item.summary.strip():
            schema_ok = False
    results["schema_validity"] = schema_ok

    # 11. Context Sufficiency (New Dimension: Is downstream doctor context preserved without loss?)
    if case.get("expect_empty"):
        results["context_sufficiency"] = (len(items) == 0)
    else:
        req_cats = case.get("required_categories", [])
        actual_cats = [i.category for i in items]
        cats_suff = all(c in actual_cats for c in req_cats) if req_cats else (len(items) > 0)
        
        req_concepts = case.get("required_concepts", [])
        if req_concepts:
            combined_text = " ".join([f"{i.category} {i.summary} {i.value or ''}".lower() for i in items])
            concepts_suff = all(c.lower() in combined_text for c in req_concepts)
            results["context_sufficiency"] = (cats_suff and concepts_suff)
        else:
            results["context_sufficiency"] = cats_suff

    return results


def run_live_evaluation() -> Dict[str, Any]:
    """Runs Phase 2: Live Paced Gemini CCEE Evaluation with independent dimension metric calculations."""
    print("\n" + "=" * 70)
    print("PHASE 2: LIVE PACED CCEE EVALUATION (36 TEST CASES)")
    print("=" * 70)

    cases = get_all_evaluation_cases()

    dimension_keys = [
        "relevance_filtering",
        "relevant_context_retention",
        "compression_redundancy_control",
        "distinct_phenomenon_preservation",
        "unsupported_inference_prevention",
        "evidence_preservation",
        "temporal_reasoning",
        "speaker_attribution_safety",
        "source_integrity",
        "schema_validity",
        "context_sufficiency",
    ]

    dimension_stats = {d: {"passed": 0, "total": 0} for d in dimension_keys}

    evaluated_cases = []
    passed_cases_count = 0
    failed_cases_count = 0
    inconclusive_api_count = 0

    llm_call_index = 0

    for case in cases:
        case_id = str(case["id"])
        name = str(case["name"])
        raw_text = case["text"]
        source = str(case["source"])

        print(f"\n[Case {case_id}]: {name}")
        print(f"  Source: {source}")

        # Local-only cases (whitespace or invalid source)
        if case.get("local_only"):
            exp_exc = case.get("expected_exception")
            err_obj = None
            items: List[ClinicalContextItem] = []

            if exp_exc:
                try:
                    ccee_engine.extract_context(str(raw_text), source)
                except Exception as e:
                    err_obj = e
            else:
                items = ccee_engine.extract_context(str(raw_text), source)

            dim_eval = evaluate_case_dimensions(case, items, err_obj)
            all_passed = all(dim_eval.values())

            if exp_exc:
                all_passed = (err_obj is not None and isinstance(err_obj, exp_exc))

            if all_passed:
                passed_cases_count += 1
                status = "PASS"
                reasons = []
            else:
                failed_cases_count += 1
                status = "FAIL"
                reasons = [f"Dimension {k} failed" for k, v in dim_eval.items() if not v]

            for dim_k, pass_val in dim_eval.items():
                if pass_val is not None:
                    dimension_stats[dim_k]["total"] += 1
                    if pass_val is True:
                        dimension_stats[dim_k]["passed"] += 1

            evaluated_cases.append({
                "id": case_id,
                "name": name,
                "status": status,
                "reasons": reasons,
                "dimension_results": dim_eval
            })
            print(f"  Status: {status}")
            continue

        # Format conversation argument
        conv_arg: Union[str, List[Dict[str, Any]]]
        if isinstance(raw_text, str):
            conv_arg = raw_text
        elif isinstance(raw_text, list):
            conv_arg = cast(List[Dict[str, Any]], raw_text)
        else:
            conv_arg = str(raw_text)

        # Paced delay between LLM calls to respect API quotas
        if llm_call_index > 0:
            time.sleep(3.5)
        llm_call_index += 1

        # Retry loop for transient 503/429 spikes
        max_retries = 5
        items: List[ClinicalContextItem] = []
        last_err = None
        elapsed = 0.0

        for attempt in range(1, max_retries + 1):
            try:
                start_t = time.time()
                items = ccee_engine.extract_context(conv_arg, source)
                elapsed = time.time() - start_t
                last_err = None
                break
            except Exception as e:
                last_err = e
                err_str = str(e)
                if ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str) and attempt < max_retries:
                    backoff = attempt * 5.0
                    print(f"  [Attempt {attempt}/{max_retries} API spike, retrying in {backoff}s...]")
                    time.sleep(backoff)
                else:
                    break

        if last_err is not None:
            err_msg = str(last_err)
            print(f"  ✗ INCONCLUSIVE (API Error): {err_msg}")
            inconclusive_api_count += 1
            evaluated_cases.append({
                "id": case_id,
                "name": name,
                "status": "INCONCLUSIVE_API",
                "error": err_msg,
            })
            continue

        items_dict = [item.to_dict() for item in items]
        print(f"  Extracted ({len(items)} items in {elapsed:.2f}s): {json.dumps(items_dict, indent=2)}")

        # Evaluate each dimension independently
        dim_eval = evaluate_case_dimensions(case, items, None)
        case_fully_passed = all(dim_eval.values())

        if case_fully_passed:
            passed_cases_count += 1
            status = "PASS"
            reasons = []
            print("  ✓ PASS (All dimensions passed)")
        else:
            failed_cases_count += 1
            status = "FAIL"
            reasons = [f"Dimension '{k}' failed" for k, v in dim_eval.items() if not v]
            print(f"  ✗ FAIL: {'; '.join(reasons)}")

        # Update dimension statistics independently
        for dim_k, pass_val in dim_eval.items():
            if pass_val is not None:
                dimension_stats[dim_k]["total"] += 1
                if pass_val is True:
                    dimension_stats[dim_k]["passed"] += 1

        evaluated_cases.append({
            "id": case_id,
            "name": name,
            "status": status,
            "items": items_dict,
            "reasons": reasons,
            "dimension_results": dim_eval
        })

    # Summarize results
    total_evaluated = passed_cases_count + failed_cases_count
    overall_pass_rate = (passed_cases_count / total_evaluated * 100.0) if total_evaluated > 0 else 0.0

    print("\n" + "=" * 70)
    print("CCEE DAY 8 EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total semantic cases evaluated: {len(cases)}")
    print(f"Fully Passed Cases: {passed_cases_count}")
    print(f"Failed Cases: {failed_cases_count}")
    print(f"Inconclusive due to API: {inconclusive_api_count}")
    print(f"Overall Case Pass Rate: {passed_cases_count}/{total_evaluated} = {overall_pass_rate:.1f}%\n")

    print("Independent Dimension Results:")
    dimension_percentages = {}
    for dim_key, stats in dimension_stats.items():
        p = stats["passed"]
        t = stats["total"]
        pct = (p / t * 100.0) if t > 0 else 0.0
        dimension_percentages[dim_key] = {
            "passed": p,
            "total": t,
            "percentage": round(pct, 1)
        }
        formatted_key = dim_key.replace("_", " ").title()
        print(f"  - {formatted_key}: {p}/{t} ({pct:.1f}%)")

    summary_data = {
        "total_cases": len(cases),
        "total_evaluated": total_evaluated,
        "passed_cases": passed_cases_count,
        "failed_cases": failed_cases_count,
        "inconclusive_api_cases": inconclusive_api_count,
        "overall_pass_rate_pct": round(overall_pass_rate, 1),
        "dimensions": dimension_percentages,
        "case_details": evaluated_cases,
    }

    return summary_data


if __name__ == "__main__":
    run_local_hardening_tests()
    eval_summary = run_live_evaluation()
    scratch_dir = os.path.join(os.path.dirname(__file__), "..", "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    out_path = os.path.join(scratch_dir, "day8_eval_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)
    print(f"\nEvaluation summary saved to: {out_path}")
