import json
from typing import Optional, List
from langchain_core.tools import tool
import functools
import inspect

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

from ..models import User


class TradeTools:
    def __init__(self, user: User) -> None:
        self.user = user
        self.trade_client = TradingClient(
            user.broker_api_key.get_secret_value(),
            user.broker_secret_key.get_secret_value(),
            paper=True,
        )
        self.data_client = StockHistoricalDataClient(
            user.broker_api_key.get_secret_value(),
            user.broker_secret_key.get_secret_value(),
        )

    @staticmethod
    def max_concentration(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            buying_power = json.load(self._get_account_summary()).get("buying_power", 0)
            sig = inspect.signature(func)
            try:
                bound_args = sig.bind(*args, **kwargs)
            except TypeError as te:
                raise TypeError(f"Error when calling {func.__name__}: {te}") from te

            if "quantity" not in bound_args:
                raise ValueError("quantity not found in arguments to function")

            quantity = bound_args.arguments.get("quantity")
            limit_price = bound_args.arguments.get("limit_price")
            max_conc = self.user.guardrails.max_concentration
            if (buying_power * max_conc) > (quantity * limit_price):
                return func(*args, **kwargs)

        return wrapper

    @max_concentration
    def _trade(
        self, ticker: str, quantity: int, limit_price: Optional[float], side: OrderSide
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
        self.trade_client.submit_order(order)

    def _get_account_summary(self) -> str:
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

        account_summary = self.trade_client.get_account()
        if not account_summary:
            return (
                f"Failed to get account summary. Reason: {account_summary['message']}"
            )
        status = {
            k: v for k, v in dict(account_summary).items() if k in keys_to_extract
        }
        return json.dumps(status, indent=2, default=str)

    def build_tools(self):
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
            return self._get_account_summary()

        @tool(
            "get_latest_quote",
            return_direct=True,
            description="Gets the latest quote for a given ticker or list of tickers. Example usage: get_latest_quote('AAPL') or get_latest_quote(['AAPL', 'GOOG'])",
        )
        def get_latest_quote(tickers: List[str]) -> str:
            if isinstance(tickers, str):
                tickers = [tickers]
            request_params = StockLatestQuoteRequest(symbol_or_symbols=tickers)
            quote = self.data_client.get_stock_latest_quote(request_params)
            if not quote:
                return f"Failed to get the latest quote for {tickers}. Reason: {quote['message']}"
            return json.dumps(quote, indent=2, default=str)

        @tool(
            "buy_stock",
            return_direct=True,
            description="Buys a stock for a given ticker symbol and quantity. If limit_price is not provided, a market order will be placed. Example usage: buy_stock('AAPL', 10) or buy_stock('AAPL', 10, limit_price=150.00)",
        )
        def buy_stock(
            ticker: str, quantity: int, limit_price: Optional[float] = None
        ) -> str:
            """Buys a stock for `ticker` and `quantity`.

            Args:
                ticker (str): The ticker to buy.
                quantity (int): The quantity to buy.
                limit_price (float, optional): The limit price for the order. If not provided, a market order will be placed.

            Returns:
                str: A message indicating the result of the buy operation.
            """
            try:
                self._trade(ticker, quantity, limit_price, OrderSide.BUY)
                return f"Successfully placed a buy order for {quantity} shares of {ticker}."
            except Exception as e:
                return f"Failed to place a buy order for {ticker}. Reason: {str(e)}"

        @tool(
            "sell_stock",
            return_direct=True,
            description="Sells a stock for a given ticker symbol and quantity. If limit_price is not provided, a market order will be placed. Example usage: sell_stock('AAPL', 10) or sell_stock('AAPL', 10, limit_price=150.00)",
        )
        def sell_stock(
            ticker: str, quantity: int, limit_price: Optional[float] = None
        ) -> str:
            """Sells a stock for `ticker` and `quantity`.

            Args:
                ticker (str): The ticker to sell.
                quantity (int): The quantity to sell.
                limit_price (float, optional): The limit price for the order. If not provided, a market order will be placed.

            Returns:
                str: A message indicating the result of the sell operation.
            """
            try:
                self._trade(ticker, quantity, limit_price, OrderSide.SELL)
                return f"Successfully placed a sell order for {quantity} shares of {ticker}."
            except Exception as e:
                return f"Failed to place a sell order for {ticker}. Reason: {str(e)}"

        return [get_account_summary, get_latest_quote, buy_stock, sell_stock]
