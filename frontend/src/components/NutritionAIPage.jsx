import React from 'react';
import { Utensils, Send, Info } from 'lucide-react';

export default function NutritionAIPage() {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title" style={{ color: '#34d399' }}>
          <Utensils size={28} /> Nutrition & Lifestyle AI Assistant
        </h1>
        <p className="page-subtitle">
          Domain-specific conversational assistant for dietary habits, appetite, hydration, and physical lifestyle.
        </p>
      </div>

      <div className="chat-container">
        <div className="chat-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="dot" style={{ background: '#10b981' }}></span>
            <strong style={{ fontSize: '0.9rem' }}>Nutrition AI Module</strong>
            <span className="status-pill placeholder">Placeholder Mode</span>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Patient ID: PAT-89210</span>
        </div>

        <div className="chat-messages">
          <div className="chat-message system">
            Hello! I am your <strong>Nutrition AI Assistant</strong>. I am here to discuss your meal patterns, food intake, appetite changes, hydration, and daily physical activity.
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              <em>Note: Information discussed will be processed by CCEE to provide your doctor with relevant context.</em>
            </div>
          </div>

          <div className="chat-message user">
            I've been skipping breakfast this week because I'm busy, and my appetite has been lower than usual.
          </div>

          <div className="chat-message system">
            [Placeholder Response] Thank you for sharing. In future steps, CCEE will extract this context (e.g. repeated breakfast skipping, appetite reduction) for your longitudinal health record.
          </div>
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            className="chat-input"
            placeholder="Type your nutrition or lifestyle message here... (Placeholder)"
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
