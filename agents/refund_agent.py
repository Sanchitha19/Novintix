import re
from typing import List
from agents.base import BaseAgent
from agents.tools import validate_eligibility, initiate_refund_gateway, order_db_lookup
from models.schemas import Query, AgentResponse, ToolCall

class RefundAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RefundAgent")

    async def process(self, query: Query) -> AgentResponse:
        order_id_match = re.search(r"ORD-\d+", query.text.upper())
        
        if not order_id_match:
            return self.create_response(
                text="To process a refund, I need your order ID. Could you please provide it?",
                confidence=0.8,
                reasoning="Missing order_id for refund request."
            )

        order_id = order_id_match.group(0)
        
        # 1. Validate eligibility
        eligibility = validate_eligibility(order_id)
        eligibility_tool = ToolCall(tool_name="validate_eligibility", args={"order_id": order_id}, result=eligibility, status="success")
        
        if not eligibility.get("eligible"):
            return self.create_response(
                text=f"I'm sorry, order {order_id} is not eligible for a refund. Reason: {eligibility.get('reason')}",
                confidence=0.9,
                reasoning="Order ineligible for refund based on policy.",
                tool_calls=[eligibility_tool]
            )

        # 2. Check Refund Cap Guardrail (Hard coded for ₹5,000 as per requirements)
        amount = eligibility.get("max_refund", 0)
        if amount > 5000:
            return self.create_response(
                text=f"Your refund request for ₹{amount} exceeds our automated limit. I am escalating this to a human manager for immediate approval.",
                confidence=1.0,
                reasoning=f"Refund amount {amount} > 5000 limit. Triggering human approval workflow.",
                tool_calls=[eligibility_tool],
                metadata={"needs_human_approval": True, "amount": amount}
            )

        # 3. Process Refund
        order_data = order_db_lookup(order_id)
        payment_method = order_data.get("payment_method", "unknown")
        
        refund_result = initiate_refund_gateway(amount, payment_method)
        refund_tool = ToolCall(tool_name="initiate_refund_gateway", args={"amount": amount, "payment_method": payment_method}, result=refund_result, status="success")

        if refund_result.get("status") == "success":
            return self.create_response(
                text=f"Great news! Your refund of ₹{amount} for order {order_id} has been initiated. Transaction ID: {refund_result.get('transaction_id')}.",
                confidence=0.95,
                reasoning="Refund processed successfully via gateway.",
                tool_calls=[eligibility_tool, refund_tool]
            )
        else:
            return self.create_response(
                text="I encountered an issue while processing your refund. I've logged this and a human agent will follow up.",
                confidence=0.9,
                reasoning=f"Refund gateway failed: {refund_result.get('reason')}",
                tool_calls=[eligibility_tool, refund_tool]
            )
