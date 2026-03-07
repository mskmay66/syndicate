from typing import Literal
from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Button
from textual.containers import HorizontalGroup, Container, Vertical
from art import text2art


class LoginSignup(Vertical):
    """A Textual app for user login and signup."""

    def compose(self) -> ComposeResult:
        yield Static(
            "Welcome to Syndicate! Please log in or sign up to continue.",
            id="login_title",
        )
        with HorizontalGroup(id="button_group"):
            yield Button("Login", id="login_button")
            yield Button("Signup", id="signup_button")


class Syndicate(App):
    """A Textual app to display the Syndicate agent's watchlist and actions."""

    CSS_PATH = "syndicate.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(LoginSignup(), id="login")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme: Literal["textual-dark", "textual-light"] = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_mount(self) -> None:
        """Called when the app is mounted. Load the watchlist and display it."""
        self.title = text2art("Syndicate", font="slant")


if __name__ == "__main__":
    app = Syndicate()
    app.run()
