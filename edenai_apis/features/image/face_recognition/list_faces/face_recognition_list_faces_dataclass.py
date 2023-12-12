from utils.parsing import NoRaiseBaseModel
from typing import List

from pydantic import BaseModel


class FaceRecognitionListFacesDataClass(NoRaiseBaseModel):
    face_ids: List[str]
