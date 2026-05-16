import React from 'react';
import { Bot, Shield, AlertTriangle, Fingerprint } from 'lucide-react';
import { parseAgentResponse } from '../mockData';

const AgentResponseCard = ({ response }) => {
  const agentInfo = parseAgentResponse(response.response_text);
  const guardrailEvents = response.metadata?.guardrail_events || [];
  const isEscalated = response.metadata?.needs_human_approval || response.agent_name === "EscalationAgent";
  const hasGuardrails = guardrailEvents.length > 0;

  const colorMap = {
    blue: 'border-brand-blue/30 bg-brand-blue/5 text-brand-blue',
    amber: 'border-brand-amber/30 bg-brand-amber/5 text-brand-amber',
    red: 'border-brand-red/30 bg-brand-red/5 text-brand-red',
    purple: 'border-brand-purple/30 bg-brand-purple/5 text-brand-purple',
  };

  return (
    <div className="flex flex-col max-w-[85%] animate-in fade-in slide-in-from-left-4 duration-300">
      <div className="flex items-center gap-2 mb-1.5 ml-1">
        <div className={`p-1 rounded-md bg-brand-${agentInfo.color}/20`}>
          <Bot className={`w-3.5 h-3.5 text-brand-${agentInfo.color}`} />
        </div>
        <span className={`text-[10px] font-bold uppercase tracking-wider text-brand-${agentInfo.color}`}>
          {agentInfo.name}
        </span>
        <span className="text-[10px] text-slate-500 font-mono">
          Confidence: {Math.round(response.confidence * 100)}%
        </span>
      </div>

      <div className="p-4 rounded-2xl bg-dark-panel border border-dark-border shadow-lg">
        <p className="text-sm leading-relaxed text-slate-200">
          {response.response_text}
        </p>

        {hasGuardrails && (
          <div className="mt-4 flex flex-wrap gap-2">
            <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-brand-amber/10 border border-brand-amber/30 text-brand-amber">
              <Shield className="w-3 h-3" />
              <span className="text-[10px] font-bold uppercase">Guardrail Active</span>
            </div>
            {guardrailEvents.map((event, i) => (
              <div key={i} className="text-[10px] text-brand-amber italic">
                • {event.action_taken}: {event.type}
              </div>
            ))}
          </div>
        )}

        {isEscalated && (
          <div className="mt-3 p-2 rounded bg-brand-red/10 border border-brand-red/30 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-brand-red" />
            <span className="text-xs font-bold text-brand-red uppercase italic">
              Escalated to Human Support
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 mt-2 ml-1 text-[9px] font-mono text-slate-600">
        <div className="flex items-center gap-1">
          <Fingerprint className="w-2.5 h-2.5" />
          TRACE: {response.trace_id?.substring(0, 8) || "N/A"}
        </div>
        <div>{new Date(response.timestamp || Date.now()).toLocaleTimeString()}</div>
      </div>
    </div>
  );
};

export default AgentResponseCard;
