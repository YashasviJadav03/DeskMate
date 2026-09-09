import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import AgentTracePanel from './components/AgentTracePanel';
import LogsModal from './components/LogsModal';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [currentTrace, setCurrentTrace] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLogsOpen, setIsLogsOpen] = useState(false);
  const [sessionId] = useState(() => 'sess-' + Math.random().toString(36).substring(2, 9));

  const handleSendMessage = async (queryText) => {
    if (!queryText || isLoading) return;

    // Add user message to state
    const userMessage = { sender: 'user', text: queryText };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          session_id: sessionId
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();

      // Add agent reply
      const botMessage = {
        sender: 'agent',
        text: data.response,
        trace: data.trace
      };

      setMessages((prev) => [...prev, botMessage]);
      setCurrentTrace(data.trace);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = {
        sender: 'agent',
        text: `⚠️ Could not reach the DeskMate backend at http://localhost:8000. Please ensure the backend is running.`
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      maxWidth: '1600px',
      margin: '0 auto',
      overflow: 'hidden'
    }}>
      {/* Top Navigation */}
      <Navbar
        onToggleLogs={() => setIsLogsOpen(!isLogsOpen)}
        isLogsOpen={isLogsOpen}
      />

      {/* Main Workspace Layout */}
      <main style={{
        flex: 1,
        display: 'flex',
        gap: '16px',
        padding: '0 20px 16px 20px',
        overflow: 'hidden'
      }}>
        {/* Chat Area (Left / Center) */}
        <section className="glass-panel" style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          padding: '16px',
          overflow: 'hidden',
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSelectQuery={handleSendMessage}
          />

          <InputBar
            onSend={handleSendMessage}
            isLoading={isLoading}
          />
        </section>

        {/* Trace & Observability Panel (Right) */}
        <AgentTracePanel
          trace={currentTrace}
          isLoading={isLoading}
        />
      </main>

      {/* Query Logs Modal */}
      <LogsModal
        isOpen={isLogsOpen}
        onClose={() => setIsLogsOpen(false)}
      />
    </div>
  );
}
