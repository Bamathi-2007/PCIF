import React, { useState } from 'react';
import PatientDashboard from './components/PatientDashboard';
import NutritionAIPage from './components/NutritionAIPage';
import MentalWellnessAIPage from './components/MentalWellnessAIPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('patient');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Patient Header */}
      <header className="pcif-header">
        <div className="pcif-brand-block">
          <span className="pcif-brand-title">PCIF</span>
          <span className="pcif-brand-sub">PATIENT CONTEXT INTELLIGENCE FRAMEWORK</span>
        </div>
      </header>

      {/* Main Patient Content Canvas */}
      <main className="pcif-main-canvas">
        {activeTab === 'patient' && <PatientDashboard setActiveTab={setActiveTab} />}
        {activeTab === 'nutrition' && <NutritionAIPage setActiveTab={setActiveTab} />}
        {activeTab === 'mental' && <MentalWellnessAIPage setActiveTab={setActiveTab} />}
      </main>
    </div>
  );
}
