import React from 'react';
import { Activity, Utensils, Brain, Stethoscope, User } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <nav className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <Activity size={20} />
        </div>
        <div>
          <span className="brand-title">PCIF Framework</span>
          <span className="brand-badge" style={{ marginLeft: '0.5rem' }}>Day 1 Prototype</span>
        </div>
      </div>

      <div className="nav-tabs">
        <button
          className={`nav-button ${activeTab === 'patient' ? 'active' : ''}`}
          onClick={() => setActiveTab('patient')}
        >
          <User size={16} />
          Patient Home
        </button>

        <button
          className={`nav-button ${activeTab === 'nutrition' ? 'active nutrition' : ''}`}
          onClick={() => setActiveTab('nutrition')}
        >
          <Utensils size={16} />
          Nutrition AI
        </button>

        <button
          className={`nav-button ${activeTab === 'mental' ? 'active mental' : ''}`}
          onClick={() => setActiveTab('mental')}
        >
          <Brain size={16} />
          Mental Wellness AI
        </button>

        <button
          className={`nav-button ${activeTab === 'doctor' ? 'active doctor' : ''}`}
          onClick={() => setActiveTab('doctor')}
        >
          <Stethoscope size={16} />
          Doctor Portal
        </button>
      </div>
    </nav>
  );
}
