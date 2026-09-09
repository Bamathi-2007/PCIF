import React from 'react';
import { Stethoscope, Search, Clock, FileText, Bot, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function DoctorDashboard() {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title" style={{ color: '#c084fc' }}>
          <Stethoscope size={28} /> Doctor Clinical Portal & AI Assistant
        </h1>
        <p className="page-subtitle">
          Longitudinal patient context retrieval and clinical decision support system.
        </p>
      </div>

      {/* Doctor Warning Banner */}
      <div style={{
        background: 'rgba(236, 72, 153, 0.1)',
        border: '1px solid rgba(236, 72, 153, 0.3)',
        borderRadius: '12px',
        padding: '1rem 1.25rem',
        marginBottom: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem'
      }}>
        <AlertTriangle size={22} color="#f472b6" />
        <div style={{ fontSize: '0.875rem', color: '#fbcfe8' }}>
          <strong>Clinical Decision Authority Notice:</strong> PCIF AI provides longitudinal decision support only. All diagnostic interpretations and final medical decisions rest strictly with the attending doctor.
        </div>
      </div>

      <div className="grid-2">
        {/* Patient Selection & History */}
        <div className="glass-card">
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Search size={18} color="#a855f7" /> Patient Retrieval
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <input
              type="text"
              className="chat-input"
              value="PAT-89210 (Demo Patient)"
              readOnly
            />
            <button className="btn btn-primary" style={{ padding: '0.5rem 1rem' }}>Select</button>
          </div>

          <h4 style={{ fontSize: '0.9rem', color: '#c084fc', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Clock size={16} /> Longitudinal Context History (CCEE Extracted)
          </h4>
          
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem', height: '220px', overflowY: 'auto' }}>
            <div style={{ borderLeft: '3px solid #06b6d4', paddingLeft: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 600 }}>SOURCE: MENTAL WELLNESS AI | PATIENT REPORTED</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Category: Sleep & Stress</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>"Reduced sleep (approx 5 hrs/night) associated with exam stress."</div>
            </div>

            <div style={{ borderLeft: '3px solid #10b981', paddingLeft: '0.75rem' }}>
              <div style={{ fontSize: '0.75rem', color: '#34d399', fontWeight: 600 }}>SOURCE: NUTRITION AI | PATIENT REPORTED</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Category: Nutrition</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>"Repeated breakfast skipping over 1 week."</div>
            </div>
          </div>
        </div>

        {/* Current Consultation & Doctor AI */}
        <div className="glass-card">
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={18} color="#a855f7" /> Current Consultation Input
          </h3>
          <textarea
            className="chat-input"
            rows={4}
            placeholder="Enter clinical examination notes, symptoms, or lab findings here... (Placeholder)"
            disabled
            style={{ width: '100%', marginBottom: '1rem', resize: 'none' }}
          ></textarea>

          <h4 style={{ fontSize: '0.9rem', color: '#c084fc', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Bot size={16} /> Doctor AI Contextual Assistant
          </h4>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '0.85rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            [Doctor AI Placeholder] Doctor consultation workflow and AI retrieval assistant scheduled for Days 12–15.
          </div>
        </div>
      </div>
    </div>
  );
}
