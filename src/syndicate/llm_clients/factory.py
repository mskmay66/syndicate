from typing import Optional

from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .gemini_client import GeminiClient
from .qwen_client import QwenClient


def create_llm_client(
    provider: str, model: str, base_url: Optional[str] = None, **kwargs
) -> BaseLLMClient:
    """Factory function to create LLM client instances based on provider.

    Args:
        provider (str): The name of the LLM provider (e.g., "openai", "anthropic", "gemini", "qwen").
        model (str): The name of the model to use (e.g., "gpt-4", "claude-2", "gemini-1.5").
        base_url (Optional[str], optional): The base URL for the provider's API. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the client constructor.

    Returns:
        BaseLLMClient: An instance of a subclass of BaseLLMClient corresponding to the specified provider.
    """
    provider = provider.lower()
    if provider in ("openai", "xai", "openrouter", "ollama", "moonshot"):
        return OpenAIClient(model=model, base_url=base_url, provider=provider, **kwargs)
    elif provider == "anthropic":
        return AnthropicClient(model=model, base_url=base_url, **kwargs)
    elif provider in ("gemini", "google"):
        return GeminiClient(model=model, base_url=base_url, **kwargs)
    elif provider == "qwen":
        return QwenClient(model=model, base_url=base_url, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
