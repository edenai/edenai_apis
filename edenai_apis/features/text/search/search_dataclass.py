from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, StrictStr


class InfosSearchDataClass(NoRaiseBaseModel):
    object: StrictStr
    document: int
    score: float


class SearchDataClass(NoRaiseBaseModel):
    items: Sequence[InfosSearchDataClass] = Field(default_factory=list)
