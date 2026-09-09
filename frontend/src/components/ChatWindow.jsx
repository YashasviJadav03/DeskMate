import React, { useRef, useEffect } from 'react';

export default function ChatWindow({ messages, isLoading, onSelectQuery }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      overflowY: 'auto',
      padding: '16px 20px',
      gap: '16px'
    }}>
      {messages.length === 0 ? (
        <div style={{
          margin: 'auto',
          maxWidth: '560px',
          textAlign: 'center',
          padding: '30px 20px'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '32px',
            margin: '0 auto 20px auto',
            boxShadow: '0 0 30px rgba(99, 102, 241, 0.25)'
          }}>
            🤖
          </div>

          <h2 style={{ fontSize: '22px', fontWeight: '800', color: '#fff', marginBottom: '8px', letterSpacing: '-0.02em' }}>
            Welcome to DeskMate
          </h2>

          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6', marginBottom: '24px' }}>
            A production multi-agent system powered by <strong>LangGraph</strong>. Queries are dynamically routed to a <strong>RAG Retrieval Agent</strong> (via ChromaDB) or an <strong>Action Agent</strong> (executing tools like order lookups & complaint tickets).
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
            textAlign: 'left'
          }}>
            <div
              onClick={() => onSelectQuery("What is your return policy?")}
              style={{
                background: 'rgba(6, 182, 212, 0.05)',
                border: '1px solid rgba(6, 182, 212, 0.2)',
                borderRadius: '12px',
                padding: '14px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.5)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.2)';
                e.currentTarget.style.transform = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <span style={{ fontSize: '14px' }}>📚</span>
                <span style={{ fontSize: '11px', fontWeight: '700', color: '#22d3ee', textTransform: 'uppercase' }}>
                  Informational (RAG)
                </span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#fff', marginBottom: '4px' }}>
                "What is your return policy?"
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Retrieval Agent queries ChromaDB FAQ vector store.
              </div>
            </div>

            <div
              onClick={() => onSelectQuery("Check status of order #12345")}
              style={{
                background: 'rgba(245, 158, 11, 0.05)',
                border: '1px solid rgba(245, 158, 11, 0.2)',
                borderRadius: '12px',
                padding: '14px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.5)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.2)';
                e.currentTarget.style.transform = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <span style={{ fontSize: '14px' }}>⚙️</span>
                <span style={{ fontSize: '11px', fontWeight: '700', color: '#fbbf24', textTransform: 'uppercase' }}>
                  Actionable (Tool)
                </span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#fff', marginBottom: '4px' }}>
                "Check status of order #12345"
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Action Agent calls check_order_status tool.
              </div>
            </div>
          </div>
        </div>
      ) : (
        messages.map((msg, index) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={index}
              className="animate-fade-in"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: isUser ? 'flex-end' : 'flex-start',
                width: '100%'
              }}
            >
              {/* Message Header (Badge) */}
              {!isUser && msg.trace && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '6px',
                  marginLeft: '4px'
                }}>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: '700',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: msg.trace.route === 'actionable'
                      ? 'rgba(245, 158, 11, 0.15)'
                      : 'rgba(6, 182, 212, 0.15)',
                    color: msg.trace.route === 'actionable' ? '#fbbf24' : '#22d3ee',
                    border: msg.trace.route === 'actionable'
                      ? '1px solid rgba(245, 158, 11, 0.3)'
                      : '1px solid rgba(6, 182, 212, 0.3)'
                  }}>
                    {msg.trace.route === 'actionable' ? '⚙️ Action Agent' : '📚 Retrieval Agent'}
                  </span>

                  {msg.trace.tool_called && (
                    <span className="font-mono" style={{
                      fontSize: '11px',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: '#34d399',
                      border: '1px solid rgba(16, 185, 129, 0.3)'
                    }}>
                      🔧 {msg.trace.tool_called}
                    </span>
                  )}

                  <span className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {msg.trace.latency_ms}ms
                  </span>
                </div>
              )}

              {/* Message Bubble */}
              <div style={{
                maxWidth: '82%',
                padding: isUser ? '12px 18px' : '16px 20px',
                borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                background: isUser
                  ? 'linear-gradient(135deg, #4f46e5 0%, #0891b2 100%)'
                  : 'rgba(18, 26, 43, 0.85)',
                border: isUser ? 'none' : '1px solid rgba(255, 255, 255, 0.08)',
                color: '#fff',
                fontSize: '14px',
                lineHeight: '1.6',
                boxShadow: isUser ? '0 4px 14px rgba(79, 70, 229, 0.35)' : 'var(--shadow-sm)',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.text}

                {/* Sources pill container if available */}
                {!isUser && msg.trace?.sources && msg.trace.sources.length > 0 && (
                  <div style={{
                    marginTop: '12px',
                    paddingTop: '10px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                    display: 'flex',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '6px'
                  }}>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Sources:</span>
                    {msg.trace.sources.map((src, i) => (
                      <span key={i} className="font-mono" style={{
                        fontSize: '10px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: 'rgba(255, 255, 255, 0.06)',
                        color: '#94a3b8'
                      }}>
                        {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })
      )}

      {/* Loading Indicator */}
      {isLoading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 12px' }}>
          <div style={{
            display: 'flex',
            gap: '4px',
            padding: '12px 18px',
            borderRadius: '16px',
            background: 'rgba(18, 26, 43, 0.85)',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#6366f1', animation: 'pulseGlow 1s infinite ease-in-out' }} />
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#06b6d4', animation: 'pulseGlow 1s infinite ease-in-out 0.2s' }} />
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', animation: 'pulseGlow 1s infinite ease-in-out 0.4s' }} />
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Routing through agents...
          </span>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
