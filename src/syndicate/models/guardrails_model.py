from pydantic import BaseModel, ConfigDict
from typing import Optional


class GuardrailsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    max_loss: Optional[float] = None
    take_profit: Optional[float] = None
    max_pos_size: Optional[float] = None
