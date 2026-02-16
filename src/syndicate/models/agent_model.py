from pydantic import BaseModel
from typing import Literal


class AgentModel(BaseModel):
    id: int
    name: Literal[
        "Qwen/Qwen2-7B-Instruct",
        "Qwen/Qwen2-7B-Chat",
        "Qwen/Qwen2-7B-VL-Instruct",
        "Qwen/Qwen2-7B-VL-Chat",
        "DeepSeeek-R1-1.5B",
    ]
    temperature: float
