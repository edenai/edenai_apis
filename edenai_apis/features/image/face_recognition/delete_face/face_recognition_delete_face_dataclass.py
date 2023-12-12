from utils.parsing import NoRaiseBaseModel
from pydantic import BaseModel


class FaceRecognitionDeleteFaceDataClass(NoRaiseBaseModel):
    deleted: bool
