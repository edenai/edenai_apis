from utils.parsing import NoRaiseBaseModel
from enum import Enum
from typing import Optional, Sequence, Literal

from pydantic import BaseModel, Field, field_validator


class SentimentEnum(Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


class SegmentSentimentAnalysisDataClass(NoRaiseBaseModel):
    """This class is used in SentimentAnalysisDataClass to describe each segment analyzed.

    Args:
        - segment (str): The segment analyzed
        - sentiment (Literal['Positve', 'Negative', 'Neutral']) (Case is ignore): Sentiment of segment
        - sentiment_rate (float between 0 and 1): Rate of sentiment
    """

    segment: str
    sentiment: Literal["Positive", "Negative", "Neutral"]
    sentiment_rate: Optional[float] = Field(ge=0, le=1)

    @field_validator("segment", mode="before")
    @classmethod
    def valid_segment(cls, value):
        if not isinstance(value, str):
            raise ValueError(f"Segment must be a string, not {type(value)}")
        return value

    @field_validator("sentiment", mode="before")
    @classmethod
    def valid_sentiment(cls, value):
        if not isinstance(value, str):
            raise ValueError(f"Sentiment must be a string, not {type(value)}")
        value = value.title()
        if not value in ["Positive", "Negative", "Neutral"]:
            raise ValueError(
                f"{value} are not allowed. Sentiment must be 'Positive' or 'Negative' or 'Neutral'"
            )
        return value

    @field_validator("sentiment_rate", mode="before")
    @classmethod
    def valid_sentiment_rate(cls, value):
        if value is None:
            return value
        if not isinstance(value, (float, int)):
            raise ValueError(f"Sentiment rate must be a float, not {type(value)}")
        return round(value, 2)


class SentimentAnalysisDataClass(NoRaiseBaseModel):
    """This class is used to standardize responses from sentiment_analysis.
    Args:
        - text (str): The text whose has been analyzed
        - general_sentiment (Literal['Positve', 'Negative', 'Neutral']) (Case is ignore): General sentiment of text
        - general_sentiment_rate (float between 0 and 1): Rate of general sentiment
        - items (Sequence[SegmentSentimentAnalysisDataClass]): Lists of the different segments analyzed. For more informations, looks at SegmentSentimentAnalysisDataClass's documentations (Default: [])
    """

    general_sentiment: Literal["Positive", "Negative", "Neutral"]
    general_sentiment_rate: Optional[float] = Field(ge=0, le=1)
    items: Sequence[SegmentSentimentAnalysisDataClass] = Field(default_factory=list)

    @field_validator("general_sentiment", mode="before")
    @classmethod
    def valid_general_sentiment(cls, value):
        if not isinstance(value, str):
            raise ValueError(f"General sentiment must be a string, not {type(value)}")
        value = value.title()
        if not value in ["Positive", "Negative", "Neutral"]:
            raise ValueError(
                f"{value} are not allowed. General sentiment must be 'Positive' or 'Negative' or 'Neutral'"
            )
        return value

    @field_validator("general_sentiment_rate", mode="before")
    @classmethod
    def valid_general_sentiment_rate(cls, value):
        if value is None:
            return value
        if not isinstance(value, (float, int)):
            raise ValueError(
                f"General sentiment rate must be a float, not {type(value)}"
            )
        return round(value, 2)
