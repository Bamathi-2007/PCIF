"""
Day 6 CCEE Test Suite - Redundancy Reduction & Minimum-Sufficient Context Compression.

Runs:
1. Local Schema, Contract, and Deterministic Deduplication Tests (No LLM calls)
2. Live Conservative Gemini CCEE Evaluation (Paced calls with rate-limit protection)
   Validates:
   - Case 1: Exact/repeated sleep meaning -> exactly 1 sleep item
   - Case 2: Stress as context, not independent record -> 1 sleep item folding exam stress
   - Case 3: Two genuinely distinct phenomena -> 2 items: sleep + appetite
   - Case 4: Repeated nutrition meaning -> exactly 1 nutrition item
   - Case 5: Related hydration repetition -> exactly 1 hydration item
   - Case 6: Independent stress with functional impact -> 2 items: stress + sleep
   - Case 7: Irrelevant repetition -> empty list []
"""

import os
import sys
import time
import json
from typing import List, Dict, Any

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


def run_local_contract_tests():
    print("\n" + "=" * 60)
    print("PHASE 1: DAY 6 LOCAL CONTRACT & DEDUPLICATION TESTS (NO LLM)")
    print("=" * 60)

    # 1. Deterministic deduplication of verbatim identical items
    dup_item1 = ClinicalContextItem(
        category="sleep",
        summary="Reduced sleep associated with exam stress",
        source="mental_wellness",
        value="5 hours/night"
    )
    dup_item2 = ClinicalContextItem(
        category="sleep",
        summary="Reduced sleep associated with exam stress",
        source="mental_wellness",
        value="5 hours/night"
    )
    deduped = ClinicalContextExtractionEngine._deduplicate_items([dup_item1, dup_item2])
    assert len(deduped) == 1
    assert deduped[0].summary == "Reduced sleep associated with exam stress"
    print("✓ Test 1 Passed: Verbatim duplicates reduced to single item")

    # 2. Case-insensitive summary deduplication with value enrichment
    item_base = ClinicalContextItem(
        category="nutrition",
        summary="Regularly skips breakfast",
        source="nutrition"
    )
    item_rich = ClinicalContextItem(
        category="nutrition",
        summary="regularly skips breakfast",
        source="nutrition",
        duration="1 week"
    )
    deduped_rich = ClinicalContextExtractionEngine._deduplicate_items([item_base, item_rich])
    assert len(deduped_rich) == 1
    assert deduped_rich[0].duration == "1 week"
    print("✓ Test 2 Passed: Deduplication preserves richer duration/value")

    # 3. Distinct categories are preserved
    sleep_item = ClinicalContextItem(
        category="sleep",
        summary="Reduced sleep",
        source="mental_wellness"
    )
    appetite_item = ClinicalContextItem(
        category="appetite",
        summary="Reduced appetite",
        source="mental_wellness"
    )
    distinct = ClinicalContextExtractionEngine._deduplicate_items([sleep_item, appetite_item])
    assert len(distinct) == 2
    print("✓ Test 3 Passed: Distinct categories preserved without over-merging")

    # 4. Frozen schema validation
    item = ClinicalContextItem(
        category="hydration",
        summary="Low water intake",
        source="nutrition",
        record_type="patient_reported",
        value="1 glass/day"
    )
    d = item.to_dict()
    assert d["category"] == "hydration"
    assert d["summary"] == "Low water intake"
    assert d["source"] == "nutrition"
    assert d["record_type"] == "patient_reported"
    assert d["value"] == "1 glass/day"
    assert "duration" not in d
    print("✓ Test 4 Passed: Frozen schema fields and serialization intact")

    # 5. Invalid category rejection
    try:
        ClinicalContextItem(category="unknown_cat", summary="Test", source="nutrition")
        assert False, "Should raise ValueError for invalid category"
    except ValueError as ve:
        assert "Invalid category" in str(ve)
        print("✓ Test 5 Passed: Invalid category properly rejected")

    # 6. Invalid source rejection
    try:
        ClinicalContextItem(category="sleep", summary="Test", source="invalid_src")
        assert False, "Should raise ValueError for invalid source"
    except ValueError as ve:
        assert "Invalid source" in str(ve)
        print("✓ Test 6 Passed: Invalid source properly rejected")

    # 7. Empty whitespace conversation
    empty = ccee_engine.extract_context("   \n\t  ", "nutrition")
    assert empty == []
    print("✓ Test 7 Passed: Whitespace conversation produces empty list []")


def run_live_gemini_day6_tests():
    print("\n" + "=" * 60)
    print("PHASE 2: LIVE GEMINI DAY 6 COMPRESSION EVALUATION (PACED)")
    print("=" * 60)

    # 7 Day 6 Synthetic Test Cases
    day6_cases = [
        {
            "id": "Day 6 Case 1",
            "name": "Exact/repeated sleep meaning",
            "source": "mental_wellness",
            "text": (
                "I've been sleeping only five hours lately. "
                "Most nights I get about five hours because I'm studying late. "
                "My sleep has definitely reduced."
            ),
            "expected_count": 1,
            "expected_categories": ["sleep"],
            "must_contain_in_any": ["5"],
        },
        {
            "id": "Day 6 Case 2",
            "name": "Stress as context, not independent record",
            "source": "mental_wellness",
            "text": "I'm stressed about my exams and because of that I'm sleeping only four hours every night.",
            "expected_count": 1,
            "expected_categories": ["sleep"],
            "must_contain_in_any": ["4"],
            "forbidden_categories": ["stress"],
        },
        {
            "id": "Day 6 Case 3",
            "name": "Two genuinely distinct phenomena",
            "source": "mental_wellness",
            "text": "I'm sleeping only four hours and I've also lost my appetite this week.",
            "expected_count": 2,
            "expected_categories": ["sleep", "appetite"],
        },
        {
            "id": "Day 6 Case 4",
            "name": "Repeated nutrition meaning",
            "source": "nutrition",
            "text": (
                "I keep skipping breakfast. "
                "I usually don't eat anything in the morning before college. "
                "Most weekdays I leave without breakfast because my first class is early."
            ),
            "expected_count": 1,
            "expected_categories": ["nutrition"],
        },
        {
            "id": "Day 6 Case 5",
            "name": "Related hydration repetition",
            "source": "nutrition",
            "text": (
                "I forget to drink water at college. "
                "Some days I only drink one glass. "
                "I stay busy and hardly drink water until evening."
            ),
            "expected_count": 1,
            "expected_categories": ["hydration"],
            "must_contain_in_any": ["1", "one", "glass"],
        },
        {
            "id": "Day 6 Case 6",
            "name": "Independent stress should remain",
            "source": "mental_wellness",
            "text": (
                "I feel overwhelmed throughout the entire day because of exams. "
                "I can't concentrate on normal tasks. "
                "I'm also sleeping around four hours at night."
            ),
            "expected_count": 2,
            "expected_categories": ["stress", "sleep"],
        },
        {
            "id": "Day 6 Case 7",
            "name": "Irrelevant repetition",
            "source": "nutrition",
            "text": (
                "Hi. "
                "Hello again. "
                "By the way my favourite colour is yellow. "
                "I really like yellow."
            ),
            "expected_count": 0,
            "expected_categories": [],
        },
    ]

    prohibited_diagnosis_terms = [
        "insomnia", "major depressive", "depression", "generalized anxiety",
        "anorexia", "eating disorder", "anemia", "diabetes", "syndrome", "chronic fatigue"
    ]

    results = []

    for i, case in enumerate(day6_cases):
        case_id = str(case["id"])
        name = str(case["name"])
        text = str(case["text"])
        source = str(case["source"])

        print(f"\nEvaluating {case_id}: {name}")
        print(f"  Source: {source}")
        print(f"  Input: \"{text}\"")

        # Paced delay between calls to respect Gemini quota
        if i > 0:
            time.sleep(3.5)

        # Retry loop for transient 503/429 Gemini API server spikes
        max_retries = 5
        items: List[ClinicalContextItem] = []
        last_err = None
        elapsed = 0.0

        for attempt in range(1, max_retries + 1):
            try:
                start_t = time.time()
                items = ccee_engine.extract_context(text, source)
                elapsed = time.time() - start_t
                last_err = None
                break
            except Exception as e:
                last_err = e
                err_str = str(e)
                if ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str) and attempt < max_retries:
                    backoff = attempt * 5.0
                    print(f"  [Attempt {attempt}/{max_retries} 503/429 spike, retrying in {backoff}s...]")
                    time.sleep(backoff)
                else:
                    break

        if last_err is not None:
            err = str(last_err)
            print(f"  ✗ ERROR: {err}")
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "503" in err or "UNAVAILABLE" in err:
                status = "RATE_LIMITED_OR_UNAVAILABLE"
            else:
                status = "ERROR"
            results.append({
                "id": case_id,
                "name": name,
                "status": status,
                "error": err,
            })
            continue

        items_dict = [item.to_dict() for item in items]
        print(f"  Extracted ({len(items)} items in {elapsed:.2f}s): {json.dumps(items_dict, indent=2)}")

        # Assertions / Checks
        checks_passed = True
        failure_reasons = []

        # 1. Item count check
        expected_count = case.get("expected_count", 0)
        if len(items) != expected_count:
            checks_passed = False
            failure_reasons.append(f"Expected {expected_count} items, got {len(items)}")

        # 2. Categories check
        actual_categories = [item.category for item in items]
        exp_cat_raw = case.get("expected_categories", [])
        expected_categories: List[str] = exp_cat_raw if isinstance(exp_cat_raw, list) else []
        for exp_cat in expected_categories:
            if exp_cat not in actual_categories:
                checks_passed = False
                failure_reasons.append(f"Expected category '{exp_cat}' not found in {actual_categories}")

        # 3. Forbidden categories check
        forb_cat_raw = case.get("forbidden_categories", [])
        forbidden: List[str] = forb_cat_raw if isinstance(forb_cat_raw, list) else []
        for forb_cat in forbidden:
            if forb_cat in actual_categories:
                checks_passed = False
                failure_reasons.append(f"Forbidden category '{forb_cat}' was extracted")

        # 4. Check expected text markers (value/summary)
        must_contain_raw = case.get("must_contain_in_any", [])
        must_contain: List[str] = must_contain_raw if isinstance(must_contain_raw, list) else []
        if must_contain:
            found_any = False
            for marker in must_contain:
                if isinstance(marker, str) and any(
                    marker.lower() in (item.value or "").lower() or marker.lower() in item.summary.lower()
                    for item in items
                ):
                    found_any = True
                    break
            if not found_any:
                checks_passed = False
                failure_reasons.append(f"None of expected markers {must_contain} found in items")

        # 5. Check prohibited diagnosis terms
        found_prohibited = []
        for item in items:
            summary_lower = item.summary.lower()
            for pw in prohibited_diagnosis_terms:
                if pw in summary_lower:
                    found_prohibited.append(pw)
        if found_prohibited:
            checks_passed = False
            failure_reasons.append(f"Prohibited diagnosis terms inferred: {found_prohibited}")

        # 6. Specific evidence-preservation check: Case 3 Temporal Attachment
        if case_id == "Day 6 Case 3":
            sleep_item = next((i for i in items if i.category == "sleep"), None)
            if sleep_item and sleep_item.duration:
                checks_passed = False
                failure_reasons.append(f"Sleep item wrongly inherited duration '{sleep_item.duration}' from appetite")
            appetite_item = next((i for i in items if i.category == "appetite"), None)
            if appetite_item and not appetite_item.duration:
                checks_passed = False
                failure_reasons.append("Appetite item missing supported duration '1 week'")

        # 7. Specific evidence-preservation check: Case 5 Hydration Uncertainty
        if case_id == "Day 6 Case 5":
            hyd_item = next((i for i in items if i.category == "hydration"), None)
            if hyd_item:
                val_lower = (hyd_item.value or "").lower()
                sum_lower = hyd_item.summary.lower()
                combined = f"{val_lower} {sum_lower}"
                if "/day" in val_lower or "per day" in val_lower:
                    checks_passed = False
                    failure_reasons.append(f"Hydration over-stated episodic report as absolute daily frequency: value='{hyd_item.value}'")
                elif "some days" not in combined and "as little as" not in combined and "occasionally" not in combined and "sometimes" not in combined:
                    checks_passed = False
                    failure_reasons.append(f"Hydration lost episodic qualifier ('some days'): value='{hyd_item.value}', summary='{hyd_item.summary}'")

        if checks_passed:
            status = "PASS"
            print(f"  ✓ PASS: Semantic compression and constraints verified.")
        else:
            status = "FAIL"
            print(f"  ✗ FAIL: {'; '.join(failure_reasons)}")

        results.append({
            "id": case_id,
            "name": name,
            "status": status,
            "items": items_dict,
            "reasons": failure_reasons
        })

    print("\n" + "=" * 60)
    print("DAY 6 LIVE EVALUATION SUMMARY:")
    print("=" * 60)
    for r in results:
        status_symbol = "✓" if r["status"] == "PASS" else "✗"
        print(f"{status_symbol} {r['id']} ({r['name']}): {r['status']}")

    return results


if __name__ == "__main__":
    run_local_contract_tests()
    run_live_gemini_day6_tests()
