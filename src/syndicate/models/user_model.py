from pydantic import BaseModel, SecretStr
from typing import List, Dict


class GuardRails(BaseModel):
    max_concentration: float
    stop_loss: float
    take_profit: float


class User(BaseModel):
    model_provider: str
    model_name: str
    watchlist: List[str]
    broker_api_key: SecretStr
    broker_secret_key: SecretStr
    model_api_key: SecretStr
    alpha_vantage_api_key: SecretStr
    cron: str
    guardrails: GuardRails
    paper: bool = False

    def to_json(self) -> Dict:
        """Convert the User object to a JSON string."""
        return {k: v for k, v in self.model_dump().items() if "key" not in k}

    def get_llm_data(self) -> dict:
        """Get the LLM configuration data."""
        return {
            "provider": self.model_provider,
            "model": self.model_name,
            "api_key": self.model_api_key.get_secret_value(),
        }

    def get_secrets(self) -> dict:
        """Get the secrets for the user."""
        return {
            "broker_api_key": self.broker_api_key.get_secret_value(),
            "broker_secret_key": self.broker_secret_key.get_secret_value(),
            "model_api_key": self.model_api_key.get_secret_value(),
            "alpha_vantage_api_key": self.alpha_vantage_api_key.get_secret_value(),
        }
