import React from 'react';
import { Activity, Users, Zap, ShieldCheck, ExternalLink } from 'lucide-react';

const HealthCards = ({ health, metrics }) => {
  const cards = [
    { 
      title: "API Status", 
      value: health.status === 'healthy' ? "Operational" : "Degraded", 
      sub: "v1.0.0", 
      icon: Activity, 
      color: health.status === 'healthy' ? "text-brand-green" : "text-brand-red",
      status: health.status === 'healthy' ? "bg-brand-green" : "bg-brand-red"
    },
    { 
      title: "Active Agents", 
      value: "4 / 4", 
      sub: "All instances live", 
      icon: Users, 
      color: "text-brand-blue",
      status: "bg-brand-green"
    },
    { 
      title: "Avg Latency", 
      value: metrics.avgResponseTime || "1.4s", 
      sub: "Last 5 mins", 
      icon: Zap, 
      color: "text-brand-amber",
      status: "bg-brand-green"
    },
    { 
      title: "Guardrail Events", 
      value: metrics.guardrailViolations || 0, 
      sub: "Triggered today", 
      icon: ShieldCheck, 
      color: "text-brand-purple",
      status: metrics.guardrailViolations > 0 ? "bg-brand-amber" : "bg-brand-green",
      onClick: onGuardrailClick
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => (
        <div 
          key={idx} 
          onClick={card.onClick}
          className={`p-4 rounded-xl glass-panel border border-dark-border relative overflow-hidden group ${card.onClick ? 'cursor-pointer hover:border-brand-blue/50' : ''}`}
        >
          <div className="flex items-start justify-between relative z-10">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">{card.title}</p>
              <h3 className={`text-xl font-bold ${card.color}`}>{card.value}</h3>
              <p className="text-[10px] text-slate-500 mt-1 font-mono">{card.sub}</p>
            </div>
            <div className={`p-2 rounded-lg bg-slate-800/50 ${card.color}`}>
              <card.icon className="w-5 h-5" />
            </div>
          </div>
          {card.onClick && (
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
               <ExternalLink className="w-3 h-3 text-brand-blue" />
            </div>
          )}
          <div className={`absolute bottom-0 left-0 w-full h-1 ${card.status} opacity-50`}></div>
          <div className={`absolute -right-4 -bottom-4 w-16 h-16 ${card.status} opacity-[0.03] rounded-full group-hover:scale-150 transition-transform duration-500`}></div>
        </div>
      ))}
    </div>
  );
};

export default HealthCards;
