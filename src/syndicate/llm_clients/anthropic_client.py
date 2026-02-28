from typing import Optional
from langchain_anthropic import ChatAnthropic

from .base_client import BaseLLMClient
from .validate import validate_model


class AnthropicClient(BaseLLMClient):
    VALID_KWARGS = ("timeout", "max_retries", "api_key", "max_tokens", "callbacks")

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = "https://api.anthropic.com/v1",
        **kwargs,
    ):
        super().__init__(model, base_url, **kwargs)
        self.model = model
        self.base_url = base_url
        self.validate_model()

    def get_llm(self) -> ChatAnthropic:
        """Get the Anthropic LLM client instance."""
        llm_kwargs = {"model": self.model_name}
        for key in AnthropicClient.VALID_KWARGS:
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]
        return ChatAnthropic(**llm_kwargs)

    def validate_model(self) -> bool:
        """Validate model for Anthropic."""
        return validate_model("anthropic", self.model)
