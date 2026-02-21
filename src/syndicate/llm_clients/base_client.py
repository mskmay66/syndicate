from abc import ABC, abstractmethod
from typing import Optional, Any


class BaseLLMClient(ABC):
    def __init__(self, model_name: str, base_url: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.base_url = base_url
        self.kwargs = kwargs

    @abstractmethod
    def get_llm(self) -> Any:
        """Method to get the LLM client instance."""
        pass

    @abstractmethod
    def validate_model(self) -> bool:
        """Method to validate if the model is compatible with the client."""
        pass
