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
        {/* Row 1: Health Cards */}
        <HealthCards health={health} metrics={metrics} />

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
                <button className="text-[10px] font-bold text-brand-blue hover:underline flex items-center gap-1">
                  DETAILED VIEW <ExternalLink className="w-3 h-3" />
                </button>
              </div>
              <AgentStatusGrid agents={metrics.agentStatus} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div className="p-6 rounded-2xl glass-panel border border-dark-border min-h-[280px]">
                  <GuardrailCounter metrics={metrics} />
               </div>
               <div className="p-6 rounded-2xl glass-panel border border-dark-border min-h-[280px]">
                  {/* Additional stats or empty for balance */}
                  <div className="flex flex-col h-full justify-center items-center opacity-40">
                    <Clock className="w-12 h-12 text-slate-600 mb-2" />
                    <span className="text-xs font-bold uppercase tracking-widest">Historical Trends Loading...</span>
                  </div>
               </div>
            </div>
          </div>
          
          <div className="p-6 rounded-2xl glass-panel border border-dark-border h-[620px]">
            <EventLog events={events} />
          </div>
        </div>
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
