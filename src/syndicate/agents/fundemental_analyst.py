from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .tools import (
    get_fundementals,
    get_balance_sheet,
    get_income_statement,
    get_cashflow,
)


def build_fundementals_analyst(llm):
    def fundementals_analyst_node(state):
        current_date = state.get("current_date")
        tickers = state.get("tickers", [])

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

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "current_date": current_date,
            "tickers": tickers,
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundementals_analyst_node
