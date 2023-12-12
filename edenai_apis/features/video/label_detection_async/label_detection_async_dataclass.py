from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class VideoLabelBoundingBox(NoRaiseBaseModel):
    top: Optional[float]
    left: Optional[float]
    height: Optional[float]
    width: Optional[float]


class VideoLabelTimeStamp(NoRaiseBaseModel):
    start: Optional[float]
    end: Optional[float]


class VideoLabel(NoRaiseBaseModel):
    name: StrictStr
    confidence: float
    timestamp: Sequence[VideoLabelTimeStamp] = Field(default_factory=list)
    category: Sequence[str] = Field(default_factory=list)
    bounding_box: Sequence[VideoLabelBoundingBox] = Field(default_factory=list)


class LabelDetectionAsyncDataClass(NoRaiseBaseModel):
    labels: Sequence[VideoLabel] = Field(default_factory=list)
