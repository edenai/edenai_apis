from utils.parsing import NoRaiseBaseModel
import base64
import importlib
import uuid
from io import BytesIO

from pydantic import BaseModel, Field


# from edenai_apis.utils.upload_s3 import upload_file_bytes_to_s3, USER_PROCESS


class BackgroundRemovalDataClass(NoRaiseBaseModel):
    """
    The response of the background removal API.

    Attributes:
        image_b64 (str): The image in base64 format.
        image_resource_url (str): The image url.
    """

    image_b64: str = Field(
        ...,
        description="The image in base64 format.",
    )

    image_resource_url: str = Field(
        ...,
        description="The image url.",
    )

    @staticmethod
    def generate_resource_url(img_b64: str, fmt: str = "png") -> str:
        """Generate resource url for image

        Args:
            img_b64 (str): image in base64 format
            fmt (str): format of image. Defaults to "png".

        Returns:
            str: resource url
        """
        data = img_b64.encode()
        content = BytesIO(base64.b64decode(data))
        uuid_name = uuid.uuid4()
        filename = f"{uuid_name}.{fmt}"

        s3_module = importlib.import_module("edenai_apis.utils.upload_s3")

        return s3_module.upload_file_bytes_to_s3(
            file=content, file_name=filename, process_type=s3_module.USER_PROCESS
        )
