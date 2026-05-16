import React from 'react';
import { ShieldAlert, ShieldX, UserMinus, Repeat } from 'lucide-react';

const GuardrailCounter = ({ metrics }) => {
  const breakdown = [
    { label: "Refund Cap", value: 2, icon: ShieldX, color: "text-brand-amber" },
    { label: "Loop Breaker", value: 1, icon: Repeat, color: "text-brand-purple" },
    { label: "PII Mask", value: 0, icon: UserMinus, color: "text-brand-blue" },
  ];

  return (
    <div className="flex flex-col h-full">
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4 px-1">Security Violations</h3>
      <div className="flex-1 flex flex-col justify-center">
        <div className="flex items-center gap-4 mb-6 p-4 rounded-xl bg-brand-red/5 border border-brand-red/20">
          <div className="p-3 rounded-full bg-brand-red/20">
            <ShieldAlert className="w-8 h-8 text-brand-red" />
          </div>
          <div>
            <div className="text-3xl font-bold text-brand-red">{metrics.guardrailViolations || 3}</div>
            <div className="text-[10px] font-bold uppercase tracking-widest text-brand-red/70">Total Violations Today</div>
          </div>
        </div>

        <div className="space-y-3">
          {breakdown.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-2 px-3 rounded-lg bg-slate-800/30 border border-dark-border/50">
              <div className="flex items-center gap-2">
                <item.icon className={`w-3.5 h-3.5 ${item.color}`} />
                <span className="text-[11px] font-bold text-slate-400">{item.label}</span>
              </div>
              <span className="text-xs font-mono font-bold text-slate-200">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GuardrailCounter;
