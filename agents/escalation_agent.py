from agents.base import BaseAgent
from agents.tools import ticket_create, assign_agent, notify_team
from models.schemas import Query, AgentResponse, ToolCall

class EscalationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="EscalationAgent")

    async def process(self, query: Query) -> AgentResponse:
        trace_id = query.trace_context.trace_id
        
        # Create Ticket
        ticket_id = ticket_create(
            user_id=query.user_id,
            subject=f"Escalated Query: {query.text[:50]}...",
            description=query.text
        )
        ticket_tool = ToolCall(tool_name="ticket_create", args={"user_id": query.user_id}, result=ticket_id, status="success")
        
        # Assign Agent
        assigned_human = assign_agent(skill_match="general")
        assign_tool = ToolCall(tool_name="assign_agent", args={"skill_match": "general"}, result=assigned_human, status="success")
        
        # Notify Team
        notify_team(channel="slack", message=f"Ticket {ticket_id} created for user {query.user_id}")
        
        system_prompt = """
You are a senior customer support coordinator at Novintix.
You handle complex issues that other agents could not resolve.
Acknowledge the customer's frustration, summarize what has been attempted, and assure them a human agent will follow up.
Give a realistic timeframe (within 2 hours during business hours).
"""
        from utils.llm import invoke_llm
        import json
        
        context_str = json.dumps(query.metadata.get("context", {}), indent=2)
        # Inject ticket info so LLM can mention it
        context_str += f"\n\nSystem Action: Created ticket {ticket_id} assigned to human agent {assigned_human}."
        
        llm_response = invoke_llm(system_prompt, context_str, query.text, query.metadata.get("history", []))
        
        return self.create_response(
            text=llm_response,
            confidence=1.0,
            reasoning="Mandatory escalation requested or triggered by guardrail.",
            trace_id=trace_id,
            tool_calls=[ticket_tool, assign_tool]
        )
