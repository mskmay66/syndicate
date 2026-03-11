import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
import getpass
from crontab import CronTab

from ..models.trade_state import TradeState
from ..trading_graph import TradingGraph
from ..secrets import get_secret_from_keyring, add_secret_to_keyring
from ..log_config import setup_logging

logger = setup_logging(__name__, "syndicate")


def add_secret(service_name: str, secret: str) -> None:
    """Adds a secret to the keyring."""
    add_secret_to_keyring(service_name, secret)
    with open("services.json", "r") as f:
        services = []
        if os.path.exists("services.json") and os.path.getsize("services.json") != 0:
            services = json.load(f)
            logger.info(f"Loaded existing services from services.json: {services}")

    with open("services.json", "w") as f:
        services.append({"name": service_name})
        json.dump(services, f, indent=2)
        logger.info(f"Added service {service_name} to services.json")


def get_secret(
    service_name: str,
) -> Optional[str]:
    """Retrieves a secret from the keyring."""
    secret = get_secret_from_keyring(service_name)
    if secret:
        logger.info(f"Got secret for {service_name}")
        return secret
    else:
        logger.warning(f"No secret found for {service_name}.")
        return None


def run(ctx: Dict[str, Any]) -> None:
    """Starts the Syndicate agent."""
    inital_state = TradeState.model_validate(
        {
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "tickers": ctx["watchlist"].tickers,
            "fundementals_report": "",
            "news_report": "",
            "messages": [],
        }
    )

    graph = TradingGraph(ctx["agent_choice"])
    trading_graph = graph.build_graph()

    result = trading_graph.invoke(inital_state, config={"recursion_limit": 50})
    logger.info(f"Final result: {result}")


def convert_input_to_cron_expression(rate: str, time_string: Optional[str]) -> str:
    """Converts a user-friendly schedule input into a cron expression.

    Args:
        schedule (str): A user-friendly schedule input (e.g., "daily at 9am", "every Monday at 8pm").

    Returns:
        str: A cron expression corresponding to the user input.

    Raises:
        ValueError: If the input format is not recognized.
    """

    def map_day_of_week(day: str) -> int:
        day = day.lower()[-3:]  # Get the first three letters
        days = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
        return days.get(day, 1)

    rate = rate.lower()
    if time_string and rate != "custom":
        time_string = time_string.lower()
        day_of_week = re.search(
            r"(mon|tue|wed|thu|fri|sat|sun)(day)*", time_string, re.I
        )
        time = re.search(r"(([0-1]?[0-9]|2[0-3]):[0-5][0-9])", time_string)
        day = (
            map_day_of_week(day_of_week.group(1)) if day_of_week else 1
        )  # Default to Monday
        if not time:
            raise ValueError("Time must be specified in HH:MM format.")

        split_time = time.group(0).split(":")
        hour, minute = map(int, split_time)

    match rate:
        case "hourly":
            if time_string:
                return f"{minute} * * * *"
            else:
                return "0 * * * *"  # Default to hourly at the top of the hour
        case "daily":
            if time_string:
                return f"{minute} {hour} * * *"
            else:
                return "0 9 * * *"  # Default to daily at 9 AM
        case "weekly":
            if time_string:
                return f"{minute} {hour} * * {day}"  # Default to every Monday at specified time
            else:
                return "0 9 * * 1"  # Default to every Monday at 9 AM
        case "monthly":
            if time_string:
                return f"{minute} {hour} 1 * *"
            else:
                return "0 9 1 * *"  # Default to monthly on the 1st at 9 AM
        case "custom":
            if time_string:
                pattern = r"^(?:((((\d+,)+\d+|(\d+(\/|-|#)\d+)|\d+L?|\*(\/\d+)?|L(-\d+)?|\?|[A-Z]{3}(-[A-Z]{3})?) ?){5,7})|(@(annually|yearly|monthly|weekly|daily|hourly|reboot))|(@every (\d+(ns|us|µs|ms|s|m|h))+))$"
                if not re.match(pattern, time_string):
                    raise ValueError("Invalid cron expression for custom schedule.")
                return time_string
            else:
                raise ValueError(
                    "Custom schedule requires a cron expression as time input."
                )
        case _:
            raise ValueError(
                "Invalid schedule rate. Must be one of: hourly, daily, weekly, monthly, custom."
            )


def register_cron(cron_expression: str) -> None:
    """Registers a cron job to run the Syndicate agent at specified intervals.

    Args:
        cron_expression (str): A cron expression specifying the schedule for running the agent (e.g., "0 9 * * *" to run every day at 9 AM).
    """
    user = getpass.getuser()
    cron = CronTab(user=user)
    logger.info(
        f"Registering syndicate cron job with expression: {cron_expression} for user {user}"
    )

    job = cron.new(command="syndicate run", comment="Syndicate Agent Cron Job")
    job.setall(cron_expression)
    cron.write()
    logger.info("Cron job registered successfully.")
