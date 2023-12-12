from utils.parsing import NoRaiseBaseModel
from typing import Any, Sequence, Optional

from pydantic import BaseModel, Field, field_validator

from edenai_apis.utils.bounding_box import BoundingBox


class ItemDataExtraction(NoRaiseBaseModel):
    key: str
    value: Any
    bounding_box: BoundingBox
    confidence_score: Optional[float] = Field(..., ge=0, le=1)

    @field_validator("confidence_score")
    @classmethod
    def round_confidence_score(cls, v) -> Optional[float]:
        if v is not None:
            v = round(v, 2)
        return v


class DataExtractionDataClass(NoRaiseBaseModel):
    fields: Sequence[ItemDataExtraction] = Field(default_factory=list)
