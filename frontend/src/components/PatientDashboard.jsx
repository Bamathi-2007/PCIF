import React from 'react';

export default function PatientDashboard({ setActiveTab }) {
  return (
    <div>
      {/* Centered Hero Section */}
      <section className="home-hero">
        <div className="home-continuity-pill">
          PERSONAL SPACE • LONGITUDINAL CONTINUITY
        </div>
        <h1 className="home-headline">Your health, understood over time.</h1>
        <p className="home-subhead">
          Talk openly about your everyday nutrition or mental wellbeing. PCIF helps preserve the context that matters.
        </p>
      </section>

      {/* Pathway Selection Header */}
      <section className="home-pathway-header">
        <div>
          <h2 className="home-pathway-title">What would you like to talk about today?</h2>
          <p className="home-pathway-desc">Select a pathway to begin your conversational log</p>
        </div>
      </section>

      {/* Two Pathway Cards */}
      <div className="home-cards-grid">
        {/* Nutrition Pathway Card */}
        <div className="home-card">
          <div className="home-card-top">
            <div className="home-card-icon-box">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#C06C54" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 11a8 8 0 0 0 16 0H4z" />
                <path d="M7 11V7" />
                <path d="M12 11V5" />
                <path d="M17 11V7" />
                <circle cx="12" cy="18" r="1" fill="#C06C54" />
              </svg>
            </div>
            <span className="home-card-badge">Daily Nourishment</span>
          </div>

          <h3 className="home-card-title">Nutrition</h3>
          <p className="home-card-text">
            Talk about meals, food habits, hydration and everyday nutrition.
          </p>
          <p className="home-card-text" style={{ marginBottom: '1.5rem' }}>
            Get practical suggestions for healthier daily habits.
          </p>

          <button
            className="home-card-btn"
            onClick={() => setActiveTab('nutrition')}
          >
            Start Nutrition Chat &rarr;
          </button>

          <div className="home-card-lock-note">
            <span>Practical support for everyday nutrition habits.</span>
          </div>
        </div>

        {/* Mental Wellness Pathway Card */}
        <div className="home-card">
          <div className="home-card-top">
            <div className="home-card-icon-box">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#528A7A" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                <ellipse cx="12" cy="17" rx="6" ry="3" />
                <ellipse cx="12" cy="12" rx="4.5" ry="2.5" />
                <circle cx="12" cy="7.5" r="2.5" />
              </svg>
            </div>
            <span className="home-card-badge">Reflective Space</span>
          </div>

          <h3 className="home-card-title">Mental Wellness</h3>
          <p className="home-card-text">
            Talk about stress, sleep, mood and everyday mental wellbeing.
          </p>
          <p className="home-card-text" style={{ marginBottom: '1.5rem' }}>
            A private space to reflect and receive supportive guidance.
          </p>

          <button
            className="home-card-btn"
            onClick={() => setActiveTab('mental')}
          >
            Start Wellness Chat &rarr;
          </button>

          <div className="home-card-lock-note">
            <span>Support for everyday stress, sleep and emotional wellbeing.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
