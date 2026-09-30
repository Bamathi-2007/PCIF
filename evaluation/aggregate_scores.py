"""
PCIF Pilot Score Aggregator (Final Frozen Specification)
=========================================================
Scores raw model outputs against dataset gold standards.
Outputs:
- docs/evaluation/results/pilot_scored_results.jsonl
- Detailed aggregated metrics report (overall, by condition, by difficulty, by domain, conflict cases, unsupported inference, 4-way provenance breakdown, channel accuracies, provenance explicitness rate).
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from evaluation.scoring import score_scenario_response

def safe_mean(values: List[Optional[float]]) -> Optional[float]:
    """Computes arithmetic mean ignoring None (N/A) values."""
    valid_vals = [v for v in values if v is not None]
    if not valid_vals:
        return None
    return sum(valid_vals) / len(valid_vals)

def format_pct(val: Optional[float]) -> str:
    """Formats float as percentage string or 'N/A' if None."""
    if val is None:
        return "N/A"
    return f"{val * 100:.1f}%"

METRIC_NAMES = [
    "relevant_historical_recall",
    "omission_rate",
    "irrelevant_inclusion_rate",
    "conflict_surfacing_rate",
    "unsupported_inference_rate",
    "provenance_accuracy",
    "provenance_explicitness_rate",
    "current_consultation_accuracy",
    "patient_reported_accuracy",
    "clinician_authored_accuracy",
]

def run_score_aggregation(
    dataset_path: str = "docs/evaluation/datasets/pcif_pilot_50.jsonl",
    raw_output_path: str = "docs/evaluation/results/pilot_raw_outputs.jsonl",
    scored_output_path: str = "docs/evaluation/results/pilot_scored_results.jsonl"
) -> Dict[str, Any]:
    # 1. Load scenarios
    scenario_map = {}
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                sc = json.loads(line)
                scenario_map[sc["scenario_id"]] = sc

    # 2. Load raw outputs
    raw_records = []
    with open(raw_output_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                raw_records.append(json.loads(line))

    # 3. Score every record
    scored_records = []
    for r in raw_records:
        sc_id = r["scenario_id"]
        condition = r["condition"]
        status = r.get("run_status", "success")

        if status != "success":
            continue

        sc = scenario_map[sc_id]
        assistant_resp = r["assistant_response"]

        scored_item = score_scenario_response(sc, condition, assistant_resp)
        scored_item["model_configuration_identifier"] = r.get("model_configuration_identifier")
        scored_item["run_timestamp"] = r.get("run_timestamp")
        scored_records.append(scored_item)

    # Save scored output jsonl
    scored_file = Path(scored_output_path)
    scored_file.parent.mkdir(parents=True, exist_ok=True)
    with open(scored_file, "w", encoding="utf-8") as f:
        for item in scored_records:
            f.write(json.dumps(item) + "\n")

    # 4. Aggregations
    metrics_by_condition = {"baseline": defaultdict(list), "pcif": defaultdict(list)}
    prov_totals_by_condition = {"baseline": Counter(), "pcif": Counter()}
    channel_totals_by_condition = {
        "baseline": defaultdict(lambda: Counter()),
        "pcif": defaultdict(lambda: Counter())
    }
    by_difficulty = {
        "baseline": defaultdict(lambda: defaultdict(list)),
        "pcif": defaultdict(lambda: defaultdict(list))
    }
    by_domain = {
        "baseline": defaultdict(lambda: defaultdict(list)),
        "pcif": defaultdict(lambda: defaultdict(list))
    }

    for item in scored_records:
        cond = item["condition"]
        diff = item["difficulty"]
        dom = item["domain"]
        m = item["metrics"]
        pc = item.get("provenance_counts", {})
        cc = item.get("channel_counts", {})

        for k, v in m.items():
            metrics_by_condition[cond][k].append(v)
            by_difficulty[cond][diff][k].append(v)
            by_domain[cond][dom][k].append(v)

        for pk, pv in pc.items():
            prov_totals_by_condition[cond][pk] += pv

        for ch, counts in cc.items():
            for outcome, val in counts.items():
                channel_totals_by_condition[cond][ch][outcome] += val

    # Summarize conditions
    summary_by_condition = {}
    for cond in ["baseline", "pcif"]:
        summary_by_condition[cond] = {
            "scenario_count": len([x for x in scored_records if x["condition"] == cond]),
            **{m_name: safe_mean(metrics_by_condition[cond][m_name]) for m_name in METRIC_NAMES}
        }

    # Slice summaries
    diff_summary = {}
    for diff in ["easy", "medium", "hard"]:
        diff_summary[diff] = {}
        for cond in ["baseline", "pcif"]:
            diff_summary[diff][cond] = {
                k: safe_mean(by_difficulty[cond][diff][k])
                for k in METRIC_NAMES
            }

    dom_summary = {}
    all_domains = sorted(list(set(item["domain"] for item in scored_records)))
    for dom in all_domains:
        dom_summary[dom] = {}
        for cond in ["baseline", "pcif"]:
            dom_summary[dom][cond] = {
                k: safe_mean(by_domain[cond][dom][k])
                for k in METRIC_NAMES
            }

    # Conflict cases analysis
    conflict_records = [x for x in scored_records if x["gold_conflict_ids"]]
    conflict_analysis = {
        "total_gold_conflict_scenarios": len(set(x["scenario_id"] for x in conflict_records)),
        "baseline_evaluable_conflict_scenarios": len([x for x in conflict_records if x["condition"] == "baseline" and len(x["evaluable_conflict_ids"]) > 0]),
        "pcif_evaluable_conflict_scenarios": len([x for x in conflict_records if x["condition"] == "pcif" and len(x["evaluable_conflict_ids"]) > 0]),
        "baseline_conflict_surfacing_rate": safe_mean([x["metrics"]["conflict_surfacing_rate"] for x in conflict_records if x["condition"] == "baseline"]),
        "pcif_conflict_surfacing_rate": safe_mean([x["metrics"]["conflict_surfacing_rate"] for x in conflict_records if x["condition"] == "pcif"])
    }

    # Total claims and unsupported inference counts
    total_claims = {"baseline": 0, "pcif": 0}
    unsupported_claims = {"baseline": 0, "pcif": 0}
    for item in scored_records:
        cond = item["condition"]
        for fc in item["factual_claims"]:
            total_claims[cond] += 1
            if not fc["supported"]:
                unsupported_claims[cond] += 1

    report = {
        "scored_output_path": str(scored_file),
        "total_scored_outputs": len(scored_records),
        "summary_by_condition": summary_by_condition,
        "provenance_breakdown": {k: dict(v) for k, v in prov_totals_by_condition.items()},
        "channel_breakdowns": {k: {ch: dict(c) for ch, c in channels.items()} for k, channels in channel_totals_by_condition.items()},
        "by_difficulty": diff_summary,
        "by_domain": dom_summary,
        "conflict_analysis": conflict_analysis,
        "factual_claims_audit": {
            "total_claims_produced": total_claims,
            "unsupported_claims_count": unsupported_claims
        }
    }
    return report

if __name__ == "__main__":
    rep = run_score_aggregation()
    print(json.dumps(rep, indent=2))
