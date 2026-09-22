/**
 * DoctorDashboard.jsx — PCIF Day 13 Clinician Context Workspace
 *
 * Provides a read-only context review interface for attending clinicians.
 * Calls POST /api/doctor/context to retrieve structured patient-reported context.
 *
 * Boundaries (Day 13):
 *  - No doctor-note persistence (Day 14)
 *  - No diagnosis / treatment / risk controls
 *  - No patient search / clinician authentication
 *  - Consultation text is transient — never stored, no localStorage/sessionStorage
 *  - Only renders assistant.context_summary, relevant_current_context,
 *    relevant_longitudinal_changes, items_to_verify, and disclaimer
 */
import React, { useState, useCallback } from "react";
import { AlertCircle, Stethoscope, ClipboardList, RefreshCw } from "lucide-react";

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

/* ─── Main component ─────────────────────────────────────────────────────── */

export default function DoctorDashboard() {
  const [patientId, setPatientId]       = useState("");
  const [consultation, setConsultation] = useState("");
  const [isLoading, setIsLoading]       = useState(false);
  const [result, setResult]             = useState(null);
  const [error, setError]               = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  /* ── Patient-switch safety ──────────────────────────────────────────────
     Immediately clear result + error whenever the clinician edits patient ID.
     This prevents Patient A context from remaining visible beside Patient B ID. */
  const handlePatientIdChange = useCallback(
    (e) => {
      setPatientId(e.target.value);
      if (result !== null || error !== null) {
        setResult(null);
        setError(null);
      }
      if (validationErrors.patientId) {
        setValidationErrors((prev) => ({ ...prev, patientId: undefined }));
      }
    },
    [result, error, validationErrors.patientId]
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

  /* ── Validation ─────────────────────────────────────────────────────── */
  function validate() {
    const errs = {};
    if (!patientId.trim())    errs.patientId    = "Patient ID is required.";
    if (!consultation.trim()) errs.consultation = "Consultation notes are required.";
    return errs;
  }

  /* ── Generate context ───────────────────────────────────────────────── */
  const handleGenerate = async () => {
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setValidationErrors(errs);
      return;
    }

    setValidationErrors({});
    setResult(null);   // always replace previous result before new request
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch("/api/doctor/context", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id:   patientId.trim(),
          consultation: consultation.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("[PCIF Doctor] Context generation failed:", err);
      // On failure: clear stale result, show safe generic error only
      // Never translate API failure into "no prior patient context"
      setResult(null);
      setError("Unable to generate patient context right now. Please try again.");
    } finally {
      setIsLoading(false);
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

      {/* ── Two-column workspace ─────────────────────────────────────── */}
      <div className="dr-workspace">

        {/* Left — Input Panel */}
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
              disabled={isLoading}
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
              rows={8}
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

        {/* Right — Results Panel */}
        <section
          className="dr-results-panel"
          aria-label="Contextual assistance results"
          aria-live="polite"
        >

          {/* Idle placeholder */}
          {!hasResult && !error && !isLoading && (
            <div className="dr-idle-state">
              <div className="dr-idle-icon" aria-hidden="true">
                <Stethoscope size={36} />
              </div>
              <p className="dr-idle-text">
                Enter a patient ID and consultation notes, then click{" "}
                <strong>Generate Context</strong> to review structured patient-reported background context.
              </p>
            </div>
          )}

          {/* Error state — generic only, never leaks stack traces or DB errors */}
          {error && !hasResult && (
            <div className="dr-error-banner" role="alert">
              <AlertCircle size={16} aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}

          {/* Results */}
          {hasResult && (
            <div className="dr-results">

              {/* Patient-reported provenance — always visible with results */}
              <div className="dr-provenance-label" role="note">
                <strong>Patient-reported context:</strong> Information shown here is derived from patient-reported
                Nutrition and Mental Wellness interactions. These records have not been clinically confirmed by a clinician.
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

              {/* 5. Disclaimer — rendered from backend response only */}
              {result.disclaimer && (
                <div className="dr-disclaimer" role="note" id="dr-disclaimer">
                  {result.disclaimer}
                </div>
              )}

            </div>
          )}

        </section>
      </div>
    </div>
  );
}
