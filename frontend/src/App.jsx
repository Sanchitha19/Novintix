import React, { useState, useEffect } from 'react';
import ChatPanel from './components/ChatPanel';
import AdminDashboard from './components/AdminDashboard';
import LoginForm from './components/LoginForm';
import { generateInitialMetrics, initialEvents } from './mockData';

function App() {
  const [token, setToken] = useState(null);
  const [metrics, setMetrics] = useState(generateInitialMetrics());
  const [events, setEvents] = useState(initialEvents);

  console.log("JWT set:", token);

  const handleLogin = (newToken) => {
    console.log("handleLogin called with:", newToken);
    setToken(newToken);
  };

  const handleNewInteraction = (queryText, responses) => {
    // 1. Update Metrics
    setMetrics(prev => {
      const newMetrics = { ...prev };
      
      // Update Agent query counts
      responses.forEach(res => {
        const agentId = res.agent_name === "OrderTrackingAgent" ? "tracking" : 
                        res.agent_name === "RefundAgent" ? "refund" :
                        res.agent_name === "FAQAgent" ? "faq" : "escalation";
        
        newMetrics.agentStatus = newMetrics.agentStatus.map(a => 
          a.id === agentId ? { ...a, queries: a.queries + 1, status: 'Active' } : a
        );

        // Update Intent Distribution
        const intentNameMap = {
          "OrderTrackingAgent": "Order Tracking",
          "RefundAgent": "Refund",
          "FAQAgent": "FAQ",
          "EscalationAgent": "Escalation"
        };
        const intentName = intentNameMap[res.agent_name] || "FAQ";
        newMetrics.intentDistribution = newMetrics.intentDistribution.map(i =>
          i.name === intentName ? { ...i, value: i.value + 1 } : i
        );

        // Update Guardrail Violation Count
        if (res.metadata?.guardrail_events?.length > 0) {
          newMetrics.guardrailViolations += 1;
        }
      });

      // Update Query Volume
      const lastPoint = newMetrics.queryVolume[newMetrics.queryVolume.length - 1];
      newMetrics.queryVolume = [
        ...newMetrics.queryVolume.slice(1),
        { 
          time: new Date().toLocaleTimeString().slice(-5), 
          total: lastPoint.total + 1, 
          escalations: responses.some(r => r.agent_name === "EscalationAgent") ? lastPoint.escalations + 1 : lastPoint.escalations 
        }
      ];

      return newMetrics;
    });

    // 2. Update Events
    const newEvents = [];
    responses.forEach(res => {
      const timestamp = new Date().toLocaleTimeString();
      
      // Routing Event
      newEvents.push({
        id: Date.now() + 1,
        type: 'ROUTING',
        text: `Query routed to ${res.agent_name} (confidence: ${res.confidence.toFixed(2)})`,
        time: timestamp,
        color: 'blue'
      });

      // Tool Call (Simulated for demo)
      if (res.agent_name === "OrderTrackingAgent") {
        newEvents.push({
          id: Date.now() + 2,
          type: 'TOOL_CALL',
          text: `Tool: fakestore_api_lookup called — latency: 184ms`,
          time: timestamp,
          color: 'green'
        });
      }

      // Guardrail Event
      if (res.metadata?.guardrail_events?.length > 0) {
        newEvents.push({
          id: Date.now() + 3,
          type: 'GUARDRAIL',
          text: `Guardrail triggered: ${res.metadata.guardrail_events[0].type} (${res.metadata.guardrail_events[0].action_taken})`,
          time: timestamp,
          color: 'amber'
        });
      }

      // Escalation Event
      if (res.agent_name === "EscalationAgent" || res.metadata?.needs_human_approval) {
        newEvents.push({
          id: Date.now() + 4,
          type: 'ESCALATION',
          text: `Policy breach or low confidence — Escalating to human support`,
          time: timestamp,
          color: 'red'
        });
      }
    });

    setEvents(prev => [...newEvents, ...prev].slice(0, 15));
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0F1117] font-sans selection:bg-brand-blue/30">
      {/* Left Panel: 40% */}
      <div className="w-[40%] flex flex-col border-r border-dark-border shadow-2xl z-10 relative">
        {!token ? (
          <LoginForm onLogin={handleLogin} />
        ) : (
          <ChatPanel token={token} onNewInteraction={handleNewInteraction} />
        )}
      </div>

      {/* Right Panel: 60% */}
      <div className="w-[60%] flex flex-col bg-dark-bg">
        <AdminDashboard metrics={metrics} events={events} />
      </div>

      {/* Decorative Glow */}
      <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-brand-blue/5 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-brand-purple/5 blur-[120px] pointer-events-none"></div>
    </div>
  );
}

export default App;
