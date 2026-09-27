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

---

## 6. Day 13: Clinician Context Workspace (Frontend Interface)

Day 13 adds a dedicated, clinician-facing web interface that connects to the Day 12 `POST /api/doctor/context` API.

### Route

The clinician interface is accessible at:

```
/doctor
/doctor/
```

It is **not** linked from the patient-facing application (`/`). Access is direct by URL. The patient UI remains visually and functionally unchanged.

### Input Fields

| Field | Description |
| :--- | :--- |
| **Patient ID** | Manually entered patient identifier (e.g. `pcif_demo_7b5a8c1d`). Editing this field immediately clears any previously displayed results to prevent stale-patient display. |
| **Current Consultation** | Clinician's current consultation notes. Transient — never stored, never persisted to localStorage or sessionStorage. |

### Displayed Output

All four structured fields from `assistant.*` plus `disclaimer` are rendered:

| Section | Source field | Empty state |
| :--- | :--- | :--- |
| Context Summary | `assistant.context_summary` | "No summary was returned." |
| Relevant Current Patient Context | `assistant.relevant_current_context` | "No relevant current patient-reported context was identified for this consultation." |
| Longitudinal Context | `assistant.relevant_longitudinal_changes` | "No relevant longitudinal changes were identified." |
| Items to Verify | `assistant.items_to_verify` | "No additional items were identified for verification." |
| Disclaimer | `disclaimer` | Hidden if not present |

### Patient-Reported Provenance

A visible label is always shown alongside results:

> **Patient-reported context:** Information shown here is derived from patient-reported Nutrition and Mental Wellness interactions. These records have not been clinically confirmed by a clinician.

This label ensures the clinician understands the provenance and limits of the displayed context.

### No Authentication (Prototype Limitation)

> [!CAUTION]
> This interface is a **prototype** and does not currently verify clinician identity or authorize access to patient identifiers. A supporting note is displayed in the UI: *"Prototype identifier only. Verified clinician authentication and patient lookup are not implemented."*
>
> Clinician authentication, role-based access control, and session management are not implemented in Day 13 and must be addressed before any production deployment.

### No Patient Search

There is no patient directory, patient search, or patient demographics database. The clinician manually enters the patient ID for prototype testing.

### Explicit Doctor-Note Persistence (Day 14)

Day 14 introduces explicit clinician-authored note persistence into the dedicated `doctor_notes` collection (`record_type = "doctor_confirmed"`). Clinician notes are stored separately from CCEE `patient_context` items (`record_type = "patient_reported"`). See [`docs/DOCTOR_NOTES.md`](file:///c:/Users/Bamathi%20G/OneDrive/Desktop/PCIF/docs/DOCTOR_NOTES.md) for complete details.


### Error Behaviour

On API or network failure, the interface:
- Clears any stale patient context result
- Displays a generic safe message: *"Unable to generate patient context right now. Please try again."*
- Never exposes stack traces, MongoDB connection details, Gemini errors, or API keys

### Design System

The clinician interface reuses all existing PCIF design tokens: `--bg-page`, `--text-dark`, `--primary-terracotta`, `--font-serif` (Playfair Display), `--font-sans` (Plus Jakarta Sans). No new fonts or design frameworks were introduced.
