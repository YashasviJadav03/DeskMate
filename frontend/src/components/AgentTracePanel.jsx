import React from 'react';

export default function AgentTracePanel({ trace, isLoading, query }) {
  if (!trace && !isLoading) {
    return (
      <aside className="glass-panel" style={{
        width: '360px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        color: 'var(--text-muted)',
        border: '1px solid rgba(255, 255, 255, 0.08)'
      }}>
        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '16px',
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px dashed rgba(99, 102, 241, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          marginBottom: '16px'
        }}>
          🧭
        </div>
        <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '8px' }}>
          Agent Trace & Observability
        </h3>
        <p style={{ fontSize: '13px', lineHeight: '1.5', maxWidth: '280px' }}>
          Send a query to see the live LangGraph execution trace, route classification, tool executions, and RAG sources.
        </p>
      </aside>
    );
  }

  const isInformational = trace?.route === 'informational';
  const isActionable = trace?.route === 'actionable';

  return (
    <aside className="glass-panel animate-fade-in" style={{
      width: '380px',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      overflowY: 'auto',
      border: '1px solid rgba(255, 255, 255, 0.08)'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '16px' }}>⚡</span>
          <h3 style={{ fontSize: '14px', fontWeight: '700', letterSpacing: '-0.01em', color: '#fff' }}>
            Agent Trace Inspector
          </h3>
        </div>
        {trace?.latency_ms !== undefined && (
          <span className="font-mono" style={{
            fontSize: '11px',
            padding: '3px 8px',
            borderRadius: '6px',
            background: 'rgba(99, 102, 241, 0.15)',
            color: '#a5b4fc',
            border: '1px solid rgba(99, 102, 241, 0.3)'
          }}>
            {trace.latency_ms} ms
          </span>
        )}
      </div>

      {isLoading ? (
        <div style={{ padding: '30px 10px', textAlign: 'center' }}>
          <div style={{
            width: '32px',
            height: '32px',
            margin: '0 auto 12px auto',
            border: '3px solid rgba(99, 102, 241, 0.2)',
            borderTopColor: 'var(--accent-indigo)',
            borderRadius: '50%',
            animation: 'spinSlow 0.8s linear infinite'
          }} />
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            LangGraph orchestrating agents...
          </p>
        </div>
      ) : (
        <>
          {/* STEP 1: ROUTER CLASSIFICATION */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: '12px',
            padding: '14px',
            border: '1px solid rgba(255, 255, 255, 0.06)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
                Step 1 • Classification
              </span>
              <span style={{
                fontSize: '11px',
                fontWeight: '700',
                padding: '2px 8px',
                borderRadius: '999px',
                background: isActionable ? 'rgba(245, 158, 11, 0.15)' : 'rgba(6, 182, 212, 0.15)',
                color: isActionable ? '#fbbf24' : '#22d3ee',
                border: isActionable ? '1px solid rgba(245, 158, 11, 0.3)' : '1px solid rgba(6, 182, 212, 0.3)'
              }}>
                {trace.route?.toUpperCase()}
              </span>
            </div>

            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>🧭</span>
              <span>Classified by: <strong style={{ color: '#fff' }}>Router Agent</strong></span>
            </div>
          </div>

          {/* STEP 2: DISPATCHED AGENT */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: '12px',
            padding: '14px',
            border: '1px solid rgba(255, 255, 255, 0.06)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
                Step 2 • Dispatched Handler
              </span>
              <span className="font-mono" style={{ fontSize: '12px', color: '#e2e8f0', fontWeight: '600' }}>
                {trace.agent}
              </span>
            </div>

            {/* If Retrieval Agent: show RAG Sources */}
            {isInformational && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Retrieved Knowledge Base Documents:
                </div>
                {trace.sources && trace.sources.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {trace.sources.map((src, idx) => (
                      <span key={idx} className="font-mono" style={{
                        fontSize: '11px',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        background: 'rgba(6, 182, 212, 0.12)',
                        color: '#67e8f9',
                        border: '1px solid rgba(6, 182, 212, 0.25)'
                      }}>
                        📄 {src}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>No direct docs matched</span>
                )}
              </div>
            )}

            {/* If Action Agent: show Tool Invocation */}
            {isActionable && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px' }}>🔧</span>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Tool Executed:</span>
                  <span className="font-mono" style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#34d399',
                    background: 'rgba(16, 185, 129, 0.12)',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    border: '1px solid rgba(16, 185, 129, 0.25)'
                  }}>
                    {trace.tool_called || 'None'}
                  </span>
                </div>

                {trace.tool_input && (
                  <div style={{ marginTop: '10px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                      Tool Input Arguments:
                    </div>
                    <pre className="font-mono" style={{
                      fontSize: '11px',
                      background: 'rgba(0, 0, 0, 0.4)',
                      padding: '8px',
                      borderRadius: '8px',
                      color: '#94a3b8',
                      overflowX: 'auto',
                      border: '1px solid rgba(255, 255, 255, 0.05)'
                    }}>
                      {JSON.stringify(trace.tool_input, null, 2)}
                    </pre>
                  </div>
                )}

                {trace.tool_output && (
                  <div style={{ marginTop: '10px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                      Tool Output Result:
                    </div>
                    <pre className="font-mono" style={{
                      fontSize: '11px',
                      background: 'rgba(0, 0, 0, 0.4)',
                      padding: '8px',
                      borderRadius: '8px',
                      color: '#a7f3d0',
                      overflowX: 'auto',
                      maxHeight: '140px',
                      border: '1px solid rgba(16, 185, 129, 0.15)'
                    }}>
                      {JSON.stringify(trace.tool_output, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* STEP 3: EXECUTION GRAPH */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: '12px',
            padding: '14px',
            border: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <div style={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em', marginBottom: '8px' }}>
              LangGraph Path
            </div>
            <div className="font-mono" style={{ fontSize: '11px', color: '#cbd5e1', lineHeight: '1.8' }}>
              <div>▶ START</div>
              <div style={{ color: 'var(--accent-indigo)' }}>  ↳ node: classify (Router)</div>
              <div style={{ color: isActionable ? 'var(--accent-amber)' : 'var(--accent-cyan)' }}>
                {isActionable ? '    ↳ edge [actionable] ➔ node: act (Tools)' : '    ↳ edge [informational] ➔ node: retrieve (RAG)'}
              </div>
              <div style={{ color: 'var(--accent-emerald)' }}>  ↳ node: respond</div>
              <div>⏹ END</div>
            </div>
          </div>
        </>
      )}
    </aside>
  );
}
