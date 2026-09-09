import React, { useState } from 'react';

const SUGGESTIONS = [
  { label: "📦 Track Order #12345", query: "Check status of order #12345" },
  { label: "🔄 Return Policy", query: "What is your return policy?" },
  { label: "🎫 File Late Delivery Complaint", query: "I want to file a complaint about late delivery" },
  { label: "💳 Payment Methods", query: "What payment methods do you accept?" },
  { label: "📧 Send Confirmation", query: "Send a confirmation email to customer@example.com" },
  { label: "🛡️ Warranty Details", query: "Tell me about your warranty policy" },
];

export default function InputBar({ onSend, isLoading }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!text.trim() || isLoading) return;
    onSend(text.trim());
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSelectSuggestion = (suggestionQuery) => {
    if (isLoading) return;
    onSend(suggestionQuery);
  };

  return (
    <div style={{ marginTop: 'auto', paddingTop: '12px' }}>
      {/* Suggestions scroll row */}
      <div style={{
        display: 'flex',
        gap: '8px',
        overflowX: 'auto',
        paddingBottom: '10px',
        paddingLeft: '4px'
      }}>
        {SUGGESTIONS.map((s, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSelectSuggestion(s.query)}
            disabled={isLoading}
            style={{
              whiteSpace: 'nowrap',
              fontSize: '12px',
              padding: '6px 12px',
              borderRadius: '20px',
              border: '1px solid rgba(255, 255, 255, 0.09)',
              background: 'rgba(255, 255, 255, 0.03)',
              color: 'var(--text-secondary)',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.background = 'rgba(99, 102, 241, 0.12)';
                e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.3)';
                e.currentTarget.style.color = '#fff';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.09)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{
        display: 'flex',
        alignItems: 'center',
        background: 'rgba(17, 24, 39, 0.85)',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        borderRadius: '16px',
        padding: '6px 8px 6px 16px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
        position: 'relative'
      }}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question or request an action (e.g. 'Track order #12345')..."
          disabled={isLoading}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: '#fff',
            fontSize: '14px',
            fontFamily: 'var(--font-sans)',
            padding: '8px 0'
          }}
        />

        <button
          type="submit"
          disabled={!text.trim() || isLoading}
          style={{
            padding: '8px 18px',
            borderRadius: '12px',
            border: 'none',
            background: text.trim() && !isLoading
              ? 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)'
              : 'rgba(255, 255, 255, 0.08)',
            color: text.trim() && !isLoading ? '#fff' : 'rgba(255, 255, 255, 0.3)',
            fontWeight: '600',
            fontSize: '13px',
            cursor: text.trim() && !isLoading ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            boxShadow: text.trim() && !isLoading ? '0 0 16px rgba(99, 102, 241, 0.35)' : 'none'
          }}
        >
          <span>Send</span>
          <span>↵</span>
        </button>
      </form>
    </div>
  );
}
