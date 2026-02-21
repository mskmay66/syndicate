from typing import Optional
from langchain_qwq import ChatQwen

from .base_client import BaseLLMClient
from .validate import validate_model


class QwenClient(BaseLLMClient):
    VALID_KWARGS = (
        "enable_thinking",
        "thinking_budget",
        "timeout",
        "max_retries",
        "api_key",
        "callbacks",
    )

    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(model, base_url, **kwargs)

    def get_llm(self) -> ChatQwen:
        """Get the Qwen LLM client instance."""
        llm_kwargs = {"model": self.model_name}
        for key in QwenClient.VALID_KWARGS:
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]
        return ChatQwen(**llm_kwargs)

    def validate_model(self) -> bool:
        return validate_model("qwen", self.model_name)
