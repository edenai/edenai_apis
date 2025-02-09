import json
from typing import List, Dict
from http import HTTPStatus
from typing import Dict, Sequence, Any, Optional
import requests
from edenai_apis.apis.winstonai.config import WINSTON_AI_API_URL, WINSTON_AI_PLAGIA_DETECTION_URL
from edenai_apis.features import ProviderInterface, TextInterface, ImageInterface
from edenai_apis.features.image.ai_detection.ai_detection_dataclass import (
    AiDetectionDataClass as ImageAiDetectionDataclass,
)
from edenai_apis.features.text.ai_detection.ai_detection_dataclass import (
    AiDetectionDataClass,
    AiDetectionItem,
)
from edenai_apis.features.text.plagia_detection.plagia_detection_dataclass import (
    PlagiaDetectionCandidate,
    PlagiaDetectionDataClass,
    PlagiaDetectionItem,
)
from edenai_apis.loaders.data_loader import ProviderDataEnum
from edenai_apis.loaders.loaders import load_provider
from edenai_apis.utils.exception import ProviderException
from edenai_apis.utils.types import ResponseType
from edenai_apis.utils.upload_s3 import upload_file_to_s3


class WinstonaiApi(ProviderInterface, TextInterface, ImageInterface):
    provider_name = "winstonai"

    def __init__(self, api_keys: Optional[Dict[str, Any]] = None):
        self.api_settings = load_provider(
            ProviderDataEnum.KEY,
            provider_name=self.provider_name,
            api_keys=api_keys or {},
        )
        self.api_url = WINSTON_AI_API_URL
        self.plagia_url = WINSTON_AI_PLAGIA_DETECTION_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.api_settings["api_key"]}',
        }

    def image__ai_detection(
        self, file: Optional[str] = None, file_url: Optional[str] = None
    ) -> ResponseType[ImageAiDetectionDataclass]:
        if not file_url and not file:
            raise ProviderException("file or file_url required")

        payload = json.dumps({"url": file_url or upload_file_to_s3(file, file)})

        response = requests.request(
            "POST",
            f"{self.api_url}/image-detection",
            headers=self.headers,
            data=payload,
        )

        if response.status_code != 200:
            raise ProviderException(response.json(), code=response.status_code)

        original_response = response.json()

        score = 1 - original_response.get("score") / 100
        prediction = ImageAiDetectionDataclass.set_label_based_on_score(score)
        if score is None:
            raise ProviderException(response.json())

        standardized_response = ImageAiDetectionDataclass(
            ai_score=score,
            prediction=prediction,
        )

        return ResponseType[ImageAiDetectionDataclass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__ai_detection(
        self, text: str, provider_params: Optional[Dict[str, Any]] = None
    ) -> ResponseType[AiDetectionDataClass]:
        if provider_params is None:
            provider_params = {}
        payload = json.dumps(
            {
                "text": text,
                "sentences": True,
                "language": provider_params.get("language", "en"),
                "version": provider_params.get("version", "2.0"),
            }
        )

        response = requests.request(
            "POST", f"{self.api_url}/predict", headers=self.headers, data=payload
        )

        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise ProviderException("Internal Server Error")

        if response.status_code != 200:
            raise ProviderException(response.json(), code=response.status_code)

        original_response = response.json()
        score = original_response.get("score") / 100
        sentences = original_response.get("sentences")

        if score is None or sentences is None:
            raise ProviderException(response.json())

        items: Sequence[AiDetectionItem] = [
            AiDetectionItem(
                text=sentence["text"],
                ai_score=1 - (sentence["score"] / 100),
                prediction=AiDetectionItem.set_label_based_on_score(
                    1 - (sentence["score"] / 100)
                ),
            )
            for sentence in sentences
        ]

        standardized_response = AiDetectionDataClass(ai_score=1 - score, items=items)

        return ResponseType[AiDetectionDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__plagia_detection(
        self,
        text: str,
        title: str = "",
        provider_params: Optional[Dict[str, Any]] = None,
    ) -> ResponseType[PlagiaDetectionDataClass]:
        if provider_params is None:
            provider_params = {}
        payload = json.dumps(
            {
                "text": text,
                "language": provider_params.get("language", "en"),
                "country": provider_params.get("country", "us"),
                "excluded_sources": provider_params.get("excluded_sources", [])
            }
        )

        response = requests.request(
            "POST", self.plagia_url, headers=self.headers, data=payload
        )

        if response.status_code != 200:
            raise ProviderException(response.json(), code=response.status_code)

        original_response = response.json()
        result = original_response.get("result")

        if result is None:
            raise ProviderException(response.json())
        
        plagiarism_score: int = result.get("score")
        sources = result.get("sources")

        candidates: Sequence[PlagiaDetectionCandidate] = []

        for source in sources:
            source_url = source.get("url")
            source_score = source.get("score")
            source_prediction = 'plagiarized' if source_score > 5 else 'not plagiarized'
            
            # startIndex, endIndex, sequence
            source_plagiarism_found: List[Dict[str, str]] = source.get("plagiarismFound")

            plagiarized_text: str = ""

            for plagiarism in source_plagiarism_found:
                plagiarism_start_index = int(plagiarism.get("startIndex"))
                plagiarism_end_index = int(plagiarism.get("endIndex"))

                plagiarized_text += " ... " + text[plagiarism_start_index:plagiarism_end_index] + " ... "
               

            plagia_detection_candidate = PlagiaDetectionCandidate(
                url=source_url,
                plagia_score=source_score,
                prediction=source_prediction,
                plagiarized_text=plagiarized_text,
                plagiarism_founds=source_plagiarism_found
            )

            candidates.append(plagia_detection_candidate)


        plagia_detection_item = PlagiaDetectionItem(text=text, candidates=candidates)
        
        standardized_response = PlagiaDetectionDataClass(
            plagia_score=plagiarism_score,
            items=[plagia_detection_item]
        )

        return ResponseType[PlagiaDetectionDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )
