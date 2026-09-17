# PCIF Database Architecture & Persistence Specification

This document details the MongoDB data persistence layer for the **Patient Context Intelligence Framework (PCIF)**.

---

## 1. MongoDB Role in PCIF

PCIF utilizes MongoDB as a shared, document-based longitudinal context store. The database provides a persistent repository for compressed clinical context items extracted by the **Clinical Context Extraction Engine (CCEE)** across patient interactions with both specialized AI conversational agents (**Nutrition AI** and **Mental Wellness AI**).

### Logical Collections

| Collection Name | Role / Purpose | Day 9 Implementation Status |
| :--- | :--- | :--- |
| `patient_context` | Stores validated CCEE clinical context items associated with patient IDs. | **Implemented & Active** |
| `users` | Stores patient and doctor user accounts and profiles. | Documented (Deferred to future Auth) |
| `doctor_notes` | Stores clinician consultation entries and confirmed findings. | Documented (Deferred to Day 12+) |

---

## 2. Core Privacy Guarantee

> [!IMPORTANT]
> **PCIF strictly prohibits persisting raw conversational data in MongoDB.**

To protect patient privacy and optimize storage efficiency:
- **Do NOT store**: Full chat transcripts, raw chat messages, system instructions, prompt strings, internal AI reasoning steps, or provider (Gemini) response objects.
- **Store ONLY**: Validated, compressed `ClinicalContextItem` records extracted by CCEE alongside database management metadata (`patient_id`, `captured_at`).

---

## 3. `patient_context` Document Structure

Each document in the `patient_context` collection represents a single extracted clinical context item.

### Schema Definition

```json
{
  "_id": "66e9c9a0f1d2e3456789abcd",
  "patient_id": "patient_demo_001",
  "category": "sleep",
  "summary": "Reduced sleep associated with exam stress",
  "source": "mental_wellness",
  "record_type": "patient_reported",
  "value": "5 hours/night",
  "duration": "this week",
  "captured_at": ISODate("2026-09-17T22:30:00.000Z")
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

## 4. Shared Longitudinal Storage & Lineage

Both **Nutrition AI** and **Mental Wellness AI** write to the **same** `patient_context` collection under a shared `patient_id`.

- **Nutrition AI Record Example**:
  ```json
  {
    "patient_id": "patient_demo_001",
    "category": "hydration",
    "summary": "Low fluid intake on college days",
    "source": "nutrition",
    "record_type": "patient_reported",
    "value": "1 glass/day",
    "captured_at": ISODate("2026-09-17T22:35:00Z")
  }
  ```

- **Mental Wellness AI Record Example**:
  ```json
  {
    "patient_id": "patient_demo_001",
    "category": "sleep",
    "summary": "Difficulty sleeping due to academic anxiety",
    "source": "mental_wellness",
    "record_type": "patient_reported",
    "value": "4-5 hours/night",
    "captured_at": ISODate("2026-09-17T22:36:00Z")
  }
  ```

Querying `get_patient_context("patient_demo_001")` retrieves both records ordered deterministically from **oldest to newest** by `captured_at`.

---

## 5. Environment Configuration

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

## 6. Database Repository API (`database/patient_context_repository.py`)

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

## 7. Connection & Error Behavior

- **Fail-Safe Exception Handling**: Missing or blank `MONGODB_URI` or database connection failures raise explicit controlled `ConnectionError` or `RuntimeError`. Errors are never swallowed, and fake success responses are never returned.
- **Health Check Safety**: `ping_database()` pings the MongoDB server and returns operational status safely without exposing credentials, connection URIs, stack traces, or patient data.

---

## 8. Current Day 9 Scope & Limitations

- **No Semantic Deduplication Yet**: Context items are saved as discrete records. Deduplication and longitudinal trend merging will be implemented in Day 11.
- **No Automatic Chat Triggers Yet**: Direct chat-to-database automatic pipeline hooks will be connected in Day 10.
- **Security Scope**: PCIF stores structured CCEE context in MongoDB. Transport and storage encryption depend on infrastructure configuration (TLS/SSL and MongoDB disk encryption).
