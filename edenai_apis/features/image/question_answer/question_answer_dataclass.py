from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field


class QuestionAnswerDataClass(NoRaiseBaseModel):
    answers: Sequence[str] = Field(default_factory=list)
