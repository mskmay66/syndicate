import httpx
from langchain_core.tools import tool
from ..secrets import get_secret_from_keyring


class AlphaVantageInterface:
    BASE_URI = "https://www.alphavantage.co/query"

    def __init__(self):
        self.api_key = self.get_api_key()
        self.client = httpx.Client(base_url=self.BASE_URI)

    def get_api_key(self) -> str:
        """Get the Alpha Vantage API key from environment variable."""
        api_key = get_secret_from_keyring("alpha_vantage_api_key")
        if not api_key:
            raise ValueError(
                "Alpha Vantage API key not found in environment variable 'ALPHA_VANTAGE_API_KEY'."
            )
        return api_key

    def get_technical_indicator(
        self, symbol: str, indicator: str, interval: str = "daily"
    ) -> dict:
        """Fetch technical indicator data for a given stock symbol."""
        try:
            params = {
                "function": indicator,
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
            }
            response = self.client.get("", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"HTTP error occurred: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}


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
    """Tool to get technical indicator data for a stock symbol."""
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

    if get_secret_from_keyring("alpha_vantage_api_key") is None:
        return "Alpha Vantage API key not found. Please set the 'ALPHA_VANTAGE_API_KEY' environment variable to use this tool."

    interface = AlphaVantageInterface()

    if indicator not in supported_indicators:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(supported_indicators.keys())}"
        )

    data = interface.get_technical_indicator(symbol, indicator, interval)
    return str(data)
