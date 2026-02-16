from pydantic import BaseModel
from typing import Literal, Optional


class AgentModel(BaseModel):
    name: Optional[
        Literal[
            "Qwen/Qwen2-7B-Instruct",
            "Qwen/Qwen2-7B-Chat",
            "Qwen/Qwen2-7B-VL-Instruct",
            "Qwen/Qwen2-7B-VL-Chat",
            "DeepSeeek-R1-1.5B",
        ]
    ] = None
    local_path: Optional[str] = None
    temperature: float = 0.7
