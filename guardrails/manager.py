from typing import List, Dict, Any
from models.schemas import Query, AgentResponse, GuardrailEvent, GuardrailType
from guardrails.pii import PIIMasker
from guardrails.loop_breaker import LoopBreaker

class GuardrailManager:
    def __init__(self):
        self.pii_masker = PIIMasker()
        self.loop_breaker = LoopBreaker(max_hops=3)

    async def pre_process(self, query: Query) -> Query:
        """Apply guardrails before agent execution."""
        # 1. PII Masking on input
        query.text = self.pii_masker.mask(query.text)
        
        # 2. Loop Breaker check
        if not self.loop_breaker.check_and_increment(query.session_id):
            raise Exception("Loop limit exceeded. Escalating to human.")
            
        return query

    async def post_process(self, responses: List[AgentResponse], trace_id: str) -> List[AgentResponse]:
        """Apply guardrails after agent execution."""
        events = []
        for response in responses:
            # 1. Mask PII in response text
            original_text = response.response_text
            response.response_text = self.pii_masker.mask(response.response_text)
            
            if original_text != response.response_text:
                events.append(GuardrailEvent(
                    type=GuardrailType.PII_MASKING,
                    action_taken="redacted",
                    details={"field": "response_text"},
                    trace_id=trace_id
                ))
            
            # 2. Check for escalation triggers in metadata (already set by agents)
            if response.metadata.get("needs_human_approval"):
                events.append(GuardrailEvent(
                    type=GuardrailType.REFUND_CAP,
                    action_taken="escalated",
                    details={"amount": response.metadata.get("amount")},
                    trace_id=trace_id
                ))

        # Store events in metadata for observability
        for response in responses:
            response.metadata["guardrail_events"] = [e.dict() for e in events]

        return responses
