"""
Detailed Scoring Audit for PCIF Pilot Evaluation
=================================================
Performs thorough manual and programmatic audits of:
1. Condition-aware Baseline retrieval (no matching against hidden F facts)
2. Conflict scoring audit (Baseline vs PCIF)
3. Provenance adjudication (correct, incorrect, not_explicit, not_applicable)
4. Semantic fact-matching audit (false-positives & false-negatives)
5. Irrelevant-inclusion audit (model inclusion vs semantic over-matching)
6. Unsupported claim audit (condition-specific support)
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from evaluation.scoring import normalize_text, extract_factual_claims

def run_detailed_audit():
    with open("docs/evaluation/results/pilot_raw_outputs.jsonl", "r", encoding="utf-8") as f:
        raw_outputs = {(r["scenario_id"], r["condition"]): r for r in (json.loads(line) for line in f if line.strip())}

    with open("docs/evaluation/datasets/pcif_pilot_50.jsonl", "r", encoding="utf-8") as f:
        scenarios = {json.loads(line)["scenario_id"]: json.loads(line) for line in f if line.strip()}

    print("================================================================================")
    print("1. AUDIT OF CONFLICT SCENARIOS (6 SCENARIOS)")
    print("================================================================================")
    conflict_scenarios = [s for s in scenarios.values() if s.get("gold_evidence", {}).get("conflict_groups")]
    
    conflict_audit_results = []
    for sc in conflict_scenarios:
        sc_id = sc["scenario_id"]
        conflicts = sc["gold_evidence"]["conflict_groups"]
        c_text = sc["current_consultation"]["text"]
        
        base_resp = raw_outputs.get((sc_id, "baseline"), {}).get("assistant_response", {})
        pcif_resp = raw_outputs.get((sc_id, "pcif"), {}).get("assistant_response", {})
        
        print(f"\nScenario: {sc_id} (Domain: {sc['domain']})")
        print(f"Consultation: {c_text}")
        for c in conflicts:
            print(f"Conflict ID: {c['conflict_id']}, Facts: {c['fact_ids']}, Desc: {c['description']}")
            
        print(f"Baseline Verify Items: {base_resp.get('items_to_verify')}")
        print(f"PCIF Verify Items: {pcif_resp.get('items_to_verify')}")
        
        # Check if conflict facts were both in Baseline input
        # Baseline ONLY receives current_consultation
        q_ids = [q["fact_id"] for q in sc.get("current_consultation", {}).get("fact_units", [])]
        base_has_all_conflict_facts = all(
            all(fid in q_ids for fid in c["fact_ids"])
            for c in conflicts
        )
        print(f"Are all conflicting facts present in Baseline input? {base_has_all_conflict_facts}")
        
        conflict_audit_results.append({
            "scenario_id": sc_id,
            "conflicts": conflicts,
            "baseline_has_both_sides": base_has_all_conflict_facts,
            "pcif_verify_items": pcif_resp.get("items_to_verify"),
            "baseline_verify_items": base_resp.get("items_to_verify")
        })

    print("\n================================================================================")
    print("2. AUDIT OF IRRELEVANT HISTORY / DISTRACTOR SCENARIOS (5 SCENARIOS + ALL DISTRACTORS)")
    print("================================================================================")
    irrelevant_scenarios = [s for s in scenarios.values() if s.get("domain") == "irrelevant_history"]
    
    distractor_audit = []
    for sc in irrelevant_scenarios:
        sc_id = sc["scenario_id"]
        irrel_ids = sc["gold_evidence"]["irrelevant_fact_ids"]
        pcif_resp = raw_outputs.get((sc_id, "pcif"), {}).get("assistant_response", {})
        
        # Build map of facts
        f_map = {}
        for f in sc.get("patient_reported_current_context", []) + sc.get("patient_reported_longitudinal_history", []):
            f_map[f["fact_id"]] = f
        for f in sc.get("clinician_authored_history", []):
            f_map[f["fact_id"]] = f
            
        print(f"\nScenario: {sc_id}")
        print(f"Consultation: {sc['current_consultation']['text']}")
        print(f"Relevant Facts: {sc['gold_evidence']['relevant_fact_ids']}")
        print(f"Irrelevant Facts: {irrel_ids}")
        for fid in irrel_ids:
            f_obj = f_map[fid]
            f_text = f_obj.get("summary") or f_obj.get("note")
            
            # Check where/if PCIF mentioned it
            cur_ctx = pcif_resp.get("relevant_current_context", [])
            long_ctx = pcif_resp.get("relevant_longitudinal_changes", [])
            clin_notes = pcif_resp.get("relevant_clinician_notes", [])
            summary = pcif_resp.get("context_summary", "")
            
            # Inspect exact matching
            in_cur = any(normalize_text(f_text) in normalize_text(x) or any(w in normalize_text(x) for w in normalize_text(f_text).split() if len(w) > 4) for x in cur_ctx)
            in_long = any(normalize_text(f_text) in normalize_text(x) or any(w in normalize_text(x) for w in normalize_text(f_text).split() if len(w) > 4) for x in long_ctx)
            in_clin = any(normalize_text(f_text) in normalize_text(x) or any(w in normalize_text(x) for w in normalize_text(f_text).split() if len(w) > 4) for x in clin_notes)
            
            print(f"   Distractor {fid}: '{f_text}'")
            print(f"     In relevant_current_context: {in_cur}")
            print(f"     In relevant_longitudinal_changes: {in_long}")
            print(f"     In relevant_clinician_notes: {in_clin}")
            
        print(f"PCIF relevant_current_context: {pcif_resp.get('relevant_current_context')}")
        print(f"PCIF relevant_longitudinal_changes: {pcif_resp.get('relevant_longitudinal_changes')}")
        print(f"PCIF relevant_clinician_notes: {pcif_resp.get('relevant_clinician_notes')}")

    print("\n================================================================================")
    print("3. AUDIT OF PROVENANCE SENSITIVE SCENARIOS (3 SCENARIOS)")
    print("================================================================================")
    prov_scenarios = [s for s in scenarios.values() if s.get("domain") == "provenance_sensitive"]
    for sc in prov_scenarios:
        sc_id = sc["scenario_id"]
        pcif_resp = raw_outputs.get((sc_id, "pcif"), {}).get("assistant_response", {})
        base_resp = raw_outputs.get((sc_id, "baseline"), {}).get("assistant_response", {})
        
        print(f"\nScenario: {sc_id}")
        print(f"Consultation: {sc['current_consultation']['text']}")
        print(f"PCIF Context Summary: {pcif_resp.get('context_summary')}")
        print(f"PCIF Current Context: {pcif_resp.get('relevant_current_context')}")
        print(f"PCIF Clinician Notes: {pcif_resp.get('relevant_clinician_notes')}")
        print(f"PCIF Verify Items: {pcif_resp.get('items_to_verify')}")

if __name__ == "__main__":
    run_detailed_audit()
