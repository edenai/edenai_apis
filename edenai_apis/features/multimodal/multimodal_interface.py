from abc import abstractmethod
from typing import Literal

from edenai_apis.features.multimodal.chat import ChatDataClass
from edenai_apis.features.multimodal.embeddings import EmbeddingsDataClass
from edenai_apis.features.multimodal.embeddings.inputsmodel import (
    InputsModel as EmbeddingsInputsModel,
)
from edenai_apis.features.multimodal.question_answer import QuestionAnswerDataClass
from edenai_apis.utils.types import ResponseType


class MultimodalInterface:
    @abstractmethod
    def multimodal__embeddings(
        self,
        inputs: EmbeddingsInputsModel,
        dimension: Literal["xs", "s", "m", "xl"] = "xl",
    ) -> ResponseType[EmbeddingsDataClass]:
        raise NotImplementedError

    @abstractmethod
    def multimodal__question_answer(self) -> ResponseType[QuestionAnswerDataClass]:
        raise NotImplementedError

    @abstractmethod
    def multimodal__chat(self) -> ResponseType[ChatDataClass]:
        raise NotImplementedError
