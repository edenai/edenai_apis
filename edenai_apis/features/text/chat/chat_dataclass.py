from utils.parsing import NoRaiseBaseModel
from typing import Dict, Generator, Optional, Sequence

from pydantic import BaseModel, StrictStr, Field


class ChatMessageDataClass(NoRaiseBaseModel):
    role: Optional[StrictStr]
    message: Optional[StrictStr]


class ChatDataClass(NoRaiseBaseModel):
    generated_text: StrictStr
    message: Sequence[ChatMessageDataClass] = Field(default_factory=list)

    @staticmethod
    def direct_response(api_response: Dict):
        return api_response["generated_text"]

class ChatStreamResponse(NoRaiseBaseModel):
    text: str
    blocked: bool
    provider: str
    
class StreamChat(NoRaiseBaseModel):
    stream: Generator[ChatStreamResponse, None, None]
