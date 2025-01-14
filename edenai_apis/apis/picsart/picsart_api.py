import base64
import json
from typing import Dict, Optional, Any

import requests
from edenai_apis.features import ProviderInterface, ImageInterface
from edenai_apis.features.image import BackgroundRemovalDataClass
from edenai_apis.loaders.data_loader import ProviderDataEnum
from edenai_apis.loaders.loaders import load_provider
from edenai_apis.utils.exception import ProviderException
from edenai_apis.utils.types import ResponseType


class PicsartApi(ProviderInterface, ImageInterface):
    provider_name = 'picsart'

    def __init__(self, api_key: Optional[str] = None):
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_key or {}
        )
        self.base_image_api_url = self.api_settings["image_api_base_url"]  # "https://api.picsart.io/tools/1.0"
        self.api_key = self.api_settings["api_key"]
        self.headers = {
            "X-Picsart-API-Key": self.api_settings["api_key"],
            "Accept": "application/json",
        }


    def image__background_removal(
            self,
            file: Optional[str] = None,
            file_url: Optional[str] = None,
            provider_params: Optional[Dict[str, Any]] = None,
    ) -> ResponseType[BackgroundRemovalDataClass]:
        """
        Calls the Picsart Remove Background API.

        :param file: The file path of the image you want to remove the background from
        :param file_url: The file url of the image you want to remove the background from
        :param provider_params: Other parameters supported by the Picsart Remove Background API.
        """
        url = f"{self.base_image_api_url}/removebg"

        if provider_params is None:
            provider_params = {}

        files = None
        image_file = None
        if file and not file_url:
            image_file = open(file, "rb")
            files = {"image": image_file}
        elif file_url and not file:
            provider_params["image_url"] = file_url
        else:
            raise ProviderException("No file or file_url provided")

        bg_image = provider_params.pop("bg_image", None)
        if bg_image:
            bg_image = open(bg_image, "rb")
            files["bg_image"] = bg_image

        try:
            response = requests.post(url, files=files, data=provider_params, headers=self.headers)
        finally:
            if image_file and not image_file.closed:
                image_file.close()
            if bg_image and not bg_image.closed:
                bg_image.close()

        self._handle_errors(response=response)

        result = response.json()
        image_url = result["data"]["url"]
        image_response = requests.get(image_url)
        image_b64 = base64.b64encode(image_response.content).decode("utf-8")

        return ResponseType[BackgroundRemovalDataClass](
            original_response=response.text,
            standardized_response=BackgroundRemovalDataClass(
                image_b64=image_b64,
                image_resource_url=image_url,
            ),
        )

    @staticmethod
    def _handle_errors(response: requests.Response):
        """
        Handles the HTTP API Response.

        :param response: The HTTP API response.
        :raises: ProviderException
        """
        if response.status_code == 200:
            return

        error_message = "Internal Server Error"
        error_code = response.status_code
        if response.status_code == 400:
            try:
                response_details = response.json()
                error_message = response_details.get("message", "Bad Request")
                error_code = response_details.get("code", response.status_code)
            except (KeyError, json.JSONDecodeError):
                pass

        raise ProviderException(error_message, code=error_code)
