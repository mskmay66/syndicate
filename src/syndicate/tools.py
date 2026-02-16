import os
from datetime import datetime, timedelta
from typing import List
import json
from langchain.tools import tool

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET_KEY = os.getenv("ALPACA_API_SECRET_KEY")
PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

data_client = StockHistoricalDataClient(API_KEY, API_SECRET_KEY)
news_client = NewsClient(API_KEY, API_SECRET_KEY)
trade_client = TradingClient(API_KEY, API_SECRET_KEY, paper=PAPER)


@tool(
    "get_latest_quote",
    return_direct=True,
    description="Get the latest stock quote for a given ticker symbol.",
)
def get_latest_quote(tickers: List[str]) -> str:
    """Gets the latest quote for `ticker`.

    Args:
        ticker (str): The ticker to get a quote for.

    Returns:
        str: The latest quote for `ticker`.
    """
    request_params = StockLatestQuoteRequest(symbol_or_symbols=tickers)
    quote = data_client.get_stock_latest_quote(request_params)
    if quote["status"] != 200:
        return (
            f"Failed to get the latest quote for {tickers}. Reason: {quote['message']}"
        )
    return json.dumps(quote["quotes"], indent=2, default=str)


@tool(
    "get_news",
    return_direct=True,
    description="Get the latest news for a given ticker symbol.",
)
def get_news(tickers: List[str], period: 60) -> str:
    """Gets the latest news for `ticker`.

    Args:
        ticker (str): The ticker to get news for.
        period (int): The number of minutes to look back for news.

    Returns:
        str: The latest news for `ticker`.
    """
    if isinstance(tickers, str):
        tickers = [tickers]

    current_time = datetime.datetime.now()
    start_time = current_time - timedelta(minutes=period)
    news_request = NewsRequest(
        symbols=tickers, start=start_time, end=current_time, limit=50
    )
    news_response = news_client.get_news(news_request)
    if news_response["status"] != 200:
        return f"Failed to get news for {tickers}. Reason: {news_response['message']}"
    return json.dumps(news_response["news"], indent=2, default=str)


def _trade(ticker: str, quantity: str, limit_price: float, side: OrderSide) -> None:
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
    "buy_stock",
    return_direct=True,
    description="Buy a stock for a given ticker symbol and quantity.",
)
def buy_stock(ticker: str, quantity: int, limit_price: float = None) -> str:
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
    description="Sell a stock for a given ticker symbol and quantity.",
)
def sell_stock(ticker: str, quantity: int, limit_price: float = None) -> str:
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
