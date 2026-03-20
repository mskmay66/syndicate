import pytest
from unittest.mock import MagicMock

from syndicate.trading_graph import TradingGraph


# ------------------------
# Dummy State + Message
# ------------------------


class DummyMessage:
    def __init__(self, tool_calls=None):
        self.tool_calls = tool_calls or []


class DummyState:
    def __init__(self):
        self.messages = [DummyMessage()]
        self.used_tools = False


# ------------------------
# Fixtures
# ------------------------


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.get_llm_data.return_value = {}
    return user


@pytest.fixture
def mock_llm():
    return MagicMock()


# ------------------------
# Mock agent node factory
# ------------------------


def make_agent_node(name):
    def node(state):
        return {
            "messages": state.messages + [DummyMessage()],
        }

    return node


# ------------------------
# Patch all dependencies
# ------------------------


@pytest.fixture
def patch_dependencies(mock_llm, monkeypatch):
    # mock LLM creation
    mock_client = MagicMock()
    mock_client.get_llm.return_value = mock_llm

    monkeypatch.setattr(
        "syndicate.trading_graph.create_llm_client",
        lambda **kwargs: mock_client,
    )

    # mock agent builders
    monkeypatch.setattr(
        "syndicate.trading_graph.build_fundementals_analyst",
        lambda llm, tools: make_agent_node("fundementals"),
    )
    monkeypatch.setattr(
        "syndicate.trading_graph.build_news_analyst",
        lambda llm, tools: make_agent_node("news"),
    )
    monkeypatch.setattr(
        "syndicate.trading_graph.build_technical_analyst",
        lambda llm, tools: make_agent_node("technical"),
    )
    monkeypatch.setattr(
        "syndicate.trading_graph.build_trader",
        lambda llm, tools, fn: make_agent_node("trader"),
    )

    # mock tools (avoid real tool execution)
    monkeypatch.setattr(
        "syndicate.trading_graph.FundementalTools",
        lambda user: MagicMock(build_tools=lambda: []),
    )
    monkeypatch.setattr(
        "syndicate.trading_graph.NewsTools",
        lambda user: MagicMock(build_tools=lambda: []),
    )
    monkeypatch.setattr(
        "syndicate.trading_graph.TechnicalTools",
        lambda user: MagicMock(build_tools=lambda: []),
    )
    monkeypatch.setattr(
        "syndicate.trading_graph.TradeTools",
        lambda user: MagicMock(build_tools=lambda: [], take_profits_stop_loss=None),
    )


def test_build_graph(mock_user, patch_dependencies):
    graph = TradingGraph(mock_user)

    compiled = graph.build_graph()

    assert compiled is not None
