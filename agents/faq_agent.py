from agents.base import BaseAgent
from models.schemas import Query, AgentResponse, ToolCall, TraceContext
from rag.retriever import HybridRetriever
from rag.ingestion import PolicyIngestor
from integrations.fakestore_client import FakeStoreClient
import asyncio

class FAQAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="FAQAgent")
        self.ingestor = PolicyIngestor()
        self.fs_client = FakeStoreClient()
        self.retriever = None
        self.initialized = False

    async def _initialize(self, trace_context: TraceContext):
        if self.initialized:
            return
            
        # 1. Load Policies
        policy_chunks = self.ingestor.load_and_split()
        
        # 2. Fetch and Ingest FakeStore Products
        try:
            products = await self.fs_client.get_products(trace_context)
            product_chunks = self.ingestor.ingest_fakestore_products(products)
        except:
            product_chunks = []
            
        all_chunks = policy_chunks + product_chunks
        self.retriever = HybridRetriever(docs=all_chunks)
        self.initialized = True

    async def process(self, query: Query) -> AgentResponse:
        await self._initialize(query.trace_context)
        
        search_tool = ToolCall(tool_name="hybrid_search", args={"query": query.text}, result=query.metadata["context"]["rag_docs"], status="success")
        
        system_prompt = """
You are the Knowledge and Policy specialist at Novintix.
Answer any question about:
- Why an order cannot be placed (payment issues, account suspension, stock, address problems, cart errors)
- Return and refund policies
- Account issues and troubleshooting
- Product information
- Shipping policies

Always give a complete, specific answer to exactly what the customer asked. Never deflect to another agent unless truly necessary. List reasons, steps, or options clearly.
"""
        from utils.llm import invoke_llm
        import json
        
        context_str = json.dumps(query.metadata["context"], indent=2)
        llm_response = invoke_llm(system_prompt, context_str, query.text, query.metadata.get("history", []))

        # Confidence heuristic based on RAG hits (for demo, if rag_docs exist, confidence is higher)
        confidence = 0.9 if query.metadata["context"]["rag_docs"] else 0.5
        
        return self.create_response(
            text=llm_response,
            confidence=confidence,
            reasoning=f"Generated response using LLM with context.",
            trace_id=query.trace_context.trace_id,
            tool_calls=[search_tool]
        )
