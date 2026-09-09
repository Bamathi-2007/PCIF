import React, { useState } from 'react';
import Navbar from './components/Navbar';
import PatientDashboard from './components/PatientDashboard';
import NutritionAIPage from './components/NutritionAIPage';
import MentalWellnessAIPage from './components/MentalWellnessAIPage';
import DoctorDashboard from './components/DoctorDashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState('patient');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-container">
        {activeTab === 'patient' && <PatientDashboard setActiveTab={setActiveTab} />}
        {activeTab === 'nutrition' && <NutritionAIPage />}
        {activeTab === 'mental' && <MentalWellnessAIPage />}
        {activeTab === 'doctor' && <DoctorDashboard />}
      </main>

      <footer className="footer">
        PCIF – Patient Context Intelligence Framework &copy; 2026 | Day 1 Research Prototype Architecture
      </footer>
    </div>
  );
}
