from utils.parsing import NoRaiseBaseModel
from typing import Sequence, Optional

from pydantic import BaseModel, StrictStr, Field


class AnonymizationBoundingBox(NoRaiseBaseModel):
    x_min: Optional[float]
    x_max: Optional[float]
    y_min: Optional[float]
    y_max: Optional[float]


class AnonymizationItem(NoRaiseBaseModel):
    kind: StrictStr
    confidence: float
    bounding_boxes: AnonymizationBoundingBox


class AnonymizationDataClass(NoRaiseBaseModel):
    image: StrictStr
    image_resource_url: StrictStr
    items: Sequence[AnonymizationItem] = Field(default_factory=list)
