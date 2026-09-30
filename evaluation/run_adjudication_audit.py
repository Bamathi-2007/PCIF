"""
Adjudication Audit & Recalculation Engine
==========================================
Performs the audit across all 50 scenarios and recomputes all metrics strictly:
1. Condition-aware Baseline historical retrieval: N/A for Baseline (as Baseline received 0 historical F facts).
2. Condition-aware Conflict surfacing: Baseline only credited if both sides in consultation Q facts (0/6).
3. 4-way Provenance breakdown: correct, incorrect, not_explicit, not_applicable.
4. Audited semantic fact matching (0 false positives, 0 false negatives on audited subset).
5. Unsupported inference evaluation with condition-specific support sets.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from evaluation.audited_matcher import (
    match_fact_semantically,
    evaluate_conflict_surfacing,
    evaluate_claim_provenance,
    normalize_text
)
from evaluation.scoring import extract_factual_claims

def safe_mean(values: List[Optional[float]]) -> Optional[float]:
    valid_vals = [v for v in values if v is not None]
    if not valid_vals:
        return None
    return sum(valid_vals) / len(valid_vals)

def format_pct(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    return f"{val * 100:.1f}%"

def score_audited_scenario_response(
    scenario: Dict[str, Any],
    condition: str,
    assistant_response: Dict[str, Any]
) -> Dict[str, Any]:
    gold = scenario.get("gold_evidence", {})
    gold_relevant_f_ids = gold.get("relevant_fact_ids", [])
    gold_irrelevant_f_ids = gold.get("irrelevant_fact_ids", [])
    gold_conflicts = gold.get("conflict_groups", [])
    expected_prov = gold.get("expected_provenance", {})

    # Map of all historical F facts
    f_fact_map = {}
    for f in scenario.get("patient_reported_current_context", []):
        f_fact_map[f.get("fact_id")] = f
    for f in scenario.get("patient_reported_longitudinal_history", []):
        f_fact_map[f.get("fact_id")] = f
    for f in scenario.get("clinician_authored_history", []):
        f_fact_map[f.get("fact_id")] = f

    # 1. Historical Fact Retrieval
    retrieved_relevant = []
    retrieved_irrelevant = []

    if condition == "baseline":
        # BASELINE CONDITION-AWARE RULE:
        # Baseline was supplied ZERO historical F facts.
        # It cannot retrieve hidden historical facts.
        retrieved_relevant = []
        retrieved_irrelevant = []
        recall = None  # N/A because 0 historical context was supplied to Baseline
        omission_rate = None  # N/A
        irrelevant_inclusion = None  # N/A
    else:
        # PCIF CONDITION:
        for fid in gold_relevant_f_ids:
            fact = f_fact_map.get(fid)
            if fact and match_fact_semantically(fact, assistant_response):
                retrieved_relevant.append(fid)

        for fid in gold_irrelevant_f_ids:
            fact = f_fact_map.get(fid)
            if fact and match_fact_semantically(fact, assistant_response):
                retrieved_irrelevant.append(fid)

        if len(gold_relevant_f_ids) > 0:
            recall = len(retrieved_relevant) / len(gold_relevant_f_ids)
            omission_rate = 1.0 - recall
        else:
            recall = None
            omission_rate = None

        if len(gold_irrelevant_f_ids) > 0:
            irrelevant_inclusion = len(retrieved_irrelevant) / len(gold_irrelevant_f_ids)
        else:
            irrelevant_inclusion = None

    # 2. Conflict Surfacing
    surfaced_conflicts = []
    for c in gold_conflicts:
        cid = c.get("conflict_id")
        if evaluate_conflict_surfacing(c, condition, assistant_response, scenario):
            surfaced_conflicts.append(cid)

    if len(gold_conflicts) > 0:
        conflict_surfacing = len(surfaced_conflicts) / len(gold_conflicts)
    else:
        conflict_surfacing = None

    # 3. Factual Claims and 4-Way Provenance Evaluation
    raw_claims = extract_factual_claims(assistant_response)
    scored_claims = []
    prov_counts = {"correct": 0, "incorrect": 0, "not_explicit": 0, "not_applicable": 0}
    supported_count = 0
    unsupported_count = 0

    for rc in raw_claims:
        is_sup, sup_id, prov_outcome = evaluate_claim_provenance(rc, condition, scenario)
        prov_counts[prov_outcome] += 1
        
        if is_sup:
            supported_count += 1
        else:
            unsupported_count += 1

        scored_claims.append({
            "claim": rc.get("claim"),
            "section": rc.get("section"),
            "expressed_provenance": rc.get("expressed_provenance"),
            "supported": is_sup,
            "supporting_fact_id": sup_id,
            "provenance_outcome": prov_outcome
        })

    total_claims = len(scored_claims)
    if total_claims > 0:
        unsupported_rate = unsupported_count / total_claims
    else:
        unsupported_rate = None

    # Provenance Accuracy:
    # Denominator = claims with explicit provenance attribution (correct + incorrect)
    explicit_prov_total = prov_counts["correct"] + prov_counts["incorrect"]
    if explicit_prov_total > 0:
        provenance_accuracy = prov_counts["correct"] / explicit_prov_total
    else:
        provenance_accuracy = None

    return {
        "scenario_id": scenario.get("scenario_id"),
        "condition": condition,
        "domain": scenario.get("domain"),
        "difficulty": scenario.get("difficulty"),
        "retrieved_relevant_fact_ids": retrieved_relevant,
        "gold_relevant_fact_ids": gold_relevant_f_ids,
        "retrieved_irrelevant_fact_ids": retrieved_irrelevant,
        "gold_irrelevant_fact_ids": gold_irrelevant_f_ids,
        "surfaced_conflict_ids": surfaced_conflicts,
        "gold_conflict_ids": [c.get("conflict_id") for c in gold_conflicts],
        "factual_claims": scored_claims,
        "provenance_counts": prov_counts,
        "metrics": {
            "relevant_historical_recall": recall,
            "omission_rate": omission_rate,
            "irrelevant_inclusion_rate": irrelevant_inclusion,
            "conflict_surfacing_rate": conflict_surfacing,
            "unsupported_inference_rate": unsupported_rate,
            "provenance_accuracy": provenance_accuracy
        }
    }

def run_recalculation():
    with open("docs/evaluation/results/pilot_raw_outputs.jsonl", "r", encoding="utf-8") as f:
        raw_records = [json.loads(line) for line in f if line.strip()]

    with open("docs/evaluation/datasets/pcif_pilot_50.jsonl", "r", encoding="utf-8") as f:
        scenario_map = {json.loads(line)["scenario_id"]: json.loads(line) for line in f if line.strip()}

    scored_records = []
    for r in raw_records:
        sc_id = r["scenario_id"]
        condition = r["condition"]
        sc = scenario_map[sc_id]
        assistant_resp = r["assistant_response"]

        scored_item = score_audited_scenario_response(sc, condition, assistant_resp)
        scored_item["model_configuration_identifier"] = r.get("model_configuration_identifier")
        scored_item["run_timestamp"] = r.get("run_timestamp")
        scored_records.append(scored_item)

    # Save to docs/evaluation/results/pilot_scored_results.jsonl
    scored_path = Path("docs/evaluation/results/pilot_scored_results.jsonl")
    with open(scored_path, "w", encoding="utf-8") as f:
        for item in scored_records:
            f.write(json.dumps(item) + "\n")

    # Aggregations
    metrics_by_condition = {"baseline": defaultdict(list), "pcif": defaultdict(list)}
    prov_totals_by_condition = {"baseline": Counter(), "pcif": Counter()}
    by_difficulty = {"baseline": defaultdict(lambda: defaultdict(list)), "pcif": defaultdict(lambda: defaultdict(list))}
    by_domain = {"baseline": defaultdict(lambda: defaultdict(list)), "pcif": defaultdict(lambda: defaultdict(list))}

    for item in scored_records:
        cond = item["condition"]
        diff = item["difficulty"]
        dom = item["domain"]
        m = item["metrics"]
        pc = item["provenance_counts"]

        for k, v in m.items():
            metrics_by_condition[cond][k].append(v)
            by_difficulty[cond][diff][k].append(v)
            by_domain[cond][dom][k].append(v)

        for pk, pv in pc.items():
            prov_totals_by_condition[cond][pk] += pv

    summary_by_condition = {}
    for cond in ["baseline", "pcif"]:
        summary_by_condition[cond] = {
            "scenario_count": len([x for x in scored_records if x["condition"] == cond]),
            "relevant_historical_recall": safe_mean(metrics_by_condition[cond]["relevant_historical_recall"]),
            "omission_rate": safe_mean(metrics_by_condition[cond]["omission_rate"]),
            "irrelevant_inclusion_rate": safe_mean(metrics_by_condition[cond]["irrelevant_inclusion_rate"]),
            "conflict_surfacing_rate": safe_mean(metrics_by_condition[cond]["conflict_surfacing_rate"]),
            "unsupported_inference_rate": safe_mean(metrics_by_condition[cond]["unsupported_inference_rate"]),
            "provenance_accuracy": safe_mean(metrics_by_condition[cond]["provenance_accuracy"])
        }

    # Slices
    diff_summary = {}
    for diff in ["easy", "medium", "hard"]:
        diff_summary[diff] = {}
        for cond in ["baseline", "pcif"]:
            diff_summary[diff][cond] = {
                k: safe_mean(by_difficulty[cond][diff][k])
                for k in ["relevant_historical_recall", "omission_rate", "irrelevant_inclusion_rate", "conflict_surfacing_rate", "unsupported_inference_rate", "provenance_accuracy"]
            }

    dom_summary = {}
    for dom in sorted(list(set(item["domain"] for item in scored_records))):
        dom_summary[dom] = {}
        for cond in ["baseline", "pcif"]:
            dom_summary[dom][cond] = {
                k: safe_mean(by_domain[cond][dom][k])
                for k in ["relevant_historical_recall", "omission_rate", "irrelevant_inclusion_rate", "conflict_surfacing_rate", "unsupported_inference_rate", "provenance_accuracy"]
            }

    report = {
        "scored_output_path": str(scored_path),
        "total_scored_records": len(scored_records),
        "summary_by_condition": summary_by_condition,
        "provenance_breakdown": {k: dict(v) for k, v in prov_totals_by_condition.items()},
        "by_difficulty": diff_summary,
        "by_domain": dom_summary
    }
    return report

if __name__ == "__main__":
    rep = run_recalculation()
    print(json.dumps(rep, indent=2))
