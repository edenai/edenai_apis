from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field, field_validator


class ExtractedTopic(NoRaiseBaseModel):
    category: str
    importance: float

    @field_validator("category", mode="before")
    @classmethod
    def valid_category(cls, value):
        if not isinstance(value, str):
            raise TypeError(f"Category must be a string, not {type(value)}")
        value = value.title()
        return value

    @field_validator("importance", mode="before")
    @classmethod
    def valid_confidence(cls, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f"Importance must be a float, not {type(value)}")
        if value < 0 or value > 1:
            raise ValueError(
                f"{value} is not allowed. Importance must be between 0 and 1"
            )
        return round(value, 2)


class TopicExtractionDataClass(NoRaiseBaseModel):
    items: Sequence[ExtractedTopic] = Field(default_factory=list)
