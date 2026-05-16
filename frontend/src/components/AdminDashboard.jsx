import React, { useState, useEffect } from 'react';
import { LayoutDashboard, RefreshCw, ExternalLink } from 'lucide-react';
import HealthCards from './HealthCards';
import EventLog from './EventLog';
import AgentStatusGrid from './AgentStatusGrid';
import { getHealth } from '../api';

const AdminDashboard = ({ metrics, events }) => {
  const [health, setHealth] = useState({ status: 'healthy' });
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const pollHealth = async () => {
      try {
        const data = await getHealth();
        if (data) setHealth(data);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch (e) {
        setHealth({ status: 'error' });
      }
    };
    pollHealth();
    const interval = setInterval(pollHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!metrics) return <div className="p-10 text-slate-500 font-mono">Loading Dashboard Data...</div>;

  return (
    <div className="flex flex-col h-full bg-[#0F1117] overflow-y-auto text-white">
      {/* Header */}
      <div className="p-6 border-b border-[#30363D] bg-[#161B22]/30 backdrop-blur-md flex items-center justify-between sticky top-0 z-20">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <LayoutDashboard className="w-5 h-5 text-blue-500" />
            <h1 className="text-xl font-bold tracking-tight">System Monitor</h1>
          </div>
          <p className="text-xs text-slate-500 font-medium">Real-time observability</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex bg-slate-800/50 rounded-lg p-1 border border-[#30363D]">
            {['overview', 'agents'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-all ${
                  activeTab === tab ? 'bg-blue-600 text-white' : 'text-slate-500'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <HealthCards health={health} metrics={metrics} />

        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-500">
            <div className="lg:col-span-2 space-y-6">
              <div className="p-6 rounded-2xl bg-[#161B22]/50 border border-[#30363D]">
                <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6">Agent Status</h3>
                <AgentStatusGrid agents={metrics.agentStatus} />
              </div>
            </div>
            <div className="p-6 rounded-2xl bg-[#161B22]/50 border border-[#30363D]">
               <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6">Live Logs</h3>
               <EventLog events={events} />
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="p-6 rounded-2xl bg-[#161B22]/50 border border-[#30363D] animate-in slide-in-from-bottom-4 duration-500">
             <AgentStatusGrid agents={metrics.agentStatus} isDetailed={true} />
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
