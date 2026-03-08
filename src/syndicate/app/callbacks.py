import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from ..models.trade_state import TradeState
from ..trading_graph import TradingGraph
from ..secrets import get_secret_from_keyring, add_secret_to_keyring
from ..log_config import setup_logging

logger = setup_logging(__name__, ".logs/syndicate.log")


def add_secret(service_name: str, username: str, secret: str) -> None:
    """Adds a secret to the keyring."""
    add_secret_to_keyring(service_name, username, secret)
    with open("services.json", "r") as f:
        services = []
        if os.path.exists("services.json") and os.path.getsize("services.json") != 0:
            services = json.load(f)
            logger.info(f"Loaded existing services from services.json: {services}")

    with open("services.json", "w") as f:
        services.append({"name": service_name, "username": username})
        json.dump(services, f, indent=2)
        logger.info(
            f"Added service {service_name} with username {username} to services.json"
        )


def get_secret(service_name: str, username: str) -> Optional[str]:
    """Retrieves a secret from the keyring."""
    secret = get_secret_from_keyring(service_name, username)
    if secret:
        logger.info(f"Got secret for {service_name} and {username}")
        return secret
    else:
        logger.warning(
            f"No secret found for {service_name} and {username}. Please add the secret using 'syndicate add-secret {service_name} {username} <secret>'"
        )
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
