from typing import Literal
from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static, Button
from textual.containers import Container
from art import text2art
import logging
from textual.logging import TextualHandler

from .components.setup import Setup
from .components.splash import Splash


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level="NOTSET",
    handlers=[TextualHandler()],
)


class SetupScreen(Screen):  #
    """A Textual screen to display the setup screen."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "Welcome to Syndicate! Let's start by configuring your trading agent.",
            id="setup_message",
        )
        yield Container(Setup(), id="setup")

    def on_mount(self) -> None:
        """Called when the screen is mounted. Start the typing effect."""
        self.title = text2art("Syndicate", font="slant")


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
