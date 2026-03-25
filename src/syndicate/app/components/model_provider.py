from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Select
from textual.reactive import reactive

from ...llm_clients import VALID_MODELS
import logging
from logging.handlers import RotatingFileHandler
from textual.logging import TextualHandler

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level="NOTSET",
    handlers=[TextualHandler(), RotatingFileHandler(filename=".logs/app.log")],
)


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
    provider = reactive("openai", recompose=True)
    pending_model: str | None = None

    def compose(self) -> ComposeResult:
        yield Static("Select your model", id="model_choice_title")

        models = VALID_MODELS.get(self.provider, [])
        options = [(model, model.replace(".", "_")) for model in models]

        value = None
        if self.pending_model:
            values = [v for _, v in options]
            if self.pending_model in values:
                value = self.pending_model
            self.pending_model = None

        if value:
            yield Select(
                options,
                id="model_choice",
                value=value,  # ✅ THIS is the key
            )
        else:
            yield Select(
                options,
                id="model_choice",
            )
