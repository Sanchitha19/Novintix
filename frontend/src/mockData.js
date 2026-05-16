export const generateInitialMetrics = () => ({
  totalQueries: 124,
  escalations: 12,
  guardrailViolations: 3,
  avgResponseTime: "1.4s",
  intentDistribution: [
    { name: 'Order Tracking', value: 45, color: '#3B82F6' },
    { name: 'Refund', value: 25, color: '#F59E0B' },
    { name: 'FAQ', value: 20, color: '#8B5CF6' },
    { name: 'Escalation', value: 10, color: '#EF4444' },
  ],
  queryVolume: Array.from({ length: 10 }, (_, i) => ({
    time: `${i * 5}s`,
    total: Math.floor(Math.random() * 20) + 10,
    escalations: Math.floor(Math.random() * 5),
  })),
  agentStatus: [
    { id: 'tracking', name: 'Order Tracking', status: 'Active', queries: 56, confidence: 0.92, icon: 'Package' },
    { id: 'refund', name: 'Refund Agent', status: 'Idle', queries: 32, confidence: 0.88, icon: 'RotateCcw' },
    { id: 'faq', name: 'FAQ Agent', status: 'Active', queries: 28, confidence: 0.81, icon: 'HelpCircle' },
    { id: 'escalation', name: 'Escalation Agent', status: 'Idle', queries: 8, confidence: 0.94, icon: 'UserCheck' },
  ]
});

export const initialEvents = [
  { id: 1, type: 'ROUTING', text: 'Query routed to Order Tracking Agent (confidence: 0.91)', time: '10:42:05', color: 'blue' },
  { id: 2, type: 'TOOL_CALL', text: 'Tool: order_db_lookup called — latency: 142ms', time: '10:42:06', color: 'green' },
  { id: 3, type: 'RAG', text: 'RAG retrieval — top score: 0.84, 3 documents retrieved', time: '10:41:50', color: 'purple' },
  { id: 4, type: 'GUARDRAIL', text: 'Refund guardrail triggered — amount exceeds Rs.5000', time: '10:40:12', color: 'amber' },
];

export const parseAgentResponse = (responseText) => {
  const text = responseText.toLowerCase();
  if (text.includes('order') || text.includes('track') || text.includes('package')) {
    return { name: 'Order Tracking Agent', color: 'blue', icon: 'Package' };
  }
  if (text.includes('refund') || text.includes('return') || text.includes('money back')) {
    return { name: 'Refund Agent', color: 'amber', icon: 'RotateCcw' };
  }
  if (text.includes('escalat') || text.includes('human') || text.includes('ticket') || text.includes('agent')) {
    return { name: 'Escalation Agent', color: 'red', icon: 'UserCheck' };
  }
  return { name: 'FAQ Agent', color: 'purple', icon: 'HelpCircle' };
};
