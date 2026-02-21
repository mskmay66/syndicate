from typing import Dict

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from .models.trade_state import TradeState
from .models.llm import LLMConfig
from .llm_clients import create_llm_client
from .agents import build_fundementals_analyst, build_news_analyst, build_trader
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
)


class TradingGraph:
    def __init__(self, llm_config: LLMConfig, selected_agents=["news", "fundementals"]):
        self.llm_config = llm_config
        self.selected_agents = selected_agents
        self.llm = create_llm_client(**self.llm_config)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for the trading graph based on the selected agents.

        Returns:
            Dict[str, ToolNode]: A dictionary mapping agent names to their corresponding ToolNode instances.
        """
        return {
            "fundementals": ToolNode(
                [
                    get_fundementals,
                    get_balance_sheet,
                    get_income_statement,
                    get_cashflow,
                ]
            ),
            "news": ToolNode(
                [
                    get_news,
                    get_global_news,
                ]
            ),
            "trader": ToolNode(
                [
                    get_latest_quote,
                    buy_stock,
                    sell_stock,
                    get_account_summary,
                ]
            ),
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
            "trader": build_trader(llm),
        }

    def build_graph(self) -> StateGraph:
        """Build the trading graph based on the selected agents and their corresponding tool nodes.

        Returns:
            Dict[str, ToolNode]: A dictionary mapping agent names to their corresponding nodes in the trading graph.
        """
        tool_nodes = self._create_tool_nodes()
        agent_nodes = self._create_agent_nodes()

        workflow = StateGraph(TradeState)
        for agent in self.selected_agents + ["trader"]:
            workflow.add_node(agent, agent_nodes[agent])

            # add tools
            for tool in tool_nodes[agent]:
                workflow.add_node(tool.name, tool)
                workflow.add_edge(agent, tool.name)

        workflow.add_edge(START, self.selected_agents[0])
        for i in range(len(self.selected_agents) - 1):
            workflow.add_edge(self.selected_agents[i], self.selected_agents[i + 1])

        workflow.add_edge(self.selected_agents[-1], "trader")
        workflow.add_edge("trader", END)
        return workflow.compile()

    def run(self, initial_state: TradeState):
        """Run the trading graph with the given initial state.

        Args:
            initial_state (TradeState): The initial state to run the trading graph with.

        Returns:
            TradeState: The final state after running the trading graph.
        """
        graph = self.build_graph()
        return graph.invoke(initial_state)
