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
        
        # Perform Hybrid Search
        search_results = await self.retriever.search(query.text)
        search_tool = ToolCall(tool_name="hybrid_search", args={"query": query.text}, result=search_results, status="success")
        
        if not search_results:
            return self.create_response(
                text="I couldn't find any information regarding that. Let me connect you with a human agent.",
                confidence=0.0,
                reasoning="No relevant documentation or products found in RAG.",
                tool_calls=[search_tool]
            )

        max_score = search_results[0]["score"]
        
        # Requirement: If confidence < 0.72 -> Escalate
        if max_score < 0.72:
            return self.create_response(
                text="I'm not entirely sure about the answer to that. To ensure you get the right information, I'll escalate this to our support team.",
                confidence=max_score,
                reasoning=f"Confidence {max_score:.2f} is below 0.72 threshold.",
                tool_calls=[search_tool],
                metadata={"knowledge_gap": True}
            )

        # Format response
        best_match = search_results[0]["text"]
        
        return self.create_response(
            text=f"Based on our catalog and policies:\n\n{best_match}",
            confidence=max_score,
            reasoning=f"Found relevant match with confidence {max_score:.2f}.",
            tool_calls=[search_tool]
        )
