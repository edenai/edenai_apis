from utils.parsing import NoRaiseBaseModel
from typing import Dict

from pydantic import BaseModel, StrictStr


class GenerationDataClass(NoRaiseBaseModel):
    generated_text: StrictStr

    @staticmethod
    def direct_response(api_response: Dict):
        return api_response["generated_text"]
