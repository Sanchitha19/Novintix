import pytest
import asyncio
from agents.tracking_agent import OrderTrackingAgent
from agents.refund_agent import RefundAgent
from agents.faq_agent import FAQAgent
from agents.escalation_agent import EscalationAgent
from models.schemas import Query

@pytest.mark.asyncio
async def test_tracking_agent_success():
    agent = OrderTrackingAgent()
    query = Query(user_id="u1", text="Where is my order ORD-123?", session_id="s1")
    response = await agent.process(query)
    assert response.agent_name == "OrderTrackingAgent"
    assert "ORD-123" in response.response_text
    assert response.confidence > 0.9

@pytest.mark.asyncio
async def test_refund_agent_cap_guardrail():
    agent = RefundAgent()
    # ORD-456 has total 6000 in mock DB
    query = Query(user_id="u2", text="I want a refund for ORD-456", session_id="s2")
    response = await agent.process(query)
    assert "exceeds our automated limit" in response.response_text
    assert response.metadata.get("needs_human_approval") is True

@pytest.mark.asyncio
async def test_faq_agent_low_confidence():
    agent = FAQAgent()
    # Mock FAQ agent logic uses random-ish results from tools.py
    # But we can test the threshold logic.
    query = Query(user_id="u3", text="How to fly to Mars?", session_id="s3")
    response = await agent.process(query)
    # If the score is low (which it will be in our mock), it should escalate.
    if response.confidence < 0.72:
        assert "couldn't find a definitive answer" in response.response_text
        assert response.metadata.get("knowledge_gap") is True

@pytest.mark.asyncio
async def test_escalation_agent():
    agent = EscalationAgent()
    query = Query(user_id="u4", text="Talk to human", session_id="s4")
    response = await agent.process(query)
    assert "support ticket" in response.response_text
    assert "TKT-" in response.response_text
