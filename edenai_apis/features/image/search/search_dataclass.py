from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class ImageItem(NoRaiseBaseModel):
    image_name: StrictStr
    score: float


class SearchDataClass(NoRaiseBaseModel):
    items: Sequence[ImageItem] = Field(default_factory=list)
