from utils.parsing import NoRaiseBaseModel
from typing import Sequence

from pydantic import BaseModel, Field


class EmbeddingDataClass(NoRaiseBaseModel):
    embedding: Sequence[float]


class EmbeddingsDataClass(NoRaiseBaseModel):
    items: Sequence[EmbeddingDataClass] = Field(default_factory=list)
