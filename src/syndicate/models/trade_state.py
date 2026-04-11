from typing import Annotated, Optional, List
from pydantic import BaseModel
import operator
from langchain_core.messages import BaseMessage


class TradeState(BaseModel):
    """The pydantic model representing the state of a trading decision, including the stock tickers involved, the current date, and any reports or messages related to the trade."""

    tickers: Annotated[list[str], "List of stock tickers involved in the trade"]
    current_date: str
    fundementals_report: Optional[str] = None
    news_report: Optional[str] = None
    trade_report: Optional[str] = None
    used_tools: bool = False
    messages: Annotated[
        List[BaseMessage],
        "List of messages exchanged in the trading process",
        operator.add,
    ]
