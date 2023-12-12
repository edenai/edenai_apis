from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class VideoTextBoundingBox(NoRaiseBaseModel):
    top: Optional[float]
    left: Optional[float]
    height: Optional[float]
    width: Optional[float]


class VideoTextFrames(NoRaiseBaseModel):
    confidence: float
    timestamp: float
    bounding_box: VideoTextBoundingBox


class VideoText(NoRaiseBaseModel):
    text: StrictStr
    frames: Sequence[VideoTextFrames] = Field(default_factory=list)


class TextDetectionAsyncDataClass(NoRaiseBaseModel):
    texts: Sequence[VideoText] = Field(default_factory=list)
