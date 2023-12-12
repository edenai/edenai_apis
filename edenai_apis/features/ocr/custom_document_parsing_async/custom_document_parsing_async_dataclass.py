from utils.parsing import NoRaiseBaseModel
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr


class CustomDocumentParsingAsyncBoundingBox(NoRaiseBaseModel):
    left: Optional[float]
    top: Optional[float]
    width: Optional[float]
    height: Optional[float]


class CustomDocumentParsingAsyncItem(NoRaiseBaseModel):
    confidence: float
    value: StrictStr
    query: StrictStr
    bounding_box: CustomDocumentParsingAsyncBoundingBox
    page: int


class CustomDocumentParsingAsyncDataClass(NoRaiseBaseModel):
    items: List[CustomDocumentParsingAsyncItem] = Field(default_factory=list)
