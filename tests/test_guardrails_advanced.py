import pytest
import asyncio
from guardrails.manager import GuardrailManager
from models.schemas import Query, AgentResponse, GuardrailType
from agents.refund_agent import RefundAgent

@pytest.mark.asyncio
async def test_refund_guardrail_below_limit():
    agent = RefundAgent()
    # ORD-123 is 2000 in mock DB
    query = Query(user_id="u1", text="Refund ORD-123", session_id="s1")
    response = await agent.process(query)
    assert "initiated" in response.response_text
    assert response.metadata.get("needs_human_approval") is not True

@pytest.mark.asyncio
async def test_refund_guardrail_above_limit():
    agent = RefundAgent()
    # ORD-456 is 6000 in mock DB
    query = Query(user_id="u2", text="Refund ORD-456", session_id="s2")
    response = await agent.process(query)
    assert "exceeds our automated limit" in response.response_text
    assert response.metadata.get("needs_human_approval") is True

@pytest.mark.asyncio
async def test_loop_breaker_forced_escalation():
    manager = GuardrailManager()
    session_id = "loop_session"
    query = Query(user_id="u3", text="Hello", session_id=session_id)
    
    # 1st hop
    await manager.pre_process(query)
    # 2nd hop
    await manager.pre_process(query)
    # 3rd hop
    await manager.pre_process(query)
    
    # 4th hop should fail
    with pytest.raises(Exception) as excinfo:
        await manager.pre_process(query)
    assert "Loop limit exceeded" in str(excinfo.value)

@pytest.mark.asyncio
async def test_pii_masking_in_responses():
    manager = GuardrailManager()
    responses = [
        AgentResponse(
            agent_name="TestAgent",
            response_text="Contact me at sanchi@example.com or 9876543210",
            confidence=1.0,
            reasoning="Test"
        )
    ]
    processed = await manager.post_process(responses, "trace_1")
    assert "sanchi@example.com" not in processed[0].response_text
    assert "[REDACTED_EMAIL]" in processed[0].response_text
    assert "[REDACTED_PHONE]" in processed[0].response_text
