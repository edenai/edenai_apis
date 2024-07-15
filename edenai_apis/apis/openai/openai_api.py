import random
from typing import Dict

import openai
from openai import OpenAI

from edenai_apis.apis.openai.openai_doc_parsing_api import OpenaiDocParsingApi
from edenai_apis.apis.openai.openai_audio_api import OpenaiAudioApi
from edenai_apis.apis.openai.openai_image_api import OpenaiImageApi
from edenai_apis.apis.openai.openai_text_api import OpenaiTextApi
from edenai_apis.apis.openai.openai_translation_api import OpenaiTranslationApi
from edenai_apis.apis.openai.openai_multimodal_api import OpenaiMultimodalApi
from edenai_apis.features.provider.provider_interface import ProviderInterface
from edenai_apis.loaders.data_loader import ProviderDataEnum
from edenai_apis.loaders.loaders import load_provider


class OpenaiApi(
    ProviderInterface,
    OpenaiImageApi,
    OpenaiTranslationApi,
    OpenaiTextApi,
    OpenaiAudioApi,
    OpenaiMultimodalApi,
    OpenaiDocParsingApi,
):
    provider_name = "openai"

    def __init__(self, api_keys: Dict = {}):
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_keys
        )

        if isinstance(self.api_settings, list):
            chosen_api_setting = random.choice(self.api_settings)
        else:
            chosen_api_setting = self.api_settings

        self.api_key = chosen_api_setting["api_key"]
        openai.api_key = self.api_key
        self.org_key = chosen_api_setting["org_key"]
        self.url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo-instruct"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Organization": self.org_key,
            "Content-Type": "application/json",
        }
        self.max_tokens = 270

        self.client = OpenAI(
                 api_key=self.api_key,
                )

        self.webhook_settings = load_provider(ProviderDataEnum.KEY, "webhooksite")
        self.webhook_token = self.webhook_settings["webhook_token"]
