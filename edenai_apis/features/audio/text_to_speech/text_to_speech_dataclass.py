from utils.parsing import NoRaiseBaseModel
from typing import Dict

from pydantic import BaseModel, StrictStr


class TextToSpeechDataClass(NoRaiseBaseModel):
    audio: StrictStr
    voice_type: int
    audio_resource_url: StrictStr

    @staticmethod
    def direct_response(api_response: Dict):
        return api_response["audio"]
