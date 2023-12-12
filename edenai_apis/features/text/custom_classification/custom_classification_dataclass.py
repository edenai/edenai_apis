from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class ItemCustomClassificationDataClass(NoRaiseBaseModel):
    input: StrictStr
    label: StrictStr
    confidence: float


class CustomClassificationDataClass(NoRaiseBaseModel):
    classifications: Sequence[ItemCustomClassificationDataClass] = Field(
        default_factory=list
    )
