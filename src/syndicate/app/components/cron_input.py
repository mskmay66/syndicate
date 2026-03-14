from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Select, Input


class CronInput(Vertical):
    """A Textual app for user login and signup."""

    VALID_SCHEDULES = ["Hourly", "Daily", "Weekly", "Monthly", "Custom"]

    def compose(self) -> ComposeResult:
        yield Static(
            "How often do you want your agent to trade?:",
            id="cron_input_title",
        )
        yield Select(
            ((sch, sch.lower()) for sch in self.VALID_SCHEDULES),
            id="cron_select",
        )
        yield Static(
            "If you selected custom, please enter your cron expression below, otherwise you can enter a specific time (e.g., 9:30 AM) or day (e.g., Monday at 9:30 AM) depending on your previous selection, otherwise leave it blank:",
            id="cron_expression_title",
        )
        yield Input(
            placeholder="Enter your cron expression",
            id="cron_expression_input",
        )
