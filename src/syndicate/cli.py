import os
import json
import typer
from typer import Context
from datetime import datetime

from .models.llm import LLMConfig
from .models.trade_state import TradeState
from .models.watchlist import Watchlist
from .trading_graph import TradingGraph
from .secrets import get_secret_from_keyring, add_secret_to_keyring
from .log_config import setup_logging

app = typer.Typer(
    help="Syndicate CLI - A command-line interface for the Syndicate trading agent.",
    no_args_is_help=True,
)
logger = setup_logging(__name__, ".logs/syndicate.log")
_initialized = False


def _load_agent_choice() -> LLMConfig:
    """Load the user's agent choice from the agent.json file.

    Returns:
        LLMConfig: The user's agent choice as an LLMConfig instance.
    """
    logger.info("Loading agent choice from agent.json")
    if not os.path.exists("agent.json"):
        logger.error(
            "agent.json not found. Please create an agent.json file with your agent choice."
        )
        raise FileNotFoundError(
            "agent.json not found. Please create an agent.json file with your agent choice."
        )

    with open("agent.json", "r") as f:
        agent_choice = LLMConfig.model_validate_json(f.read())
    logger.info(
        "Syndicate agent installed successfully. You can now run 'syndicate start' to start the agent."
    )
    return agent_choice


def _load_watchlist() -> Watchlist:
    """Load the user's watchlist from the watchlist.json file.

    Returns:
        Watchlist: The user's watchlist as a Watchlist instance.
    """
    logger.info("Loading watchlist from watchlist.json")
    if not os.path.exists("watchlist.json"):
        logger.warning("watchlist.json not found. Creating a default watchlist.")
        default_watchlist = Watchlist(tickers=["AAPL", "GOOG", "TSLA"])
        with open("watchlist.json", "w") as f:
            f.write(default_watchlist.model_dump_json(indent=2))

    with open("watchlist.json", "r") as f:
        watchlist = Watchlist.model_validate_json(f.read())
    return watchlist


@app.callback(invoke_without_command=True)
def main(ctx: Context) -> None:
    """Main entry point for the Syndicate CLI."""
    logger.info("Entered main callback")
    logger.info(f"Running Subcommand: {ctx.invoked_subcommand}")
    global _initialized
    if not _initialized:
        logger.info("Initializing Syndicate CLI...")
        ctx.obj = {
            "agent_choice": _load_agent_choice(),
            "watchlist": _load_watchlist(),
        }
        _initialized = True


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
    # set_env_vars(secret, service_name)


@app.command()
def get_secret(service_name: str, username: str):
    """Retrieves a secret from the keyring."""
    secret = get_secret_from_keyring(service_name, username)
    if secret:
        logger.info(f"Got secret for {service_name} and {username}")
        typer.echo(secret)
    else:
        logger.warning(
            f"No secret found for {service_name} and {username}. Please add the secret using 'syndicate add-secret {service_name} {username} <secret>'"
        )


@app.command()
def run(ctx: Context):
    """Starts the Syndicate agent."""
    inital_state = TradeState.model_validate(
        {
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "tickers": ctx.obj["watchlist"].tickers,
            "fundementals_report": "",
            "news_report": "",
            "messages": [],
        }
    )

    graph = TradingGraph(ctx.obj["agent_choice"])
    trading_graph = graph.build_graph()

    result = trading_graph.invoke(inital_state, config={"recursion_limit": 50})
    logger.info(f"Final result: {result}")


if __name__ == "__main__":
    app()
