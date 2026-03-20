from ..log_config import setup_logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

logger = setup_logging(__name__, "relationship_manager")


def build_relationship_manager(llm, tools):
    store = {}

    def get_session_history(session_id: str):
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    def relationship_manager_node(state):
        system_prompt = "You are a financial relationship manager. Your task is to interact with clients, answer their questions regarding their portfolio, and explain actions that other members of the traiding team take."

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_prompt)
        prompt = prompt.partial(tool_names=tools)

        chain = prompt | llm.bind_tools(tools)
        with_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

        logger.info("Invoking Relationship manager ")
        result = with_history.invoke(state.messages)
        logger.info(f"Relationship manager  result: {result}")

        tools_used = False
        if tools_used:
            report = result.content
            logger.info(f"Report: {report}")
        else:
            logger.info(
                f"Relationship manager used tools. Tool calls: {result.tool_calls}"
            )
        return {"messages": [result]}

    return relationship_manager_node
