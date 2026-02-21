from typing import Optional

from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .gemini_client import GeminiClient
from .qwen_client import QwenClient


def create_llm_client(
    provider: str, model: str, base_url: Optional[str] = None, **kwargs
) -> BaseLLMClient:
    """Factory function to create LLM client instances based on provider."""
    provider = provider.lower()
    if provider in ("openai", "xai", "openrouter", "ollama", "kimi"):
        return OpenAIClient(model=model, base_url=base_url, provider=provider, **kwargs)
    elif provider == "anthropic":
        return AnthropicClient(model=model, base_url=base_url, **kwargs)
    elif provider in ("gemini", "google"):
        return GeminiClient(model=model, base_url=base_url, **kwargs)
    elif provider == "qwen":
        return QwenClient(model=model, base_url=base_url, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
