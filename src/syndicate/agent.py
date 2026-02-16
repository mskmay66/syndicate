import json
import re
import time
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

from .tools import (
    get_account_summary,
    get_latest_quote,
    get_news,
    buy_stock,
    sell_stock,
)
from .models.portfolio_model import PortfolioModel
from .models.agent_model import AgentModel
from .models.decision_model import DecisionModel

logging.basicConfig(level=logging.INFO)


class SyndicateAgent:
    def __init__(
        self, portfolio: PortfolioModel, agent_model: AgentModel, sleep_time: int = 60
    ):
        self.portfolio = portfolio
        self.agent_model = agent_model
        self.sleep_time = sleep_time
        self.model, self.tokenizer = self.load_model_and_tokenizer(agent_model)

    @staticmethod
    def extract_json(s: str) -> dict:
        """Extracts a JSON object from a string.

        Args:
            s (str): The string to extract the JSON object from.

        Returns:
            dict: The extracted JSON object.
        """
        match = re.findall(r"\{.+[:,].+\}|\[.+[:,].+\]", s)
        if match:
            try:
                return json.loads(match[0])
            except json.JSONDecodeError:
                logging.error("Failed to decode JSON from string: %s", s)
                return {}
        else:
            logging.warning("No JSON object found in string: %s", s)
            return {}

    def load_model_and_tokenizer(self, agent_model: AgentModel) -> HuggingFacePipeline:
        logging.info(
            f"Loading agent {agent_model.name} with temperature {agent_model.temperature}"
        )
        if agent_model.local_path:
            logging.info(f"Loading model from local path {agent_model.local_path}")
            tokenizer = AutoTokenizer.from_pretrained(agent_model.local_path)
            llm = AutoModelForCausalLM.from_pretrained(agent_model.local_path)
        else:
            tokenizer = AutoTokenizer.from_pretrained(agent_model.name)
            llm = AutoModelForCausalLM.from_pretrained(agent_model.name)

        logging.info(f"Agent {agent_model.name} loaded successfully")
        return llm, tokenizer

    def run(self):
        while True:
            # 1. Get current state of the portfolio and account summary
            account_summary = get_account_summary()

            # 2. Get the latest news and stock quotes for the tickers in the portfolio
            news = get_news(self.portfolio.tickers)

            # 3. Get the current quotes for the tickers in the portfolio
            quotes = get_latest_quote(self.portfolio.tickers)

            # 4. Build the messages to send to the language model, including the account summary, news, and stock quotes, and ask the model to decide on a trade action to take (buy/sell/hold)
            messages = [
                {
                    "role": "system",
                    "content": """You are a financial expert and prolific trader that helps users manage their stock portfolios. You have access to the following tools: buy_stock and sell_stock.
                         - buy_stock(ticker: str, quantity: int, limit_price: float = None) -> str: Buys a stock for a given ticker symbol and quantity. If limit_price is not provided, a market order will be placed.
                         - sell_stock(ticker: str, quantity: int, limit_price: float = None) -> str: Sells a stock for a given ticker symbol and quantity. If limit_price is not provided, a market order will be placed.
                         
                         To use these tools return a list of actions in the following format:
                        [
                         {
                            "direction": "buy" or "sell",
                            "ticker": "the ticker symbol of the stock to trade",
                            "quantity": "the quantity of shares to trade"
                         }
                        ]
                         
                        If you want to hold and not make any trades, return an empty list. Always return a list of actions, even if it's empty. Do not include any explanations or reasoning in your response, only return the list of actions in the specified format.
                        """,
                },
                {
                    "role": "user",
                    "content": """Review the following account summary, news, and stock quotes, and decide on a trade action to take. Only return a list of actions in the specified format. Do not include any explanations or reasoning in your response.\n\n
                            Account Summary:\n{account_summary}\n\n
                            Latest News:\n{news}\n\n
                            Latest Stock Quotes:\n{quotes}
                            """.format(
                        account_summary=account_summary,
                        news=news,
                        quotes=quotes,
                    ),
                },
            ]

            # 5. Apply the tokenizer and model to the messages to get the agent's response
            input_ids = self.tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, return_tensors="pt"
            ).to(self.model.device)
            input_len = input_ids["input_ids"].shape[-1]
            with torch.no_grad():
                result = self.model.generate(
                    **input_ids,
                    max_length=2048,
                    temperature=self.agent_model.temperature,
                )
            result_text = self.tokenizer.batch_decode(
                result[0][input_len:], skip_special_tokens=True
            )[0]
            logging.info(f"Agent response: {result_text}")

            # 5. Parse the agent's response to extract the trade action, and execute the trade using the appropriate tool function
            model_decision = self.extract_json(result_text)
            for action in model_decision:
                decision = DecisionModel(**action)
                if decision.direction == "buy":
                    buy_result = buy_stock(decision.ticker, decision.quantity)
                    logging.info(f"Buying stock: {buy_result}")
                elif decision.direction == "sell":
                    sell_result = sell_stock(decision.ticker, decision.quantity)
                    logging.info(f"Selling stock: {sell_result}")
                else:
                    logging.warning(
                        f"Invalid trade direction: {decision.direction}. Skipping action."
                    )

            # 6. Sleep for a certain period of time before repeating the process
            logging.info(
                f"Sleeping for {self.sleep_time} seconds before next iteration..."
            )
            time.sleep(self.sleep_time)
