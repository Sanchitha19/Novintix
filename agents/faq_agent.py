from agents.base import BaseAgent
from agents.tools import policy_lookup
from models.schemas import Query, AgentResponse, ToolCall
from rag.retriever import HybridRetriever
from rag.ingestion import PolicyIngestor

class FAQAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="FAQAgent")
        self.ingestor = PolicyIngestor()
        self.chunks = self.ingestor.load_and_split()
        self.retriever = HybridRetriever(docs=self.chunks)

    async def process(self, query: Query) -> AgentResponse:
        # Real Hybrid Search
        search_results = await self.retriever.search(query.text, docs=self.chunks)
        search_tool = ToolCall(tool_name="vector_search", args={"query": query.text}, result=search_results, status="success")
        
        # Check confidence threshold (per requirements: if max_score < 0.72 -> do NOT answer -> escalate)
        max_score = max([res["score"] for res in search_results]) if search_results else 0
        
        if max_score < 0.72:
            return self.create_response(
                text="I'm sorry, I couldn't find a definitive answer in our knowledge base. Let me connect you with someone who can help.",
                confidence=max_score,
                reasoning=f"Knowledge gap detected. Max score {max_score} < 0.72 threshold.",
                tool_calls=[search_tool],
                metadata={"knowledge_gap": True}
            )

        # Rerank / Format response
        best_match = search_results[0]["text"]
        
        return self.create_response(
            text=f"Based on our documentation: {best_match}",
            confidence=max_score,
            reasoning=f"Found relevant answer with confidence {max_score}.",
            tool_calls=[search_tool]
        )
