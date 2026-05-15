from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Metrics definitions
QUERY_COUNT = Counter("novintix_queries_total", "Total number of queries processed", ["intent"])
LATENCY = Histogram("novintix_request_latency_seconds", "Latency of requests in seconds")
GUARDRAIL_VIOLATIONS = Counter("novintix_guardrail_violations_total", "Total number of guardrail violations", ["type"])
REFUND_AMOUNT = Counter("novintix_refund_amount_total", "Total amount refunded")
AGENT_LOAD = Gauge("novintix_agent_load", "Current number of active agent tasks", ["agent_name"])

def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
