from typing import Literal
from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static, Button, Input, RadioSet, RadioButton
from textual.containers import HorizontalGroup, Container, Vertical
from textual.reactive import reactive
from art import text2art
import asyncio

import logging

from ..llm_clients import VALID_MODELS

logging.basicConfig(
    filename=".logs/test.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class ApiKeyInput(Vertical):
    """A Textual app for user login and signup."""

    def __init__(self, id: str, provider: str):
        super().__init__(id=id)
        self.provider = provider

    def compose(self) -> ComposeResult:
        yield Static(
            f"Enter your API key for your {self.provider}:",
            id="api_key_input_title",
        )
        yield Input(placeholder="Enter your API key", id="api_key_input")


class ProviderChoice(Vertical):
    """A Textual app for user login and signup."""

    def compose(self) -> ComposeResult:
        with RadioSet(id="provider_choice"):
            yield RadioButton("OpenAI", id="openai")
            yield RadioButton("Anthropic", id="anthropic")
            yield RadioButton("Google Gemini", id="google")
            yield RadioButton("Qwen", id="qwen")
            yield RadioButton("Moonshot", id="moonshot")
            yield RadioButton("OpenRouter", id="custom")
            yield RadioButton("Ollama", id="ollama")
            yield RadioButton("xai", id="xai")


class ModelChoiceFromProvider(Vertical):
    """A Textual app for user login and signup."""

    provider = reactive("openai", recompose=True)

    def compose(self) -> ComposeResult:
        yield Static(
            "Select your model model:",
            id="model_choice_title",
        )
        with RadioSet(id="model_choice"):
            models = VALID_MODELS.get(self.provider, [])
            for model in models:
                yield RadioButton(model, id=model.replace(".", "_"))


class Setup(Vertical):
    """A Textual app for user login and signup."""

    def compose(self) -> ComposeResult:
        yield Static(
            "Welcome to Syndicate! Let's start by configuring your trading agent.",
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
        yield ApiKeyInput(id="technical_api", provider="tech")

    @on(RadioSet.Changed, "#provider_choice")
    def provider_changed(self, event: RadioSet.Changed) -> None:
        """Handle the provider choice change."""
        logging.info(f"Provider changed: {event.pressed}")
        self.query_one(ModelChoiceFromProvider).provider = event.pressed.id

    @on(Input.Submitted, "#watchlist_input")
    def watchlist_submitted(self, event: Input.Submitted) -> None:
        """Handle the watchlist input submission."""

        ## TODO: Add validation for the watchlist input (e.g., check if it's a valid list of tickers) + store the watchlist in a config file or state
        watchlist = event.value
        # Here you would typically save the watchlist to a config file or state
        logging.info(f"Watchlist submitted: {watchlist}")


class SetupScreen(Screen):  #
    """A Textual screen to display the setup screen."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Configure your trading agent.", id="setup_message")
        yield Container(Setup(), id="setup")


class Splash(Vertical):
    """A Textual app for user login and signup."""

    text = reactive("")
    full_text = "Welcome to Syndicate! If you're new here, click 'Setup' to configure your agent. If you're a returning user, click 'Enter' to access your dashboard."

    def compose(self) -> ComposeResult:
        yield Static(
            self.text,
            id="splash_title",
        )
        with HorizontalGroup(id="button_group"):
            yield Button("Setup", id="setup_button")
            yield Button("Enter", id="enter_button")

    def on_mount(self):
        self.set_interval(0.05, self.update_text)

    async def update_text(self):
        """Update the text to create a typing effect."""
        if len(self.text) < len(self.full_text):
            self.text += self.full_text[len(self.text)]
        else:
            self.text = ""
            await asyncio.sleep(2)
        self.query_one("#splash_title", Static).update(self.text)


class SplashScreen(Screen):
    """A Textual screen to display the splash screen."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(Splash(), id="splash")

    def on_mount(self) -> None:
        """Called when the screen is mounted. Start the typing effect."""
        self.title = text2art("Syndicate", font="slant")

    @on(Button.Pressed, "#enter_button")
    def handle_enter(self) -> None:
        """Handle the login button press."""
        pass

    @on(Button.Pressed, "#setup_button")
    def handle_setup(self) -> None:
        """Handle the signup button press."""
        self.app.push_screen("setup")


class Syndicate(App):
    """A Textual app to display the Syndicate agent's watchlist and actions."""

    CSS_PATH = "syndicate.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    SCREENS = {"splash": SplashScreen, "setup": SetupScreen}

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme: Literal["textual-dark", "textual-light"] = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_mount(self) -> None:
        """Called when the app is mounted. Load the watchlist and display it."""
        self.push_screen("splash")


def main():
    """The main entry point for the Syndicate app."""
    app = Syndicate()
    app.run()


if __name__ == "__main__":
    main()
