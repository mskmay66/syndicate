from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from textual.reactive import reactive
import asyncio


class Splash(Vertical):
    """A Textual app for user login and signup."""

    text = reactive("")
    full_text = "Welcome to Syndicate! If you're new here, press the s key to enter the setup wizard. Otherwise, press the e key to enter the app."

    def compose(self) -> ComposeResult:
        yield Static(
            self.text,
            id="splash_title",
        )

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
