from pydantic import BaseModel
import operator
from langchain_core.messages import BaseMessage
from typing import Annotated, List


class ChatState(BaseModel):
    """The pydantic model representing the state of a conversation, including the messages exchanged between the user and the LLM."""

    messages: Annotated[
        List[BaseMessage],
        "List of messages exchanged in the course of conversation",
        operator.add,
    ]
