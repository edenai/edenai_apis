from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, StrictStr, Field


class PromptDataClass(NoRaiseBaseModel):
    text: StrictStr


class PromptOptimizationDataClass(NoRaiseBaseModel):
    missing_information: StrictStr
    items: Sequence[PromptDataClass] = Field(default_factory=list)
