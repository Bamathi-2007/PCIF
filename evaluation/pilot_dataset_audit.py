"""
PCIF Pilot Dataset Coverage and Audit Tool
===========================================
Performs a comprehensive scenario-level coverage audit and duplicate detection
over the 50 pilot scenarios in docs/evaluation/datasets/pcif_pilot_50.jsonl.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, Any, List

def run_pilot_dataset_audit(dataset_path: str = "docs/evaluation/datasets/pcif_pilot_50.jsonl") -> Dict[str, Any]:
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at {path}")

    scenarios = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                scenarios.append(json.loads(line))

    total_scenarios = len(scenarios)

    # Coverage metrics
    with_patient_reported = 0
    with_clinician_authored = 0
    with_both_sources = 0
    with_longitudinal_superseded = 0
    with_irrelevant_distractors = 0
    with_conflict_groups = 0
    sparse_history_count = 0
    no_history_count = 0

    domain_counts = Counter()
    difficulty_counts = Counter()

    consultation_texts = defaultdict(list)
    historical_summaries = defaultdict(list)

    total_hist_facts = 0
    total_relevant_facts = 0
    total_irrelevant_facts = 0
    total_conflict_groups = 0

    for idx, s in enumerate(scenarios):
        sc_id = s.get("scenario_id", f"INDEX-{idx}")
        domain = s.get("domain", "unknown")
        difficulty = s.get("difficulty", "unknown")

        domain_counts[domain] += 1
        difficulty_counts[difficulty] += 1

        if domain == "sparse_history":
            sparse_history_count += 1
        elif domain == "no_history":
            no_history_count += 1

        # Sources
        cur_ctx = s.get("patient_reported_current_context", [])
        long_ctx = s.get("patient_reported_longitudinal_history", [])
        clin_notes = s.get("clinician_authored_history", [])

        has_pr = len(cur_ctx) > 0 or len(long_ctx) > 0
        has_ca = len(clin_notes) > 0

        if has_pr:
            with_patient_reported += 1
        if has_ca:
            with_clinician_authored += 1
        if has_pr and has_ca:
            with_both_sources += 1

        # Longitudinal / superseded
        has_long_or_super = (len(long_ctx) > 0) or any(f.get("status") == "superseded" for f in (cur_ctx + long_ctx))
        if has_long_or_super:
            with_longitudinal_superseded += 1

        # Gold evidence
        gold = s.get("gold_evidence", {})
        rel_ids = gold.get("relevant_fact_ids", [])
        irrel_ids = gold.get("irrelevant_fact_ids", [])
        conflicts = gold.get("conflict_groups", [])

        if len(irrel_ids) > 0:
            with_irrelevant_distractors += 1
        if len(conflicts) > 0:
            with_conflict_groups += 1

        total_hist_facts += (len(cur_ctx) + len(long_ctx) + len(clin_notes))
        total_relevant_facts += len(rel_ids)
        total_irrelevant_facts += len(irrel_ids)
        total_conflict_groups += len(conflicts)

        # Duplicate checking
        c_text = s.get("current_consultation", {}).get("text", "").strip()
        if c_text:
            consultation_texts[c_text].append(sc_id)

        for f_item in cur_ctx + long_ctx:
            summary = f_item.get("summary", "").strip()
            if summary:
                historical_summaries[summary].append((sc_id, f_item.get("fact_id")))

        for n_item in clin_notes:
            note = n_item.get("note", "").strip()
            if note:
                historical_summaries[note].append((sc_id, n_item.get("fact_id")))

    # Duplicates
    duplicate_consultations = {k: v for k, v in consultation_texts.items() if len(v) > 1}
    duplicate_summaries = {k: v for k, v in historical_summaries.items() if len(v) > 1}

    report = {
        "dataset_path": dataset_path,
        "total_scenarios": total_scenarios,
        "coverage": {
            "scenarios_with_patient_reported_context": with_patient_reported,
            "scenarios_with_clinician_authored_history": with_clinician_authored,
            "scenarios_with_both_sources": with_both_sources,
            "scenarios_with_longitudinal_superseded_history": with_longitudinal_superseded,
            "scenarios_with_irrelevant_distractor_facts": with_irrelevant_distractors,
            "scenarios_with_conflict_groups": with_conflict_groups,
            "sparse_history_scenarios": sparse_history_count,
            "no_history_scenarios": no_history_count,
            "sparse_or_no_history_total": sparse_history_count + no_history_count
        },
        "domain_distribution": dict(domain_counts),
        "difficulty_distribution": dict(difficulty_counts),
        "fact_totals": {
            "total_historical_facts": total_hist_facts,
            "total_relevant_facts": total_relevant_facts,
            "total_irrelevant_facts": total_irrelevant_facts,
            "total_conflict_groups": total_conflict_groups
        },
        "duplicate_audit": {
            "exact_duplicate_consultations_count": len(duplicate_consultations),
            "exact_duplicate_consultations": duplicate_consultations,
            "exact_duplicate_historical_items_count": len(duplicate_summaries),
            "exact_duplicate_historical_items": duplicate_summaries
        }
    }
    return report

if __name__ == "__main__":
    rep = run_pilot_dataset_audit()
    print(json.dumps(rep, indent=2))
