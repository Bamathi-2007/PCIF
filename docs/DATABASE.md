# PCIF Database Architecture & Persistence Specification

This document details the MongoDB data persistence layer for the **Patient Context Intelligence Framework (PCIF)**.

---

## 1. MongoDB Role in PCIF

PCIF utilizes MongoDB as a shared, document-based longitudinal context store. The database provides a persistent repository for compressed clinical context items extracted by the **Clinical Context Extraction Engine (CCEE)** across patient interactions with both specialized AI conversational agents (**Nutrition AI** and **Mental Wellness AI**).

### Logical Collections

| Collection Name | Role / Purpose | Implementation Status |
| :--- | :--- | :--- |
| `patient_context` | Stores validated CCEE clinical context items associated with patient IDs. | **Implemented & Active (Day 9/10)** |
| `users` | Stores patient and doctor user accounts and profiles. | Documented (Deferred to future Auth) |
| `doctor_notes` | Stores clinician consultation entries and confirmed findings. | Documented (Deferred to Day 12+) |

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
  "captured_at": ISODate("2026-09-18T22:30:00.000Z")
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

> [!NOTE]
> `captured_at` is purely database metadata indicating when the record was persisted by PCIF. It does **not** represent clinical onset date or historical symptom origin.

---

## 5. Prototype Patient Session Identifier (Without Authentication)

During the current prototype phase (Day 10), authentication is not implemented.
- **Frontend Utility**: `frontend/src/utils/patientSession.js` generates an opaque UUID (`crypto.randomUUID()`) and stores ONLY that identifier in browser `sessionStorage`.
- **Cross-Pathway Reuse**: The same anonymous ID is reused across both Nutrition AI and Mental Wellness AI pages during that browser session.
- **Disclaimer**: This session identifier is an anonymous prototype identifier, not authentication, and does not establish verified patient identity. It will later be replaced by an authenticated application-level patient ID.

---

## 6. Shared Longitudinal Storage & Lineage

Both **Nutrition AI** and **Mental Wellness AI** write to the **same** `patient_context` collection under a shared `patient_id`.

- **Nutrition AI Record Example**:
  ```json
  {
    "patient_id": "pcif_demo_7b5a8c1d-...",
    "category": "hydration",
    "summary": "Low fluid intake on college days",
    "source": "nutrition",
    "record_type": "patient_reported",
    "value": "1 glass/day",
    "captured_at": ISODate("2026-09-18T22:35:00Z")
  }
  ```

- **Mental Wellness AI Record Example**:
  ```json
  {
    "patient_id": "pcif_demo_7b5a8c1d-...",
    "category": "sleep",
    "summary": "Difficulty sleeping due to academic anxiety",
    "source": "mental_wellness",
    "record_type": "patient_reported",
    "value": "4-5 hours/night",
    "captured_at": ISODate("2026-09-18T22:36:00Z")
  }
  ```

Querying `get_patient_context("pcif_demo_7b5a8c1d-...")` retrieves both records ordered deterministically from **oldest to newest** by `captured_at`.

---

## 7. Operational Resilience & Error Isolation

1. **Independent Chat Availability**: Patient chat generation and context storage persistence are separate concerns. If CCEE or MongoDB persistence fails, the patient-facing conversational AI answer is STILL returned successfully.
2. **Distinguishable Outcomes**:
   - `saved`: CCEE extracted items and MongoDB persisted them (`saved_count > 0`).
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
   - Persists a single `ClinicalContextItem`.
   - Returns inserted document ID string.

2. **`save_context_items(patient_id: str, items: List[ClinicalContextItem]) -> List[str]`**
   - Persists a batch of `ClinicalContextItem` objects.
   - Rejects empty/blank `patient_id` (raises `ValueError`).
   - If `items == []`, performs zero DB operations and returns `[]`.
   - Returns list of inserted document ID strings.

3. **`get_patient_context(patient_id: str) -> List[Dict[str, Any]]`**
   - Retrieves all stored records for `patient_id`.
   - Ordered deterministically: `captured_at` ascending (`oldest → newest`).
   - Converts `_id` to `str` format so downstream domain code receives clean standard Python types without requiring `bson.ObjectId`.

4. **`delete_patient_context(patient_id: str) -> int`**
   - Deletes all records for `patient_id`.
   - Used for test isolation and cleanup.

### Indexing

The repository automatically ensures the following background indexes exist:
- Single index: `patient_id` (ascending)
- Compound index: `(patient_id, captured_at)` (ascending)

---

## 10. Current Day 10 Scope & Known Limitations

- **Cross-Session / Turn Duplication**: Repeated user turns or multi-turn chats may temporarily extract duplicate or recurring records across turns in Day 10. Database-level deduplication and longitudinal consolidation will be implemented in **Day 11**.
- **Frozen CCEE Unchanged**: CCEE schema and extraction rules remain frozen from Day 5-8.
- **Security & Privacy Wording**: Only structured CCEE context is persisted. The anonymous browser session patient ID is a prototype identifier, not authentication.
