from ..log_config import setup_logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


logger = setup_logging(__name__, "news_analyst")


def build_news_analyst(llm, tools):
    """This agent will analyze the latest news articles related to the stocks in the portfolio and provide insights that can help inform trading decisions. It will use the provided tools to gather and analyze data, and then generate a report with its findings.

    Args:
        llm: The language model to use for generating insights and reports.
        tools: The tools available for the news analyst to use in its analysis.

    Returns:
        A function that takes the current state of the trading process and returns an updated state with the news analysis report and information about which tools were used.
    """

    def news_analyst_node(state):
        current_date = state.current_date
        tickers = state.tickers

        system_prompt = "You are a financial news analyst. Your task is to analyze the latest news articles related to the stocks in the portfolio and provide insights that can help inform trading decisions."

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
                    f"For your reference, the current date is {current_date}. We are looking at the following companies {','.join(tickers)}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_prompt)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

        chain = prompt | llm.bind_tools(tools)
        logger.info("Invoking news analyst")
        result = chain.invoke(state.messages)
        logger.info(f"News analyst result: {result}")

        report = ""
        used_all_tools = False
        tools_used = set()
        if len(result.tool_calls) == 0:
            report = result.content
            logger.info(f"Report: {report}")
        else:
            logger.info(f"News analyst used tools. Tool calls: {result.tool_calls}")
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

    return news_analyst_node
