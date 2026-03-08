from datetime import datetime
from typing import Dict, Union

from .models.trade_state import TradeState
from .models.llm import LLMConfig
from .models.watchlist import Watchlist
from .trading_graph import TradingGraph
from .log_config import setup_logging
from .file_manager import read_config_file

logger = setup_logging(__name__, ".logs/syndicate.log")


def _load_agent_choice() -> LLMConfig:
    """Load the user's agent choice from the agent.json file.

    Returns:
        LLMConfig: The user's agent choice as an LLMConfig instance.
    """
    logger.info("Loading agent choice from agent.json")
    agent_config = read_config_file("agent.json")
    agent_choice = LLMConfig.model_validate(agent_config)
    logger.info("Successfully loaded agent choice.")
    return agent_choice


def _load_watchlist() -> Watchlist:
    """Load the user's watchlist from the watchlist.json file.

    Returns:
        Watchlist: The user's watchlist as a Watchlist instance.
    """
    logger.info("Loading watchlist from watchlist.json")
    watchlist_config = read_config_file("watchlist.json")
    watchlist = Watchlist.model_validate(watchlist_config)
    logger.info("Successfully loaded watchlist.")
    return watchlist


def main() -> None:
    """The main entry point for the Syndicate application."""
    ctx: Dict[str, Union[Watchlist, LLMConfig]] = {
        "watchlist": _load_watchlist(),
        "agent_choice": _load_agent_choice(),
    }

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


if __name__ == "__main__":
    main()
