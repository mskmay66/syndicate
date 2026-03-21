from ..log_config import setup_logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

logger = setup_logging(__name__, "relationship_manager")


def build_relationship_manager(llm, tools):
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
        logger.info("Invoking Relationship manager ")
        result = chain.invoke(state.messages)
        logger.info(f"Relationship manager  result: {result}")
        return {"messages": [result]}

    return relationship_manager_node
