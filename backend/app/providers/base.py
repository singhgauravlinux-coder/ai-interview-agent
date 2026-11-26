from abc import ABC, abstractmethod
from typing import Any

class AIProvider(ABC):
    @abstractmethod
    def generate_json(self, *, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> dict[str, Any]:
        """Return a parsed JSON object. Raise an exception on provider/API errors."""
        raise NotImplementedError
