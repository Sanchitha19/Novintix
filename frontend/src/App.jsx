import React, { useState, useEffect } from 'react';
import ChatPanel from './components/ChatPanel';
import AdminDashboard from './components/AdminDashboard';
import LoginForm from './components/LoginForm';
import { generateInitialMetrics, initialEvents } from './mockData';

function App() {
  const [token, setToken] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [events, setEvents] = useState([]);
  const [renderError, setRenderError] = useState(null);

  // Initialize data in useEffect to prevent SSR/Init mismatches
  useEffect(() => {
    try {
      setMetrics(generateInitialMetrics());
      setEvents(initialEvents);
      console.log("App state initialized successfully");
    } catch (err) {
      console.error("Initialization Error:", err);
      setRenderError(err.message);
    }
  }, []);

  const handleLogin = (newToken) => {
    console.log("Login Success. Token length:", newToken?.length);
    setToken(newToken);
  };

  const handleNewInteraction = (queryText, responses) => {
    // Metric update logic (Simplified for stability)
    setEvents(prev => [{
      id: Date.now(),
      type: 'ROUTING',
      text: `User query processed`,
      time: new Date().toLocaleTimeString(),
      color: 'blue'
    }, ...prev].slice(0, 10));
  };

  // If there's a fatal render error, show it!
  if (renderError) {
    return (
      <div className="h-screen w-screen bg-slate-900 flex items-center justify-center p-10">
        <div className="bg-red-900/20 border border-red-500 p-6 rounded-xl max-w-2xl">
          <h1 className="text-red-500 font-bold text-xl mb-4">Fatal Rendering Error</h1>
          <pre className="text-red-300 text-xs overflow-auto bg-black/50 p-4 rounded">{renderError}</pre>
          <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg">Retry Reload</button>
        </div>
      </div>
    );
  }

  // Waiting for init
  if (!metrics) {
    return <div className="h-screen w-screen bg-[#0F1117] flex items-center justify-center text-slate-500 font-mono">Initializing Novintix OS...</div>;
  }

  try {
    return (
      <div className="flex h-screen w-screen overflow-hidden bg-[#0F1117] text-white font-sans">
        {/* Left Panel: 40% */}
        <div className="w-[40%] min-w-[400px] flex flex-col border-r border-[#30363D] shadow-2xl z-10 relative bg-[#0F1117]">
          {!token ? (
            <LoginForm onLogin={handleLogin} />
          ) : (
            <ChatPanel token={token} onNewInteraction={handleNewInteraction} />
          )}
        </div>

        {/* Right Panel: 60% */}
        <div className="w-[60%] flex flex-col bg-[#0F1117] relative">
          <AdminDashboard metrics={metrics} events={events} />
        </div>

        {/* Decorative Glow */}
        <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-blue-500/5 blur-[120px] pointer-events-none"></div>
      </div>
    );
  } catch (err) {
    setRenderError(err.message);
    return null;
  }
}

export default App;
