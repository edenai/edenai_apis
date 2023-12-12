from utils.parsing import NoRaiseBaseModel
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr


class Entity(NoRaiseBaseModel):
    type: StrictStr = Field(description="Recognized Entity type")
    text: StrictStr = Field(description="Text corresponding to the entity")
    sentiment: Literal["Positive", "Negative", "Neutral", "Mixed"]
    begin_offset: Optional[StrictInt] = None
    end_offset: Optional[StrictInt] = None


class EntitySentimentDataClass(NoRaiseBaseModel):
    items: List[Entity]
