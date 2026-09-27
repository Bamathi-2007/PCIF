/**
 * DoctorDashboard.jsx — PCIF Day 14 Clinician Context Workspace & Confirmed Note Persistence
 *
 * Provides a context review and explicit clinician-note persistence interface for attending clinicians.
 *
 * Core Trust Boundary:
 *  - AI-generated assistance != clinician-confirmed record.
 *  - patient_context (CCEE, "patient_reported") is strictly separated from doctor_notes ("doctor_confirmed").
 *  - Clinician-authored notes are explicitly typed and saved; AI context is NEVER auto-saved.
 *  - Append-only doctor_notes persistence; no CCEE or Day 11 consolidation.
 *  - Security Note: The current prototype does not verify clinician identity or authorize access to patient records.
 */
import React, { useState, useCallback } from "react";
import {
  AlertCircle,
  Stethoscope,
  ClipboardList,
  RefreshCw,
  FileEdit,
  Save,
  CheckCircle2,
  BookmarkCheck,
  Clock,
  ShieldAlert,
} from "lucide-react";

/* ─── Helper Functions ──────────────────────────────────────────────────── */

function formatNoteDate(isoString) {
  if (!isoString) return "";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return String(isoString);
    return d.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(isoString);
  }
}

/* ─── Sub-components ─────────────────────────────────────────────────────── */

function ContextItemList({ items, emptyMessage }) {
  if (!items || items.length === 0) {
    return <p className="dr-empty-state">{emptyMessage}</p>;
  }
  return (
    <ul className="dr-context-list" aria-label="Context items">
      {items.map((item, idx) => (
        <li key={idx} className="dr-context-item">
          {typeof item === "string" ? item : JSON.stringify(item)}
        </li>
      ))}
    </ul>
  );
}

function VerifyItemList({ items }) {
  if (!items || items.length === 0) {
    return (
      <p className="dr-empty-state">No additional items were identified for verification.</p>
    );
  }
  return (
    <ul className="dr-context-list" aria-label="Items to verify">
      {items.map((item, idx) => (
        <li key={idx} className="dr-context-item dr-verify-item">
          {typeof item === "string" ? item : JSON.stringify(item)}
        </li>
      ))}
    </ul>
  );
}

function PreviousNotesList({ notes, hasLoadedNotes }) {
  if (!hasLoadedNotes) {
    return (
      <p className="dr-empty-state">
        Generate context or save a note to review previous clinician notes for this patient.
      </p>
    );
  }
  if (!notes || notes.length === 0) {
    return (
      <p className="dr-empty-state">
        No clinician-authored notes have been saved for this patient.
      </p>
    );
  }
  return (
    <div className="dr-notes-list" aria-label="Previous Clinician Notes">
      {notes.map((n, idx) => (
        <div key={n.id || idx} className="dr-note-card">
          <div className="dr-note-header">
            <span className="dr-note-badge">
              <BookmarkCheck size={12} aria-hidden="true" />
              Clinician-authored
            </span>
            {n.created_at && (
              <span className="dr-note-date">
                <Clock size={12} aria-hidden="true" />
                Saved on {formatNoteDate(n.created_at)}
              </span>
            )}
          </div>
          <p className="dr-note-body">{n.note}</p>
        </div>
      ))}
    </div>
  );
}

/* ─── Main Component ─────────────────────────────────────────────────────── */

export default function DoctorDashboard() {
  // Input states
  const [patientId, setPatientId]               = useState("");
  const [consultation, setConsultation]         = useState("");
  const [clinicianNote, setClinicianNote]       = useState("");

  // Context assistance states (Day 12/13)
  const [isLoading, setIsLoading]               = useState(false);
  const [result, setResult]                     = useState(null);
  const [error, setError]                       = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  // Clinician notes states (Day 14)
  const [doctorNotes, setDoctorNotes]           = useState([]);
  const [hasLoadedNotes, setHasLoadedNotes]     = useState(false);
  const [isSavingNote, setIsSavingNote]         = useState(false);
  const [saveStatus, setSaveStatus]             = useState(null);
  const [saveError, setSaveError]               = useState(null);
  const [noteValidationError, setNoteValidationError] = useState(null);

  /* ── Fetch Doctor Notes ───────────────────────────────────────────────── */
  const fetchDoctorNotes = useCallback(async (pid) => {
    if (!pid || !pid.trim()) return;
    try {
      const response = await fetch(`/api/doctor/notes/${encodeURIComponent(pid.trim())}`);
      if (response.ok) {
        const data = await response.json();
        setDoctorNotes(data.notes || []);
        setHasLoadedNotes(true);
      }
    } catch (err) {
      console.error("[PCIF Doctor] Failed to fetch clinician notes:", err);
    }
  }, []);

  /* ── Patient-switch safety ──────────────────────────────────────────────
     Immediately clear all patient-specific context, errors, and clinician notes
     whenever the patient ID changes. This ensures Patient A data never appears
     alongside a Patient B ID. */
  const handlePatientIdChange = useCallback(
    (e) => {
      const newPid = e.target.value;
      setPatientId(newPid);

      // Immediately clear all previous patient data
      setResult(null);
      setError(null);
      setClinicianNote("");
      setDoctorNotes([]);
      setHasLoadedNotes(false);
      setSaveStatus(null);
      setSaveError(null);
      setNoteValidationError(null);

      if (validationErrors.patientId) {
        setValidationErrors((prev) => ({ ...prev, patientId: undefined }));
      }
    },
    [validationErrors.patientId]
  );

  const handleConsultationChange = useCallback(
    (e) => {
      setConsultation(e.target.value);
      if (validationErrors.consultation) {
        setValidationErrors((prev) => ({ ...prev, consultation: undefined }));
      }
    },
    [validationErrors.consultation]
  );

  const handleClinicianNoteChange = useCallback((e) => {
    setClinicianNote(e.target.value);
    if (noteValidationError) {
      setNoteValidationError(null);
    }
    if (saveStatus) {
      setSaveStatus(null);
    }
    if (saveError) {
      setSaveError(null);
    }
  }, [noteValidationError, saveStatus, saveError]);

  /* ── Validation ─────────────────────────────────────────────────────── */
  function validateContextInput() {
    const errs = {};
    if (!patientId.trim())    errs.patientId    = "Patient ID is required.";
    if (!consultation.trim()) errs.consultation = "Consultation notes are required.";
    return errs;
  }

  /* ── Generate Context ───────────────────────────────────────────────── */
  const handleGenerate = async () => {
    const errs = validateContextInput();
    if (Object.keys(errs).length > 0) {
      setValidationErrors(errs);
      return;
    }

    setValidationErrors({});
    setResult(null);   // always replace previous result before new request
    setError(null);
    setIsLoading(true);

    const cleanPid = patientId.trim();

    try {
      const response = await fetch("/api/doctor/context", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id:   cleanPid,
          consultation: consultation.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      setResult(data);

      // On successful context generation, also retrieve clinician-authored notes
      await fetchDoctorNotes(cleanPid);
    } catch (err) {
      console.error("[PCIF Doctor] Context generation failed:", err);
      // On failure: clear stale result, show safe generic error only
      setResult(null);
      setError("Unable to generate patient context right now. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  /* ── Save Clinician Note (Day 14) ───────────────────────────────────── */
  const handleSaveNote = async () => {
    if (!patientId.trim()) {
      setNoteValidationError("Patient ID is required to save a note.");
      return;
    }
    if (!clinicianNote.trim()) {
      setNoteValidationError("Note content is required.");
      return;
    }

    setNoteValidationError(null);
    setSaveError(null);
    setSaveStatus(null);
    setIsSavingNote(true);

    const cleanPid = patientId.trim();
    const cleanNote = clinicianNote.trim();

    try {
      const response = await fetch("/api/doctor/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: cleanPid,
          note: cleanNote,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      // Success handling:
      // 1. Show confirmation
      setSaveStatus("Clinician note saved.");
      // 2. Clear note textarea
      setClinicianNote("");
      // 3. Refresh previous clinician notes
      await fetchDoctorNotes(cleanPid);
      // (Current Doctor Context AI result is preserved; not regenerated)
    } catch (err) {
      console.error("[PCIF Doctor] Save clinician note failed:", err);
      // On failure: KEEP the unsaved clinician text, show safe error message
      setSaveError("Unable to save the clinician note right now. Please try again.");
    } finally {
      setIsSavingNote(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      handleGenerate();
    }
  };

  const hasResult = Boolean(result && result.assistant);

  /* ── Render ─────────────────────────────────────────────────────────── */
  return (
    <div className="dr-page">

      {/* ── Clinician Header ─────────────────────────────────────────── */}
      <header className="dr-header" role="banner">
        <div className="dr-header-brand">
          <span className="dr-brand-title">PCIF</span>
          <span className="dr-brand-sub">CLINICIAN CONTEXT WORKSPACE</span>
        </div>
        <div className="dr-header-badge" aria-hidden="true">
          <Stethoscope size={14} />
          <span>Context Review · Prototype</span>
        </div>
      </header>

      {/* ── Security & Trust Boundary Notification ─────────────────────── */}
      <div className="dr-top-banner" role="note">
        <div className="dr-top-banner-inner">
          <ShieldAlert size={15} aria-hidden="true" />
          <span>
            The current prototype does not verify clinician identity or authorize access to patient records.
          </span>
        </div>
      </div>

      {/* ── Two-column workspace ─────────────────────────────────────── */}
      <div className="dr-workspace">

        {/* Left Column — Inputs */}
        <div className="dr-left-column">

          {/* Section 1: Patient & Consultation */}
          <section className="dr-input-panel" aria-label="Consultation input">
            <div className="dr-panel-heading-row">
              <ClipboardList size={18} aria-hidden="true" />
              <h2 className="dr-panel-heading">Patient &amp; Consultation</h2>
            </div>

            {/* Patient ID */}
            <div className="dr-field-group">
              <label htmlFor="dr-patient-id" className="dr-field-label">
                Patient ID
              </label>
              <input
                id="dr-patient-id"
                type="text"
                className={"dr-text-input" + (validationErrors.patientId ? " dr-input-error" : "")}
                placeholder="e.g. pcif_demo_7b5a8c1d"
                value={patientId}
                onChange={handlePatientIdChange}
                disabled={isLoading || isSavingNote}
                autoComplete="off"
                spellCheck={false}
                aria-describedby={validationErrors.patientId ? "dr-pid-err" : "dr-pid-note"}
              />
              {validationErrors.patientId ? (
                <span id="dr-pid-err" className="dr-field-error" role="alert">
                  {validationErrors.patientId}
                </span>
              ) : (
                <span id="dr-pid-note" className="dr-proto-note">
                  Prototype identifier only. Verified clinician authentication and patient lookup are not implemented.
                </span>
              )}
            </div>

            {/* Consultation textarea */}
            <div className="dr-field-group">
              <label htmlFor="dr-consultation" className="dr-field-label">
                Current Consultation
              </label>
              <textarea
                id="dr-consultation"
                className={"dr-textarea" + (validationErrors.consultation ? " dr-input-error" : "")}
                placeholder="Patient reports morning fatigue and difficulty concentrating…"
                rows={6}
                value={consultation}
                onChange={handleConsultationChange}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                aria-describedby={validationErrors.consultation ? "dr-con-err" : "dr-con-note"}
              />
              {validationErrors.consultation ? (
                <span id="dr-con-err" className="dr-field-error" role="alert">
                  {validationErrors.consultation}
                </span>
              ) : (
                <span id="dr-con-note" className="dr-proto-note">
                  Consultation text is transient and is not stored. Ctrl+Enter to generate.
                </span>
              )}
            </div>

            {/* Generate button */}
            <button
              id="dr-generate-btn"
              className="dr-generate-btn"
              onClick={handleGenerate}
              disabled={isLoading}
              aria-busy={isLoading}
            >
              {isLoading ? (
                <>
                  <RefreshCw size={15} className="dr-spin" aria-hidden="true" />
                  Reviewing patient context…
                </>
              ) : (
                "Generate Context"
              )}
            </button>
          </section>

          {/* Section 2: Clinician-Authored Notes (Day 14) */}
          <section className="dr-input-panel dr-notes-panel" aria-label="Clinician-Authored Notes">
            <div className="dr-panel-heading-row">
              <FileEdit size={18} aria-hidden="true" />
              <h2 className="dr-panel-heading">Clinician-Authored Notes</h2>
            </div>

            {/* Provenance note */}
            <div className="dr-notes-provenance-note" role="note">
              This note is entered by the person using the clinician workspace and stored separately from patient-reported context.
            </div>

            {/* Note textarea */}
            <div className="dr-field-group">
              <label htmlFor="dr-clinician-note" className="dr-field-label">
                Clinician-Authored Note
              </label>
              <textarea
                id="dr-clinician-note"
                className={"dr-textarea" + (noteValidationError ? " dr-input-error" : "")}
                placeholder="Enter findings or context you have personally reviewed and wish to preserve..."
                rows={5}
                value={clinicianNote}
                onChange={handleClinicianNoteChange}
                disabled={isSavingNote}
                aria-describedby={noteValidationError ? "dr-note-err" : undefined}
              />
              {noteValidationError && (
                <span id="dr-note-err" className="dr-field-error" role="alert">
                  {noteValidationError}
                </span>
              )}
            </div>

            {/* Save Status / Error banner */}
            {saveStatus && (
              <div className="dr-save-success-banner" role="status">
                <CheckCircle2 size={15} aria-hidden="true" />
                <span>{saveStatus}</span>
              </div>
            )}
            {saveError && (
              <div className="dr-error-banner" role="alert">
                <AlertCircle size={15} aria-hidden="true" />
                <span>{saveError}</span>
              </div>
            )}

            {/* Save Clinician Note Button */}
            <button
              id="dr-save-note-btn"
              className="dr-save-note-btn"
              onClick={handleSaveNote}
              disabled={isSavingNote || !patientId.trim() || !clinicianNote.trim()}
              aria-busy={isSavingNote}
            >
              {isSavingNote ? (
                <>
                  <RefreshCw size={15} className="dr-spin" aria-hidden="true" />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={15} aria-hidden="true" />
                  Save Clinician Note
                </>
              )}
            </button>
          </section>

        </div>

        {/* Right Column — Results & Stored Records Panel */}
        <section
          className="dr-results-panel"
          aria-label="Contextual assistance and clinician notes"
          aria-live="polite"
        >

          {/* Idle placeholder */}
          {!hasResult && !error && !isLoading && !hasLoadedNotes && (
            <div className="dr-idle-state">
              <div className="dr-idle-icon" aria-hidden="true">
                <Stethoscope size={36} />
              </div>
              <p className="dr-idle-text">
                Enter a patient ID and consultation notes, then click{" "}
                <strong>Generate Context</strong> to review structured patient-reported background context and clinician notes.
              </p>
            </div>
          )}

          {/* Error state */}
          {error && !hasResult && (
            <div className="dr-error-banner" role="alert">
              <AlertCircle size={16} aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          {/* ── Class A: Patient-Reported Context (Day 12/13) ──────────────── */}
          {hasResult && (
            <div className="dr-results">

              {/* Provenance Header for Patient-Reported Context */}
              <div className="dr-provenance-header dr-provenance-patient">
                <span className="dr-provenance-title">PATIENT-REPORTED CONTEXT</span>
                <span className="dr-provenance-desc">
                  Information shown below is derived from patient interactions with Nutrition and Mental Wellness AI.
                  These records have not been clinically confirmed by a clinician.
                </span>
              </div>

              {/* 1. Context Summary */}
              <div className="dr-card" id="dr-section-summary">
                <h3 className="dr-section-heading">Context Summary</h3>
                <p className="dr-summary-text">
                  {result.assistant.context_summary || "No summary was returned."}
                </p>
              </div>

              {/* 2. Relevant Current Patient Context */}
              <div className="dr-card" id="dr-section-current">
                <h3 className="dr-section-heading">Relevant Current Patient Context</h3>
                <ContextItemList
                  items={result.assistant.relevant_current_context}
                  emptyMessage="No relevant current patient-reported context was identified for this consultation."
                />
              </div>

              {/* 3. Longitudinal Context */}
              <div className="dr-card" id="dr-section-longitudinal">
                <h3 className="dr-section-heading">Longitudinal Context</h3>
                <ContextItemList
                  items={result.assistant.relevant_longitudinal_changes}
                  emptyMessage="No relevant longitudinal changes were identified."
                />
              </div>

              {/* 4. Items to Verify */}
              <div className="dr-card dr-card-verify" id="dr-section-verify">
                <h3 className="dr-section-heading">Items to Verify</h3>
                <VerifyItemList items={result.assistant.items_to_verify} />
              </div>

              {/* 5. Disclaimer */}
              {result.disclaimer && (
                <div className="dr-disclaimer" role="note" id="dr-disclaimer">
                  {result.disclaimer}
                </div>
              )}

            </div>
          )}

          {/* ── Class B: Clinician-Authored Notes (Day 14) ──────────────────── */}
          {(hasLoadedNotes || hasResult) && (
            <div className="dr-confirmed-section" id="dr-section-confirmed-notes">
              <div className="dr-provenance-header dr-provenance-clinician">
                <span className="dr-provenance-title">CLINICIAN-AUTHORED NOTES</span>
                <span className="dr-provenance-desc">
                  Entered in the clinician workspace and stored separately in the doctor_notes collection.
                </span>
              </div>

              <div className="dr-card">
                <h3 className="dr-section-heading">Previous Clinician Notes</h3>
                <PreviousNotesList notes={doctorNotes} hasLoadedNotes={hasLoadedNotes} />
              </div>
            </div>
          )}

        </section>
      </div>
    </div>
  );
}

