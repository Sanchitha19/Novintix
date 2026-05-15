import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Mock Database for testing
MOCK_ORDER_DB = {
    "ORD-123": {
        "user_id": "user_001",
        "status": "delivered",
        "tracking_id": "TRK-987654",
        "items": [{"id": "item_1", "price": 1200}, {"id": "item_2", "price": 800}],
        "total_amount": 2000,
        "payment_method": "upi",
        "created_at": datetime.utcnow() - timedelta(days=2)
    },
    "ORD-456": {
        "user_id": "user_002",
        "status": "delivered",
        "tracking_id": "TRK-112233",
        "items": [{"id": "item_3", "price": 6000}],
        "total_amount": 6000,
        "payment_method": "card",
        "created_at": datetime.utcnow() - timedelta(days=5)
    }
}

# --- Order Tracking Tools ---

def order_db_lookup(order_id: str) -> Dict[str, Any]:
    """Look up order details in the primary database."""
    order = MOCK_ORDER_DB.get(order_id)
    if not order:
        return {"error": f"Order {order_id} not found."}
    return order

def logistics_api_status(tracking_id: str) -> Dict[str, Any]:
    """Get real-time tracking status from logistics partner API."""
    # Mocking external API call
    if tracking_id == "TRK-987654":
        return {
            "status": "In Transit",
            "location": "Mumbai Hub",
            "last_updated": datetime.utcnow().isoformat()
        }
    return {"error": "Tracking ID not found in logistics system."}

def eta_estimator(coordinates: str) -> str:
    """Estimate arrival time based on current location coordinates."""
    return "Estimated delivery: 2 days from now."

# --- Refund Tools ---

def validate_eligibility(order_id: str, policy_version: str = "v1.0") -> Dict[str, Any]:
    """Validate if an order is eligible for refund based on policies."""
    order = MOCK_ORDER_DB.get(order_id)
    if not order:
        return {"eligible": False, "reason": "Order not found."}
    
    # Mock logic: Eligible if status is delivered and within 7 days
    if order["status"] == "delivered":
        return {"eligible": True, "max_refund": order["total_amount"]}
    return {"eligible": False, "reason": "Order not yet delivered."}

def calculate_refund_amount(items: List[Dict[str, Any]]) -> float:
    """Calculate the total refund amount for specific items."""
    return sum(item.get("price", 0) for item in items)

def initiate_refund_gateway(amount: float, payment_method: str) -> Dict[str, Any]:
    """Process refund through the payment gateway."""
    # Guardrail check should happen before this tool is called, 
    # but we can add a safety check here too.
    if amount > 5000:
        return {"status": "blocked", "reason": "Amount exceeds automated refund limit."}
    
    return {
        "status": "success",
        "transaction_id": f"REF-{os.urandom(4).hex()}",
        "amount": amount
    }

def notify_customer(template_id: str, data: Dict[str, Any]) -> bool:
    """Send notification to customer via email/SMS."""
    print(f"DEBUG: Notifying customer using template {template_id} with data {data}")
    return True

# --- FAQ Tools ---

def vector_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search vector database for relevant documentation chunks."""
    # Mocking RAG response
    return [
        {"text": "Our return policy allows returns within 30 days for most items.", "score": 0.85},
        {"text": "Refunds are processed within 5-7 business days.", "score": 0.78}
    ]

def policy_lookup(category: str) -> str:
    """Get the full text of a specific policy category."""
    policies = {
        "returns": "Items can be returned within 30 days if unused and in original packaging.",
        "shipping": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 days."
    }
    return policies.get(category, "Policy category not found.")

# --- Escalation Tools ---

def ticket_create(user_id: str, subject: str, description: str) -> str:
    """Create a support ticket in Zendesk/Freshdesk."""
    ticket_id = f"TKT-{os.urandom(3).hex().upper()}"
    return ticket_id

def assign_agent(skill_match: str, availability: bool = True) -> str:
    """Find and assign an available human agent with the right skills."""
    return "Agent_Rahul_S"

def notify_team(channel: str, message: str) -> bool:
    """Send alert to internal team channel (e.g., Slack)."""
    print(f"DEBUG: Alerting team on {channel}: {message}")
    return True
