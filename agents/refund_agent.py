import re
from typing import List
from agents.base import BaseAgent
from models.schemas import Query, AgentResponse, ToolCall
from integrations.fakestore_client import FakeStoreClient
from monitoring.logger import log_event
import os

class RefundAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RefundAgent")
        self.client = FakeStoreClient()

    async def process(self, query: Query) -> AgentResponse:
        trace_id = query.trace_context.trace_id
        
        system_prompt = """
You are the Refund Processing specialist at Novintix.
You have access to the customer's order and cart data in the context.
Help customers with refund eligibility, refund status, and return procedures. 
If the refund amount exceeds Rs.5000 inform the customer it requires manager approval.
Be empathetic and solution-focused.
"""
        from utils.llm import invoke_llm
        import json
        
        context_str = json.dumps(query.metadata.get("context", {}), indent=2)
        llm_response = invoke_llm(system_prompt, context_str, query.text, query.metadata.get("history", []))

        # We keep the business logic for metadata/tool calls
        needs_approval = False
        amount = 0
        
        # Simple extraction for demo metadata
        order_id_match = re.search(r"ORD-(\d+)", query.text.upper())
        if order_id_match:
            fs_cart_id = int(order_id_match.group(1))
            orders = query.metadata.get("context", {}).get("orders", [])
            target_order = next((o for o in orders if o["order_id"] == f"ORD-{fs_cart_id}"), None)
            if target_order:
                amount = target_order.get("total_amount", 0)
                if amount > 5000:
                    needs_approval = True
                    log_event("Refund Guardrail Triggered", trace_id, {"amount": amount, "limit": 5000})

        tool_calls = []
        if order_id_match:
            tool_calls.append(ToolCall(
                tool_name="validate_eligibility", 
                args={"order_id": f"ORD-{order_id_match.group(1)}"}, 
                result={"eligible": True, "amount": amount}, 
                status="success"
            ))

        return self.create_response(
            text=llm_response,
            confidence=0.95,
            reasoning="Generated using LLM with full context.",
            trace_id=trace_id,
            tool_calls=tool_calls,
            metadata={"needs_human_approval": needs_approval, "amount": amount} if needs_approval else {}
        )
