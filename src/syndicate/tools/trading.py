import os
import json
from typing import Optional
from langchain_core.tools import tool

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET_KEY = os.getenv("ALPACA_API_SECRET_KEY")
PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

trade_client = TradingClient(API_KEY, API_SECRET_KEY, paper=PAPER)


def _trade(
    ticker: str, quantity: int, limit_price: Optional[float], side: OrderSide
) -> None:
    """Trades stocker for `ticker` and `quantity`.

    Args:
        ticker (str): The ticker to trade.
        quantity (str): The quantity to trade.
        limit_price (float): The limit price for the order. If not provided, a market order will be placed.
        side (OrderSide): The side of the order (BUY or SELL).

    Returns:
        str: A message indicating the result of the trade operation.
    """
    if limit_price:
        order = LimitOrderRequest(
            symbol=ticker,
            qty=quantity,
            limit_price=limit_price,
            side=side,
            time_in_force=TimeInForce.DAY,
        )
    else:
        order = MarketOrderRequest(
            symbol=ticker, qty=quantity, side=side, time_in_force=TimeInForce.DAY
        )
    trade_client.submit_order(order)


@tool(
    "get_account_summary",
    return_direct=True,
    description="Gets the account summary for the current account. Example usage: get_account_summary()",
)
def get_account_summary() -> str:
    """Gets the account summary for the current account.

    Returns:
        str: The account summary for the current account.
    """
    keys_to_extract = [
        "buying_power",
        "cash",
        "equity",
        "last_equity",
        "portfolio_value",
        "long_market_value",
        "short_market_value",
        "initial_margin",
        "maintenance_margin",
        "multiplier",
    ]
    account_summary = trade_client.get_account()
    if not account_summary:
        return f"Failed to get account summary. Reason: {account_summary['message']}"
    status = {k: v for k, v in dict(account_summary).items() if k in keys_to_extract}
    return json.dumps(status, indent=2, default=str)


@tool(
    "buy_stock",
    return_direct=True,
    description="Buys a stock for a given ticker symbol and quantity. If limit_price is not provided, a market order will be placed. Example usage: buy_stock('AAPL', 10) or buy_stock('AAPL', 10, limit_price=150.00)",
)
def buy_stock(ticker: str, quantity: int, limit_price: Optional[float] = None) -> str:
    """Buys a stock for `ticker` and `quantity`.

    Args:
        ticker (str): The ticker to buy.
        quantity (int): The quantity to buy.
        limit_price (float, optional): The limit price for the order. If not provided, a market order will be placed.

    Returns:
        str: A message indicating the result of the buy operation.
    """
    try:
        _trade(ticker, quantity, limit_price, OrderSide.BUY)
        return f"Successfully placed a buy order for {quantity} shares of {ticker}."
    except Exception as e:
        return f"Failed to place a buy order for {ticker}. Reason: {str(e)}"


@tool(
    "sell_stock",
    return_direct=True,
    description="Sells a stock for a given ticker symbol and quantity. If limit_price is not provided, a market order will be placed. Example usage: sell_stock('AAPL', 10) or sell_stock('AAPL', 10, limit_price=150.00)",
)
def sell_stock(ticker: str, quantity: int, limit_price: Optional[float] = None) -> str:
    """Sells a stock for `ticker` and `quantity`.

    Args:
        ticker (str): The ticker to sell.
        quantity (int): The quantity to sell.
        limit_price (float, optional): The limit price for the order. If not provided, a market order will be placed.

    Returns:
        str: A message indicating the result of the sell operation.
    """
    try:
        _trade(ticker, quantity, limit_price, OrderSide.SELL)
        return f"Successfully placed a sell order for {quantity} shares of {ticker}."
    except Exception as e:
        return f"Failed to place a sell order for {ticker}. Reason: {str(e)}"
