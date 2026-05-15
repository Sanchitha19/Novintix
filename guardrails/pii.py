import re
from typing import Any

class PIIMasker:
    def __init__(self):
        self.patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b",
            "card": r"\b(?:\d[ -]*?){13,16}\b"
        }

    def mask(self, text: str) -> str:
        """Redact PII from text."""
        masked_text = text
        for pii_type, pattern in self.patterns.items():
            masked_text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", masked_text)
        return masked_text

    def mask_object(self, obj: Any) -> Any:
        """Recursively mask PII in dicts and lists."""
        if isinstance(obj, str):
            return self.mask(obj)
        elif isinstance(obj, dict):
            return {k: self.mask_object(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.mask_object(i) for i in obj]
        else:
            return obj
