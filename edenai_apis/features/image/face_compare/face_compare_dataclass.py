from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field


class FaceCompareBoundingBox(NoRaiseBaseModel):
    top: Optional[float]
    left: Optional[float]
    height: Optional[float]
    width: Optional[float]


class FaceMatch(NoRaiseBaseModel):
    confidence: Optional[float]
    bounding_box: FaceCompareBoundingBox


class FaceCompareDataClass(NoRaiseBaseModel):
    items: Sequence[FaceMatch] = Field(default_factory=list)
