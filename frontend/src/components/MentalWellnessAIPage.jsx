import React from 'react';
import { Brain, Send, Info } from 'lucide-react';

export default function MentalWellnessAIPage() {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title" style={{ color: '#38bdf8' }}>
          <Brain size={28} /> Mental Wellness AI Assistant
        </h1>
        <p className="page-subtitle">
          Domain-specific conversational assistant for mood, sleep patterns, stress levels, and emotional wellness.
        </p>
      </div>

      <div className="chat-container">
        <div className="chat-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="dot" style={{ background: '#06b6d4' }}></span>
            <strong style={{ fontSize: '0.9rem' }}>Mental Wellness AI Module</strong>
            <span className="status-pill placeholder">Placeholder Mode</span>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Patient ID: PAT-89210</span>
        </div>

        <div className="chat-messages">
          <div className="chat-message system">
            Welcome! I am your <strong>Mental Wellness Assistant</strong>. I am here to help you reflect on your sleep quality, stress levels, mood fluctuations, and daily emotional well-being.
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              <em>Note: Relevant health context will be stored in your shared patient history for doctor review.</em>
            </div>
          </div>

          <div className="chat-message user">
            I'm sleeping only 5 hours a night due to exam stress, and I wake up feeling anxious every morning.
          </div>

          <div className="chat-message system">
            [Placeholder Response] Thank you for opening up. In future steps, CCEE will extract this context (e.g. reduced sleep of 5 hrs/night associated with stress) into your longitudinal context history.
          </div>
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            className="chat-input"
            placeholder="Type your wellness or sleep experience here... (Placeholder)"
            disabled
          />
          <button className="btn btn-primary btn-disabled" disabled>
            <Send size={16} /> Send
          </button>
        </div>
      </div>

      <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', color: 'var(--text-dim)' }}>
        <Info size={14} /> Conversational LLM integration scheduled for Days 1–3.
      </div>
    </div>
  );
}
