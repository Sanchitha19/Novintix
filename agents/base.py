from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models.schemas import Query, AgentResponse, ToolCall

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process(self, query: Query) -> AgentResponse:
        pass

    def create_response(self, text: str, confidence: float, reasoning: str, tool_calls: List[ToolCall] = [], metadata: Dict[str, Any] = {}) -> AgentResponse:
        return AgentResponse(
            agent_name=self.name,
            response_text=text,
            confidence=confidence,
            reasoning=reasoning,
            tool_calls=tool_calls,
            metadata=metadata
        )
