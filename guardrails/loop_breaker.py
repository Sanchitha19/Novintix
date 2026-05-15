from typing import Dict, Any

class LoopBreaker:
    def __init__(self, max_hops: int = 3):
        self.max_hops = max_hops
        self.session_hops: Dict[str, int] = {}

    def check_and_increment(self, session_id: str) -> bool:
        """Return True if within limits, False if limit exceeded."""
        current_hops = self.session_hops.get(session_id, 0)
        if current_hops >= self.max_hops:
            return False
        
        self.session_hops[session_id] = current_hops + 1
        return True

    def reset_session(self, session_id: str):
        if session_id in self.session_hops:
            del self.session_hops[session_id]
