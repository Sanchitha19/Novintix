import pytest
from orchestrator.engine import Orchestrator
from models.schemas import Query

@pytest.mark.asyncio
async def test_e2e_complex_query():
    orch = Orchestrator()
    # Query that triggers Refund Agent and exceeds limit
    query = Query(
        user_id="user_test_99",
        text="I want a refund for my order ORD-456.",
        session_id="session_e2e_1"
    )
    
    responses = await orch.route_and_execute(query)
    
    assert len(responses) >= 1
    # Check for refund logic (ORD-456 mock total is 6000)
    assert any(res.metadata.get("needs_human_approval") for res in responses)
    assert any("exceeds our automated limit" in res.response_text for res in responses)

@pytest.mark.asyncio
async def test_e2e_pii_masking():
    orch = Orchestrator()
    # Query with PII. We check if the orchestrator (via guardrails) handles it.
    query = Query(
        user_id="user_test_101",
        text="Contact me at sanchi@example.com",
        session_id="session_e2e_pii"
    )
    
    # We'll mock the agent to return the same text to see if it gets masked in post-process
    with pytest.MonkeyPatch.context() as m:
        # Mocking FAQ agent to return the input text
        from agents.faq_agent import FAQAgent
        async def mock_process(self, q):
            return self.create_response(text=q.text, confidence=1.0, reasoning="Mock")
        m.setattr(FAQAgent, "process", mock_process)
        
        responses = await orch.route_and_execute(query)
        assert "[REDACTED_EMAIL]" in responses[0].response_text
        assert "sanchi@example.com" not in responses[0].response_text

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
    assert "faq" in intents
