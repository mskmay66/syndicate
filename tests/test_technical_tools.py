import pytest
from syndicate.tools import TechnicalTools

from unittest.mock import MagicMock
import httpx


class DummyUser:
    def __init__(self, api_key="test_key"):
        self.alpha_vantage_api_key = MagicMock()
        self.alpha_vantage_api_key.get_secret_value.return_value = api_key


def test_get_technical_indicator_success():
    user = DummyUser()
    tools = TechnicalTools(user)

    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "ok"}
    mock_response.raise_for_status.return_value = None

    tools.client.get = MagicMock(return_value=mock_response)

    result = tools.get_technical_indicator("AAPL", "rsi")

    assert result == {"data": "ok"}
    tools.client.get.assert_called_once()


def test_get_technical_indicator_http_error():
    user = DummyUser()
    tools = TechnicalTools(user)

    tools.client.get = MagicMock(side_effect=httpx.HTTPError("boom"))

    result = tools.get_technical_indicator("AAPL", "rsi")

    assert "error" in result
    assert "HTTP error occurred" in result["error"]


def test_get_technical_indicator_generic_error():
    user = DummyUser()
    tools = TechnicalTools(user)

    tools.client.get = MagicMock(side_effect=Exception("unexpected"))

    result = tools.get_technical_indicator("AAPL", "rsi")

    assert "error" in result
    assert "An error occurred" in result["error"]


def test_get_indicator_tool_valid():
    user = DummyUser()
    tools = TechnicalTools(user)

    tools.get_technical_indicator = MagicMock(return_value={"value": 42})

    tool_fn = tools.build_tools()[0].func

    result = tool_fn("AAPL", "rsi")

    assert result == str({"value": 42})
    tools.get_technical_indicator.assert_called_once_with("AAPL", "rsi", "daily")


def test_get_indicator_tool_invalid_indicator():
    user = DummyUser()
    tools = TechnicalTools(user)

    tool_fn = tools.build_tools()[0].func

    with pytest.raises(ValueError) as exc:
        tool_fn("AAPL", "not_real_indicator")

    assert "not supported" in str(exc.value)


def test_get_indicator_tool_custom_interval():
    user = DummyUser()
    tools = TechnicalTools(user)

    tools.get_technical_indicator = MagicMock(return_value={"value": 1})

    tool_fn = tools.build_tools()[0].func

    tool_fn("AAPL", "rsi", interval="weekly")

    tools.get_technical_indicator.assert_called_once_with("AAPL", "rsi", "weekly")


def test_get_technical_indicator_params():
    user = DummyUser(api_key="abc123")
    tools = TechnicalTools(user)

    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None

    tools.client.get = MagicMock(return_value=mock_response)

    tools.get_technical_indicator("AAPL", "rsi", "weekly")

    _, kwargs = tools.client.get.call_args

    assert kwargs["params"]["symbol"] == "AAPL"
    assert kwargs["params"]["function"] == "rsi"
    assert kwargs["params"]["interval"] == "weekly"
    assert kwargs["params"]["apikey"] == "abc123"
