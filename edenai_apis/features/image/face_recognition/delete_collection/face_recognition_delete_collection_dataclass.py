from utils.parsing import NoRaiseBaseModel
from pydantic import BaseModel


class FaceRecognitionDeleteCollectionDataClass(NoRaiseBaseModel):
    deleted: bool
