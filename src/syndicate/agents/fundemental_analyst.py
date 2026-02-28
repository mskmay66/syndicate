from ..log_config import setup_logging

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..tools import (
    get_fundementals,
    get_balance_sheet,
    get_income_statement,
    get_cashflow,
)

logger = setup_logging(__name__, ".logs/fundementals_analyst.log")


def build_fundementals_analyst(llm):
    def fundementals_analyst_node(state):
        current_date = state.current_date
        tickers = state.tickers

        tools = [
            get_fundementals,
            get_balance_sheet,
            get_income_statement,
            get_cashflow,
        ]

        system_prompt = "You are a financial fundementals analyst. Your task is to analyze the fundemental data related to the stocks in the portfolio and provide insights that can help inform trading decisions."

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The companies we want to look at are {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_prompt)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=",".join(tickers))

        chain = prompt | llm.bind_tools(tools)

        logger.info("Invoking fundementals analyst")
        result = chain.invoke(state.messages)
        logger.info(f"Fundementals analyst result: {result}")

        report = ""
        tools_used = set()
        used_all_tools = False
        if len(result.tool_calls) == 0:
            report = result.content
            logger.info(f"Fundemental analyst report: {report}")
        else:
            logger.info(f"Tools used by fundementals analyst: {result.tool_calls}")
            for tool_call in result.tool_calls:
                tools_used.add(tool_call["name"])
            if len(tools_used) == len(tools):
                used_all_tools = True

        return {
            "current_date": current_date,
            "tickers": tickers,
            "messages": [result],
            "tools_used": used_all_tools,
            "fundamentals_report": report,
        }

    return fundementals_analyst_node
