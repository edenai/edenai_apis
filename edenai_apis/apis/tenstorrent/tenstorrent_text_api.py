from logging import exception
import requests

from edenai_apis.features.text.keyword_extraction.keyword_extraction_dataclass import (
    KeywordExtractionDataClass,
)
from edenai_apis.features.text.sentiment_analysis.sentiment_analysis_dataclass import (
    SentimentAnalysisDataClass,
)
from edenai_apis.features.text.text_interface import TextInterface
from edenai_apis.utils.exception import ProviderException
from edenai_apis.utils.types import ResponseType


class TenstorrentTextApi(TextInterface):
    def text__keyword_extraction(
        self, language: str, text: str
    ) -> ResponseType[KeywordExtractionDataClass]:
        base_url = "https://keyword-extraction--eden-ai.workload.tenstorrent.com"
        url = f"{base_url}/predictions/keyword_extraction"
        payload = {
            "text": text,
        }

        try:
            original_response = requests.post(url, json=payload, headers=self.headers)
        except requests.exceptions.RequestException as exc:
            raise ProviderException(message=str(exc))
        if original_response.status_code != 200:
            raise ProviderException(message=original_response.text, code=original_response.status_code)

        original_response = original_response.json()

        # Check for errors
        self.__check_for_errors(original_response)

        standardized_response = KeywordExtractionDataClass(
            items=original_response["items"]
        )
        return ResponseType[KeywordExtractionDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__sentiment_analysis(
        self, language: str, text: str
    ) -> ResponseType[SentimentAnalysisDataClass]:
        base_url = "https://sentiment-analysis--eden-ai.workload.tenstorrent.com"
        url = f"{base_url}/predictions/sentiment_analysis"
        payload = {
            "text": text,
        }
        try:
            original_response = requests.post(url, json=payload, headers=self.headers)
        except requests.exceptions.RequestException as exc:
            raise ProviderException(message=str(exc))
        if original_response.status_code != 200:
            raise ProviderException(message=original_response.text, code=original_response.status_code)

        original_response = original_response.json()

        # Check for errors
        self.__check_for_errors(original_response)

        # Create output response
        confidence = float(original_response["confidence"])
        prediction = original_response["prediction"]
        standardized_response = SentimentAnalysisDataClass(
            general_sentiment=prediction,
            general_sentiment_rate=confidence,
        )

        return ResponseType[SentimentAnalysisDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def __check_for_errors(self, response):
        if "message" in response:
            raise ProviderException(response["message"])
