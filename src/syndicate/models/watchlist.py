from pydantic import BaseModel, ConfigDict


class Watchlist(BaseModel):
    model_config = ConfigDict(extra="allow")
    tickers: list[str]
