from typing import Literal
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Button
from textual.containers import HorizontalGroup, Container, Vertical
from textual.reactive import reactive
from art import text2art
import asyncio


class LoginSignup(Vertical):
    """A Textual app for user login and signup."""

    text = reactive("")
    full_text = "Welcome to Syndicate! Please log in or sign up to continue."

    def compose(self) -> ComposeResult:
        yield Static(
            self.text,
            id="login_title",
        )
        with HorizontalGroup(id="button_group"):
            yield Button("Login", id="login_button")
            yield Button("Signup", id="signup_button")

    def on_mount(self):
        self.set_interval(0.05, self.update_text)

    async def update_text(self):
        """Update the text to create a typing effect."""
        if len(self.text) < len(self.full_text):
            self.text += self.full_text[len(self.text)]
        else:
            self.text = ""
            await asyncio.sleep(2)
        self.query_one("#login_title", Static).update(self.text)


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

    @on(Button.Pressed, "#login_button")
    def handle_login(self) -> None:
        """Handle the login button press."""
        pass

    @on(Button.Pressed, "#signup_button")
    def handle_signup(self) -> None:
        """Handle the signup button press."""
        pass


def main():
    """The main entry point for the Syndicate app."""
    app = Syndicate()
    app.run()


if __name__ == "__main__":
    main()
