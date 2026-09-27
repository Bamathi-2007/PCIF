# PCIF Clinician-Authored Notes Specification (`doctor_notes`)

This document details the architecture, data model, security boundaries, and trust principles for clinician-authored note persistence in the **Patient Context Intelligence Framework (PCIF)**.

---

## 1. Purpose & Core Trust Boundary

PCIF maintains a strict distinction between patient-reported information and clinician-confirmed medical records:

$$\text{AI-Generated Assistance} \neq \text{Clinician-Confirmed Record}$$

To enforce this boundary at the database level:
- **`patient_context` Collection**: Stores validated clinical context items extracted by CCEE from patient conversational interactions (`record_type = "patient_reported"`).
- **`doctor_notes` Collection**: Stores text explicitly authored and saved by an attending clinician (`record_type = "doctor_confirmed"`).

> [!IMPORTANT]
> **Separation Guarantee**:
> 1. Clinician notes are **never** stored in `patient_context`.
> 2. AI-generated assistance outputs, summaries, or items to verify are **never** automatically persisted to `doctor_notes`.
> 3. `doctor_notes` records are strictly authored and confirmed by the clinician.

---

## 2. Document Schema

Documents in the `doctor_notes` collection have the following minimal schema:

```json
{
  "_id": "66e9c9a0f1d2e3456789abcd",
  "patient_id": "pcif_demo_7b5a8c1d",
  "note": "Reviewed fatigue symptoms. Recommended thyroid panel and routine blood work.",
  "record_type": "doctor_confirmed",
  "created_at": "2026-09-27T14:30:00.000Z"
}
```

### Field Reference

| Field Name | Type | Controlled By | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` / `string` | MongoDB / Server | Unique document identifier (converted to `string` in API responses). |
| `patient_id` | `string` | Client | Application-level patient identifier. Must be non-empty. |
| `note` | `string` | Client (Clinician) | Explicit clinician-authored clinical findings and notes. Must be non-empty. |
| `record_type` | `string` | Server | Strict provenance tag, unconditionally set to `"doctor_confirmed"`. Caller cannot override. |
| `created_at` | `UTC DateTime` | Server | Database persistence timestamp (`datetime.now(timezone.utc)`). |

### `created_at` Semantics
`created_at` indicates the exact timestamp when the record was persisted into the database by PCIF. It does **not** indicate:
- Symptom onset date
- Clinical diagnosis date
- Encounter/consultation date

---

## 3. Append-Only Persistence Model

In Day 14, clinician notes are strictly **append-only**:
- If multiple notes are explicitly saved for the same patient, all records are preserved independently.
- Doctor notes **never** pass through CCEE or Day 11 duplicate/update/distinct longitudinal consolidation.
- No notes are merged, deduplicated, overwritten, or marked superseded.
- Fields like `is_current`, `superseded_by`, and `superseded_at` are not present on `doctor_notes`.

---

## 4. Repository Architecture (`database/doctor_notes_repository.py`)

The repository uses the existing shared `MongoDBManager` connection without instantiating separate `MongoClient` objects.

### Methods

1. **`save_doctor_note(patient_id: str, note: str) -> Dict[str, Any]`**
   - Validates `patient_id` and `note` (rejects blank/whitespace).
   - Inserts document into `doctor_notes` collection with server-controlled `record_type="doctor_confirmed"` and UTC `created_at`.
   - Returns clean dictionary with string ID.

2. **`get_doctor_notes(patient_id: str) -> List[Dict[str, Any]]`**
   - Validates `patient_id`.
   - Queries `doctor_notes` by `patient_id`.
   - Returns notes ordered newest-first by `created_at` descending (`DESCENDING`).
   - Converts `_id` to string `id`. Returns `[]` if no notes exist.

3. **`delete_doctor_notes(patient_id: str) -> int`**
   - Deletes all notes for `patient_id` for test isolation and cleanup.

### Indexes
The repository ensures the following background indexes on `doctor_notes`:
- Single index: `patient_id` (ascending)
- Compound index: `(patient_id, created_at)` (ascending / timeline)

---

## 5. API Endpoints

### 1. `POST /api/doctor/notes`
Saves an explicitly clinician-authored note.

- **Request**:
  ```json
  {
    "patient_id": "pcif_demo_7b5a8c1d",
    "note": "Clinician personally reviewed fatigue symptoms. No red flag signs."
  }
  ```
- **Response** (`HTTP 200`):
  ```json
  {
    "status": "saved",
    "note": {
      "id": "66e9c9a0f1d2e3456789abcd",
      "patient_id": "pcif_demo_7b5a8c1d",
      "note": "Clinician personally reviewed fatigue symptoms. No red flag signs.",
      "record_type": "doctor_confirmed",
      "created_at": "2026-09-27T14:30:00.000Z"
    }
  }
  ```

### 2. `GET /api/doctor/notes/{patient_id}`
Retrieves all saved clinician notes for a given patient ID, ordered newest-first.

- **Response** (`HTTP 200`):
  ```json
  {
    "patient_id": "pcif_demo_7b5a8c1d",
    "notes": [
      {
        "id": "66e9c9a0f1d2e3456789abcd",
        "patient_id": "pcif_demo_7b5a8c1d",
        "note": "Clinician personally reviewed fatigue symptoms. No red flag signs.",
        "record_type": "doctor_confirmed",
        "created_at": "2026-09-27T14:30:00.000Z"
      }
    ]
  }
  ```

---

## 6. Frontend Trust Boundary & UI Behavior

### Clinician Workspace (`/doctor`)
1. **Visibly Separate Sections**:
   - **Patient & Consultation**: Transient consultation input and patient ID.
   - **Clinician-Authored Notes**: Dedicated note editor and previous saved notes list.
2. **Dual Provenance Display**:
   - `PATIENT-REPORTED CONTEXT`: Unconfirmed lifestyle/wellness context extracted by CCEE.
   - `CLINICIAN-AUTHORED NOTES`: Explicit notes entered in the clinician workspace.

3. **Empty Textarea**: The note textarea starts empty and is never prefilled from AI summaries or consultation text.
4. **Save Behavior**:
   - On save success: note textarea clears, Previous Clinician Notes refreshes, and the current Doctor AI assistance result is preserved (not regenerated).
   - On save failure: the unsaved clinician text is retained in the textarea, and a safe error banner is displayed.
5. **Patient-Switch Safety**: Changing the patient ID immediately clears Doctor AI assistance results, error messages, note textarea, loaded clinician notes, and save status states.

---

## 7. Security & Prototype Limitations

> [!CAUTION]
> **The current prototype does not verify clinician identity or authorize access to patient records.**
>
> 1. **No Clinician Authentication**: The system does not authenticate clinician logins, licence numbers, hospital affiliations, or department roles.
> 2. **No Role-Based Access Control**: Any user with access to `/doctor` can input patient IDs and save notes in this research prototype.
> 3. **Doctor Context AI Integration (Day 15)**: Stored clinician notes are retrieved by `DoctorContextService` (capped at 10 most recent notes) to provide context for the Doctor Context AI, while strictly preserving clinician-authored provenance. Doctor AI outputs are never auto-saved into `doctor_notes`.
> 4. **No Editing / Deleting in UI**: Notes are append-only. Note editing, revision trees, and soft-deletes are not implemented in Day 15.

