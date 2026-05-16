import React from 'react';
import { Package, RotateCcw, HelpCircle, UserCheck, CheckCircle2, Clock } from 'lucide-react';

const icons = {
  Package: Package,
  RotateCcw: RotateCcw,
  HelpCircle: HelpCircle,
  UserCheck: UserCheck
};

const AgentStatusGrid = ({ agents }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {agents.map((agent, idx) => {
        const Icon = icons[agent.icon] || HelpCircle;
        return (
          <div key={idx} className="p-4 rounded-xl border border-dark-border bg-dark-panel/30 hover:border-brand-blue/30 transition-all group">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-slate-800 text-slate-300 group-hover:text-brand-blue transition-colors">
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-200">{agent.name}</h4>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <div className={`w-1.5 h-1.5 rounded-full ${agent.status === 'Active' ? 'bg-brand-green' : 'bg-slate-600'}`}></div>
                    <span className="text-[10px] uppercase font-bold tracking-tighter text-slate-500">{agent.status}</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs font-mono font-bold text-brand-blue">{Math.round(agent.confidence * 100)}%</div>
                <div className="text-[9px] uppercase font-bold text-slate-600 tracking-tighter">Confidence</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-3 border-t border-dark-border/50">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-slate-500" />
                <div className="text-[10px] text-slate-400 font-medium">
                  <span className="text-slate-200">{agent.queries}</span> Queries
                </div>
              </div>
              <div className="flex items-center gap-2 justify-end">
                <Clock className="w-3 h-3 text-slate-500" />
                <div className="text-[10px] text-slate-500 font-mono">2m ago</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AgentStatusGrid;
