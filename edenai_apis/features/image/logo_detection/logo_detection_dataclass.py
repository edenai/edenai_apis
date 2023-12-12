from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class LogoVertice(NoRaiseBaseModel):
    x: Optional[float]
    y: Optional[float]


class LogoBoundingPoly(NoRaiseBaseModel):
    vertices: Sequence[LogoVertice]


class LogoItem(NoRaiseBaseModel):
    bounding_poly: Optional[LogoBoundingPoly]
    description: Optional[StrictStr]
    score: Optional[float]


class LogoDetectionDataClass(NoRaiseBaseModel):
    items: Sequence[LogoItem] = Field(default_factory=list)
