import React from 'react';
import { Terminal, Shield, Zap, AlertCircle, Cpu, Search } from 'lucide-react';

const icons = {
  ROUTING: Search,
  GUARDRAIL: Shield,
  ESCALATION: AlertCircle,
  RAG: Zap,
  TOOL_CALL: Cpu
};

const colors = {
  blue: 'text-brand-blue bg-brand-blue/10 border-brand-blue/20',
  amber: 'text-brand-amber bg-brand-amber/10 border-brand-amber/20',
  red: 'text-brand-red bg-brand-red/10 border-brand-red/20',
  purple: 'text-brand-purple bg-brand-purple/10 border-brand-purple/20',
  green: 'text-brand-green bg-brand-green/10 border-brand-green/20'
};

const EventLog = ({ events }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-4 px-1">
        <Terminal className="w-4 h-4 text-brand-blue" />
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Live System Events</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
        {events.map((event, idx) => {
          const Icon = icons[event.type] || Terminal;
          const colorClass = colors[event.color] || colors.blue;
          
          return (
            <div key={event.id || idx} className="p-3 rounded-lg bg-dark-panel/20 border border-dark-border/50 flex items-start gap-3 animate-in slide-in-from-top-2 duration-300">
              <div className={`p-1.5 rounded border ${colorClass}`}>
                <Icon className="w-3.5 h-3.5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-[10px] font-bold uppercase tracking-tighter ${colorClass.split(' ')[0]}`}>
                    {event.type}
                  </span>
                  <span className="text-[9px] font-mono text-slate-600">{event.time}</span>
                </div>
                <p className="text-[11px] text-slate-400 font-medium leading-relaxed truncate">
                  {event.text}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EventLog;
