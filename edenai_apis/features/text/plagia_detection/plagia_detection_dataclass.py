from utils.parsing import NoRaiseBaseModel

from typing import Sequence

from pydantic import BaseModel, Field, root_validator, field_validator


class PlagiaDetectionCandidate(NoRaiseBaseModel):
    url: str
    plagia_score: float
    prediction: str
    plagiarized_text: str

    @root_validator(pre=True)
    def _set_prediction(cls, values: dict) -> dict:
        plag_score = values.get('plagia_score', None)
        if not plag_score:
            return values
        values["prediction"] = "not plagiarized"
        if plag_score > 0.5:
            values["prediction"] = "plagiarized"
        return values
    
    @field_validator("plagia_score")
    def check_min_max(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Value should be between 0 and 1")
        return v

class PlagiaDetectionItem(NoRaiseBaseModel):
    text: str
    candidates: Sequence[PlagiaDetectionCandidate] = Field(default_factory=list)


class PlagiaDetectionDataClass(NoRaiseBaseModel):
    plagia_score : float
    items : Sequence[PlagiaDetectionItem] = Field(default_factory=list)
