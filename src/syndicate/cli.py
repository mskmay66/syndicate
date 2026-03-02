import os
import json
import typer
import logging
from datetime import datetime

from .models.llm import LLMConfig
from .models.trade_state import TradeState
from .models.watchlist import Watchlist
from .trading_graph import TradingGraph
from .secrets import get_secret_from_keyring, add_secret_to_keyring, set_env_vars

app = typer.Typer(
    help="Syndicate CLI - A command-line interface for the Syndicate trading agent.",
    no_args_is_help=True,
)
logging.basicConfig(level=logging.INFO)

# keep track of a user's agent choice in file agent.json
logging.info("Loading agent choice from agent.json")
if not os.path.exists("agent.json"):
    logging.error(
        "agent.json not found. Please create an agent.json file with your agent choice."
    )
    raise FileNotFoundError(
        "agent.json not found. Please create an agent.json file with your agent choice."
    )

with open("agent.json", "r") as f:
    agent_choice = LLMConfig.model_validate_json(f.read())
logging.info(
    "Syndicate agent installed successfully. You can now run 'syndicate start' to start the agent."
)

logging.info("Loading watchlist from watchlist.json")
if not os.path.exists("watchlist.json"):
    logging.warning("watchlist.json not found. Creating a default watchlist.")
    default_watchlist = Watchlist(tickers=["AAPL", "GOOG", "TSLA"])
    with open("watchlist.json", "w") as f:
        f.write(default_watchlist.model_dump_json(indent=2))

with open("watchlist.json", "r") as f:
    watchlist = Watchlist.model_validate_json(f.read())

logging.info("Loading secrets from services listed in services.json")
if not os.path.exists("services.json"):
    logging.error("services.json not found. Creating an empty services.json.")
    raise FileNotFoundError(
        'services.json not found. Please create a services.json file with the services you want to load secrets for. Example: [{"name": "alpaca", "username": "your_alpaca_username"}]'
    )

services = []
with open("services.json", "r") as f:
    if os.path.getsize("services.json") != 0:
        services = json.load(f)

    for service in services:
        logging.info(f"Loading secret for {service['name']}")
        secret = get_secret_from_keyring(service["name"], service["username"])
        if secret:
            set_env_vars(secret, service["name"])
            logging.info(f"Secret for {service['name']} loaded successfully.")
        else:
            logging.warning(
                f"No secret found for {service['name']} and {service['username']}. Please add the secret using 'syndicate add-secret {service['name']} {service['username']} <secret>'"
            )


@app.command()
def add_secret(service_name: str, username: str, secret: str):
    """Adds a secret to the keyring."""
    add_secret_to_keyring(service_name, username, secret)
    with open("services.json", "r") as f:
        services = []
        if os.path.exists("services.json") and os.path.getsize("services.json") != 0:
            services = json.load(f)

    with open("services.json", "w") as f:
        services.append({"name": service_name, "username": username})
        json.dump(services, f, indent=2)
    set_env_vars(secret, service_name)


@app.command()
def run():
    """Starts the Syndicate agent."""
    inital_state = TradeState.model_validate(
        {
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "tickers": watchlist.tickers,
            "fundementals_report": "",
            "news_report": "",
            "messages": [],
        }
    )

    graph = TradingGraph(agent_choice)
    trading_graph = graph.build_graph()

    result = trading_graph.invoke(inital_state, config={"recursion_limit": 50})
    logging.info(f"Final result: {result}")


if __name__ == "__main__":
    app()
