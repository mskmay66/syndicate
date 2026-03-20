from pydantic import BaseModel
import operator
from langchain_core.messages import BaseMessage
from typing import Annotated, List


class ChatState(BaseModel):
    messages: Annotated[
        List[BaseMessage],
        "List of messages exchanged in the course of conversation",
        operator.add,
    ]
