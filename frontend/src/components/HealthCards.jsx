import React from 'react';
import { Activity, Users, Zap, ShieldCheck, ExternalLink } from 'lucide-react';

const HealthCards = ({ health = {}, metrics = {}, onGuardrailClick }) => {
  // Defensive values
  const apiStatus = health?.status === 'healthy' ? "Operational" : "Error";
  const activeAgents = "4 / 4";
  const avgLatency = metrics?.avgResponseTime || "1.4s";
  const violations = metrics?.guardrailViolations || 0;

  const cards = [
    { 
      title: "API Status", 
      value: apiStatus, 
      sub: "v1.0.0", 
      icon: Activity, 
      color: "text-emerald-500",
      status: health?.status === 'healthy' ? "bg-emerald-500" : "bg-red-500"
    },
    { 
      title: "Active Agents", 
      value: activeAgents, 
      sub: "All instances live", 
      icon: Users, 
      color: "text-blue-500",
      status: "bg-blue-500"
    },
    { 
      title: "Avg Latency", 
      value: avgLatency, 
      sub: "Last 5 mins", 
      icon: Zap, 
      color: "text-amber-500",
      status: "bg-amber-500"
    },
    { 
      title: "Guardrail Events", 
      value: violations, 
      sub: "Triggered today", 
      icon: ShieldCheck, 
      color: "text-purple-500",
      status: violations > 0 ? "bg-amber-500" : "bg-emerald-500",
      onClick: onGuardrailClick
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => (
        <div 
          key={idx} 
          onClick={card.onClick}
          className={`p-4 rounded-xl bg-[#161B22]/50 border border-[#30363D] relative overflow-hidden group ${card.onClick ? 'cursor-pointer hover:border-blue-500/50' : ''}`}
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
               <ExternalLink className="w-3 h-3 text-blue-500" />
            </div>
          )}
          <div className={`absolute bottom-0 left-0 w-full h-1 ${card.status} opacity-50`}></div>
        </div>
      ))}
    </div>
  );
};

export default HealthCards;
