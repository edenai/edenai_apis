from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class InfosNamedEntityRecognitionDataClass(NoRaiseBaseModel):
    entity: StrictStr
    category: Optional[StrictStr]
    importance: Optional[float]


class NamedEntityRecognitionDataClass(NoRaiseBaseModel):
    items: Sequence[InfosNamedEntityRecognitionDataClass] = Field(default_factory=list)
