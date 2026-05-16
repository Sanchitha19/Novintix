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
        
        # Identity Resolution: Map user_id to Fake Store user_id (1-10)
        # Assuming user_id is like 'user_001' or similar
        try:
            numeric_id = int(re.search(r"\d+", query.user_id).group())
            fs_user_id = (numeric_id % 10) + 1
        except:
            fs_user_id = 1 # Fallback for demo

        log_event("Resolving Identity", trace_id, {"internal_user": query.user_id, "fs_user": fs_user_id})

        # Extraction logic
        order_id_match = re.search(r"ORD-(\d+)", query.text.upper())
        
        # Tool Call: Get User Carts
        try:
            raw_carts = await self.client.get_user_carts(fs_user_id, query.trace_context)
            # To get full details (prices), we need products
            products_list = await self.client.get_products(query.trace_context)
            products_map = {p["id"]: p for p in products_list}
            
            orders = [self.client.map_cart_to_order(c, products_map) for c in raw_carts]
        except Exception as e:
            log_event("FakeStore API Error", trace_id, {"error": str(e)})
            return self.create_response(
                text="I'm having trouble accessing our order database right now. Please try again in a few minutes.",
                confidence=0.5,
                reasoning=f"API Failure: {str(e)}"
            )

        target_order = None
        if order_id_match:
            order_id = order_id_match.group(1)
            target_order = next((o for o in orders if o["order_id"] == f"ORD-{order_id}"), None)
            if not target_order:
                return self.create_response(
                    text=f"I couldn't find an order with ID ORD-{order_id} in your account.",
                    confidence=0.9,
                    reasoning="Order ID provided but not found for this user."
                )
        else:
            # Multi-order disambiguation
            if len(orders) > 1:
                # Prioritize: undelivered, then recent
                undelivered = [o for o in orders if o["status"] != "Delivered"]
                if undelivered:
                    undelivered.sort(key=lambda x: x["created_at"], reverse=True)
                    options = ", ".join([o["order_id"] for o in undelivered])
                    return self.create_response(
                        text=f"I see you have {len(orders)} orders. Which one would you like to track? Recent pending orders: {options}.",
                        confidence=0.9,
                        reasoning="Multiple orders found. Requesting disambiguation based on priority (undelivered/recent).",
                        metadata={"order_options": [o["order_id"] for o in orders]}
                    )
                else:
                    orders.sort(key=lambda x: x["created_at"], reverse=True)
                    options = ", ".join([o["order_id"] for o in orders[:3]])
                    return self.create_response(
                        text=f"I found several past orders ({options}). Which one are you looking for?",
                        confidence=0.9,
                        reasoning="Multiple delivered orders found. Requesting disambiguation."
                    )
            elif len(orders) == 1:
                target_order = orders[0]
            else:
                return self.create_response(
                    text="I couldn't find any recent orders associated with your account.",
                    confidence=0.8,
                    reasoning="No orders found for user in Fake Store API."
                )

        # Process the target order
        status = target_order["status"]
        eta = target_order["eta"].strftime("%A, %d %B")
        
        # Simulate shipment delay
        is_delayed = target_order["order_id"].endswith("5") or target_order["order_id"].endswith("0")
        
        response_text = f"Your order {target_order['order_id']} is currently **{status}**."
        
        if status == "Delivered":
            response_text += " It was delivered on " + target_order["created_at"].strftime("%d %B") + "."
        else:
            response_text += f" The current estimated delivery date is **{eta}**."
            if is_delayed:
                response_text += "\n\n⚠️ **Update**: We're experiencing a slight delay due to high seasonal volume. Your package is safe and moving through our network."

        return self.create_response(
            text=response_text,
            confidence=1.0,
            reasoning=f"Retrieved live status from FakeStore API for user {fs_user_id}.",
            tool_calls=[
                ToolCall(tool_name="get_user_carts", args={"user_id": fs_user_id}, result=raw_carts, status="success")
            ],
            metadata={"is_delayed": is_delayed, "order_details": target_order}
        )
