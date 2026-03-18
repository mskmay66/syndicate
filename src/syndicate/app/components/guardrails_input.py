from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input


class GuardrailsInput(Vertical):
    """A Textual app for user login and signup."""

    labels = ["Max Position Concentration %", "Stop Losses %", "Take Profits %"]

    def compose(self) -> ComposeResult:
        for label in self.labels:
            yield Input(
                placeholder=f"Enter {label}",
                id=f"{label[:-2].lower().replace(' ', '_')}_input",
            )

    # @on(Input.Changed)
    # def handle_input_change(self, event: Input.Changed) -> None:
    #     """Handle input changes and update the corresponding guardrail values."""
    #     value = event.value.strip()
    #     if value:
    #         try:
    #             value = abs(float(event.value.strip()))
    #         except ValueError:

    #         if value > 1:
    #             value /= 100
