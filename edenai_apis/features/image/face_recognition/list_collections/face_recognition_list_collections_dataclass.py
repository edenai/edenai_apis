from utils.parsing import NoRaiseBaseModel
from typing import List

from pydantic import BaseModel, Field


class FaceRecognitionListCollectionsDataClass(NoRaiseBaseModel):
    collections: List[str] = Field(default_factory=list)
