from datetime import datetime

from .models import TradeState
from .models import User

from .trading_graph import TradingGraph
from .log_config import setup_logging
from .file_manager import read_config_file
from .secrets import load_all_secrets

logger = setup_logging(__name__, "syndicate")


def _load_user_config() -> User:
    """Load the user's configuration from the user_config.json file.

    Returns:
        User: The user's configuration as a User instance.
    """
    logger.info("Loading user configuration from user_config.json")
    non_secret_config = read_config_file("user_config.json")
    api_keys = load_all_secrets()
    user_config_data = {**non_secret_config, **api_keys}
    user_config = User.model_validate(user_config_data)
    logger.info("Successfully loaded user configuration.")
    return user_config


def main() -> None:
    """The main entry point for the Syndicate application."""
    user = _load_user_config()
    logger.info(f"User config: {user}")

    initial_state = TradeState.model_validate(
        {
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "tickers": user.watchlist,
            "fundementals_report": "",
            "news_report": "",
            "messages": [],
        }
    )

    graph = TradingGraph(user)

    result = graph.run(initial_state)
    logger.info(f"Final result: {result}")


if __name__ == "__main__":
    main()
