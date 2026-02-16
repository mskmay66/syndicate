from pydantic import BaseModel


class PortfolioModel(BaseModel):
    name: str
    created_at: str
    updated_at: str
    tickers: list[str]
