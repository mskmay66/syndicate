from pydantic import BaseModel, SecretStr
from typing import List


class User(BaseModel):
    model_provider: str
    model_name: str
    watchlist: List[str]
    broker_api_key: SecretStr
    broker_secret_key: SecretStr
    model_api_key: SecretStr
    alpha_vantage_api_key: SecretStr
    cron: str
    guardrails: dict[str, float]

    def to_json(self) -> str:
        """Convert the User object to a JSON string."""
        values = {k: v for k, v in self.model_dump().items() if "key" not in k}
        return str(values)

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
