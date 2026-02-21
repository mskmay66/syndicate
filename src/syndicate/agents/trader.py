from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .tools import get_account_summary, buy_stock, sell_stock, get_latest_quote


def build_trader(llm):
    def trader_node(state):
        current_date = state.get("current_date")
        tickers = state.get("tickers", [])
        fundementals_report = state.get("fundementals_report", "")
        news_report = state.get("news_report", "")

        tools = [get_account_summary, buy_stock, sell_stock, get_latest_quote]

        curr_situation = f"{fundementals_report}\n\n{news_report}"

        system_prompt = (
            "You are a trader. Your task is to make trading decisions based on the insights provided by the other analysts and the current state of the portfolio. You have access to the following tools: {tool_names}.\n{system_message}"
            "For your reference, the current date is {current_date}. The market is sitution is as follows: {curr_situation}. We are looking at the following companies {tickers}."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_prompt)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(curr_situation=curr_situation)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(tickers=",".join(tickers))

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "trading_decision": result.content,
        }

    return trader_node
