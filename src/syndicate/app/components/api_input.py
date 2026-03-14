from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input


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
