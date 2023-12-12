from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class VideoObjectBoundingBox(NoRaiseBaseModel):
    top: Optional[float]
    left: Optional[float]
    height: Optional[float]
    width: Optional[float]


class ObjectFrame(NoRaiseBaseModel):
    timestamp: float
    bounding_box: VideoObjectBoundingBox


class ObjectTrack(NoRaiseBaseModel):
    description: StrictStr
    confidence: float
    frames: Sequence[ObjectFrame] = Field(default_factory=list)


class ObjectTrackingAsyncDataClass(NoRaiseBaseModel):
    objects: Sequence[ObjectTrack] = Field(default_factory=list)
