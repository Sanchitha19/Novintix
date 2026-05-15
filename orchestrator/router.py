import torch
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any, Tuple
from models.schemas import Intent

class IntentClassifier:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        # Define reference sentences for each intent
        self.intent_examples = {
            Intent.TRACK_ORDER: [
                "Where is my order?",
                "Track my package",
                "Delivery status",
                "When will my order arrive?",
                "shipping status"
            ],
            Intent.REFUND: [
                "I want a refund",
                "Cancel my order and refund",
                "Return this item",
                "Money back for order",
                "refund policy"
            ],
            Intent.FAQ: [
                "How do I return?",
                "What is your shipping policy?",
                "Do you ship to Mumbai?",
                "payment methods",
                "contact support"
            ],
            Intent.HUMAN_ESCALATION: [
                "Talk to a human",
                "I want to speak to an agent",
                "Connect me to a person",
                "Customer care number",
                "help me"
            ]
        }
        
        # Pre-compute embeddings for examples
        self.intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            self.intent_embeddings[intent] = self.model.encode(examples, convert_to_tensor=True)

    def classify(self, text: str, threshold: float = 0.40) -> List[Tuple[Intent, float]]:
        """Classify intent using embedding similarity. Returns list of (Intent, Score)."""
        query_embedding = self.model.encode(text, convert_to_tensor=True)
        
        results = []
        for intent, embeddings in self.intent_embeddings.items():
            # Calculate max similarity with any example for this intent
            cos_scores = util.cos_sim(query_embedding, embeddings)[0]
            max_score = float(torch.max(cos_scores))
            if max_score >= threshold:
                results.append((intent, max_score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        if not results:
            results.append((Intent.UNKNOWN, 0.0))
            
        return results
