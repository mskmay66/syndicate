import typer
import logging
from .models.portfolio_model import PortfolioModel
from .models.agent_model import AgentModel
from .agent import SyndicateAgent

app = typer.Typer()
logging.basicConfig(level=logging.INFO)

logging.info("Loading portfolio data from portfolio.json")
with open("portfolio.json", "r") as f:
    portfolio_data = PortfolioModel.model_validate_json(f.read())

# keep track of a user's agent choice in file agent.json
logging.info("Loading agent choice from agent.json")
with open("agent.json", "r") as f:
    agent_choice = AgentModel.model_validate_json(f.read())
logging.info(
    "Syndicate agent installed successfully. You can now run 'syndicate start' to start the agent."
)


@app.command()
def start():
    """Starts the Syndicate agent."""
    agent = SyndicateAgent(portfolio_data, agent_choice)
    agent.run()


if __name__ == "__main__":
    app()
