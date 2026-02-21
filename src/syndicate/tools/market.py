import os
import json
from typing import List

from langchain_core.tools import tool
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET_KEY = os.getenv("ALPACA_API_SECRET_KEY")

data_client = StockHistoricalDataClient(API_KEY, API_SECRET_KEY)


@tool(
    "get_latest_quote",
    return_direct=True,
    description="Gets the latest quote for a given ticker or list of tickers. Example usage: get_latest_quote('AAPL') or get_latest_quote(['AAPL', 'GOOG'])",
)
def get_latest_quote(tickers: List[str]) -> str:
    if isinstance(tickers, str):
        tickers = [tickers]
    request_params = StockLatestQuoteRequest(symbol_or_symbols=tickers)
    quote = data_client.get_stock_latest_quote(request_params)
    if not quote:
        return (
            f"Failed to get the latest quote for {tickers}. Reason: {quote['message']}"
        )
    return json.dumps(quote, indent=2, default=str)
