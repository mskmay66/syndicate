from typing import Callable
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static, Input, Select
from textual import on
import logging
from logging.handlers import RotatingFileHandler
from textual.logging import TextualHandler

from .model_provider import ProviderChoice, ModelChoiceFromProvider
from .api_input import ApiKeyInput
from .cron_input import CronInput
from .guardrails_input import GuardrailsInput


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level="NOTSET",
    handlers=[TextualHandler(), RotatingFileHandler(filename=".logs/app.log")],
)


class Setup(Vertical):
    """A Textual app for user login and signup."""

    def __init__(self, callbacks: dict[str, Callable] | None = None) -> None:
        super().__init__()
        self.callbacks = callbacks or {}

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="setup_scroll"):
            yield Static(
                "Enter a list of tickers you want to trade",
                id="setup_title",
            )
            yield Input(
                placeholder="Enter your watchlist (comma-separated tickers)",
                id="watchlist_input",
            )
            yield ProviderChoice(id="provider_choice")
            yield ModelChoiceFromProvider(id="model_choice_from_provider")
            yield ApiKeyInput(
                id="model_api", input_id="model_api_input", provider="llm"
            )
            yield ApiKeyInput(
                id="broker_api", input_id="broker_api_input", provider="alpaca"
            )
            yield ApiKeyInput(
                id="broker_secret_api",
                input_id="broker_secret_input",
                provider="alpaca secret",
            )
            yield ApiKeyInput(
                id="technical_api",
                input_id="technical_api_input",
                provider="alpha vantage",
            )
            yield CronInput(id="cron_input")
            yield GuardrailsInput(id="guardrails_input")

    @on(Select.Changed, "#provider_select")
    def provider_changed(self, event: Select.Changed) -> None:
        """Handle the provider choice change."""
        self.query_one(
            "#model_choice_from_provider", ModelChoiceFromProvider
        ).provider = str(event.value)
        self.callbacks.get("provider_updated", lambda x: None)(event.value)

    @on(Select.Changed, "#model_choice")
    def model_changed(self, event: Select.Changed) -> None:
        """Handle the Model choice change."""
        logging.info("Called model_changed")
        self.callbacks.get("model_updated", lambda x: None)(event.value)

    @on(Input.Changed, "#watchlist_input")
    def watchlist_submitted(self, event: Input.Changed) -> None:
        """Handle the watchlist input submission."""
        watchlist = event.value
        self.callbacks.get("watchlist_updated", lambda x: None)(watchlist)

    @on(Input.Changed, "#model_api_input")
    def model_api_submitted(self, event: Input.Changed) -> None:
        """Handle the model API key input submission."""
        api_key = event.value
        self.callbacks.get("model_api_key_updated", lambda x: None)(api_key)

    @on(Input.Changed, "#broker_api_input")
    def broker_api_submitted(self, event: Input.Changed) -> None:
        """Handle the broker API key input submission."""
        api_key = event.value
        logging.info("broker api changed")
        self.callbacks.get("broker_api_key_updated", lambda x: None)(api_key)

    @on(Input.Changed, "#broker_secret_input")
    def broker_secret_submitted(self, event: Input.Changed) -> None:
        """Handle the broker secret key input submission."""
        secret_key = event.value
        self.callbacks.get("broker_secret_updated", lambda x: None)(secret_key)

    @on(Input.Changed, "#technical_api_input")
    def technical_api_submitted(self, event: Input.Changed) -> None:
        """Handle the technical API key input submission."""
        api_key = event.value
        self.callbacks.get("technical_api_key_updated", lambda x: None)(api_key)

    @on(Select.Changed, "#cron_select")
    def cron_selection_changed(self, event: Select.Changed) -> None:
        """Handle the cron selection change."""
        cron_choice = event.value
        self.callbacks.get("cron_selection_updated", lambda x: None)(cron_choice)

    @on(Input.Changed, "#cron_expression_input")
    def cron_expression_submitted(self, event: Input.Changed) -> None:
        """Handle the cron expression input submission."""
        cron_expression = event.value
        self.callbacks.get("cron_expression_updated", lambda x: None)(cron_expression)

    @on(Input.Changed, "#guardrails_input")
    def guardrails_selection_changed(self, event: Input.Changed) -> None:
        """Handle the guardrails selection change."""
        guardrail_choice = event.value
        self.callbacks.get("guardrails_updated", lambda x: None)(guardrail_choice)
