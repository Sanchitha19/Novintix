from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class Intent(str, Enum):
    TRACK_ORDER = "track_order"
    REFUND = "refund"
    FAQ = "faq"
    HUMAN_ESCALATION = "human_escalation"
    UNKNOWN = "unknown"

class TraceContext(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None

class Query(BaseModel):
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    text: str
    session_id: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_context: TraceContext = Field(default_factory=TraceContext)

class ToolCall(BaseModel):
    tool_name: str
    args: Dict[str, Any]
    result: Optional[Any] = None
    status: str = "pending" # pending, success, failed

class AgentResponse(BaseModel):
    agent_name: str
    response_text: str
    confidence: float
    reasoning: str
    trace_id: str
    tool_calls: List[ToolCall] = []
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GuardrailType(str, Enum):
    PII_MASKING = "pii_masking"
    REFUND_CAP = "refund_cap"
    LOOP_BREAKER = "loop_breaker"
    PROMPT_INJECTION = "prompt_injection"
    SENTIMENT_ESCALATION = "sentiment_escalation"

class GuardrailEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: GuardrailType
    action_taken: str # e.g., "redacted", "blocked", "escalated"
    details: Dict[str, Any]
    trace_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RoutingDecision(BaseModel):
    query_id: str
    intent: Intent
    confidence: float
    reasoning: str
    assigned_agent: str
    latency_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class OrderStatus(BaseModel):
    order_id: str
    status: str
    tracking_id: Optional[str]
    eta: Optional[datetime]
    last_location: Optional[str]
    carrier: Optional[str]

class RefundStatus(BaseModel):
    order_id: str
    refund_id: Optional[str]
    amount: float
    status: str # pending, approved, rejected, processing
    reason: str
    approval_required: bool = False
