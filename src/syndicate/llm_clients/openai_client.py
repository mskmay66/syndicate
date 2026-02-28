from langchain_openai import ChatOpenAI
from typing import Optional
import os

from .base_client import BaseLLMClient
from .validate import validate_model


class UnifiedChatOpenAI(ChatOpenAI):
    def __init__(self, **kwargs):
        model = kwargs.get("model", "")
        if self._is_reasoning_model(model):
            kwargs.pop("temperature", None)
            kwargs.pop("top_p", None)
        super().__init__(**kwargs)

    @staticmethod
    def _is_reasoning_model(model: str) -> bool:
        """Check if model is a reasoning model that doesn't support temperature."""
        model_lower = model.lower()
        return (
            model_lower.startswith("o1")
            or model_lower.startswith("o3")
            or "gpt-5" in model_lower
        )


class OpenAIClient(BaseLLMClient):
    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        provider: str = "openai",
        **kwargs,
    ):
        super().__init__(model, base_url, **kwargs)
        self.provider = provider.lower()
        self.model = model
        self.base_url = base_url
        self.validate_model()

    def get_llm(self) -> UnifiedChatOpenAI:
        """Get the OpenAI LLM client instance."""
        llm_kwargs = {"model": self.model}

        if self.provider == "xai":
            llm_kwargs["base_url"] = "https://api.x.ai/v1"
            api_key = os.environ.get("XAI_API_KEY")
            if api_key:
                llm_kwargs["api_key"] = api_key
        elif self.provider == "openrouter":
            llm_kwargs["base_url"] = "https://openrouter.ai/api/v1"
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if api_key:
                llm_kwargs["api_key"] = api_key
        elif self.provider == "ollama":
            llm_kwargs["base_url"] = "http://localhost:11434/v1"
            llm_kwargs["api_key"] = "ollama"  # Ollama doesn't require auth
        elif self.provider == "kimi":
            llm_kwargs["base_url"] = "https://api.moonshot.ai/v1"
            api_key = os.environ.get("KIMI_API_KEY")
            if api_key:
                llm_kwargs["api_key"] = api_key
        elif self.base_url:
            llm_kwargs["base_url"] = self.base_url

        for key in (
            "timeout",
            "max_retries",
            "reasoning_effort",
            "api_key",
            "callbacks",
        ):
            if key in self.kwargs:
                if key not in llm_kwargs:
                    llm_kwargs[key] = self.kwargs[key]

        return UnifiedChatOpenAI(**llm_kwargs)

    def validate_model(self) -> bool:
        """Validate if the model is compatible with the OpenAI client."""
        return validate_model(self.provider, self.model)
