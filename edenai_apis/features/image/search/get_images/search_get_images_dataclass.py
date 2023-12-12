from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class ImageSearchItem(NoRaiseBaseModel):
    image_name: StrictStr


class SearchGetImagesDataClass(NoRaiseBaseModel):
    list_images: Sequence[ImageSearchItem] = Field(default_factory=list)
