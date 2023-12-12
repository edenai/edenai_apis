from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class VideoLogoBoundingBox(NoRaiseBaseModel):
    top: Optional[float]
    left: Optional[float]
    height: Optional[float]
    width: Optional[float]


class VideoLogo(NoRaiseBaseModel):
    timestamp: float
    bounding_box: VideoLogoBoundingBox
    confidence: Optional[float]


class LogoTrack(NoRaiseBaseModel):
    description: StrictStr
    tracking: Sequence[VideoLogo] = Field(default_factory=list)


class LogoDetectionAsyncDataClass(NoRaiseBaseModel):
    logos: Sequence[LogoTrack] = Field(default_factory=list)
