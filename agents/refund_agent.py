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
        
        # Identity Resolution
        try:
            numeric_id = int(re.search(r"\d+", query.user_id).group())
            fs_user_id = (numeric_id % 10) + 1
        except:
            fs_user_id = 1

        order_id_match = re.search(r"ORD-(\d+)", query.text.upper())
        
        if not order_id_match:
            return self.create_response(
                text="To process a refund, I need your order ID (e.g., ORD-1). Which order would you like to discuss?",
                confidence=0.8,
                reasoning="Missing order_id for refund request."
            )

        fs_cart_id = int(order_id_match.group(1))
        
        # 1. Fetch Order (Cart)
        try:
            raw_carts = await self.client.get_user_carts(fs_user_id, query.trace_context)
            cart = next((c for c in raw_carts if c["id"] == fs_cart_id), None)
            
            if not cart:
                return self.create_response(
                    text=f"I couldn't find order ORD-{fs_cart_id} in your account records.",
                    confidence=0.9,
                    reasoning="Order not found for this user in FakeStore API."
                )

            products_list = await self.client.get_products(query.trace_context)
            products_map = {p["id"]: p for p in products_list}
            order_data = self.client.map_cart_to_order(cart, products_map)
        except Exception as e:
            log_event("Refund API Error", trace_id, {"error": str(e)})
            return self.create_response(
                text="I'm unable to verify your order details at the moment. Please try again shortly.",
                confidence=0.5,
                reasoning=str(e)
            )

        # 2. Validate Eligibility
        # Demo logic: Delivered orders are eligible
        is_eligible = order_data["status"] == "Delivered"
        amount = order_data["total_amount"]
        
        eligibility_tool = ToolCall(
            tool_name="validate_eligibility", 
            args={"order_id": order_data["order_id"]}, 
            result={"eligible": is_eligible, "amount": amount}, 
            status="success"
        )
        
        if not is_eligible:
            return self.create_response(
                text=f"I see order {order_data['order_id']} is currently '{order_data['status']}'. Refunds can only be processed once the order is 'Delivered'.",
                confidence=1.0,
                reasoning="Refund denied: Order not yet delivered.",
                tool_calls=[eligibility_tool]
            )

        # 3. Check Refund Cap Guardrail (₹5,000)
        # Assuming prices in FakeStore are in USD, I'll treat them as credits or simulate ₹ conversion
        # For demo, I'll treat 1 unit = ₹100 or just use the raw amount if it's small.
        # Actually, let's stick to the requirement: "preserve existing ₹5000 guardrail"
        if amount > 5000:
            log_event("Refund Guardrail Triggered", trace_id, {"amount": amount, "limit": 5000})
            return self.create_response(
                text=f"Your refund request for ₹{amount:.2f} exceeds our automated approval limit. I have initiated an escalation to our finance manager for priority review.",
                confidence=1.0,
                reasoning=f"Refund amount {amount} > 5000 limit. Human approval required.",
                tool_calls=[eligibility_tool],
                metadata={"needs_human_approval": True, "amount": amount}
            )

        # 4. Process Refund (Simulation)
        payment_method = order_data["payment_method"]
        refund_id = f"REF-{os.urandom(4).hex().upper()}"
        
        refund_tool = ToolCall(
            tool_name="initiate_refund_gateway", 
            args={"amount": amount, "method": payment_method}, 
            result={"status": "success", "refund_id": refund_id}, 
            status="success"
        )

        return self.create_response(
            text=f"Success! I have processed a refund of ₹{amount:.2f} to your original payment method ({payment_method}).\n\n**Refund ID**: {refund_id}",
            confidence=1.0,
            reasoning="Refund processed successfully within automated limits.",
            tool_calls=[eligibility_tool, refund_tool]
        )
