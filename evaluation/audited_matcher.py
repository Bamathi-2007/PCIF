"""
Audited Semantic Matcher and Provenance Adjudicator
===================================================
Implements the audited matching logic:
1. Strict Concept Matching (eliminates false positives from generic words like 'patient', 'habit', 'diet')
2. Condition-aware retrieval (Baseline does NOT match hidden F facts)
3. Condition-aware conflict surfacing (Baseline only credited if both sides in consultation Q facts)
4. 4-way Provenance breakdown (correct, incorrect, not_explicit, not_applicable)
5. Strict condition-specific support checking (Baseline claims only supported by Q facts)
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\d]", " ", text)
    return " ".join(text.split())

STOPWORDS = {
    "patient", "reports", "reported", "history", "notes", "documented",
    "discussing", "discussed", "previous", "earlier", "during", "recent",
    "stating", "states", "shows", "noted", "review", "reviewed", "consultation",
    "present", "presents", "about", "with", "from", "that", "this", "over",
    "past", "daily", "every", "also", "have", "been", "there"
}

def extract_content_keywords(text: str) -> List[str]:
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
    category = fact.get("category") or ""
    
    # Target sections to check
    sections = [
        assistant_response.get("context_summary", ""),
        " ".join(assistant_response.get("relevant_current_context", [])),
        " ".join(assistant_response.get("relevant_longitudinal_changes", [])),
        " ".join(assistant_response.get("relevant_clinician_notes", [])),
        " ".join(assistant_response.get("items_to_verify", []))
    ]
    full_text = " ".join(sections)
    full_norm = normalize_text(full_text)
    
    keywords = extract_content_keywords(summary)
    if not keywords:
        return False

    # Check key noun/verb phrases
    # A fact matches if:
    # 1. Distinctive keyword matching: at least 60% of informative keywords appear, OR
    # 2. Strong core concept / value match (e.g. specific numbers/metrics like "4.5 hours", "2.5 L")
    matched_kw = [w for w in keywords if w in full_norm]
    kw_ratio = len(matched_kw) / len(keywords)

    if value:
        val_norm = normalize_text(value)
        val_nums = re.findall(r"\b\d+(?:\.\d+)?\b", val_norm)
        corpus_nums = re.findall(r"\b\d+(?:\.\d+)?\b", full_norm)
        
        has_num = any(num in corpus_nums for num in val_nums) if val_nums else False
        if has_num and kw_ratio >= 0.40:
            return True

    # For multi-word concepts, require at least 2 keywords if len >= 2
    if len(keywords) >= 2:
        return len(matched_kw) >= 2 and kw_ratio >= 0.50
    else:
        return len(matched_kw) >= 1 and keywords[0] in full_norm

def evaluate_conflict_surfacing(
    conflict: Dict[str, Any],
    condition: str,
    assistant_response: Dict[str, Any],
    scenario: Dict[str, Any]
) -> bool:
    """
    Audited conflict surfacing evaluation.
    - Baseline can ONLY surface a conflict if BOTH conflicting facts were present in the consultation Q facts.
      (If conflict involves hidden F history, Baseline did not receive the evidence).
    - PCIF is evaluated against supplied conflict evidence.
    """
    fact_ids = conflict.get("fact_ids", [])
    q_ids = [q["fact_id"] for q in scenario.get("current_consultation", {}).get("fact_units", [])]
    
    if condition == "baseline":
        # Baseline must have both facts in consultation
        if not all(fid in q_ids for fid in fact_ids):
            return False

    verify_items = assistant_response.get("items_to_verify", [])
    context_summary = assistant_response.get("context_summary", "")
    
    discrepancy_markers = {
        "discrepancy", "conflict", "verify", "verification", "contradict",
        "contradicts", "difference", "contrasting", "inconsistent", "inconsistency",
        "versus", "vs", "whereas", "while", "reconcile", "confirm", "clarify",
        "divergence", "contrasts"
    }
    
    verify_text = " ".join(verify_items)
    summary_norm = normalize_text(context_summary)
    has_summary_marker = any(m in summary_norm for m in discrepancy_markers)
    
    combined_verify_text = verify_text + (" " + context_summary if has_summary_marker else "")
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

def evaluate_claim_provenance(
    claim_dict: Dict[str, Any],
    condition: str,
    scenario: Dict[str, Any]
) -> Tuple[bool, Optional[str], str]:
    """
    Evaluates factual support and 4-way provenance outcome:
    Outcomes: 'correct', 'incorrect', 'not_explicit', 'not_applicable'
    """
    claim_text = claim_dict.get("claim", "")
    section = claim_dict.get("section", "")
    claim_norm = normalize_text(claim_text)
    
    # Boilerplate / non-factual default statements
    if any(k in claim_norm for k in ["no prior", "not available", "no structured", "blank", "empty"]):
        return True, "SYSTEM_DEFAULT", "not_applicable"

    q_facts = scenario.get("current_consultation", {}).get("fact_units", [])
    consultation_raw = scenario.get("current_consultation", {}).get("text", "")
    
    # 1. Check Consultation Q Support
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

    # For BASELINE: ONLY Q facts are available evidence!
    if condition == "baseline":
        if is_q_supported:
            # Check provenance attribution
            if section in ("relevant_current_context", "context_summary", "items_to_verify"):
                return True, sup_q_id, "correct"
            elif section == "relevant_clinician_notes":
                return True, sup_q_id, "incorrect"  # Described consultation as clinician note
            return True, sup_q_id, "correct"
        else:
            # Baseline made a claim unsupported by consultation
            return False, None, "not_applicable"

    # For PCIF: check Q facts and F facts
    if is_q_supported and section in ("relevant_current_context", "context_summary", "items_to_verify"):
        return True, sup_q_id, "correct"

    # Check Patient-Reported F facts
    all_pr_facts = (
        scenario.get("patient_reported_current_context", []) +
        scenario.get("patient_reported_longitudinal_history", [])
    )
    for f in all_pr_facts:
        kw = extract_content_keywords(f.get("summary", ""))
        if kw and (sum(1 for w in kw if w in claim_norm) >= max(1, len(kw) // 2) or any(w in claim_norm for w in kw if len(w) > 5)):
            if section in ("relevant_current_context", "relevant_longitudinal_changes"):
                return True, f.get("fact_id"), "correct"
            elif section == "relevant_clinician_notes":
                return True, f.get("fact_id"), "incorrect"  # Mislabeled patient report as clinician note
            elif section == "context_summary":
                if any(k in claim_norm for k in ["patient reported", "background", "history", "log", "tracker", "habit", "intake", "reports"]):
                    return True, f.get("fact_id"), "correct"
                else:
                    return True, f.get("fact_id"), "not_explicit"
            return True, f.get("fact_id"), "correct"

    # Check Clinician-Authored F facts
    clin_notes = scenario.get("clinician_authored_history", [])
    for n in clin_notes:
        kw = extract_content_keywords(n.get("note", ""))
        if kw and (sum(1 for w in kw if w in claim_norm) >= max(1, len(kw) // 2) or any(w in claim_norm for w in kw if len(w) > 5)):
            if section == "relevant_clinician_notes":
                return True, n.get("fact_id"), "correct"
            elif section in ("relevant_current_context", "relevant_longitudinal_changes"):
                return True, n.get("fact_id"), "incorrect"  # Mislabeled clinician note as patient report
            elif section == "context_summary":
                if any(k in claim_norm for k in ["clinician", "doctor", "physician", "prior visit", "historical note", "documented"]):
                    return True, n.get("fact_id"), "correct"
                else:
                    return True, n.get("fact_id"), "not_explicit"
            return True, n.get("fact_id"), "correct"

    if is_q_supported:
        return True, sup_q_id, "correct"

    # Unsupported claim
    return False, None, "not_applicable"
