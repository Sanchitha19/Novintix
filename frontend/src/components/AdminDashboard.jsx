import React, { useState, useEffect } from 'react';
import { LayoutDashboard, RefreshCw, Clock, ExternalLink } from 'lucide-react';
import HealthCards from './HealthCards';
import QueryVolumeChart from './QueryVolumeChart';
import IntentDonut from './IntentDonut';
import AgentStatusGrid from './AgentStatusGrid';
import EventLog from './EventLog';
import GuardrailCounter from './GuardrailCounter';
import { getHealth } from '../api';

const AdminDashboard = ({ metrics, events }) => {
  const [health, setHealth] = useState({ status: 'healthy' });
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'security', 'agents'

  useEffect(() => {
    const pollHealth = async () => {
      try {
        const data = await getHealth();
        setHealth(data);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch (e) {
        setHealth({ status: 'error' });
      }
    };

    const interval = setInterval(pollHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full bg-[#0F1117] overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b border-dark-border bg-dark-panel/30 backdrop-blur-md flex items-center justify-between sticky top-0 z-20">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <LayoutDashboard className="w-5 h-5 text-brand-blue" />
            <h1 className="text-xl font-bold text-white tracking-tight">Live System Monitor</h1>
          </div>
          <p className="text-xs text-slate-500 font-medium">Real-time agent observability & guardrail metrics</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex bg-slate-800/50 rounded-lg p-1 border border-dark-border mr-4">
            {['overview', 'security', 'agents'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-all ${
                  activeTab === tab 
                    ? 'bg-brand-blue text-white shadow-lg shadow-brand-blue/20' 
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-dark-border">
            <RefreshCw className={`w-3.5 h-3.5 text-brand-blue ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Auto-Refresh ON</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-bold text-slate-600 uppercase tracking-tighter">Last Pulse</span>
            <span className="text-xs font-mono text-brand-blue">{lastUpdated}</span>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Row 1: Health Cards (Always Visible) */}
        <HealthCards 
          health={health} 
          metrics={metrics} 
          onGuardrailClick={() => setActiveTab('security')} 
        />

        {activeTab === 'overview' && (
          <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
            {/* Row 2: Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 p-6 rounded-2xl glass-panel border border-dark-border min-h-[300px]">
                <QueryVolumeChart data={metrics.queryVolume} />
              </div>
              <div className="p-6 rounded-2xl glass-panel border border-dark-border min-h-[300px]">
                <IntentDonut data={metrics.intentDistribution} />
              </div>
            </div>

            {/* Row 3: Agents & Events */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="p-6 rounded-2xl glass-panel border border-dark-border">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Agent Performance Cluster</h3>
                    <button 
                      onClick={() => setActiveTab('agents')}
                      className="text-[10px] font-bold text-brand-blue hover:underline flex items-center gap-1"
                    >
                      DETAILED VIEW <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                  <AgentStatusGrid agents={metrics.agentStatus} />
                </div>
              </div>
              <div className="p-6 rounded-2xl glass-panel border border-dark-border h-full">
                <EventLog events={events} />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in slide-in-from-right-4 duration-300">
            <div className="p-6 rounded-2xl glass-panel border border-dark-border">
              <GuardrailCounter metrics={metrics} />
            </div>
            <div className="p-6 rounded-2xl glass-panel border border-dark-border">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6">Security Incident Feed</h3>
              <div className="space-y-4">
                {events.filter(e => e.type === 'GUARDRAIL' || e.type === 'ESCALATION').map((e, i) => (
                  <div key={i} className="p-4 rounded-xl bg-dark-bg border border-dark-border">
                    <div className="flex justify-between items-center mb-2">
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${e.type === 'GUARDRAIL' ? 'bg-brand-amber/20 text-brand-amber' : 'bg-brand-red/20 text-brand-red'}`}>{e.type}</span>
                      <span className="text-[10px] font-mono text-slate-600">{e.time}</span>
                    </div>
                    <p className="text-sm text-slate-300">{e.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="animate-in slide-in-from-bottom-4 duration-300">
            <div className="p-6 rounded-2xl glass-panel border border-dark-border">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6">Deep Agent Performance Profiling</h3>
              <AgentStatusGrid agents={metrics.agentStatus} isDetailed={true} />
            </div>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <div className="p-8 border-t border-dark-border flex items-center justify-between opacity-30 mt-12">
        <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
          Novintix Agentic AI • Observability v2.4
        </div>
        <div className="flex gap-4">
          <div className="w-2 h-2 rounded-full bg-brand-green"></div>
          <div className="w-2 h-2 rounded-full bg-brand-blue"></div>
          <div className="w-2 h-2 rounded-full bg-brand-purple"></div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
