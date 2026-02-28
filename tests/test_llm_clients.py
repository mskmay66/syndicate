import pytest

from syndicate.llm_clients import (
    create_llm_client,
    OpenAIClient,
    AnthropicClient,
    GeminiClient,
    QwenClient,
)


@pytest.mark.parametrize(
    "provider, model, expected_class",
    [
        ("openai", "gpt-4o-mini", OpenAIClient),
        ("anthropic", "claude-haiku-4-5", AnthropicClient),
        ("gemini", "gemini-3-pro-preview", GeminiClient),
        ("qwen", "qwen2-7b-instruct", QwenClient),
    ],
)
def test_create_llm_client(provider, model, expected_class):
    client = create_llm_client(provider=provider, model=model)
    assert isinstance(client, expected_class), (
        f"Expected {expected_class} for provider '{provider}', got {type(client)}"
    )


@pytest.mark.parametrize(
    "provider, model",
    [
        ("openai", "invalid-model"),
        ("anthropic", "invalid-model"),
        ("google", "invalid-model"),
        ("qwen", "invalid-model"),
    ],
)
def test_create_llm_client_invalid_model(provider, model):
    with pytest.raises(
        ValueError, match=f"Unsupported model '{model}' for provider '{provider}'."
    ):
        create_llm_client(provider=provider, model=model)


@pytest.mark.parametrize(
    "provider",
    [
        "invalid-provider",
        "unknown",
        "unsupported",
    ],
)
def test_invalid_provider(provider):
    with pytest.raises(ValueError, match=f"Unsupported provider: {provider}"):
        create_llm_client(provider=provider, model="some-model")
