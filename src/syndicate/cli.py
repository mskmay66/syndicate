import typer
import logging
from rich import print
from datetime import datetime

from .models.llm import LLMConfig
from .model.trade_state import TradeState
from .models.watchlist import Watchlist
from .trading_graph import TradingGraph


app = typer.Typer()
logging.basicConfig(level=logging.INFO)

# keep track of a user's agent choice in file agent.json
logging.info("Loading agent choice from agent.json")
with open("agent.json", "r") as f:
    agent_choice = LLMConfig.model_validate_json(f.read())
logging.info(
    "Syndicate agent installed successfully. You can now run 'syndicate start' to start the agent."
)

logging.info("Loading watchlist from watchlist.json")
with open("watchlist.json", "r") as f:
    watchlist = Watchlist.model_validate_json(f.read())


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

    result = trading_graph.invoke(inital_state)
    print(f"Trading decision: {result.trading_decision}")


if __name__ == "__main__":
    app()
