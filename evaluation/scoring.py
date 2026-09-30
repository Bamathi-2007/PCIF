"""
PCIF Evaluation Scoring and Metric Engine (Final Frozen Specification)
======================================================================
Computes evaluation metrics across paired Baseline and PCIF condition outputs.

Key Principles Enforced:
1. Condition-Aware Historical Retrieval:
   - Baseline received 0 historical F facts. Therefore, Baseline historical recall, omission rate,
     and irrelevant inclusion are strictly N/A (None).
   - PCIF is scored against supplied gold historical F facts.

2. Condition-Aware Conflict Surfacing:
   - For each condition, conflict scoring uses ONLY conflicts whose required facts were actually
     available to that condition.
   - If a conflict requires historical F facts not supplied to Baseline, it is not evaluable for Baseline.
   - If the count of evaluable conflicts for a condition is 0, Conflict Surfacing Rate is None (N/A).

3. 4-Way Provenance Breakdown & Channel Accuracies:
   - Evaluates claims into: 'correct', 'incorrect', 'not_explicit', 'not_applicable'.
   - Overall Provenance Accuracy = correct / (correct + incorrect) on explicit attributions.
   - Channel-specific accuracies computed for current_consultation, patient_reported, and clinician_authored.
   - Provenance Explicitness Rate = (correct + incorrect) / (correct + incorrect + not_explicit).

4. Condition-Specific Evidence Support:
   - Baseline claims can ONLY be supported by consultation Q facts.
   - PCIF claims can be supported by consultation Q facts + supplied F facts.

5. Zero-Denominator Handling:
   - Explicitly returns None (rendered as N/A in reports). Never silently coerced to 0% or 100%.
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set

def normalize_text(text: str) -> str:
    """Normalizes text for robust semantic matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s\d]", " ", text)
    return " ".join(text.split())

STOPWORDS: Set[str] = {
    "patient", "reports", "reported", "history", "notes", "documented",
    "discussing", "discussed", "previous", "earlier", "during", "recent",
    "stating", "states", "shows", "noted", "review", "reviewed", "consultation",
    "present", "presents", "about", "with", "from", "that", "this", "over",
    "past", "daily", "every", "also", "have", "been", "there"
}

def extract_content_keywords(text: str) -> List[str]:
    """Extracts distinctive informative words from text."""
    words = normalize_text(text).split()
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]

def match_fact_semantically(fact: Dict[str, Any], assistant_response: Dict[str, Any]) -> bool:
    """
    Audited semantic matching for a gold historical fact F.
    Checks relevant sections: relevant_current_context, relevant_longitudinal_changes,
    relevant_clinician_notes, items_to_verify, and context_summary.
    """
    summary = fact.get("summary") or fact.get("note") or ""
    value = fact.get("value") or ""
    
    sections = [
        assistant_response.get("context_summary", ""),
        " ".join(assistant_response.get("relevant_current_context", [])),
        " ".join(assistant_response.get("relevant_longitudinal_changes", [])),
        " ".join(assistant_response.get("relevant_clinician_notes", [])),
        " ".join(assistant_response.get("items_to_verify", []))
    ]
    full_norm = normalize_text(" ".join(sections))
    
    keywords = extract_content_keywords(summary)
    if not keywords:
        return False

    matched_kw = [w for w in keywords if w in full_norm]
    kw_ratio = len(matched_kw) / len(keywords)

    if value:
        val_norm = normalize_text(value)
        val_nums = re.findall(r"\b\d+(?:\.\d+)?\b", val_norm)
        corpus_nums = re.findall(r"\b\d+(?:\.\d+)?\b", full_norm)
        
        has_num = any(num in corpus_nums for num in val_nums) if val_nums else False
        if has_num and kw_ratio >= 0.40:
            return True

    if len(keywords) >= 2:
        return len(matched_kw) >= 2 and kw_ratio >= 0.50
    else:
        return len(matched_kw) >= 1 and keywords[0] in full_norm

def is_conflict_evaluable(conflict: Dict[str, Any], condition: str, scenario: Dict[str, Any]) -> bool:
    """
    Checks if a conflict is evaluable under the specified condition.
    A conflict is evaluable if ALL required facts in conflict['fact_ids'] were available
    in the input provided to that condition.
    """
    fact_ids = conflict.get("fact_ids", [])
    if condition == "baseline":
        q_ids = [q["fact_id"] for q in scenario.get("current_consultation", {}).get("fact_units", [])]
        return all(fid in q_ids for fid in fact_ids)
    elif condition == "pcif":
        # PCIF received all Q and declared F facts
        return True
    return False

def evaluate_conflict_surfacing(
    conflict: Dict[str, Any],
    condition: str,
    assistant_response: Dict[str, Any],
    scenario: Dict[str, Any]
) -> bool:
    """
    Audited conflict surfacing evaluation.
    Returns True if the conflict was surfaced and was evaluable for that condition.
    """
    if not is_conflict_evaluable(conflict, condition, scenario):
        return False

    fact_ids = conflict.get("fact_ids", [])
    verify_items = assistant_response.get("items_to_verify", [])
    context_summary = assistant_response.get("context_summary", "")
    
    discrepancy_markers = {
        "discrepancy", "conflict", "verify", "verification", "contradict",
        "contradicts", "difference", "contrasting", "inconsistent", "inconsistency",
        "versus", "vs", "whereas", "while", "reconcile", "confirm", "clarify",
        "divergence", "contrasts"
    }
    
    summary_norm = normalize_text(context_summary)
    has_summary_marker = any(m in summary_norm for m in discrepancy_markers)
    
    combined_verify_text = " ".join(verify_items) + (" " + context_summary if has_summary_marker else "")
    combined_norm = normalize_text(combined_verify_text)
    
    if not combined_norm.strip():
        return False

    fact_map = {}
    for q in scenario.get("current_consultation", {}).get("fact_units", []):
        fact_map[q.get("fact_id")] = q.get("text", "")
    for f in scenario.get("patient_reported_current_context", []):
        fact_map[f.get("fact_id")] = f.get("summary", "")
    for f in scenario.get("patient_reported_longitudinal_history", []):
        fact_map[f.get("fact_id")] = f.get("summary", "")
    for f in scenario.get("clinician_authored_history", []):
        fact_map[f.get("fact_id")] = f.get("note", "")

    matched_facts = 0
    for fid in fact_ids:
        text = fact_map.get(fid, "")
        if not text:
            continue
        kw = extract_content_keywords(text)
        if any(w in combined_norm for w in kw):
            matched_facts += 1

    return matched_facts >= len(fact_ids) and (len(verify_items) > 0 or has_summary_marker)

def extract_factual_claims(assistant_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts atomic factual claims produced by the model across response sections
    and records their expressed provenance.
    """
    claims = []
    
    for item in assistant_response.get("relevant_current_context", []):
        if item.strip():
            claims.append({
                "claim": item.strip(),
                "section": "relevant_current_context",
                "expressed_provenance": "patient_reported"
            })
            
    for item in assistant_response.get("relevant_longitudinal_changes", []):
        if item.strip():
            claims.append({
                "claim": item.strip(),
                "section": "relevant_longitudinal_changes",
                "expressed_provenance": "patient_reported"
            })
            
    for item in assistant_response.get("relevant_clinician_notes", []):
        if item.strip():
            claims.append({
                "claim": item.strip(),
                "section": "relevant_clinician_notes",
                "expressed_provenance": "clinician_authored"
            })
            
    summary = assistant_response.get("context_summary", "")
    if summary.strip():
        sentences = [s.strip() for s in re.split(r"[.!?]+", summary) if len(s.strip()) > 5]
        for sent in sentences:
            sent_norm = sent.lower()
            if any(k in sent_norm for k in ["clinician", "doctor", "physician", "prior visit", "historical note", "documented"]):
                prov = "clinician_authored"
            elif any(k in sent_norm for k in ["patient reported", "background", "history", "log", "tracker", "habit", "intake", "reports"]):
                prov = "patient_reported"
            else:
                prov = "current_consultation"
                
            claims.append({
                "claim": sent,
                "section": "context_summary",
                "expressed_provenance": prov
            })
            
    for item in assistant_response.get("items_to_verify", []):
        if item.strip():
            claims.append({
                "claim": item.strip(),
                "section": "items_to_verify",
                "expressed_provenance": "current_consultation"
            })

    return claims

def evaluate_claim_provenance(
    claim_dict: Dict[str, Any],
    condition: str,
    scenario: Dict[str, Any]
) -> Tuple[bool, Optional[str], str, Optional[str]]:
    """
    Evaluates factual support, provenance channel, and 4-way provenance outcome.
    Returns:
      (is_supported, supporting_fact_id, provenance_outcome, channel)
      where provenance_outcome is in ('correct', 'incorrect', 'not_explicit', 'not_applicable')
      and channel is in ('current_consultation', 'patient_reported', 'clinician_authored', None)
    """
    claim_text = claim_dict.get("claim", "")
    section = claim_dict.get("section", "")
    claim_norm = normalize_text(claim_text)
    
    if any(k in claim_norm for k in ["no prior", "not available", "no structured", "blank", "empty", "notice"]):
        return True, "SYSTEM_DEFAULT", "not_applicable", None

    q_facts = scenario.get("current_consultation", {}).get("fact_units", [])
    consultation_raw = scenario.get("current_consultation", {}).get("text", "")
    
    is_q_supported = False
    sup_q_id = None
    for q in q_facts:
        kw = extract_content_keywords(q.get("text", ""))
        if kw and any(w in claim_norm for w in kw):
            is_q_supported = True
            sup_q_id = q.get("fact_id")
            break
            
    if not is_q_supported:
        raw_kw = extract_content_keywords(consultation_raw)
        if raw_kw and sum(1 for w in raw_kw if w in claim_norm) >= 2:
            is_q_supported = True
            sup_q_id = "Q_CONSULTATION"

    # For BASELINE: ONLY Q facts are available evidence
    if condition == "baseline":
        if is_q_supported:
            if section in ("relevant_current_context", "context_summary", "items_to_verify"):
                return True, sup_q_id, "correct", "current_consultation"
            elif section == "relevant_clinician_notes":
                return True, sup_q_id, "incorrect", "current_consultation"
            return True, sup_q_id, "correct", "current_consultation"
        else:
            return False, None, "not_applicable", None

    # For PCIF:
    if is_q_supported and section in ("relevant_current_context", "context_summary", "items_to_verify"):
        return True, sup_q_id, "correct", "current_consultation"

    all_pr_facts = (
        scenario.get("patient_reported_current_context", []) +
        scenario.get("patient_reported_longitudinal_history", [])
    )
    for f in all_pr_facts:
        kw = extract_content_keywords(f.get("summary", ""))
        if kw and (sum(1 for w in kw if w in claim_norm) >= max(1, len(kw) // 2) or any(w in claim_norm for w in kw if len(w) > 5)):
            if section in ("relevant_current_context", "relevant_longitudinal_changes"):
                return True, f.get("fact_id"), "correct", "patient_reported"
            elif section == "relevant_clinician_notes":
                return True, f.get("fact_id"), "incorrect", "patient_reported"
            elif section == "context_summary":
                if any(k in claim_norm for k in ["patient reported", "background", "history", "log", "tracker", "habit", "intake", "reports"]):
                    return True, f.get("fact_id"), "correct", "patient_reported"
                else:
                    return True, f.get("fact_id"), "not_explicit", "patient_reported"
            return True, f.get("fact_id"), "correct", "patient_reported"

    clin_notes = scenario.get("clinician_authored_history", [])
    for n in clin_notes:
        kw = extract_content_keywords(n.get("note", ""))
        if kw and (sum(1 for w in kw if w in claim_norm) >= max(1, len(kw) // 2) or any(w in claim_norm for w in kw if len(w) > 5)):
            if section == "relevant_clinician_notes":
                return True, n.get("fact_id"), "correct", "clinician_authored"
            elif section in ("relevant_current_context", "relevant_longitudinal_changes"):
                return True, n.get("fact_id"), "incorrect", "clinician_authored"
            elif section == "context_summary":
                if any(k in claim_norm for k in ["clinician", "doctor", "physician", "prior visit", "historical note", "documented"]):
                    return True, n.get("fact_id"), "correct", "clinician_authored"
                else:
                    return True, n.get("fact_id"), "not_explicit", "clinician_authored"
            return True, n.get("fact_id"), "correct", "clinician_authored"

    if is_q_supported:
        return True, sup_q_id, "correct", "current_consultation"

    return False, None, "not_applicable", None

def score_scenario_response(
    scenario: Dict[str, Any],
    condition: str,
    assistant_response: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Scores a single model response against scenario gold evidence with full condition-awareness.
    """
    gold = scenario.get("gold_evidence", {})
    gold_relevant_f_ids = gold.get("relevant_fact_ids", [])
    gold_irrelevant_f_ids = gold.get("irrelevant_fact_ids", [])
    gold_conflicts = gold.get("conflict_groups", [])

    f_fact_map = {}
    for f in scenario.get("patient_reported_current_context", []):
        f_fact_map[f.get("fact_id")] = f
    for f in scenario.get("patient_reported_longitudinal_history", []):
        f_fact_map[f.get("fact_id")] = f
    for f in scenario.get("clinician_authored_history", []):
        f_fact_map[f.get("fact_id")] = f

    # 1. Historical Fact Retrieval (Condition-Aware)
    retrieved_relevant = []
    retrieved_irrelevant = []

    if condition == "baseline":
        # Baseline was supplied 0 historical context
        recall = None
        omission_rate = None
        irrelevant_inclusion = None
    else:
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

    # 2. Conflict Surfacing (Condition-Aware Denominator)
    evaluable_conflicts = [c for c in gold_conflicts if is_conflict_evaluable(c, condition, scenario)]
    surfaced_conflicts = []
    for c in evaluable_conflicts:
        cid = c.get("conflict_id")
        if evaluate_conflict_surfacing(c, condition, assistant_response, scenario):
            surfaced_conflicts.append(cid)

    if len(evaluable_conflicts) > 0:
        conflict_surfacing = len(surfaced_conflicts) / len(evaluable_conflicts)
    else:
        conflict_surfacing = None

    # 3. Factual Claims and 4-Way Provenance Analysis
    raw_claims = extract_factual_claims(assistant_response)
    scored_claims = []
    prov_counts = {"correct": 0, "incorrect": 0, "not_explicit": 0, "not_applicable": 0}
    channel_counts = {
        "current_consultation": {"correct": 0, "incorrect": 0},
        "patient_reported": {"correct": 0, "incorrect": 0},
        "clinician_authored": {"correct": 0, "incorrect": 0},
    }
    supported_count = 0
    unsupported_count = 0

    for rc in raw_claims:
        is_sup, sup_id, prov_outcome, channel = evaluate_claim_provenance(rc, condition, scenario)
        prov_counts[prov_outcome] += 1
        
        if channel and prov_outcome in ("correct", "incorrect"):
            channel_counts[channel][prov_outcome] += 1

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
            "provenance_outcome": prov_outcome,
            "channel": channel
        })

    total_claims = len(scored_claims)
    if total_claims > 0:
        unsupported_rate = unsupported_count / total_claims
    else:
        unsupported_rate = None

    # Provenance Accuracies:
    explicit_prov_total = prov_counts["correct"] + prov_counts["incorrect"]
    if explicit_prov_total > 0:
        provenance_accuracy = prov_counts["correct"] / explicit_prov_total
    else:
        provenance_accuracy = None

    # Provenance Explicitness Rate:
    evaluable_claims_total = prov_counts["correct"] + prov_counts["incorrect"] + prov_counts["not_explicit"]
    if evaluable_claims_total > 0:
        provenance_explicitness_rate = explicit_prov_total / evaluable_claims_total
    else:
        provenance_explicitness_rate = None

    # Channel accuracies
    channel_accuracies = {}
    for ch, counts in channel_counts.items():
        ch_total = counts["correct"] + counts["incorrect"]
        channel_accuracies[f"{ch}_accuracy"] = counts["correct"] / ch_total if ch_total > 0 else None

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
        "evaluable_conflict_ids": [c.get("conflict_id") for c in evaluable_conflicts],
        "gold_conflict_ids": [c.get("conflict_id") for c in gold_conflicts],
        "factual_claims": scored_claims,
        "provenance_counts": prov_counts,
        "channel_counts": channel_counts,
        "metrics": {
            "relevant_historical_recall": recall,
            "omission_rate": omission_rate,
            "irrelevant_inclusion_rate": irrelevant_inclusion,
            "conflict_surfacing_rate": conflict_surfacing,
            "unsupported_inference_rate": unsupported_rate,
            "provenance_accuracy": provenance_accuracy,
            "provenance_explicitness_rate": provenance_explicitness_rate,
            **channel_accuracies
        }
    }
