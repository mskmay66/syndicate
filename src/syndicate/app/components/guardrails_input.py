from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input
from textual import on


class GuardrailsInput(Vertical):
    """A Textual app for user login and signup."""

    labels = ["Max Position Concentration %", "Stop Losses %", "Take Profits %"]

    def compose(self) -> ComposeResult:
        for label in self.labels:
            yield Input(
                placeholder=f"Enter {label}",
                id=f"{label[:-2].lower().replace(' ', '_')}_input",
            )

    # def on_mount(self) -> None:
    #     """Called when the screen is mounted. Start the typing effect."""
    #     self.query_one("#guardrails_select", SelectionList).border_title = "Select guardrails/constraints for your agent (optional)"

    @on(Input.Changed)
    def handle_input_change(self, event: Input.Changed) -> None:
        """Handle input changes and update the corresponding guardrail values."""
        # input_id = event.input.id
        value = event.value.strip()

        value /= 100
