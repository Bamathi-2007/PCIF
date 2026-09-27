# PCIF Database Architecture & Persistence Specification

This document details the MongoDB data persistence layer for the **Patient Context Intelligence Framework (PCIF)**.

---

## 1. MongoDB Role in PCIF

PCIF utilizes MongoDB as a shared, document-based longitudinal context store. The database provides a persistent repository for compressed clinical context items extracted by the **Clinical Context Extraction Engine (CCEE)** across patient interactions with both specialized AI conversational agents (**Nutrition AI** and **Mental Wellness AI**).

### Logical Collections

| Collection Name | Role / Purpose | Implementation Status |
| :--- | :--- | :--- |
| `patient_context` | Stores validated CCEE clinical context items associated with patient IDs. | **Implemented & Active (Day 9/10/11)** |
| `users` | Stores patient and doctor user accounts and profiles. | Documented (Deferred to future Auth) |
| `doctor_notes` | Stores explicitly clinician-authored notes and confirmed findings. | **Implemented & Active (Day 14)** |

---

## 2. Core Privacy Guarantee

> [!IMPORTANT]
> **PCIF strictly prohibits persisting raw conversational data in MongoDB.**

To protect patient privacy and optimize storage efficiency:
- **Do NOT store**: Full chat transcripts, raw chat messages, assistant responses, system instructions, prompt strings, internal AI reasoning steps, or provider (Gemini) response objects.
- **Store ONLY**: Validated, compressed `ClinicalContextItem` records extracted by CCEE alongside database management metadata (`patient_id`, `captured_at`).

---

## 3. Day 10 Integration Architecture & Flow

```text
Nutrition AI conversation ────────┐
                                  │
                                  ├──► CCEE ──► VALIDATED CONTEXT ──► MONGODB patient_context
                                  │
Mental Wellness AI conversation ──┘
```

### End-to-End Primary Flow
1. Patient sends a message to **Nutrition AI** or **Mental Wellness AI** endpoint (`/api/nutrition/chat` or `/api/mental-wellness/chat`).
2. Endpoint generates the patient-facing AI conversational response via Google Gemini.
3. System sends the role-aware conversation (ending with the current user turn) to the frozen **Clinical Context Extraction Engine (CCEE)**.
4. CCEE validates and compresses clinical facts into a list of `ClinicalContextItem` objects.
5. **Context Persistence Service** saves valid items to MongoDB `patient_context` collection using `PatientContextRepository`.
6. API returns the conversational reply alongside `context_persistence` metadata (`status`: `saved` | `no_relevant_context` | `failed`, `saved_count`: N).

---

## 4. `patient_context` Document Structure

Each document in the `patient_context` collection represents a single extracted clinical context item.

### Schema Definition

### Schema Definition

```json
{
  "_id": "66e9c9a0f1d2e3456789abcd",
  "patient_id": "pcif_demo_7b5a8c1d-...",
  "category": "sleep",
  "summary": "Reduced sleep associated with exam stress",
  "source": "mental_wellness",
  "record_type": "patient_reported",
  "value": "5 hours/night",
  "duration": "this week",
  "captured_at": ISODate("2026-09-18T22:30:00.000Z"),
  "is_current": true,
  "superseded_at": null,
  "superseded_by": null
}
```

### Field Reference

| Field Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `string` | Yes | MongoDB unique document identifier (converted from `ObjectId` to `str` for clean domain representation). |
| `patient_id` | `string` | Yes | Application-level patient identifier. |
| `category` | `string` | Yes | Clinical category (e.g. `sleep`, `hydration`, `mood`, `nutrition`). |
| `summary` | `string` | Yes | Concise clinical summary of reported phenomenon. |
| `source` | `string` | Yes | Lineage origin (`nutrition` or `mental_wellness`). |
| `record_type` | `string` | Yes | Validation status, strictly `"patient_reported"`. |
| `value` | `string` | Optional | Quantitative or qualitative metric (omitted if `None`). |
| `duration` | `string` | Optional | Reported timeframe or duration (omitted if `None`). |
| `captured_at` | `UTC DateTime` | Yes | Database timestamp (`datetime.now(timezone.utc)`) when PCIF persisted the extracted record. |
| `is_current` | `boolean` | Yes | Indicates if record represents active current patient state (`true`) or superseded historical state (`false`). Defaults to `true`. |
| `superseded_at` | `UTC DateTime` | Optional | Timestamp when record was superseded by a newer update (omitted/null if `is_current` is `true`). |
| `superseded_by` | `string` | Optional | String `_id` of the newer record that superseded this record (omitted/null if `is_current` is `true`). |

> [!NOTE]
> `captured_at` is purely database metadata indicating when the record was persisted by PCIF. It does **not** represent clinical onset date or historical symptom origin. `is_current`, `superseded_at`, and `superseded_by` are database-level document metadata; `ClinicalContextItem` in `ccee/schema.py` remains completely frozen.

---

## 5. Day 11 Longitudinal Consolidation Architecture

Day 11 introduces **Database-Level Longitudinal Consolidation** to prevent repeated chat turns from accumulating noisy duplicate records while preserving meaningful historical changes over time.

```text
                                  ┌──► DUPLICATE ──► Skip insert (keep existing record active)
                                  │
CCEE Output ──► Candidate Matching ┼──► UPDATE    ──► Insert NEW record (is_current=true)
                                  │                   └─► Supersede OLD record (is_current=false)
                                  │
                                  └──► DISTINCT  ──► Insert NEW record (is_current=true)
```

### Three Relation Types & Decision Logic

1. **DUPLICATE**:
   - The new item describes essentially the same underlying phenomenon and materially the same current state.
   - **Fast Path**: Deterministic exact/normalized comparison (trim, lowercase, space normalization) across `category`, `summary`, `source`, `record_type`, `value`, `duration`. Executes immediately without Gemini API call.
   - **Poorer Record Safeguard**: If an existing active record contains duration/detail and a new item matches summary/value but lacks duration, it is treated as DUPLICATE (a poorer representation never replaces a richer active record).
   - **Action**: Skip insertion, increment `duplicate_count`. Old record remains active.

2. **UPDATE**:
   - The new item refers to the same underlying phenomenon but contains a materially changed metric (e.g. sleep 5h → 7h) or enriched state (e.g. adding duration).
   - **Fail-Safe Sequence**:
     1. Insert NEW record first with `is_current = true`.
     2. Only after successful insertion, mark previous record `is_current = false`, `superseded_at = UTC timestamp`, `superseded_by = <new_record_id>`.
     3. If superseding the old record fails, both records remain active (preserving history).
   - **Action**: Insert new record, supersede old record, increment `inserted_count` and `superseded_count`.

3. **DISTINCT**:
   - The new item describes a genuinely separate phenomenon (e.g. headache vs stomach discomfort).
   - **Default Rule**: When semantic classification is uncertain or fails, system defaults to DISTINCT to prioritize information preservation over false merges.
   - **Action**: Insert new record with `is_current = true`, increment `inserted_count`.

### Source-Aware Scope
Deduplication and update candidate matching occur strictly within the same `patient_id` + `source` + `category`. Cross-source items (e.g. Nutrition AI vs Mental Wellness AI) are preserved independently to protect source provenance.

---

## 6. Prototype Patient Session Identifier (Without Authentication)

During the current prototype phase (Day 10/11), authentication is not implemented.
- **Frontend Utility**: `frontend/src/utils/patientSession.js` generates an opaque UUID (`crypto.randomUUID()`) and stores ONLY that identifier in browser `sessionStorage`.
- **Cross-Pathway Reuse**: The same anonymous ID is reused across both Nutrition AI and Mental Wellness AI pages during that browser session.
- **Disclaimer**: This session identifier is an anonymous prototype identifier, not authentication, and does not establish verified patient identity. It will later be replaced by an authenticated application-level patient ID.

---

## 7. Operational Resilience & Error Isolation

1. **Independent Chat Availability**: Patient chat generation and context storage persistence are separate concerns. If CCEE or MongoDB persistence fails, the patient-facing conversational AI answer is STILL returned successfully.
2. **Distinguishable Outcomes**:
   - `saved`: CCEE extracted items and MongoDB persisted or deduplicated them (`inserted_count > 0` or `duplicate_count > 0`).
   - `no_relevant_context`: CCEE successfully ran and returned `[]` (`saved_count == 0`). Zero DB calls performed.
   - `failed`: CCEE or database persistence raised an exception (`saved_count == 0`). Controlled server-side error logging occurs without exposing DB credentials or stack traces to the client.
3. **No Fake Success**: `failed` persistence is NEVER translated into `no_relevant_context`.

---

## 8. Environment Configuration

MongoDB connection settings are configured strictly via environment variables. `MONGODB_URI` must be explicitly configured (no silent fallback to localhost):

```bash
# Environment variables (.env)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=pcif
```

- Local Development: `MONGODB_URI=mongodb://localhost:27017`
- Production / Cloud: MongoDB Atlas or managed URI supplied via `MONGODB_URI`.
- Credentials must **never** be hardcoded or committed to version control.
- Missing or blank `MONGODB_URI` raises a controlled `ConnectionError` without leaking URI credentials.

---

## 9. Database Repository API (`database/patient_context_repository.py`)

### Core Methods

1. **`save_context_item(patient_id: str, item: ClinicalContextItem) -> str`**
   - Persists a single `ClinicalContextItem` with `is_current=True`.
   - Returns inserted document ID string.

2. **`save_context_items(patient_id: str, items: List[ClinicalContextItem]) -> List[str]`**
   - Persists a batch of `ClinicalContextItem` objects with `is_current=True`.
   - Rejects empty/blank `patient_id` (raises `ValueError`).
   - If `items == []`, performs zero DB operations and returns `[]`.
   - Returns list of inserted document ID strings.

3. **`get_patient_context(patient_id: str) -> List[Dict[str, Any]]`**
   - Retrieves full historical record timeline for `patient_id` (both active and superseded records).
   - Ordered deterministically: `captured_at` ascending (`oldest → newest`).
   - Converts `_id` to `str` format.

4. **`get_current_patient_context(patient_id: str) -> List[Dict[str, Any]]`**
   - Retrieves active current profile records for `patient_id` (`is_current == true` or missing `is_current` field).
   - Ordered deterministically: `captured_at` ascending.

5. **`get_current_context_candidates(patient_id: str, source: str, category: str) -> List[Dict[str, Any]]`**
   - Retrieves active candidate records matching `patient_id`, `source`, and `category`.

6. **`mark_context_superseded(old_id: str, new_id: str, superseded_at: Optional[datetime] = None, patient_id: Optional[str] = None) -> bool`**
   - Updates document `_id = ObjectId(old_id)`: sets `is_current = false`, `superseded_at = UTC timestamp`, `superseded_by = new_id`.

7. **`delete_patient_context(patient_id: str) -> int`**
   - Deletes all records for `patient_id`.
   - Used for test isolation and cleanup.

### Indexing

The repository automatically ensures the following background indexes exist:
- Single index: `patient_id` (ascending)
- Compound index: `(patient_id, captured_at)` (ascending)
- Compound index: `(patient_id, is_current, captured_at)` (ascending)
- Compound index: `(patient_id, source, category)` (ascending)

---

## 10. Day 11 Scope & Known Limitations

- **Explicit Resolution Limitation**: An empty CCEE extraction `[]` means "No new relevant context extracted from this turn". It does **not** mean previous clinical problems have resolved. PCIF does not automatically deactivate old records based on `[]`.
- **Frozen CCEE Unchanged**: CCEE schema and extraction rules remain frozen from Day 5-8.
- **Security & Privacy Wording**: Only structured CCEE context and storage metadata are persisted. Raw chat transcripts remain unpersisted.

---

## 11. Day 14 Clinician-Authored Note Persistence (`doctor_notes`)

Day 14 implements dedicated persistence for explicitly clinician-authored notes in the isolated `doctor_notes` collection:
- **Trust Boundary**: `patient_context` (`patient_reported`) and `doctor_notes` (`doctor_confirmed`) remain strictly separated in different collections.
- **Append-Only**: Clinician notes are append-only; no CCEE processing or Day 11 consolidation is performed.
- **Server-Controlled Provenance**: `record_type = "doctor_confirmed"` and `created_at` (UTC persistence timestamp) are strictly server-controlled.
- **Detailed Specification**: See [`docs/DOCTOR_NOTES.md`](file:///c:/Users/Bamathi%20G/OneDrive/Desktop/PCIF/docs/DOCTOR_NOTES.md).


