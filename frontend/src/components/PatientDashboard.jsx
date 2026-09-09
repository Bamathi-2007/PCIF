import React from 'react';
import { Utensils, Brain, ShieldCheck, Database, Cpu, ArrowRight } from 'lucide-react';

export default function PatientDashboard({ setActiveTab }) {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Patient Context Intelligence Dashboard</h1>
        <p className="page-subtitle">
          Preserving meaningful physical, lifestyle, and mental wellness context over time.
        </p>
      </div>

      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div style={{ padding: '0.5rem', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', borderRadius: '8px' }}>
              <Utensils size={24} />
            </div>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem' }}>Nutrition & Physical AI</h3>
              <span className="status-pill placeholder">Placeholder Interface</span>
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
            Handles food habits, meal patterns, appetite, hydration, activity level, and lifestyle routines.
          </p>
          <button className="btn btn-primary" onClick={() => setActiveTab('nutrition')}>
            Launch Nutrition AI <ArrowRight size={16} />
          </button>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div style={{ padding: '0.5rem', background: 'rgba(6, 182, 212, 0.15)', color: '#38bdf8', borderRadius: '8px' }}>
              <Brain size={24} />
            </div>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem' }}>Mental Wellness AI</h3>
              <span className="status-pill placeholder">Placeholder Interface</span>
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
            Handles mood, stress levels, sleep hygiene, anxiety experiences, and emotional wellness context.
          </p>
          <button className="btn btn-primary" onClick={() => setActiveTab('mental')}>
            Launch Mental Wellness AI <ArrowRight size={16} />
          </button>
        </div>
      </div>

      <div className="glass-card" style={{ background: 'rgba(18, 24, 40, 0.5)' }}>
        <h3 style={{ fontFamily: 'var(--font-heading)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={20} color="#818cf8" /> Framework Principles & Data Flow
        </h3>
        <div className="grid-3">
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '10px' }}>
            <h4 style={{ fontSize: '0.95rem', color: '#a5b4fc', marginBottom: '0.35rem' }}>1. CCEE Compression</h4>
            <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
              Filters conversational fluff and extracts structured clinical items without saving raw logs.
            </p>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '10px' }}>
            <h4 style={{ fontSize: '0.95rem', color: '#a5b4fc', marginBottom: '0.35rem' }}>2. Unified Patient DB</h4>
            <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
              Nutrition and Mental Wellness contribute to the same patient context history with clear source attribution.
            </p>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '10px' }}>
            <h4 style={{ fontSize: '0.95rem', color: '#a5b4fc', marginBottom: '0.35rem' }}>3. Doctor Authority</h4>
            <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
              Longitudinal context supports doctor consultation. Final medical decision belongs to the doctor.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
