from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class LandmarkVertice(NoRaiseBaseModel):
    x: int
    y: int


class LandmarkLatLng(NoRaiseBaseModel):
    latitude: float
    longitude: float


class LandmarkLocation(NoRaiseBaseModel):
    lat_lng: LandmarkLatLng


class LandmarkItem(NoRaiseBaseModel):
    description: StrictStr
    confidence: float
    bounding_box: Sequence[LandmarkVertice] = Field(default_factory=list)
    locations: Sequence[LandmarkLocation] = Field(default_factory=list)


class LandmarkDetectionDataClass(NoRaiseBaseModel):
    items: Sequence[LandmarkItem] = Field(default_factory=list)
