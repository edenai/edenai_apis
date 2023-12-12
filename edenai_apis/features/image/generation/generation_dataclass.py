from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class GeneratedImageDataClass(NoRaiseBaseModel):
    image: str
    image_resource_url: StrictStr


class GenerationDataClass(NoRaiseBaseModel):
    items: Sequence[GeneratedImageDataClass] = Field(default_factory=list)
