from agents.base import BaseAgent
from agents.tools import order_db_lookup, logistics_api_status, MOCK_ORDER_DB
from models.schemas import Query, AgentResponse, ToolCall

class OrderTrackingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="OrderTrackingAgent")

    async def process(self, query: Query) -> AgentResponse:
        import re
        # Simple extraction logic for demonstration
        order_id_match = re.search(r"ORD-\d+", query.text.upper())
        
        if not order_id_match:
            # Check for multi-order disambiguation
            user_orders = [oid for oid, details in MOCK_ORDER_DB.items() if details["user_id"] == query.user_id]
            if len(user_orders) > 1:
                order_list = ", ".join(user_orders)
                return self.create_response(
                    text=f"I see you have multiple pending orders ({order_list}). Which one would you like to track?",
                    confidence=0.9,
                    reasoning="Multiple orders found for user. Requesting disambiguation."
                )
            elif len(user_orders) == 1:
                order_id = user_orders[0]
            else:
                return self.create_response(
                    text="I couldn't find an order ID in your request. Could you please provide your order number (e.g., ORD-123)?",
                    confidence=0.8,
                    reasoning="No order_id found and no prior orders for user."
                )
        else:
            order_id = order_id_match.group(0)
        
        # Tool Call 1: DB Lookup
        order_data = order_db_lookup(order_id)
        db_tool_call = ToolCall(tool_name="order_db_lookup", args={"order_id": order_id}, result=order_data, status="success")

        if "error" in order_data:
            return self.create_response(
                text=f"I'm sorry, I couldn't find any details for order {order_id}. Please double-check the ID.",
                confidence=0.9,
                reasoning="Order not found in database.",
                tool_calls=[db_tool_call]
            )

        # Tool Call 2: Logistics API (if applicable)
        tracking_id = order_data.get("tracking_id")
        logistics_data = {}
        tool_calls = [db_tool_call]

        if tracking_id:
            logistics_data = logistics_api_status(tracking_id)
            tool_calls.append(ToolCall(tool_name="logistics_api_status", args={"tracking_id": tracking_id}, result=logistics_data, status="success"))

        status = logistics_data.get("status", order_data.get("status"))
        location = logistics_data.get("location", "N/A")
        
        response_text = f"Your order {order_id} is currently {status}."
        if location != "N/A":
            response_text += f" It was last seen at {location}."
        
        return self.create_response(
            text=response_text,
            confidence=0.95,
            reasoning=f"Successfully retrieved status for {order_id} from DB and Logistics API.",
            tool_calls=tool_calls
        )
