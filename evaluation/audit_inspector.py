"""
Inspection Script for Pilot Scoring Audit
=========================================
Audits raw model outputs against gold standards and semantic matcher predictions.
"""

import json
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from evaluation.scoring import match_fact_in_text, normalize_text, extract_factual_claims

def run_inspection():
    with open("docs/evaluation/results/pilot_raw_outputs.jsonl", "r", encoding="utf-8") as f:
        raw_outputs = {(r["scenario_id"], r["condition"]): r for r in (json.loads(line) for line in f if line.strip())}

    with open("docs/evaluation/datasets/pcif_pilot_50.jsonl", "r", encoding="utf-8") as f:
        scenarios = {json.loads(line)["scenario_id"]: json.loads(line) for line in f if line.strip()}

    audit_scenario_ids = [
        "SCN-PILOT-005", "SCN-PILOT-034", "SCN-PILOT-035", "SCN-PILOT-036", "SCN-PILOT-037", "SCN-PILOT-038",  # 6 conflicts
        "SCN-PILOT-004", "SCN-PILOT-039", "SCN-PILOT-040", "SCN-PILOT-041", "SCN-PILOT-042",  # 5 irrelevant history
        "SCN-PILOT-048", "SCN-PILOT-049", "SCN-PILOT-050",  # 3 provenance sensitive
        "SCN-PILOT-001", "SCN-PILOT-002", "SCN-PILOT-003", "SCN-PILOT-046", "SCN-PILOT-047"   # 5 additional controls/cases
    ]

    print(f"Total audit scenarios: {len(audit_scenario_ids)}\n")

    false_positives = []
    false_negatives = []
    distractor_audit_examples = []

    for sc_id in audit_scenario_ids:
        sc = scenarios[sc_id]
        print("="*80)
        print(f"SCENARIO: {sc_id} | Domain: {sc['domain']} | Difficulty: {sc['difficulty']}")
        print(f"Consultation: {sc['current_consultation']['text']}")
        
        # Build lookup of all facts
        f_map = {}
        for f in sc.get("patient_reported_current_context", []) + sc.get("patient_reported_longitudinal_history", []):
            f_map[f["fact_id"]] = f
        for f in sc.get("clinician_authored_history", []):
            f_map[f["fact_id"]] = f

        print(f"Gold Relevant Facts: {sc['gold_evidence']['relevant_fact_ids']}")
        for r_id in sc['gold_evidence']['relevant_fact_ids']:
            f_obj = f_map.get(r_id, {})
            print(f"   {r_id}: {f_obj.get('summary') or f_obj.get('note')} (val: {f_obj.get('value')}, dur: {f_obj.get('duration')})")
            
        print(f"Gold Irrelevant Facts: {sc['gold_evidence']['irrelevant_fact_ids']}")
        for ir_id in sc['gold_evidence']['irrelevant_fact_ids']:
            f_obj = f_map.get(ir_id, {})
            print(f"   {ir_id}: {f_obj.get('summary') or f_obj.get('note')} (val: {f_obj.get('value')}, dur: {f_obj.get('duration')})")

        print(f"Gold Conflicts: {sc['gold_evidence']['conflict_groups']}")

        # Examine PCIF output
        pcif_record = raw_outputs.get((sc_id, "pcif"), {})
        pcif_resp = pcif_record.get("assistant_response", {})
        pcif_full_text = " ".join([
            pcif_resp.get("context_summary", ""),
            " ".join(pcif_resp.get("relevant_current_context", [])),
            " ".join(pcif_resp.get("relevant_longitudinal_changes", [])),
            " ".join(pcif_resp.get("relevant_clinician_notes", [])),
            " ".join(pcif_resp.get("items_to_verify", []))
        ])

        print("\n--- PCIF Structured Response ---")
        print(f"  Summary: {pcif_resp.get('context_summary')}")
        print(f"  Current Context: {pcif_resp.get('relevant_current_context')}")
        print(f"  Longitudinal: {pcif_resp.get('relevant_longitudinal_changes')}")
        print(f"  Clinician Notes: {pcif_resp.get('relevant_clinician_notes')}")
        print(f"  Verify Items: {pcif_resp.get('items_to_verify')}")

        # Check fact match predictions
        print("\n--- Match Predictions for PCIF ---")
        for fid, f_obj in f_map.items():
            matched = match_fact_in_text(f_obj, pcif_full_text)
            is_relevant = fid in sc['gold_evidence']['relevant_fact_ids']
            is_irrelevant = fid in sc['gold_evidence']['irrelevant_fact_ids']
            
            f_text = f_obj.get("summary") or f_obj.get("note")
            
            # Check manual alignment
            # Look if f_text key concepts are actually in pcif_full_text
            print(f"   Fact {fid} ({'RELEVANT' if is_relevant else 'IRRELEVANT'}): matched={matched} | text='{f_text}'")
            
            if is_irrelevant:
                distractor_audit_examples.append({
                    "scenario_id": sc_id,
                    "fact_id": fid,
                    "fact_text": f_text,
                    "matched": matched,
                    "in_pcif_output": any(w in pcif_full_text.lower() for w in normalize_text(f_text).split() if len(w) > 4)
                })

        # Examine Baseline output
        base_record = raw_outputs.get((sc_id, "baseline"), {})
        base_resp = base_record.get("assistant_response", {})
        base_full_text = " ".join([
            base_resp.get("context_summary", ""),
            " ".join(base_resp.get("relevant_current_context", [])),
            " ".join(base_resp.get("relevant_longitudinal_changes", [])),
            " ".join(base_resp.get("relevant_clinician_notes", [])),
            " ".join(base_resp.get("items_to_verify", []))
        ])

        print("\n--- BASELINE Structured Response ---")
        print(f"  Summary: {base_resp.get('context_summary')}")
        print(f"  Current Context: {base_resp.get('relevant_current_context')}")
        print(f"  Longitudinal: {base_resp.get('relevant_longitudinal_changes')}")
        print(f"  Clinician Notes: {base_resp.get('relevant_clinician_notes')}")
        print(f"  Verify Items: {base_resp.get('items_to_verify')}")

if __name__ == "__main__":
    run_inspection()
