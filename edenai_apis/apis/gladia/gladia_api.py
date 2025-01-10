from json import JSONDecodeError
from pathlib import Path
from time import time
from typing import Dict, List, Optional

import requests

from edenai_apis.features import ProviderInterface, AudioInterface
from edenai_apis.features.audio import SpeechDiarizationEntry, SpeechDiarization
from edenai_apis.features.audio.speech_to_text_async.speech_to_text_async_dataclass import (
    SpeechToTextAsyncDataClass,
)
from edenai_apis.loaders.data_loader import ProviderDataEnum
from edenai_apis.loaders.loaders import load_provider
from edenai_apis.utils.exception import ProviderException
from edenai_apis.utils.types import (
    AsyncBaseResponseType,
    AsyncLaunchJobResponseType,
    AsyncPendingResponseType,
    AsyncResponseType,
)
from edenai_apis.utils.upload_s3 import upload_file_to_s3


class GladiaApi(ProviderInterface, AudioInterface):
    provider_name = "gladia"

    def __init__(self, api_keys: Dict = {}) -> None:
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_keys
        )
        self.api_key = self.api_settings["gladia_key"]
        self.url = "https://api.gladia.io/v2/transcription/"

    def audio__speech_to_text_async__launch_job(
        self,
        file: str,
        language: str,
        speakers: int,
        profanity_filter: bool,
        vocabulary: Optional[List[str]],
        audio_attributes: tuple,
        model: Optional[str] = None,
        file_url: str = "",
        provider_params: Optional[dict] = None,
    ) -> AsyncLaunchJobResponseType:
        provider_params = provider_params or {}
        headers = {"x-gladia-key": self.api_key, "accept": "application/json"}
        
        with open(file, "rb") as f:
            file_content = f.read()
        extension = Path(file).suffix[1:]
        files = [
            ("audio", (file, file_content, f"audio/{extension}"))
        ]
        upload_response = requests.post(
            "https://api.gladia.io/v2/upload/",
            headers=headers,
            files=files
        )
        if upload_response.status_code != 200:
            raise ProviderException(
                message=upload_response.text, code=upload_response.status_code
            )
        upload_json = upload_response.json()
        audio_url = upload_json.get("audio_url")
        if not audio_url:
            raise ProviderException("Failed to upload file: missing audio_url")
        
        data = {
            "audio_url": audio_url,
            "diarization": True,
            "diarization_config": {
                "number_of_speakers": speakers,
                "min_speakers": speakers,
                "max_speakers": speakers,
            },
            "enable_code_switching": False,
            "detect_language": False,
            "language": language,
            "custom_vocabulary": vocabulary,
        }
        if language:
            data.update({"detect_language": False, "language": language})
        data.update(provider_params)

        transcription_response = requests.post(self.url, headers=headers, json=data)
        if transcription_response.status_code not in (200, 201):
            raise ProviderException(
                message=transcription_response.text, code=transcription_response.status_code
            )
        transcription_json = transcription_response.json()
        
        result_url = transcription_json.get("result_url", "")
        if not result_url:
            raise ProviderException("Failed to get result_url from transcription response")
        
        return AsyncLaunchJobResponseType(provider_job_id=result_url)

    def audio__speech_to_text_async__get_job_result(
        self, provider_job_id: str
    ) -> AsyncBaseResponseType[SpeechToTextAsyncDataClass]:
        if not provider_job_id:
            raise ProviderException("Job id is None or empty!")
        
        headers = {"x-gladia-key": self.api_key, "accept": "application/json"}

        response = requests.get(provider_job_id, headers=headers)
        if response.status_code != 200:
            raise ProviderException(message=response.text, code=response.status_code)
        
        try:
            original_response = response.json()
        except JSONDecodeError:
            raise ProviderException(message="Internal Server Error", code=500)
        
        status = original_response.get("status")
        if status in ("processing", "queued"):
            return AsyncPendingResponseType[SpeechToTextAsyncDataClass](
                provider_job_id=provider_job_id
            )
        elif status == "error":
            raise ProviderException(f"Transcription failed: {original_response}")
        
        result = original_response.get("result", {})
        transcription = result.get("transcription", {})
        text = transcription.get("full_transcript", " ")
        
        entries = []
        total_speakers = 0
        for utterance in transcription.get("utterances", []):
            for word in utterance.get("words", []):
                entries.append(
                    SpeechDiarizationEntry(
                        segment=word.get("word", " "),
                        start_time=str(word.get("start", 0)),
                        end_time=str(word.get("end", 0)),
                        speaker=utterance.get("speaker", 0),
                        confidence=word.get("confidence", 0),
                    )
                )
            total_speakers = max(utterance.get("speaker", 0), total_speakers)
        
        diarization = SpeechDiarization(total_speakers=total_speakers, entries=entries)
        if total_speakers == 0:
            diarization.error_message = (
                "Speaker diarization not available for the data specified"
            )
        
        return AsyncResponseType[SpeechToTextAsyncDataClass](
            original_response=original_response,
            standardized_response=SpeechToTextAsyncDataClass(
                text=text,
                diarization=diarization
            ),
            provider_job_id=provider_job_id,
        )
