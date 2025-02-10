import openai
import json
from typing import Dict, List, Literal, Optional, Union
from edenai_apis.utils.exception import ProviderException
from edenai_apis.features import ProviderInterface, TextInterface
from edenai_apis.features.text import ChatDataClass, ChatMessageDataClass
from edenai_apis.features.text.chat.chat_dataclass import (
    StreamChat,
    ChatStreamResponse,
    ToolCall,
)
from edenai_apis.utils.types import ResponseType
from edenai_apis.loaders.loaders import load_provider
from edenai_apis.loaders.data_loader import ProviderDataEnum
from edenai_apis.features.text.chat.helpers import get_tool_call_from_history_by_id
from edenai_apis.apis.openai.helpers import convert_tools_to_openai


class TogetheraiApi(ProviderInterface, TextInterface):
    provider_name = "together_ai"

    def __init__(self, api_keys: Dict = {}) -> None:
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_keys
        )
        self.api_key = self.api_settings["api_key"]
        self.client = openai.OpenAI(
            api_key=self.api_key, base_url="https://api.together.xyz/v1"
        )

    def text__chat(
        self,
        text: str,
        chatbot_global_action: Optional[str],
        previous_history: Optional[List[Dict[str, str]]],
        temperature: float,
        max_tokens: int,
        model: str,
        stream: bool=False,
        available_tools: Optional[List[dict]] = None,
        tool_choice: Literal["auto", "required", "none"] = "auto",
        tool_results: Optional[List[dict]] = None,
    ) -> ResponseType[Union[ChatDataClass, StreamChat]]:
        previous_history = previous_history or []
        messages = []
        for msg in previous_history:
            message = {
                "role": msg.get("role"),
                "content": msg.get("message"),
            }
            if msg.get("tool_calls"):
                message["tool_calls"] = [
                    {
                        "id": tool["id"],
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "arguments": tool["arguments"],
                        },
                    }
                    for tool in msg["tool_calls"]
                ]
            messages.append(message)

        if text and not tool_results:
            messages.append({"role": "user", "content": text})

        if tool_results:
            for tool in tool_results or []:
                tool_call = get_tool_call_from_history_by_id(
                    tool["id"], previous_history
                )
                try:
                    result = json.dumps(tool["result"])
                except json.JSONDecodeError:
                    result = str(result)
                messages.append(
                    {
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call["id"],
                    }
                )

        if chatbot_global_action:
            messages.insert(0, {"role": "system", "content": chatbot_global_action})

        payload = {
            "model": f"{model}",
            "temperature": temperature,
            "messages": messages,
            "max_completion_tokens": max_tokens,
            "stream": stream,
        }

        if available_tools and not tool_results:
            payload["tools"] = convert_tools_to_openai(available_tools)
            payload["tool_choice"] = tool_choice

        try:
            response = self.client.chat.completions.create(**payload)
        except Exception as exc:
            raise ProviderException(str(exc))

        # Standardize the response
        if stream is False:
            message = response.choices[0].message
            generated_text = message.content
            original_tool_calls = message.tool_calls or []
            tool_calls = []
            for call in original_tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=call["id"],
                        name=call["function"]["name"],
                        arguments=call["function"]["arguments"],
                    )
                )
            messages = [
                ChatMessageDataClass(role="user", message=text, tools=available_tools),
                ChatMessageDataClass(
                    role="assistant",
                    message=generated_text,
                    tool_calls=tool_calls,
                ),
            ]
            messages_json = [m.model_dump() for m in messages]

            standardized_response = ChatDataClass(
                generated_text=generated_text, message=messages_json
            )

            return ResponseType[ChatDataClass](
                original_response=response.to_dict(),
                standardized_response=standardized_response,
            )
        else:
            stream = (
                ChatStreamResponse(
                    text=chunk.to_dict()["choices"][0]["delta"].get("content", ""),
                    blocked=not chunk.to_dict()["choices"][0].get("finish_reason")
                    in (None, "stop"),
                    provider="together_ai",
                )
                for chunk in response
                if chunk
            )

            return ResponseType[StreamChat](
                original_response=None, standardized_response=StreamChat(stream=stream)
            )
