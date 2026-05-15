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

class Orchestrator:
    def __init__(self):
        self.router = IntentClassifier()
        self.guardrails = GuardrailManager()
        self.agents = {
            Intent.TRACK_ORDER: OrderTrackingAgent(),
            Intent.REFUND: RefundAgent(),
            Intent.FAQ: FAQAgent(),
            Intent.HUMAN_ESCALATION: EscalationAgent()
        }
        self.fallback_agent = EscalationAgent()

    async def route_and_execute(self, query: Query) -> List[AgentResponse]:
        start_time = time.time()
        
        # 1. Pre-process Guardrails
        log_event("Processing query", query.trace_context.trace_id, {"query_text": query.text})
        try:
            query = await self.guardrails.pre_process(query)
        except Exception as e:
            log_event("Guardrail violation", query.trace_context.trace_id, {"error": str(e)})
            # Forced escalation on loop limit
            response = await self.fallback_agent.process(query)
            response.reasoning = str(e)
            return [response]
        
        # 2. Classify Intent
        intents = self.router.classify(query.text)
        
        # Parallel routing for multiple intents if they have high confidence
        # For this implementation, we take all intents above threshold
        primary_intents = [i for i in intents if i[1] > 0.5]
        if not primary_intents:
            primary_intents = [intents[0]] # Take the best one even if low confidence

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
        responses = await asyncio.gather(*tasks)
        
        # 4. Post-process Guardrails
        responses = await self.guardrails.post_process(responses, query.trace_context.trace_id)
        
        # Add routing info to metadata
        for i, response in enumerate(responses):
            response.metadata["routing"] = routing_decisions[i].model_dump()

        return responses
