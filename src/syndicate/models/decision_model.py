from pydantic import BaseModel, Field


class DecisionModel(BaseModel):
    direction: str = Field(
        ..., description="The direction of the trade, either 'buy' or 'sell'"
    )
    ticker: str = Field(..., description="The ticker symbol of the stock to trade")
    quantity: int = Field(..., description="The quantity of shares to trade")
