from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field


class VideoBoundingBox(NoRaiseBaseModel):
    top: Optional[float]
    left: Optional[float]
    height: Optional[float]
    width: Optional[float]


class VideoFacePoses(NoRaiseBaseModel):
    pitch: Optional[float]
    roll: Optional[float]
    yawn: Optional[float]


class FaceAttributes(NoRaiseBaseModel):
    headwear: Optional[float]
    frontal_gaze: Optional[float]
    eyes_visible: Optional[float]
    glasses: Optional[float]
    mouth_open: Optional[float]
    smiling: Optional[float]
    brightness: Optional[float]
    sharpness: Optional[float]
    pose: VideoFacePoses


class LandmarksVideo(NoRaiseBaseModel):
    eye_left: Sequence[float] = Field(default_factory=list)
    eye_right: Sequence[float] = Field(default_factory=list)
    nose: Sequence[float] = Field(default_factory=list)
    mouth_left: Sequence[float] = Field(default_factory=list)
    mouth_right: Sequence[float] = Field(default_factory=list)


class VideoFace(NoRaiseBaseModel):
    offset: Optional[float]
    bounding_box: VideoBoundingBox
    attributes: FaceAttributes
    landmarks: LandmarksVideo


class FaceDetectionAsyncDataClass(NoRaiseBaseModel):
    faces: Sequence[VideoFace] = Field(default_factory=list)
