from agents.base import BaseAgent
from agents.tools import ticket_create, assign_agent, notify_team
from models.schemas import Query, AgentResponse, ToolCall

class EscalationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="EscalationAgent")

    async def process(self, query: Query) -> AgentResponse:
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
        
        return self.create_response(
            text=f"I've created a support ticket ({ticket_id}) for you. A human agent ({assigned_human}) will get back to you shortly via your registered email.",
            confidence=1.0,
            reasoning="Mandatory escalation requested or triggered by guardrail.",
            tool_calls=[ticket_tool, assign_tool]
        )
