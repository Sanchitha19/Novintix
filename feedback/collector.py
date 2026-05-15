import json
import os
from datetime import datetime
from typing import List, Dict, Any
from models.schemas import Query, AgentResponse

class FeedbackCollector:
    def __init__(self, dataset_path: str = "feedback/dataset.jsonl"):
        self.dataset_path = dataset_path
        self.feedback_store: List[Dict[str, Any]] = []
        self.knowledge_gaps: List[str] = []
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.dataset_path), exist_ok=True)

    def collect_csat(self, query_id: str, score: int, comment: str = "", query_text: str = "", response_text: str = ""):
        """Store customer satisfaction scores and write to dataset if low rated."""
        entry = {
            "query_id": query_id,
            "score": score,
            "comment": comment,
            "query_text": query_text,
            "response_text": response_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.feedback_store.append(entry)
        
        if score <= 2: # Low rated
            with open(self.dataset_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def log_knowledge_gap(self, query_text: str):
        """Log queries that the FAQ agent couldn't answer."""
        self.knowledge_gaps.append(query_text)
        print(f"DEBUG: Knowledge gap logged: {query_text}")

collector = FeedbackCollector()
