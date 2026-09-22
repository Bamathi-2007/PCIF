import React, { useState } from "react";
import PatientDashboard from "./components/PatientDashboard";
import NutritionAIPage from "./components/NutritionAIPage";
import MentalWellnessAIPage from "./components/MentalWellnessAIPage";
import DoctorDashboard from "./components/DoctorDashboard";

/**
 * App.jsx — PCIF Top-level Router
 *
 * Routing strategy: pathname-based tab switch (no React Router dependency).
 *
 *   /doctor  or  /doctor/  → DoctorDashboard (clinician interface, fully isolated)
 *   /        (any other)   → Patient-facing application
 *
 * The doctor interface is NOT linked from the patient-facing UI.
 * Access /doctor directly in the browser.
 */

const path = window.location.pathname;
const IS_DOCTOR_ROUTE = path === "/doctor" || path === "/doctor/";

export default function App() {
  /* ── Doctor route: render only the clinician workspace ─────────────── */
  if (IS_DOCTOR_ROUTE) {
    return <DoctorDashboard />;
  }

  /* ── Patient route: existing app unchanged ──────────────────────────── */
  const [activeTab, setActiveTab] = useState("patient");

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* Patient Header */}
      <header className="pcif-header">
        <div className="pcif-brand-block">
          <span className="pcif-brand-title">PCIF</span>
          <span className="pcif-brand-sub">PATIENT CONTEXT INTELLIGENCE FRAMEWORK</span>
        </div>
      </header>

      {/* Main Patient Content Canvas */}
      <main className="pcif-main-canvas">
        {activeTab === "patient"   && <PatientDashboard setActiveTab={setActiveTab} />}
        {activeTab === "nutrition" && <NutritionAIPage  setActiveTab={setActiveTab} />}
        {activeTab === "mental"    && <MentalWellnessAIPage setActiveTab={setActiveTab} />}
      </main>
    </div>
  );
}
