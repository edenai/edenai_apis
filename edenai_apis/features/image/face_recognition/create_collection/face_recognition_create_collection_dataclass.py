from utils.parsing import NoRaiseBaseModel
from pydantic import BaseModel


class FaceRecognitionCreateCollectionDataClass(NoRaiseBaseModel):
    collection_id: str
