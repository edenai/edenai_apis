from utils.parsing import NoRaiseBaseModel
from pydantic import BaseModel


class SearchUploadImageDataClass(NoRaiseBaseModel):
    status: str
