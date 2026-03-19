import pytest
import json
from syndicate.tools import TradeTools, MaxConcetrationError
from unittest.mock import MagicMock
from alpaca.trading.enums import OrderSide, PositionSide
from datetime import datetime


def test_get_account_summary_serializes_non_json_types():
    user = MagicMock()
    trader = TradeTools(user)

    mock_account = {
        "equity": 1000,
        "cash": datetime(2024, 1, 1),  # not JSON serializable normally
    }

    trader.trade_client = MagicMock()
    trader.trade_client.get_account.return_value = mock_account

    result = trader._get_account_summary()
    parsed = json.loads(result)

    assert isinstance(parsed["cash"], str)


def test_get_account_summary_parses_expected_keys():
    user = MagicMock()
    trader = TradeTools(user)

    mock_account = {
        "buying_power": 1000,
        "cash": 500,
        "equity": 1500,
        "last_equity": 1400,
        "long_market_value": 1200,
        "short_market_value": 0,
        "initial_margin": 100,
        "maintenance_margin": 50,
        "multiplier": 2,
        "extra_field": "should_not_be_included",
    }

    trader.trade_client = MagicMock()
    trader.trade_client.get_account.return_value = mock_account

    result = trader._get_account_summary()

    parsed = json.loads(result)

    assert set(parsed.keys()) == {
        "buying_power",
        "cash",
        "equity",
        "last_equity",
        "long_market_value",
        "short_market_value",
        "initial_margin",
        "maintenance_margin",
        "multiplier",
    }

    assert parsed["equity"] == 1500
    assert "extra_field" not in parsed


def test_take_profits():
    trader = MagicMock()

    # Mock user + guardrails
    trader.user.guardrails.take_profit = 0.05
    trader.user.guardrails.stop_loss = 0.05
    trader.user.watchlist = ["AAPL"]

    # Mock position
    mock_position = MagicMock()
    mock_position.unrealized_plpc = 0.10  # 10% profit
    mock_position.side = PositionSide.LONG
    mock_position.qty = 10

    trader.trade_client.get_open_position.return_value = mock_position

    # Mock _trade
    trader._trade = MagicMock()

    # Call function
    TradeTools.take_profits_stop_loss(trader)

    # Assert trade executed
    trader._trade.assert_called_once_with("AAPL", 10, OrderSide.SELL)


def test_stop_loss():
    trader = MagicMock()

    # Mock user + guardrails
    trader.user.guardrails.take_profit = 0.05
    trader.user.guardrails.stop_loss = 0.25
    trader.user.watchlist = ["AAPL"]

    # Mock position
    mock_position = MagicMock()
    mock_position.unrealized_plpc = 0.3  # 10% profit
    mock_position.side = PositionSide.LONG
    mock_position.qty = 10

    trader.trade_client.get_open_position.return_value = mock_position

    # Mock _trade
    trader._trade = MagicMock()

    # Call function
    TradeTools.take_profits_stop_loss(trader)

    # Assert trade executed
    trader._trade.assert_called_once_with("AAPL", 10, OrderSide.SELL)


def test_trade_blocked_by_max_concentration():
    user = MagicMock()
    user.guardrails.max_concentration = 0.1  # 10%
    trader = TradeTools(user)

    # Mock account summary (portfolio value)
    trader._get_account_summary = MagicMock(return_value=json.dumps({"equity": 1000}))

    # Mock current position (already large)
    mock_position = MagicMock()
    mock_position.market_value = 900  # already 90% of portfolio

    trader.trade_client = MagicMock()
    trader.trade_client.get_open_position.return_value = mock_position

    # Spy on submit_order
    trader.trade_client.submit_order = MagicMock()

    # Act + Assert
    with pytest.raises(MaxConcetrationError):
        trader._trade(
            ticker="AAPL",
            quantity=10,
            limit_price=20,  # adds 200 more → exceeds concentration
            side=OrderSide.BUY,
        )

    trader.trade_client.submit_order.assert_not_called()


def test_trade_allowed_under_max_concentration():
    user = MagicMock()
    user.guardrails.max_concentration = 0.5  # 50%
    trader = TradeTools(user)

    trader._get_account_summary = MagicMock(return_value=json.dumps({"equity": 1000}))

    mock_position = MagicMock()
    mock_position.market_value = 100

    trader.trade_client = MagicMock()
    trader.trade_client.get_open_position.return_value = mock_position
    trader.trade_client.submit_order = MagicMock()

    trader._trade(
        ticker="AAPL",
        quantity=10,
        limit_price=10,  # +100 → total 200 (20% of portfolio)
        side=OrderSide.BUY,
    )

    trader.trade_client.submit_order.assert_called_once()
