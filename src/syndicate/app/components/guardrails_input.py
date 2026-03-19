from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Static


class GuardrailsInput(Vertical):
    """A Textual app for user login and signup."""

    labels = ["Max Position Concentration %", "Stop Losses %", "Take Profits %"]

    def compose(self) -> ComposeResult:
        yield Static("Set the guardrails you want for you agent.")
        for label in self.labels:
            yield Input(
                placeholder=f"Enter {label}",
                id=f"{label[:-2].lower().replace(' ', '_')}_input",
            )
