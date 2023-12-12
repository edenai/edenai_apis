from utils.parsing import NoRaiseBaseModel
from typing import Dict, Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class InfosSyntaxAnalysisDataClass(NoRaiseBaseModel):
    word: StrictStr
    importance: Optional[float]
    tag: StrictStr
    lemma: Optional[StrictStr]
    others: Optional[Dict[str, object]] = Field(default_factory=dict)


class SyntaxAnalysisDataClass(NoRaiseBaseModel):
    items: Sequence[InfosSyntaxAnalysisDataClass] = Field(default_factory=list)
