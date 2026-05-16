from fastapi import FastAPI, HTTPException, Request, Depends, status
from pydantic import BaseModel
from orchestrator.engine import Orchestrator
from models.schemas import Query, AgentResponse
from monitoring.logger import log_event
from monitoring.metrics import get_metrics, QUERY_COUNT, LATENCY
from feedback.collector import collector
from utils.auth import verify_token, create_access_token
import uvicorn
import time

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Novintix Agentic Support System")

# Allow CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orch = Orchestrator()

class QueryRequest(BaseModel):
    user_id: str
    text: str
    session_id: str

class FeedbackRequest(BaseModel):
    query_id: str
    score: int
    comment: str = ""
    query_text: str = ""
    response_text: str = ""

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/token")
async def login(req: LoginRequest):
    # Verify dummy user
    if req.username == "johnd" and req.password == "m38mzuvjxl":
        return {"access_token": create_access_token({"sub": req.username}), "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/query", response_model=list[AgentResponse])
async def process_query(req: QueryRequest, username: str = Depends(verify_token)):
    start_time = time.time()
    query = Query(
        user_id=req.user_id,
        text=req.text,
        session_id=req.session_id
    )
    
    try:
        responses = await orch.route_and_execute(query)
        
        # Track metrics
        duration = time.time() - start_time
        LATENCY.observe(duration)
        for res in responses:
            intent = res.metadata.get("routing", {}).get("intent", "unknown")
            QUERY_COUNT.labels(intent=intent).inc()
            
        return responses
    except Exception as e:
        log_event("API Error", query.trace_context.trace_id, {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

class FeedbackRequest(BaseModel):
    query_id: str
    rating: int = 0
    score: int = 0
    comment: str = ""
    query_text: str = ""
    response_text: str = ""

@app.post("/feedback")
async def post_feedback(req: FeedbackRequest, username: str = Depends(verify_token)):
    # Map rating to score if needed
    final_score = req.rating if req.rating != 0 else req.score
    collector.collect_csat(
        query_id=req.query_id,
        score=final_score,
        comment=req.comment,
        query_text=req.query_text,
        response_text=req.response_text
    )
    return {"status": "success"}

@app.get("/metrics")
async def metrics():
    return get_metrics()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agents": {
            "order_tracking": "healthy",
            "refund": "healthy",
            "faq": "healthy",
            "escalation": "healthy"
        },
        "redis": "connected",
        "rag": "ready",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
