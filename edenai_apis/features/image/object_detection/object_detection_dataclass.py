from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, StrictStr, Field


class ObjectItem(NoRaiseBaseModel):
    label: StrictStr
    confidence: float
    x_min: Optional[float]
    x_max: Optional[float]
    y_min: Optional[float]
    y_max: Optional[float]


class ObjectDetectionDataClass(NoRaiseBaseModel):
    items: Sequence[ObjectItem] = Field(default_factory=list)
