import React from 'react';

export default function Navbar({ onToggleLogs, isLogsOpen, currentProvider = 'Mock (Zero Cost)' }) {
  return (
    <header className="glass-panel" style={{
      margin: '16px 20px 12px 20px',
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      background: 'rgba(11, 17, 30, 0.8)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px',
          boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)'
        }}>
          ⚡
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: '800', letterSpacing: '-0.02em', color: '#fff' }}>
              DeskMate
            </h1>
            <span style={{
              fontSize: '11px',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              background: 'linear-gradient(90deg, #6366f1, #06b6d4)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              padding: '1px 6px',
              borderRadius: '4px',
              border: '1px solid rgba(99, 102, 241, 0.3)'
            }}>
              Multi-Agent
            </span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Orchestrated Query Resolution System • LangGraph + ChromaDB
          </p>
        </div>
      </div>

      {/* Center architecture status badges */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '20px',
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          fontSize: '12px',
          color: '#a5b4fc'
        }}>
          <span>🧭</span>
          <span>Router</span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '20px',
          background: 'rgba(6, 182, 212, 0.1)',
          border: '1px solid rgba(6, 182, 212, 0.25)',
          fontSize: '12px',
          color: '#67e8f9'
        }}>
          <span>📚</span>
          <span>RAG Retrieval</span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '20px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          fontSize: '12px',
          color: '#6ee7b7'
        }}>
          <span>⚙️</span>
          <span>Action Tools</span>
        </div>
      </div>

      {/* Right controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          borderRadius: '8px',
          background: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          fontSize: '12px',
          color: 'var(--text-secondary)'
        }}>
          <span className="pulse-dot" />
          <span>LLM: <strong style={{ color: '#fff' }}>{currentProvider}</strong></span>
        </div>

        <button
          onClick={onToggleLogs}
          style={{
            padding: '7px 14px',
            borderRadius: '8px',
            border: isLogsOpen ? '1px solid #6366f1' : '1px solid rgba(255, 255, 255, 0.12)',
            background: isLogsOpen ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.05)',
            color: '#fff',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease'
          }}
        >
          <span>📊</span>
          <span>Query Logs</span>
        </button>
      </div>
    </header>
  );
}
