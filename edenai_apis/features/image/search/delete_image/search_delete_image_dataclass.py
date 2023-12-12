from utils.parsing import NoRaiseBaseModel
from pydantic import BaseModel


class SearchDeleteImageDataClass(NoRaiseBaseModel):
    status: str
