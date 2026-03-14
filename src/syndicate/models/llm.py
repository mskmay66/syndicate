from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict


class LLMConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    provider: Annotated[
        str, "The LLM provider (e.g., 'openai', 'anthropic', 'gemini', 'qwen')"
    ]
    model: Annotated[str, "The specific model name to use (e.g., 'gpt-4', 'claude-2')"]
    base_url: Optional[str] = None
    # api_key: Optional[str] = None
