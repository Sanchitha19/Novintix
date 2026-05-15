import pytest
from orchestrator.engine import Orchestrator
from models.schemas import Query

@pytest.mark.asyncio
async def test_e2e_complex_query():
    orch = Orchestrator()
    # Complex query that might trigger multiple agents or guardrails
    query = Query(
        user_id="user_test_99",
        text="I want a refund for my order ORD-456. My email is test@example.com and phone is +91-9876543210.",
        session_id="session_e2e_1"
    )
    
    responses = await orch.route_and_execute(query)
    
    assert len(responses) >= 1
    # Check for PII masking
    assert "test@example.com" not in responses[0].response_text
    assert "[REDACTED_EMAIL]" in responses[0].response_text
    
    # Check for refund logic (ORD-456 is 6000, should trigger escalation)
    assert any(res.metadata.get("needs_human_approval") for res in responses)
    assert any("exceeds our automated limit" in res.response_text for res in responses)

@pytest.mark.asyncio
async def test_e2e_faq_and_tracking():
    orch = Orchestrator()
    query = Query(
        user_id="user_test_100",
        text="Where is ORD-123? Also, what is your return period?",
        session_id="session_e2e_2"
    )
    
    responses = await orch.route_and_execute(query)
    
    # Should have tracking response and FAQ response
    intents = [r.metadata["routing"]["intent"] for r in responses]
    assert "track_order" in intents
    assert "faq" in intents or "refund" in intents
