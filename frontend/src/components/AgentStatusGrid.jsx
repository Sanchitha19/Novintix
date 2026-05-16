import React from 'react';
import { Package, RotateCcw, HelpCircle, UserCheck, CheckCircle2, Clock } from 'lucide-react';

const icons = {
  Package: Package,
  RotateCcw: RotateCcw,
  HelpCircle: HelpCircle,
  UserCheck: UserCheck
};

const AgentStatusGrid = ({ agents = [], isDetailed = false }) => {
  if (!agents || agents.length === 0) return <div className="text-slate-500 text-xs">Waiting for agent data...</div>;

  return (
    <div className={`grid grid-cols-1 ${isDetailed ? 'lg:grid-cols-2' : 'sm:grid-cols-2'} gap-4`}>
      {agents.map((agent, idx) => {
        const Icon = icons[agent.icon] || HelpCircle;
        const statusColor = agent.status === 'Active' ? 'text-emerald-500' : 'text-amber-500';
        
        return (
          <div key={idx} className={`p-4 rounded-xl border border-[#30363D] bg-[#161B22]/30 hover:border-blue-500/30 transition-all group ${isDetailed ? 'p-6' : ''}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-slate-800 text-slate-300 group-hover:text-blue-500 transition-colors">
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">{agent.name || "Unknown Agent"}</h4>
                  <div className="flex items-center gap-1.5">
                    <div className={`w-1.5 h-1.5 rounded-full ${agent.status === 'Active' ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${statusColor}`}>{agent.status}</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <span className="text-[10px] font-bold text-slate-500 uppercase block tracking-tighter">Confidence</span>
                <span className="text-xs font-mono text-blue-500">{Math.round((agent.confidence || 0) * 100)}%</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-3 border-t border-[#30363D]/50">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-slate-500" />
                <div className="text-[10px] text-slate-400 font-medium">
                  <span className="text-slate-200">{agent.queries || 0}</span> Queries
                </div>
              </div>
              <div className="flex items-center gap-2 justify-end">
                <Clock className="w-3 h-3 text-slate-500" />
                <div className="text-[10px] text-slate-500 font-mono">Live</div>
              </div>
            </div>

            {isDetailed && (
              <div className="mt-4 pt-4 border-t border-[#30363D]/50 space-y-3 animate-in fade-in duration-500">
                <div className="flex justify-between items-center">
                   <span className="text-[10px] uppercase font-bold text-slate-500 tracking-tighter">Uptime Stability</span>
                   <span className="text-[10px] font-mono text-emerald-500">99.9%</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                   <div className="h-full bg-emerald-500 w-[99.9%]"></div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default AgentStatusGrid;
