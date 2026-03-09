from typing import Dict, List, Callable

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from .models.trade_state import TradeState
from .models.llm import LLMConfig
from .llm_clients import create_llm_client
from .agents import (
    build_fundementals_analyst,
    build_news_analyst,
    build_technical_analyst,
    build_trader,
)
from .tools import (
    get_fundementals,
    get_balance_sheet,
    get_income_statement,
    get_cashflow,
    get_news,
    get_global_news,
    get_latest_quote,
    buy_stock,
    sell_stock,
    get_account_summary,
    get_indicator,
)


class TradingGraph:
    def __init__(
        self,
        llm_config: LLMConfig,
        selected_agents=["news", "fundementals", "technical"],
    ):
        self.llm_config = llm_config
        self.selected_agents = selected_agents
        self.llm = create_llm_client(**self.llm_config.model_dump()).get_llm()

    @property
    def tool_map(self) -> Dict[str, List[Callable]]:
        """Map agent names to their corresponding tools.

        Returns:
            Dict[str, List[Callable]]: A dictionary mapping agent names to their corresponding tools.
        """
        return {
            "fundementals_tools": [
                get_fundementals,
                get_balance_sheet,
                get_income_statement,
                get_cashflow,
            ],
            "news_tools": [
                get_news,
                get_global_news,
            ],
            "technical_tools": [get_indicator, get_latest_quote],
            "trader_tools": [
                get_latest_quote,
                buy_stock,
                sell_stock,
                get_account_summary,
            ],
        }

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for the trading graph based on the selected agents.

        Returns:
            Dict[str, ToolNode]: A dictionary mapping agent names to their corresponding ToolNode instances.
        """
        tools = self.tool_map
        return {
            "fundementals": ToolNode(tools=tools.get("fundementals_tools", [])),
            "news": ToolNode(tools=tools.get("news_tools", [])),
            "technical": ToolNode(tools=tools.get("technical_tools", [])),
            "trader": ToolNode(tools=tools.get("trader_tools", [])),
        }

    def _create_agent_nodes(self) -> Dict[str, ToolNode]:
        """Create agent nodes for the trading graph based on the selected agents and their corresponding tool nodes.

        Args:
            tool_nodes (Dict[str, ToolNode]): A dictionary mapping agent names to their corresponding ToolNode instances.

        Returns:
            Dict[str, ToolNode]: A dictionary mapping agent names to their corresponding agent nodes.
        """
        llm = self.llm
        return {
            "fundementals": build_fundementals_analyst(llm),
            "news": build_news_analyst(llm),
            "technical": build_technical_analyst(llm),
            "trader": build_trader(llm),
        }

    def build_graph(self) -> StateGraph:
        """Build the trading graph based on the selected agents and their corresponding tool nodes.

        Returns:
            Dict[str, ToolNode]: A dictionary mapping agent names to their corresponding nodes in the trading graph.
        """

        def should_use_tools(state):
            last = state.messages[-1]
            if getattr(last, "tool_calls", None) and not state.used_tools:
                return "tools"
            return "continue"

        tool_nodes = self._create_tool_nodes()
        agent_nodes = self._create_agent_nodes()

        workflow = StateGraph(TradeState)
        execution_order = self.selected_agents + ["trader"]
        for agent in execution_order:
            workflow.add_node(agent, agent_nodes[agent])

        for i, agent in enumerate(execution_order):
            is_last = i == len(execution_order) - 1
            next_node = END if is_last else execution_order[i + 1]

            tool_node = tool_nodes.get(agent)
            if tool_node:
                tool_node_name = f"{agent}_tools"
                workflow.add_node(tool_node_name, tool_node)

                workflow.add_conditional_edges(
                    agent,
                    should_use_tools,
                    {
                        "tools": tool_node_name,
                        "continue": next_node,
                    },
                )

                workflow.add_edge(tool_node_name, agent)
            else:
                workflow.add_edge(agent, next_node)

        workflow.add_edge(START, self.selected_agents[0])
        return workflow.compile()

    def run(self, initial_state: TradeState):
        """Run the trading graph with the given initial state.

        Args:
            initial_state (TradeState): The initial state to run the trading graph with.

        Returns:
            TradeState: The final state after running the trading graph.
        """
        graph = self.build_graph()
        return graph.invoke(initial_state, config={"recursion_limit": 50})
