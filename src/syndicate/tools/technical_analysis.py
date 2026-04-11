import httpx
from langchain_core.tools import tool
from ..models import User


class TechnicalTools:
    """A set of tools for fetching technical indicator data from the Alpha Vantage API."""

    BASE_URI = "https://www.alphavantage.co/query"

    def __init__(self, user: User) -> None:
        self.user = user
        self.client = httpx.Client(base_url=self.BASE_URI)

    def get_technical_indicator(
        self, symbol: str, indicator: str, interval: str = "daily"
    ) -> dict:
        """Fetch technical indicator data for a given stock symbol.

        Args:
            symbol (str): The stock symbol to fetch data for (e.g., 'AAPL').
            indicator (str): The technical indicator to fetch (e.g., 'close_50_sma').
            interval (str): The time interval for the data (e.g., 'daily', 'weekly', 'monthly'). Default is 'daily'.

        Returns:
            dict: The technical indicator data returned by the Alpha Vantage API, or an error message if the request fails.
        """
        try:
            params = {
                "function": indicator,
                "symbol": symbol,
                "interval": interval,
                "apikey": self.user.alpha_vantage_api_key.get_secret_value(),
            }
            response = self.client.get("", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"HTTP error occurred: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def build_tools(self):
        @tool(
            "get_indicator",
            return_direct=True,
            description=(
                "Gets technical indicator data for a given stock symbol. "
                "Supported indicators include: close_50_sma, close_200_sma, close_10_ema, macd, macds, macdh, rsi, boll, boll_ub, boll_lb, atr, vwma. "
                "Example usage: get_indicator('AAPL', 'close_50_sma')"
            ),
        )
        def get_indicator(symbol: str, indicator: str, interval: str = "daily") -> str:
            """Tool to get technical indicator data for a stock symbol.

            Args:
                symbol (str): The stock symbol to fetch data for (e.g., 'AAPL').
                indicator (str): The technical indicator to fetch. Supported indicators include: close_50_sma, close_200_sma, close_10_ema, macd, macds, macdh, rsi, boll, boll_ub, boll_lb, atr, vwma.
                interval (str): The time interval for the data (e.g., 'daily', 'weekly', 'monthly'). Default is 'daily'.

            Returns:
                str: The technical indicator data in JSON format, or an error message if the request fails.
            """
            supported_indicators = {
                "close_50_sma": ("50 SMA", "close"),
                "close_200_sma": ("200 SMA", "close"),
                "close_10_ema": ("10 EMA", "close"),
                "macd": ("MACD", "close"),
                "macds": ("MACD Signal", "close"),
                "macdh": ("MACD Histogram", "close"),
                "rsi": ("RSI", "close"),
                "boll": ("Bollinger Middle", "close"),
                "boll_ub": ("Bollinger Upper Band", "close"),
                "boll_lb": ("Bollinger Lower Band", "close"),
                "atr": ("ATR", None),
                "vwma": ("VWMA", "close"),
            }

            if indicator not in supported_indicators:
                raise ValueError(
                    f"Indicator {indicator} is not supported. Please choose from: {list(supported_indicators.keys())}"
                )

            data = self.get_technical_indicator(symbol, indicator, interval)
            return str(data)

        return [get_indicator]
