from ..log_config import setup_logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..tools import (
    get_account_summary,
    buy_stock,
    sell_stock,
    get_latest_quote,
    max_loss,
    take_profit,
)

logger = setup_logging(__name__, "trader")


def build_trader(llm):
    def trader_node(state):
        current_date = state.current_date
        tickers = state.tickers
        fundementals_report = state.fundementals_report
        news_report = state.news_report

        tools = [get_account_summary, buy_stock, sell_stock, get_latest_quote]

        curr_situation = f"{fundementals_report}\n\n{news_report}"

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " use the buy_stock or sell_stock tools to execute those transactions."
                    " Always report what you bought and sold in your response so the team knows what you did."
                    " Always make your report your final action, buy or sell stock before reporting"
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}.  We are looking at the following companies: {tickers}"
                    "Here is the current situation based on the fundementals and news analysis:\n{curr_situation}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        system_prompt = "You are a trader. Your task is to execute trades based on the insights provided by the other analysts and the current state of the portfolio."

        prompt = prompt.partial(system_message=system_prompt)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(curr_situation=curr_situation)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(tickers=",".join(tickers))

        chain = prompt | llm.bind_tools(tools)
        logger.info("Invoking trader")
        result = chain.invoke(state.messages)
        logger.info(f"Trader result: {result}")

        report = ""
        tools_used = False
        if len(result.tool_calls) == 0:
            report = result.content
            logger.info(f"Trader did not use any tools. Report: {report}")
            max_loss()
            take_profit()
        else:
            logger.info(f"Trader used tools. Tool calls: {result.tool_calls}")

        return {
            "current_date": current_date,
            "tickers": tickers,
            "messages": [result],
            "trade_report": report,
            "tools_used": tools_used,
        }

    return trader_node
