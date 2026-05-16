import re
import asyncio
from typing import List, Dict, Any
from agents.base import BaseAgent
from models.schemas import Query, AgentResponse, ToolCall
from integrations.fakestore_client import FakeStoreClient
from monitoring.metrics import ORDER_TRACKING_REQUESTS
from monitoring.logger import log_event

class OrderTrackingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="OrderTrackingAgent")
        self.client = FakeStoreClient()

    async def process(self, query: Query) -> AgentResponse:
        ORDER_TRACKING_REQUESTS.inc()
        trace_id = query.trace_context.trace_id
        
        system_prompt = """
You are the Order Tracking specialist at Novintix.
You have access to the customer's order data provided in the context. Answer questions about delivery status, estimated arrival, delays, and shipment updates.
Be specific — reference the actual order details.
Never say "I need your order ID" if order data is already provided in context.
If multiple orders exist and the customer didn't specify, ask them which one they mean, listing the most recent ones.
If an order ends in 5 or 0, mention a slight delay due to high seasonal volume.
"""
        from utils.llm import invoke_llm
        import json
        
        context_str = json.dumps(query.metadata.get("context", {}), indent=2)
        llm_response = invoke_llm(system_prompt, context_str, query.text, query.metadata.get("history", []))

        # We can still mock a tool call for the UI if we want to show it
        tool_calls = [
            ToolCall(tool_name="get_user_carts", args={"user_id": query.metadata.get("context", {}).get("customer_id", 1)}, result="Fetched from context", status="success")
        ]

        return self.create_response(
            text=llm_response,
            confidence=0.95,
            reasoning="Generated using LLM with full context.",
            trace_id=trace_id,
            tool_calls=tool_calls
        )
