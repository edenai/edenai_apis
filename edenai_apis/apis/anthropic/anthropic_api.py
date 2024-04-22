from typing import Dict, List, Union, Optional, Generator
import httpx
import base64
import json
import boto3
from anthropic_bedrock import AnthropicBedrock
from edenai_apis.features import ProviderInterface, TextInterface
from edenai_apis.features.text import GenerationDataClass, SummarizeDataClass
from edenai_apis.features.text.chat.chat_dataclass import (
    StreamChat,
    ChatStreamResponse,
    ChatMessageDataClass,
    ChatDataClass,
)
from edenai_apis.features.multimodal.chat.chat_dataclass import (
    ChatDataClass as ChatMultimodalDataClass,
    StreamChat as StreamChatMultimodal,
)
from edenai_apis.loaders.data_loader import ProviderDataEnum
from edenai_apis.loaders.loaders import load_provider
from edenai_apis.utils.types import ResponseType
from edenai_apis.apis.amazon.helpers import handle_amazon_call
from edenai_apis.utils.exception import ProviderException


class AnthropicApi(ProviderInterface, TextInterface):
    provider_name = "anthropic"

    def __init__(self, api_keys: Dict = {}) -> None:
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_keys
        )
        self.bedrock = boto3.client(
            "bedrock-runtime",
            region_name=self.api_settings["region_name"],
            aws_access_key_id=self.api_settings["aws_access_key_id"],
            aws_secret_access_key=self.api_settings["aws_secret_access_key"],
        )
        self.client = AnthropicBedrock()

    def __anthropic_request(self, request_body: str, model: str):
        # Headers for the HTTP request
        accept_header = "application/json"
        content_type_header = "application/json"

        # Parameters for the HTTP request
        request_params = {
            "body": request_body,
            "modelId": f"{self.provider_name}.{model}",
            "accept": accept_header,
            "contentType": content_type_header,
        }
        response = handle_amazon_call(self.bedrock.invoke_model, **request_params)
        response_body = json.loads(response.get("body").read())
        return response_body

    def __calculate_usage(self, prompt: str, generated_text: str):
        """
        Calculate token usage based on the provided prompt and generated text.

        Args:
            prompt (str): The prompt provided to the language model.
            generated_text (str): The text generated by the language model.

        Returns:
            dict: A dictionary containing token usage details including total tokens,
                prompt tokens, and completion tokens.
        """
        try:
            prompt_tokens = self.client.count_tokens(prompt)
            completion_tokens = self.client.count_tokens(generated_text)
            return {
                "total_tokens": prompt_tokens + completion_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            }
        except Exception:
            raise ProviderException("Client Error", status_code=500)

    def __chat_stream_generator(self, response) -> Generator:
        """returns a generator of chat messages

        Args:
            response : The post request response

        Yields:
            Generator: generator of messages
        """
        for event in response.get("body"):
            chunk = json.loads(event["chunk"]["bytes"])

            if chunk["type"] == "message_delta":
                yield ChatStreamResponse(
                    text="", blocked=True, provider=self.provider_name
                )

            if chunk["type"] == "content_block_delta":
                if chunk["delta"]["type"] == "text_delta":
                    yield ChatStreamResponse(
                        text=chunk["delta"]["text"],
                        blocked=False,
                        provider=self.provider_name,
                    )

    @staticmethod
    def __format_anthropic_messages(
        messages: List[ChatMessageDataClass],
    ) -> List[Dict[str, str]]:
        """
        Format messages into a format accepted by Anthropic.

        Args:
            messages (List[ChatMessageDataClass]): List of messages to be formatted.

        Returns:
            List[Dict[str, str]]: Transformed messages in Anthropic accepted format.

        >>> Accepted format:
            [
                {
                    "role": <role>,
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": "iVBORw..."
                            }
                        },
                        {
                            "type": "text",
                            "text": <text_content>
                        }
                    ]
                }
            ]
        """
        transformed_messages = []
        for item in messages:
            if item["role"] == "user":
                transformed_message = {"role": item["role"], "content": []}
                for content_item in item["content"]:
                    if content_item["type"] == "text":
                        transformed_message["content"].append(
                            {"type": "text", "text": content_item["content"]["text"]}
                        )
                    elif content_item["type"] == "media_url":
                        media_url = content_item["content"]["media_url"]
                        media_data = base64.b64encode(
                            httpx.get(media_url).content
                        ).decode("utf-8")
                        if media_data:
                            transformed_message["content"].append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": media_data,
                                    },
                                }
                            )
                    elif content_item["type"] == "media_base64":
                        transformed_message["content"].append(
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": content_item["content"]["media_base64"],
                                },
                            }
                        )
            else:
                transformed_message = {
                    "role": item["role"],
                    "content": item.get("content")[0].get("content").get("text"),
                }
            transformed_messages.append(transformed_message)
        return transformed_messages

    def text__generation(
        self,
        text: str,
        temperature: float,
        max_tokens: int,
        model: str,
    ) -> ResponseType[GenerationDataClass]:
        prompt = f"\n\nHuman:{text}\n\nAssistant:"
        # Body of the HTTP request, containing text, maxTokens, and temperature
        request_body = json.dumps(
            {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens_to_sample": max_tokens,
            }
        )
        response = self.__anthropic_request(request_body=request_body, model=model)
        generated_text = response["completion"]
        response["usage"] = self.__calculate_usage(
            prompt=prompt, generated_text=generated_text
        )
        standardized_response = GenerationDataClass(generated_text=generated_text)

        return ResponseType[GenerationDataClass](
            original_response=response,
            standardized_response=standardized_response,
        )

    def text__summarize(
        self,
        text: str,
        output_sentences: int,
        language: str,
        model: Optional[str] = None
    ) -> ResponseType[SummarizeDataClass]:
        messages = [
            {
                "role": "user",
                "content": f"Given the following text, please provide a concise summary of this text : {text}",
            },
            {
                "role": "assistant",
                "content": """Summary:""",
            },
        ]
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10000,
            "temperature": 0,
            "messages": messages,
        }

        request_body = json.dumps(body)

        original_response = self.__anthropic_request(
            request_body=request_body, model=model
        )

        # Calculate total usage
        original_response["usage"]["total_tokens"] = (
            original_response["usage"]["input_tokens"]
            + original_response["usage"]["output_tokens"]
        )

        result = original_response["content"][0]["text"]

        standardized_response = SummarizeDataClass(result=result)
        return ResponseType[SummarizeDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__chat(
        self,
        text: str,
        chatbot_global_action: Optional[str] = None,
        previous_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 25,
        model: Optional[str] = None,
        stream: bool = False,
    ) -> ResponseType[Union[ChatDataClass, StreamChat]]:
        messages = [{"role": "user", "content": text}]

        if previous_history:
            for idx, message in enumerate(previous_history):
                messages.insert(
                    idx,
                    {"role": message.get("role"), "content": message.get("message")},
                )

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if chatbot_global_action:
            body["system"] = chatbot_global_action

        request_body = json.dumps(body)

        if stream is False:
            original_response = self.__anthropic_request(
                request_body=request_body, model=model
            )

            # Calculate total usage
            original_response["usage"]["total_tokens"] = (
                original_response["usage"]["input_tokens"]
                + original_response["usage"]["output_tokens"]
            )

            generated_text = original_response["content"][0]["text"]
            message = [
                ChatMessageDataClass(role="user", message=text),
                ChatMessageDataClass(role="assistant", message=generated_text),
            ]

            standardized_response = ChatDataClass(
                generated_text=generated_text, message=message
            )

            return ResponseType[ChatDataClass](
                original_response=original_response,
                standardized_response=standardized_response,
            )
        else:
            # Parameters for the HTTP request
            request_params = {
                "body": request_body,
                "modelId": f"{self.provider_name}.{model}",
            }
            response = handle_amazon_call(
                self.bedrock.invoke_model_with_response_stream, **request_params
            )
            stream_response = self.__chat_stream_generator(response)

            return ResponseType[StreamChat](
                original_response=None,
                standardized_response=StreamChat(stream=stream_response),
            )

    def multimodal__chat(
        self,
        messages: List[Dict[str, str]],
        chatbot_global_action: str = None,
        temperature: float = 0,
        max_tokens: int = 25,
        model: str = None,
        stop_sequences: List[str] = None,
        top_k: int = None,
        top_p: int = None,
        stream: bool = False,
        provider_params: dict = None,
    ) -> ResponseType[Union[ChatMultimodalDataClass, StreamChatMultimodal]]:

        formated_messages = self.__format_anthropic_messages(messages=messages)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": formated_messages,
        }
        if stop_sequences:
            body["stop_sequences"] = stop_sequences

        if top_k:
            body["top_k"] = top_k

        if top_p:
            body["top_p"] = top_p

        if chatbot_global_action:
            body["system"] = chatbot_global_action

        request_body = json.dumps(body)

        if stream is False:
            original_response = self.__anthropic_request(
                request_body=request_body, model=model
            )

            generated_text = original_response["content"][0]["text"]

            standardized_response = (
                ChatMultimodalDataClass.generate_standardized_response(
                    generated_text=generated_text, messages=messages
                )
            )
            return ResponseType[ChatMultimodalDataClass](
                original_response=original_response,
                standardized_response=standardized_response,
            )
        else:
            request_params = {
                "body": request_body,
                "modelId": f"{self.provider_name}.{model}",
            }
            response = handle_amazon_call(
                self.bedrock.invoke_model_with_response_stream, **request_params
            )
            stream_response = self.__chat_stream_generator(response)

            return (
                ResponseType[StreamChat](
                    original_response=None,
                    standardized_response=StreamChat(stream=stream_response),
                ),
            )
