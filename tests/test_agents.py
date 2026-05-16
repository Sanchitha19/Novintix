import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from agents.tracking_agent import OrderTrackingAgent
from agents.refund_agent import RefundAgent
from agents.faq_agent import FAQAgent
from agents.escalation_agent import EscalationAgent
from models.schemas import Query

@pytest.mark.asyncio
async def test_tracking_agent_success():
    agent = OrderTrackingAgent()
    query = Query(user_id="user_001", text="Where is my order ORD-123?", session_id="s1")
    response = await agent.process(query)
    assert response.agent_name == "OrderTrackingAgent"
    assert "ORD-123" in response.response_text
    assert response.confidence >= 0.9

@pytest.mark.asyncio
async def test_refund_agent_cap_guardrail():
    agent = RefundAgent()
    # conftest mocks ORD-456 to have 6000
    query = Query(user_id="user_001", text="I want a refund for ORD-456", session_id="s2")
    response = await agent.process(query)
    assert "exceeds our automated limit" in response.response_text
    assert response.metadata.get("needs_human_approval") is True

@pytest.mark.asyncio
async def test_faq_agent_low_confidence():
    agent = FAQAgent()
    # Mocking the internal init and retriever to avoid API calls and force low confidence
    agent.initialized = True
    agent.retriever = AsyncMock()
    agent.retriever.search = AsyncMock(return_value=[{"text": "Irrelevant", "score": 0.5}])
    
    query = Query(user_id="u3", text="How to fly to Mars?", session_id="s3")
    response = await agent.process(query)
    assert "not entirely sure" in response.response_text
    assert response.metadata.get("knowledge_gap") is True

@pytest.mark.asyncio
async def test_escalation_agent():
    agent = EscalationAgent()
    query = Query(user_id="u4", text="Talk to human", session_id="s4")
    response = await agent.process(query)
    assert "support ticket" in response.response_text
    assert "TKT-" in response.response_text
