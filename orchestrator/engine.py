import asyncio
import time
from typing import List, Dict, Any
from models.schemas import Query, AgentResponse, Intent, RoutingDecision, TraceContext
from orchestrator.router import IntentClassifier
from agents.tracking_agent import OrderTrackingAgent
from agents.refund_agent import RefundAgent
from agents.faq_agent import FAQAgent
from agents.escalation_agent import EscalationAgent
from guardrails.manager import GuardrailManager
from monitoring.logger import log_event
from integrations.fakestore_client import FakeStoreClient
from rag.ingestion import PolicyIngestor
from rag.retriever import HybridRetriever
import re

class Orchestrator:
    def __init__(self):
        self.router = IntentClassifier()
        self.guardrails = GuardrailManager()
        self.fs_client = FakeStoreClient()
        self.ingestor = PolicyIngestor()
        self.retriever = None
        self.retriever_initialized = False
        self.agents = {
            Intent.TRACK_ORDER: OrderTrackingAgent(),
            Intent.REFUND: RefundAgent(),
            Intent.FAQ: FAQAgent(),
            Intent.HUMAN_ESCALATION: EscalationAgent()
        }
        self.fallback_agent = EscalationAgent()

    async def _initialize_retriever(self, trace_context):
        if self.retriever_initialized:
            return
        policy_chunks = self.ingestor.load_and_split()
        try:
            products = await self.fs_client.get_products(trace_context)
            product_chunks = self.ingestor.ingest_fakestore_products(products)
        except:
            product_chunks = []
        all_chunks = policy_chunks + product_chunks
        self.retriever = HybridRetriever(docs=all_chunks)
        self.retriever_initialized = True

    async def route_and_execute(self, query: Query) -> List[AgentResponse]:
        start_time = time.time()
        
        # 1. Pre-process Guardrails
        log_event("Processing query", query.trace_context.trace_id, {"query_text": query.text})
        try:
            query = await self.guardrails.pre_process(query)
        except Exception as e:
            log_event("Guardrail violation", query.trace_context.trace_id, {"error": str(e)})
            response = await self.fallback_agent.process(query)
            response.reasoning = str(e)
            return [response]
        
        # Fetch Context
        await self._initialize_retriever(query.trace_context)
        
        try:
            numeric_id = int(re.search(r"\d+", query.user_id).group())
            fs_user_id = (numeric_id % 10) + 1
        except:
            fs_user_id = 1
            
        try:
            raw_carts = await self.fs_client.get_user_carts(fs_user_id, query.trace_context)
            products_list = await self.fs_client.get_products(query.trace_context)
            products_map = {p["id"]: p for p in products_list}
            orders = [self.fs_client.map_cart_to_order(c, products_map) for c in raw_carts]
        except:
            orders = []
            
        search_results = await self.retriever.search(query.text)
        
        query.metadata["context"] = {
            "customer_id": fs_user_id,
            "orders": orders,  # already plain dicts from map_cart_to_order
            "rag_docs": [res["text"] for res in search_results],
            # Assume conversation history is passed in query.metadata["history"] from frontend/API
            "conversation_history": query.metadata.get("history", [])
        }
        
        # 2. Classify Intent
        intents = self.router.classify(query.text)
        
        # Take only the top-scoring intent above threshold
        primary_intents = [(intents[0][0], intents[0][1])] if intents and intents[0][1] >= 0.3 else []
        if not primary_intents:
            primary_intents = [intents[0]]

        tasks = []
        routing_decisions = []

        for intent, score in primary_intents:
            agent = self.agents.get(intent, self.fallback_agent)
            
            # Log Routing Decision
            decision = RoutingDecision(
                query_id=query.query_id,
                intent=intent,
                confidence=score,
                reasoning=f"Classified as {intent} with score {score:.2f}",
                assigned_agent=agent.name,
                latency_ms=(time.time() - start_time) * 1000
            )
            routing_decisions.append(decision)
            
            # Prepare task
            tasks.append(agent.process(query))

        # 3. Execute Agents in Parallel
        try:
            responses = await asyncio.gather(*tasks)
        except Exception as e:
            log_event("Agent execution error", query.trace_context.trace_id, {"error": str(e)})
            response = await self.fallback_agent.process(query)
            response.reasoning = f"Agent failed: {str(e)}"
            return [response]
        
        # 4. Post-process Guardrails
        responses = await self.guardrails.post_process(responses, query.trace_context.trace_id)
        
        # Add routing info to metadata
        for i, response in enumerate(responses):
            response.metadata["routing"] = routing_decisions[i].model_dump()

        return responses
