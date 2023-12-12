from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class InfosCustomNamedEntityRecognitionDataClass(NoRaiseBaseModel):
    entity: StrictStr
    category: StrictStr


class CustomNamedEntityRecognitionDataClass(NoRaiseBaseModel):
    items: Sequence[InfosCustomNamedEntityRecognitionDataClass] = Field(
        default_factory=list
    )
