from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static, Input, Select
from textual import on

from .model_provider import ProviderChoice, ModelChoiceFromProvider
from .api_input import ApiKeyInput
from .cron_input import CronInput


class Setup(Vertical):
    """A Textual app for user login and signup."""

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
            yield ApiKeyInput(id="model_api", provider="llm")
            yield ApiKeyInput(id="broker_api", provider="alpaca")
            yield ApiKeyInput(id="technical_api", provider="alpha vantage")
            yield CronInput(id="cron_input")

    @on(Select.Changed, "#provider_select")
    def provider_changed(self, event: Select.Changed) -> None:
        """Handle the provider choice change."""
        self.query_one(
            "#model_choice_from_provider", ModelChoiceFromProvider
        ).provider = str(event.value)

    @on(Input.Submitted, "#watchlist_input")
    def watchlist_submitted(self, event: Input.Submitted) -> None:
        """Handle the watchlist input submission."""

        ## TODO: Add validation for the watchlist input (e.g., check if it's a valid list of tickers) + store the watchlist in a config file or state
        # watchlist = event.value
        # Here you would typically save the watchlist to a config file or state
        pass

    @on(Input.Submitted, "#model_api_input")
    def model_api_submitted(self, event: Input.Submitted) -> None:
        """Handle the model API key input submission."""
        # api_key = event.value
        # Here you would typically save the API key to a config file or state
        pass

    @on(Input.Submitted, "#broker_api_input")
    def broker_api_submitted(self, event: Input.Submitted) -> None:
        """Handle the broker API key input submission."""
        # api_key = event.value
        # Here you would typically save the API key to a config file or state
        pass

    @on(Input.Submitted, "#technical_api_input")
    def technical_api_submitted(self, event: Input.Submitted) -> None:
        """Handle the technical API key input submission."""
        # api_key = event.value
        # Here you would typically save the API key to a config file or state
        pass

    @on(Select.Changed, "#cron_select")
    def cron_selection_changed(self, event: Select.Changed) -> None:
        """Handle the cron selection change."""
        # cron_choice = event.value
        # Here you would typically save the cron choice to a config file or state
        pass
