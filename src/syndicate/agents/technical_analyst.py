from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..log_config import setup_logging
from ..tools import get_indicator, get_latest_quote

logger = setup_logging(__name__, ".logs/technical_analyst.log")


def build_technical_analyst(llm):
    def technical_analyst_node(state):
        current_date = state.current_date
        tickers = state.tickers

        tools = [get_indicator, get_latest_quote]

        system_prompt = "You are a financial technical analyst. Your task is to analyze the technical indicators related to the stocks in the portfolio and provide insights that can help inform trading decisions."

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
                    "For your reference, the current date is {current_date}. We are looking at the following companies {tickers}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_prompt)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(tickers=",".join(tickers))

        chain = prompt | llm.bind_tools(tools)
        logger.info("Invoking technical analyst")
        result = chain.invoke(state.messages)
        logger.info(f"Technical analyst result: {result}")

        report = ""
        tools_used = set()
        used_all_tools = False
        if len(result.tool_calls) == 0:
            report = result.content
            logger.info(f"Technical analyst did not use any tools. Report: {report}")
        else:
            logger.info(
                f"Technical analyst used tools. Tool calls: {result.tool_calls}"
            )
            for tool_call in result.tool_calls:
                tools_used.add(tool_call["name"])
            if len(tools_used) == len(tools):
                used_all_tools = True

        return {
            "current_date": current_date,
            "tickers": tickers,
            "messages": [result],
            "tools_used": used_all_tools,
            "news_report": report,
        }

    return technical_analyst_node
