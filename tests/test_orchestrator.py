import pytest
from orchestrator.engine import Orchestrator
from models.schemas import Query, Intent

@pytest.mark.asyncio
async def test_orchestrator_routing_tracking():
    orch = Orchestrator()
    query = Query(user_id="u1", text="Where is my order ORD-123?", session_id="s1")
    responses = await orch.route_and_execute(query)
    
    assert len(responses) >= 1
    assert responses[0].agent_name == "OrderTrackingAgent"
    assert "routing" in responses[0].metadata
    assert responses[0].metadata["routing"]["intent"] == Intent.TRACK_ORDER

@pytest.mark.asyncio
async def test_orchestrator_multi_intent():
    orch = Orchestrator()
    # Multi-intent query
    query = Query(user_id="u2", text="Track my order ORD-123 and also tell me about your refund policy", session_id="s2")
    responses = await orch.route_and_execute(query)
    
    # Check if both agents were triggered (or at least classified)
    intents = [r.metadata["routing"]["intent"] for r in responses]
    assert Intent.TRACK_ORDER in intents
    assert Intent.FAQ in intents or Intent.REFUND in intents
