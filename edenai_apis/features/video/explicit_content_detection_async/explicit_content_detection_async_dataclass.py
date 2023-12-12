from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class ContentNSFW(NoRaiseBaseModel):
    timestamp: float
    confidence: float
    category: StrictStr


class ExplicitContentDetectionAsyncDataClass(NoRaiseBaseModel):
    moderation: Sequence[ContentNSFW] = Field(default_factory=list)
