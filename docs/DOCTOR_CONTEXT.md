# PCIF Doctor-Side Context Assistance Specification

This document details the architecture, boundaries, and evaluation design for the **Doctor-Side Context Assistance Layer** in the **Patient Context Intelligence Framework (PCIF)**.

---

## 1. Purpose & Scope

The Doctor Context Assistant provides clinician-facing decision support by synthesizing structured patient-reported health context extracted from patient conversations (**Nutrition AI** and **Mental Wellness AI**) with the attending clinician's active consultation notes.

> [!IMPORTANT]
> **Clinical Boundary**: The Doctor AI is strictly an assistive context engine. It does **not** diagnose diseases, assign clinical codes, prescribe medications, or replace clinician judgment. The treating physician remains solely responsible for all medical evaluations, diagnoses, and treatment decisions.

---

## 2. System Architecture & Information Flow

```text
Clinician Consultation Notes ────┐
                                 │
Active Current Context Profile ──┼──► Doctor Context AI ──► DoctorContextResponse
(is_current=true)                │    (Google Gemini)      (JSON Schema)
                                 │
Longitudinal Context History ────┘
(Max 20 recent records)
```

### Input Sources

1. **Clinician Consultation Notes** (`consultation`): Transient text input entered by the attending clinician during the visit.
2. **Active Current Context Profile**: Active context items retrieved via `get_current_patient_context(patient_id)` where `is_current == true`.
3. **Longitudinal Context History**: Historical timeline records retrieved via `get_patient_context(patient_id)` (capped at a deterministic maximum limit of 20 records).

---

## 3. Core Safety & Operational Principles

1. **Patient-Reported Provenance**:
   - All stored context items retain `record_type = "patient_reported"`.
   - The AI explicitly identifies stored context as patient-reported, avoiding representation as doctor-confirmed findings.

2. **Transient Consultation & Output**:
   - Clinician consultation notes and generated Doctor AI outputs are transient inputs/outputs for the assistance layer.
   - Day 12 does **not** persist clinician notes or Doctor AI responses to MongoDB.

3. **Strict Non-Diagnostic Boundary**:
   - Prohibited outputs: Diagnoses, disease labels, ICD codes, prescription recommendations, medication adjustment suggestions, or automated risk scores.
   - Permitted outputs: Neutral context summaries ("Relevant prior patient-reported context includes...", "Previously reported...", "Consider verifying...").

4. **Conflict & Discrepancy Flagging**:
   - If stored context conflicts with current consultation details (e.g. stored sleep = 5 hours/night vs consultation notes sleep = 7 hours/night), the AI surfaces the discrepancy under `items_to_verify` for clinician confirmation.

5. **Empty-History Handling**:
   - If a patient has zero prior stored context, the endpoint executes successfully and returns `"No prior structured patient context is available for this patient."` without fabricating history.

6. **Raw Chat Privacy**:
   - The doctor-side assistant works strictly from structured CCEE context items. Raw chat transcripts are never retrieved, persisted, or required.

---

## 4. API Request & Response Specification

### Endpoint: `POST /api/doctor/context`

#### Request Payload
```json
{
  "patient_id": "pcif_demo_7b5a8c1d",
  "consultation": "Patient presents with morning fatigue and difficulty concentrating."
}
```

#### Response Payload (`DoctorContextResponse`)
```json
{
  "patient_id": "pcif_demo_7b5a8c1d",
  "assistant": {
    "context_summary": "Patient-reported background includes reduced sleep associated with exam stress and low fluid intake.",
    "relevant_current_context": [
      "Reduced sleep associated with exam stress (5 hours/night)",
      "Low water intake on college days (1 glass/day)"
    ],
    "relevant_longitudinal_changes": [
      "Reported sleep duration decreased from 7 hours/night to 5 hours/night over past observations."
    ],
    "items_to_verify": [
      "Verify current daily fluid consumption during college hours.",
      "Discrepancy: Current consultation notes sleep improvement, while stored context reports 5 hours/night."
    ]
  },
  "disclaimer": "This system provides patient-reported context support for clinician review. Clinical diagnosis, prescribing, and medical decisions remain the sole responsibility of the treating clinician."
}
```

---

## 5. Comparative Evaluation Protocol (Future Research Design)

Day 12 establishes the **PCIF Condition** for comparative clinical evaluation against a standard baseline:

| Evaluation Condition | Information Available to Doctor AI |
| :--- | :--- |
| **Baseline Condition** | Current Consultation Notes ONLY |
| **PCIF Condition** | Current Consultation Notes + Structured Longitudinal CCEE Context |

### Primary Evaluation Metrics
1. **Contextual Completeness**: Percentage of relevant historical lifestyle/wellness factors identified.
2. **Omission Rate**: Frequency of missed clinically relevant context.
3. **Unsupported Inference Rate**: Rate of unwarranted diagnostic claims or hallucinations (Target: 0%).
4. **Summary Usability**: Clinician-rated usefulness of background context summaries.

> [!NOTE]
> Comparative evaluation experiments will be conducted in subsequent phases. Day 12 establishes the technical infrastructure for the PCIF condition.
