import json
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.agents import create_agent

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
    def __init__(self, portfolio: PortfolioModel, agent_model: AgentModel):
        self.portfolio = portfolio
        self.agent_model = agent_model
        self.model = self.load_model(agent_model)
        self.agent = self.build_agent(self.model)

    def load_model(self, agent_model: AgentModel) -> HuggingFacePipeline:
        logging.info(
            f"Loading agent {agent_model.name} with temperature {agent_model.temperature}"
        )
        tokenizer = AutoTokenizer.from_pretrained(agent_model.name)
        model = AutoModelForCausalLM.from_pretrained(agent_model.name)
        agent_pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            temperature=agent_model.temperature,
            device_map="auto",
        )
        llm = HuggingFacePipeline(pipeline=agent_pipe).with_structured_output(
            DecisionModel
        )
        logging.info(f"Agent {agent_model.name} loaded successfully")
        return llm

    def build_agent(self, llm: HuggingFacePipeline):
        sys_prompt = """
        You are a stock trading assistant. You have access to the following tools:  
        1. buy_stock: Buys a given quantity of a stock.
        2. sell_stock: Sells a given quantity of a stock.
        3. get_account_summary: Gets the account summary for the current account.
        4. get_latest_quote: Gets the latest stock quote for a given ticker symbol.
        5. get_news: Gets the latest news for a given ticker symbol.
        When given a prompt, you should first analyze the account summary, quotes, and news to make an informed decision about whether to buy or sell any stocks in the portfolio. If you decide to buy or sell, you should use the buy_stock or sell_stock tool to execute the trade.
        Use get_account_summary to get the account summary, get_latest_quote to get the latest stock quote for a given ticker symbol, and get_news to get the latest news for a given ticker symbol. Use buy_stock to buy a given quantity of a stock and sell_stock to sell a given quantity of a stock.
        """
        tools = [buy_stock, sell_stock, get_account_summary, get_latest_quote, get_news]
        agent = create_agent(llm, tools, sys_prompt)
        return agent

    def run(self):
        while True:
            result = self.agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": "What should I do with my portfolio?",
                        }
                    ]
                }
            )
            logging.info(f"Agent decision: {json.dumps(result, indent=2)}")
