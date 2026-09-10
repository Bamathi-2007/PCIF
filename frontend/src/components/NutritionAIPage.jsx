import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, ArrowUp, AlertCircle, Sprout, User } from 'lucide-react';
import nutritionStudyImg from '../assets/nutrition_study.jpg';

export default function NutritionAIPage({ setActiveTab }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hi! What would you like to explore regarding your food habits, hydration, or daily nutrition routines today?"
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async () => {
    const textToSend = inputValue.trim();
    if (!textToSend || isLoading) return;

    setError(null);

    const newUserMessage = {
      id: 'msg-' + Date.now(),
      sender: 'user',
      text: textToSend
    };

    // Prepare temporary conversation history for backend
    const historyPayload = messages.map((m) => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.text
    }));

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/nutrition/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: textToSend,
          history: historyPayload
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();

      const aiResponse = {
        id: 'reply-' + Date.now(),
        sender: 'assistant',
        text: data.reply || "I didn't receive a response text."
      };

      setMessages((prev) => [...prev, aiResponse]);
    } catch (err) {
      console.error('Failed to send nutrition chat message:', err);
      setError('Could not communicate with the nutrition service. Please check that the server is active.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div>
      {/* Navigation and Title Header */}
      <button className="chat-nav-back" onClick={() => setActiveTab('patient')}>
        <ArrowLeft size={16} /> Back to Home
      </button>

      <div className="chat-page-header">
        <div>
          <h1 className="chat-page-title">Nutrition Assistant</h1>
          <p className="chat-page-subtitle">
            Practical guidance for healthier everyday eating habits.
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
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#234B41" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 11a8 8 0 0 0 16 0H4z" />
                <path d="M12 11V5" />
                <circle cx="12" cy="18" r="1" fill="#234B41" />
              </svg>
              <span>Nutrition Support</span>
            </div>
          </div>

          {/* Messages Area */}
          <div className="chat-messages-container">
            {error && (
              <div className="chat-error-notice">
                <AlertCircle size={15} />
                <span>{error}</span>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className="chat-msg-block">
                {msg.sender === 'assistant' ? (
                  <>
                    <div className="chat-msg-header">
                      <div style={{ width: 18, height: 18, borderRadius: '50%', background: '#D6EFE5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Sprout size={11} color="#2D7A5E" strokeWidth={2.5} />
                      </div>
                      <span>Nutrition Assistant</span>
                    </div>
                    <div className="chat-msg-bubble assistant">
                      {msg.text}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="chat-msg-header user">
                      <span>You</span>
                      <div style={{ width: 18, height: 18, borderRadius: '50%', background: '#E69E87', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
                        <User size={11} strokeWidth={2.5} />
                      </div>
                    </div>
                    <div className="chat-msg-bubble user">
                      {msg.text}
                    </div>
                  </>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="chat-msg-block">
                <div className="chat-msg-header">
                  <div style={{ width: 18, height: 18, borderRadius: '50%', background: '#D6EFE5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Sprout size={11} color="#2D7A5E" strokeWidth={2.5} />
                  </div>
                  <span>Nutrition Assistant</span>
                </div>
                <div className="chat-msg-bubble assistant" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.82rem', color: '#456E63' }}>Thinking...</span>
                  <div className="typing-dots">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form
            className="chat-input-bar"
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
          >
            <input
              type="text"
              className="chat-text-input"
              placeholder="Ask about meals, hydration or food habits..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              autoFocus
            />
            <button
              type="submit"
              className="chat-send-btn"
              disabled={!inputValue.trim() || isLoading}
            >
              Send <ArrowUp size={15} strokeWidth={2.5} />
            </button>
          </form>
        </div>

        {/* Right: Visual / Motivational Area (Non-interactive) */}
        <aside className="chat-side-card" aria-label="Routine and Reflection">
          {/* Top Circular Emblem */}
          <div className="chat-side-emblem">
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#3D685C" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v8" />
              <path d="M12 5c2-2 4-1 4 1s-2 3-4 3" />
              <path d="M12 7c-2-2-4-1-4 1s2 3 4 3" />
              <path d="M9 14h6a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2z" />
            </svg>
          </div>

          <span className="chat-side-pillar">Pillar of Routine</span>

          <blockquote className="chat-side-quote">
            &ldquo;Small choices, repeated daily, can shape healthier routines.&rdquo;
          </blockquote>

          <p className="chat-side-desc">
            Use this space to reflect on your everyday habits and make gradual improvements.
          </p>

          <div className="chat-side-photo-box">
            <img
              src={nutritionStudyImg}
              alt="Nourishing morning breakfast still life study"
              className="chat-side-photo"
            />
          </div>

          <div className="chat-side-caption">
            Nourishing Foundations &middot; Morning Study
          </div>

          <div className="chat-side-companion">
            PCIF Thoughtful Care Companion
          </div>
        </aside>
      </div>
    </div>
  );
}
