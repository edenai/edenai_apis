from utils.parsing import NoRaiseBaseModel
from typing import List

from pydantic import BaseModel, Field


class FaceRecognitionRecognizedFaceDataClass(NoRaiseBaseModel):
    confidence: float
    face_id: str


class FaceRecognitionRecognizeDataClass(NoRaiseBaseModel):
    items: List[FaceRecognitionRecognizedFaceDataClass] = Field(default_factory=list)
