import os
import json
import functools
from typing import Optional
from langchain_core.tools import tool

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from ..secrets import get_secret_from_keyring
from ..file_manager import read_config_file

API_KEY = get_secret_from_keyring("broker_api_key")
API_SECRET_KEY = get_secret_from_keyring("broker_secret_key")

guardrails_config = {}
if os.path.exists("guardrails.json"):
    guardrails_config = read_config_file("guardrails.json")

MAX_PURCHASE = guardrails_config.get(
    "max_purchase_amount"
)  # Default to 10% of buying power
MIN_CASH = guardrails_config.get(
    "min_cash_required"
)  # Default to 10% of portfolio value
MAX_LOSS = guardrails_config.get("max_loss_percentage")  # Default to 10% loss
TAKE_PROFIT = guardrails_config.get("take_profit_percentage")  # Default to 10% profit
PAPER = guardrails_config.get("paper_trading", True)  # Default to paper trading mode

WATCHLIST = read_config_file("watchlist.json").get(
    "tickers", []
)  # List of tickers to watch for trading opportunities

trade_client = None
if API_KEY and API_SECRET_KEY:
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
    if not trade_client:
        raise Exception(
            "Alpaca API key and secret key are required to use this tool. Please set the ALPACA_API_KEY and ALPACA_API_SECRET_KEY environment variables."
        )
    trade_client.submit_order(order)


def _get_account_summary() -> str:
    """Gets the account summary for the current account.

    Returns:
        dict: The account summary for the current account.
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
    if not trade_client:
        return "Alpaca API key and secret key are required to use this tool. Please set the ALPACA_API_KEY and ALPACA_API_SECRET_KEY environment variables."

    account_summary = trade_client.get_account()
    if not account_summary:
        return f"Failed to get account summary. Reason: {account_summary['message']}"
    status = {k: v for k, v in dict(account_summary).items() if k in keys_to_extract}
    return json.dumps(status, indent=2, default=str)


def max_purchase_amount(allowed_pct: Optional[float]):
    def innner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if allowed_pct:
                account_summary = _get_account_summary()
                buying_power = account_summary.get("buying_power", 0)
                max_purchase = buying_power * allowed_pct
                if args["quantity"] * args["limit_price"] > max_purchase:
                    args["quantity"] = int(max_purchase / args["limit_price"])
            return func(*args, **kwargs)

        return wrapper

    return innner


def min_cash_required(cash_pct: Optional[float]):
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            account_summary = _get_account_summary()
            cash = account_summary.get("cash", 0)
            port_value = account_summary.get("portfolio_value", 0)
            if cash_pct is None or cash > port_value * cash_pct:
                return func(*args, **kwargs)
            else:
                return f"Not enough cash available to place the order. Minimum required cash is {cash_pct * 100}% of portfolio value."

        return wrapper

    return inner


def validate_limit_price(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        limit_price = kwargs.get("limit_price")
        if limit_price is not None and limit_price <= 0:
            return "Limit price must be a positive number."
        return func(*args, **kwargs)

    return wrapper


def validate_watchlist(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ticker = args[0]  # Assuming ticker is the first argument
        if ticker not in WATCHLIST:
            return f"Ticker not in watchlist. Please choose from: {WATCHLIST}"
        return func(*args, **kwargs)

    return wrapper


def max_loss():
    if not MAX_LOSS:
        return

    for ticker in WATCHLIST:
        position = trade_client.get_open_position(ticker)
        percentage_loss = float(position.unrealized_plpc)
        if percentage_loss < MAX_LOSS:
            # Logic to sell the position to prevent further losses
            quantity = int(position.qty)
            _trade(ticker, quantity, None, OrderSide.SELL)


def take_profit():
    if not TAKE_PROFIT:
        return

    for ticker in WATCHLIST:
        position = trade_client.get_open_position(ticker)
        percentage_gain = float(position.unrealized_plpc)
        if percentage_gain > TAKE_PROFIT:
            # Logic to sell the position to take profits
            quantity = int(position.qty)
            _trade(ticker, quantity, None, OrderSide.SELL)


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
    return _get_account_summary()


@tool(
    "buy_stock",
    return_direct=True,
    description="Buys a stock for a given ticker symbol and quantity. If limit_price is not provided, a market order will be placed. Example usage: buy_stock('AAPL', 10) or buy_stock('AAPL', 10, limit_price=150.00)",
)
@min_cash_required(MIN_CASH)
@max_purchase_amount(MAX_PURCHASE)
@validate_limit_price
@validate_watchlist
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
@validate_limit_price
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
