from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Select
from textual.reactive import reactive

from ...llm_clients import VALID_MODELS


class ProviderChoice(Vertical):
    """A Textual app for user login and signup."""

    PROVIDERS = ["OpenAI", "Anthropic", "Google", "Qwen", "Moonshot", "xai"]

    def compose(self) -> ComposeResult:
        yield Static(
            "Select your Model Provider",
            id="provider_choice_title",
        )
        yield Select(
            (
                (provider, provider.lower().replace(" ", "_"))
                for provider in self.PROVIDERS
            ),
            id="provider_select",
        )


class ModelChoiceFromProvider(Vertical):
    """A Textual app for user login and signup."""

    provider = reactive("openai", recompose=True)

    def compose(self) -> ComposeResult:
        yield Static(
            "Select your model",
            id="model_choice_title",
        )
        models = VALID_MODELS.get(self.provider, [])
        yield Select((model, model.replace(".", "_")) for model in models)
