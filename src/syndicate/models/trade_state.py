from typing import Annotated, Optional
from pydantic import BaseModel
import operator
from langchain_core.messages import BaseMessage


class TradeState(BaseModel):
    tickers: Annotated[list[str], "List of stock tickers involved in the trade"]
    current_date: str
    fundementals_report: Optional[str] = None
    news_report: Optional[str] = None
    messages: Annotated[
        list[BaseMessage],
        "List of messages exchanged in the trading process",
        operator.add,
    ]
