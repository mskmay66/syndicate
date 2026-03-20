from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
import uuid

from .models import ChatState, User
from .llm_clients import create_llm_client
from .tools.relationship_tools import get_reports
from .agents import build_relationship_manager


class ChatGraph:
    def __init__(self, user: User):
        llm = create_llm_client(**user.get_llm_data()).get_llm()
        self.tools = [get_reports]
        self.agent = build_relationship_manager(llm, self.tools)

    def build_graph(self) -> StateGraph:
        """Build the relationship graph based on the selected agents and their corresponding tool nodes.

        Returns:
            Dict[str, ToolNode]: A dictionary mapping agent names to their corresponding nodes in the  relationship graph
        """

        def should_use_tools(state):
            last = state.messages[-1]
            if getattr(last, "tool_calls", None) and not state.used_tools:
                return "tools"
            return "continue"

        workflow = StateGraph(ChatState)
        workflow.add_node("relationship_manager", self.agent)
        workflow.add_edge(START, "relationship_manager")

        workflow.add_node("relationship_tools", ToolNode(tools=self.tools))
        workflow.add_conditional_edges(
            self.agent,
            should_use_tools,
            {
                "tools": "relationship_tools",
                "continue": END,
            },
        )
        return workflow.compile()

    def run(self, initial_state: ChatState):
        graph = self.build_graph()
        return graph.invoke(
            initial_state, config={"recursion_limit": 5, "thread_id": uuid.uuid4()}
        )
