from utils.parsing import NoRaiseBaseModel
from typing import Sequence, Optional

from pydantic import BaseModel, StrictStr, Field


class SpeechDiarizationEntry(NoRaiseBaseModel):
    segment: StrictStr
    start_time: Optional[StrictStr]
    end_time: Optional[StrictStr]
    speaker: int
    confidence: Optional[float]


class SpeechDiarization(NoRaiseBaseModel):
    total_speakers: int
    entries: Sequence[SpeechDiarizationEntry] = Field(default_factory=list)
    error_message: Optional[str] = None


class SpeechToTextAsyncDataClass(NoRaiseBaseModel):
    text: StrictStr
    diarization: SpeechDiarization
