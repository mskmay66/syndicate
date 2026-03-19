from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input


class ApiKeyInput(Vertical):
    """A Textual app for user login and signup."""

    def __init__(self, id: str, input_id: str, provider: str, classes: str):
        super().__init__(id=id, classes=classes)
        self.provider = provider
        self.input_id = input_id

    def compose(self) -> ComposeResult:
        yield Static(
            f"Enter your API key for your {self.provider}:",
            id="api_key_input_title",
        )
        yield Input(placeholder="Enter your API key", id=self.input_id)
