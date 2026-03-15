from typing import Literal, Dict
from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static, Button, Footer
from textual.containers import Container
from art import text2art
import logging
from textual.logging import TextualHandler

from .components.setup import Setup
from .components.splash import Splash

from ..models import User
from ..file_manager import add_config_file
from .callbacks import convert_input_to_cron_expression, register_cron
from ..secrets import set_all_secrets


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level="NOTSET",
    handlers=[TextualHandler()],
)


class SetupScreen(Screen):  #
    """A Textual screen to display the setup screen."""

    BINDINGS = [("f", "finish_setup", "Finish setup and enter app")]
    guardrails: Dict[str, float] = {}

    def compose(self) -> ComposeResult:
        callbacks = {
            k.replace("callback", "updated"): v
            for k, v in self.__dict__.items()
            if "callback" in k
        }
        yield Header(show_clock=True)
        yield Static(
            "Welcome to Syndicate! Let's start by configuring your trading agent.",
            id="setup_message",
        )
        yield Setup(callbacks=callbacks)
        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted. Start the typing effect."""
        self.title = text2art("Syndicate", font="slant")

    def _watchlist_callback(self, watchlist: str) -> None:
        """A callback function to handle watchlist updates."""
        logging.info(f"Watchlist updated: {watchlist}")
        # Here you would typically save the watchlist to a config file or state
        self.watchlist = watchlist

    def _provider_callback(self, provider: str) -> None:
        """A callback function to handle provider updates."""
        logging.info(f"Provider updated: {provider}")
        self.provider = provider

    def _model_callback(self, model: str) -> None:
        """A callback function to handle model updates."""
        logging.info(f"Model updated: {model}")
        self.model = model

    def _model_api_key_callback(self, api_key: str) -> None:
        self.model_api_key = api_key

    def _broker_api_key_callback(self, api_key: str) -> None:
        self.broker_api_key = api_key

    def _broker_secret_callback(self, secret_key: str) -> None:
        self.broker_secret_key = secret_key

    def _technical_api_key_callback(self, api_key: str) -> None:
        self.technical_api_key = api_key

    def _guardrails_callback(self, guardrail_name, pct) -> None:
        self.guardrails[guardrail_name] = pct

    def _cron_selection_callback(self, sch: str) -> None:
        logging.info(f"Cron schedule updated: {sch}")
        self.cron_schedule = sch

    def _cron_expression_callback(self, expr: str) -> None:
        logging.info(f"Cron expression updated: {expr}")
        self.cron_expression = expr

    def on_finish_setup(self) -> None:
        """ "Handle the finish setup action."""
        logging.info("Finishing setup and entering app")

        # generate the cron
        cron = convert_input_to_cron_expression(
            self.cron_schedule, self.cron_expression
        )
        register_cron(cron)

        # create a UserConfig
        user_config = User(
            model_provider=self.provider,
            model_name=self.model,
            watchlist=self.watchlist.strip().split(","),
            broker_api_key=self.broker_api_key,
            broker_secret_key=self.broker_secret_key,
            model_api_key=self.model_api_key,
            alpha_vantage_api_key=self.technical_api_key,
            cron=cron,
            guardrails=self.guardrails,
        )

        # Save the user config to a file
        add_config_file(user_config.to_json(), "user_config.json")

        # add the secrets to the keyring
        set_all_secrets(user_config.get_secrets())


class SplashScreen(Screen):
    """A Textual screen to display the splash screen."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(Splash(), id="splash")
        yield Footer()

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
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "setup", "Go to setup screen"),
        ("q", "quit", "Quit the app"),
        ("enter", "enter_app", "Go main screen"),
        ("b", "back", "Go back to splash screen"),
    ]
    SCREENS = {"splash": SplashScreen, "setup": SetupScreen}

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme: Literal["textual-dark", "textual-light"] = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_setup(self) -> None:
        """An action to go to the setup screen."""
        self.push_screen("setup")

    def action_enter_app(self) -> None:
        """An action to go to the main screen."""
        pass

    def action_quit(self) -> None:
        """An action to quit the app."""
        self.exit()

    def action_back(self):
        """An action to go back to the splash screen."""
        self.pop_screen()

    def on_mount(self) -> None:
        """Called when the app is mounted. Load the watchlist and display it."""
        logging.info("Starting Syndicate app")
        self.push_screen("splash")


def main():
    """The main entry point for the Syndicate app."""
    logging.info("Starting Syndicate app")
    app = Syndicate()
    app.run()


if __name__ == "__main__":
    logging.info("Starting Syndicate app")
    main()
