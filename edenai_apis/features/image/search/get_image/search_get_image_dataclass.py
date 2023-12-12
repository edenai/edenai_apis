from utils.parsing import NoRaiseBaseModel
from pydantic import BaseModel


class SearchGetImageDataClass(NoRaiseBaseModel):
    image: bytes
