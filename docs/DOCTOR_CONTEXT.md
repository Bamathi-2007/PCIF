# PCIF Doctor-Side Context Assistance Specification

This document details the architecture, boundaries, provenance channels, and evaluation design for the **Doctor-Side Context Assistance Layer** in the **Patient Context Intelligence Framework (PCIF)**.

---

## 1. Purpose & Scope

The Doctor Context Assistant provides clinician-facing decision support by synthesizing three separate evidence streams:
1. Active Clinician Consultation Notes (`transient`)
2. Structured Patient-Reported Context (`patient_context`, `patient_reported`)
3. Clinician-Authored Historical Notes (`doctor_notes`, `doctor_confirmed`)

> [!IMPORTANT]
> **Clinical Boundary**: The Doctor AI is strictly an assistive context engine. It does **not** diagnose diseases, assign clinical codes, prescribe medications, or replace clinician judgment. The treating physician remains solely responsible for all medical evaluations, diagnoses, and treatment decisions.

---

## 2. System Architecture & Three Provenance Channels

```text
SOURCE A: Transient Consultation Notes ──────────┐
                                                 │
SOURCE B: Patient-Reported Context ──────────────┼──► Doctor Context AI ──► DoctorContextResponse
  - Active Current Profile (is_current=true)     │    (configured Gemini model) (Structured JSON)
  - Longitudinal History (Max 20 records)        │
                                                 │
SOURCE C: Clinician-Authored Notes History ──────┘
  (doctor_notes, Max 10 recent notes)
```

### Three Input Sources

1. **Source A: Current Clinician Consultation Notes** (`consultation`): Transient text input entered by the attending clinician during the visit (not automatically persisted, not a confirmed diagnosis).
2. **Source B: Patient-Reported Structured Context** (`patient_context`):
   - Active Current Context Profile retrieved via `get_current_patient_context(patient_id)`.
   - Longitudinal Context History retrieved via `get_patient_context(patient_id)` (capped at a deterministic limit of `MAX_HISTORY_LIMIT = 20` records).
3. **Source C: Clinician-Authored Historical Notes** (`doctor_notes`):
   - Notes history retrieved via `get_doctor_notes(patient_id)` (capped at a deterministic limit of `MAX_CLINICIAN_NOTES = 10` most recent notes).

---

## 3. Core Safety & Operational Principles

1. **Strict Provenance Separation**:
   - Patient-reported records retain `record_type = "patient_reported"`.
   - Clinician-authored notes retain internal `record_type = "doctor_confirmed"`.
   - The AI explicitly identifies each source and never silently converts patient-reported facts into clinician-authored findings, or vice versa.

2. **Transient Consultation & Zero Writeback**:
   - Clinician consultation notes and generated Doctor AI outputs are transient inputs/outputs.
   - Doctor AI execution causes zero database writes (neither `patient_context` nor `doctor_notes` is modified).

3. **Strict Non-Diagnostic Boundary**:
   - Prohibited outputs: Diagnoses, disease labels, ICD codes, prescription recommendations, medication adjustment suggestions, or automated risk scores.
   - Permitted outputs: Neutral context summaries ("Relevant prior patient-reported context includes...", "A prior clinician-authored note recorded...", "Consider verifying...").

4. **Multi-Source Conflict & Discrepancy Flagging**:
   - If sources conflict (e.g. patient-reported sleep = 5h/night vs clinician-authored note = 7h/night vs current consultation = 6h/night), the AI surfaces the discrepancy under `items_to_verify` for clinician review without silently deciding which source is "correct".

5. **Empty-History Handling**:
   - Handles empty states cleanly across all permutations (no clinician notes, no patient context, or completely empty history) without fabricating past records.

6. **Timestamp Semantics**:
   - Database records persist `created_at` (or `captured_at` for patient context). In the Doctor AI prompt payload, `saved_at` is a presentation/prompt representation derived from `created_at` and represents PCIF database persistence time only. Timestamps are never interpreted as clinical symptom onset or disease start dates.

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
    "context_summary": "Patient-reported background includes reduced sleep associated with exam stress and low fluid intake. A prior clinician-authored note documented persistent daytime fatigue.",
    "relevant_current_context": [
      "Reduced sleep associated with exam stress (5 hours/night)",
      "Low water intake on college days (1 glass/day)"
    ],
    "relevant_longitudinal_changes": [
      "Reported sleep duration decreased from 7 hours/night to 5 hours/night over past observations."
    ],
    "relevant_clinician_notes": [
      "Reviewed persistent morning fatigue; recommended routine blood work."
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

## 5. Comparative Evaluation Protocol (Research Design)

By Day 15, PCIF preserves explicit lineage across three distinct information channels:
1. `CURRENT CONSULTATION`
2. `PATIENT-REPORTED LONGITUDINAL CONTEXT`
3. `CLINICIAN-AUTHORED HISTORY`

This infrastructure enables future empirical evaluation comparing:
- **Baseline Condition**: Current Consultation Notes ONLY
- **PCIF Multi-Source Condition**: Current Consultation Notes + Structured Longitudinal Context + Clinician-Authored Notes

### Primary Evaluation Metrics
1. **Contextual Completeness**: Percentage of relevant historical factors identified.
2. **Omission Rate**: Frequency of missed clinically relevant context.
3. **Unsupported Inference Rate**: Rate of unwarranted diagnostic claims or unsupported assertions (metric to be measured).
4. **Summary Usability**: Clinician-rated usefulness of background context summaries.

> [!NOTE]
> Formal comparative evaluation experiments will be conducted in subsequent phases. Day 15 establishes the technical integration for multi-source provenance assistance.

---

## 6. Clinician Context Workspace (Frontend Interface)

The clinician interface at `/doctor` renders all structured output sections:

| Section | Source field | Empty state |
| :--- | :--- | :--- |
| **Context Summary** | `assistant.context_summary` | "No summary was returned." |
| **Relevant Current Patient Context** | `assistant.relevant_current_context` | "No relevant current patient-reported context was identified for this consultation." |
| **Longitudinal Context** | `assistant.relevant_longitudinal_changes` | "No relevant longitudinal changes were identified." |
| **Relevant Clinician-Authored History** | `assistant.relevant_clinician_notes` | "No relevant clinician-authored history was identified for this consultation." |
| **Items to Verify** | `assistant.items_to_verify` | "No additional items were identified for verification." |
| **Disclaimer** | `disclaimer` | Hidden if not present |
| **Previous Clinician Notes** | `doctor_notes` collection | "No clinician-authored notes have been saved for this patient." |

### Dual Provenance UI
- **`PATIENT-REPORTED CONTEXT`**: Highlighted in amber/cream with clear patient-origin disclosure.
- **`CLINICIAN-AUTHORED NOTES`**: Highlighted in mint/teal with clinician workspace origin disclosure.
- **Security Notice**: *"The current prototype does not verify clinician identity or authorize access to patient records."*
