from pydantic import BaseModel


class PortfolioModel(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str
    tickers: list[str]
