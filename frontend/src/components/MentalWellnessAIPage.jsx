import React, { useState } from 'react';
import { ArrowLeft, ArrowUp, Brain, Sprout } from 'lucide-react';
import mindfulnessStudyImg from '../assets/mindfulness_study.jpg';

export default function MentalWellnessAIPage({ setActiveTab }) {
  const [messages] = useState([
    {
      id: 'welcome-mental',
      sender: 'assistant',
      text: "Welcome to your Mental Wellness space. This is a quiet place to reflect on your stress, sleep patterns, mood, and daily emotional wellbeing.\n\nHow has your energy, sleep, or stress felt recently?"
    }
  ]);
  const [inputValue, setInputValue] = useState('');

  return (
    <div>
      {/* Navigation and Title Header */}
      <button className="chat-nav-back" onClick={() => setActiveTab('patient')}>
        <ArrowLeft size={16} /> Back to Home
      </button>

      <div className="chat-page-header">
        <div>
          <h1 className="chat-page-title">Mental Wellness Assistant</h1>
          <p className="chat-page-subtitle">
            A reflective space for everyday stress, sleep, mood and mental wellbeing.
          </p>
        </div>
      </div>

      {/* Main Split Layout: Left Chat + Right Motivational Side */}
      <div className="chat-layout-grid">
        {/* Left: Chat Container */}
        <div className="chat-main-card">
          {/* Header Bar */}
          <div className="chat-stream-header">
            <div className="chat-stream-left">
              <Brain size={18} color="#234B41" />
              <span>Mindful Reflection & Rest</span>
            </div>
          </div>

          {/* Messages Area */}
          <div className="chat-messages-container">
            {messages.map((msg) => (
              <div key={msg.id} className="chat-msg-block">
                <div className="chat-msg-header">
                  <div style={{ width: 18, height: 18, borderRadius: '50%', background: '#D6EFE5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Sprout size={11} color="#2D7A5E" strokeWidth={2.5} />
                  </div>
                  <span>Mental Wellness Assistant</span>
                </div>
                <div className="chat-msg-bubble assistant">
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          {/* Input Area (Placeholder for Mental Wellness) */}
          <div className="chat-input-bar">
            <input
              type="text"
              className="chat-text-input"
              placeholder="Reflect on your stress, sleep, or mood today..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled
            />
            <button
              type="button"
              className="chat-send-btn"
              disabled
            >
              Send <ArrowUp size={15} strokeWidth={2.5} />
            </button>
          </div>
        </div>

        {/* Right: Visual / Motivational Area (Non-interactive) */}
        <aside className="chat-side-card" aria-label="Rest and Reflection">
          <div className="chat-side-emblem">
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#3D685C" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 3a9 9 0 0 0 0 18v-9" />
            </svg>
          </div>

          <span className="chat-side-pillar">Pillar of Mindfulness</span>

          <blockquote className="chat-side-quote">
            &ldquo;Gentle awareness of today creates clarity for tomorrow.&rdquo;
          </blockquote>

          <p className="chat-side-desc">
            Take a moment to breathe and observe how your body and mind are resting.
          </p>

          <div className="chat-side-photo-box">
            <img
              src={mindfulnessStudyImg}
              alt="Mindful still life with zen stones and sprig"
              className="chat-side-photo"
            />
          </div>

          <div className="chat-side-caption">
            Quiet Reflection &middot; Daily Study
          </div>

          <div className="chat-side-companion">
            PCIF Thoughtful Care Companion
          </div>
        </aside>
      </div>
    </div>
  );
}
