import requests
from typing import Dict, List, Literal, Optional, Sequence, Union

from edenai_apis.features.text.keyword_extraction.keyword_extraction_dataclass import (
    KeywordExtractionDataClass,
)
from edenai_apis.features.text.sentiment_analysis.sentiment_analysis_dataclass import (
    SentimentAnalysisDataClass,
)
from edenai_apis.features.text.question_answer.question_answer_dataclass import (
    QuestionAnswerDataClass,
)
from edenai_apis.features.text.topic_extraction.topic_extraction_dataclass import (
    TopicExtractionDataClass,
)
from edenai_apis.features.text.named_entity_recognition.named_entity_recognition_dataclass import (
    NamedEntityRecognitionDataClass,
)
from edenai_apis.features.text.text_interface import TextInterface
from edenai_apis.utils.exception import ProviderException
from edenai_apis.utils.types import ResponseType

from edenai_apis.features.text.chat import ChatDataClass, ChatMessageDataClass


from edenai_apis.features.text.chat.chat_dataclass import (
    StreamChat,
    ChatStreamResponse,
    ToolCall,
)

from openai import OpenAI


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
            original_response.raise_for_status()
        except Exception as exc:
            raise ProviderException(original_response.text)

        original_response = original_response.json()

        # Check for errors
        self.check_for_errors(original_response)

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
            original_response.raise_for_status()
        except Exception as exc:
            raise ProviderException(original_response.text)

        original_response = original_response.json()

        # Check for errors
        self.check_for_errors(original_response)

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

    def text__question_answer(
        self,
        texts: List[str],
        question: str,
        temperature: float,
        examples_context: str,
        examples: List[List[str]],
        model: Optional[str],
    ) -> ResponseType[QuestionAnswerDataClass]:
        base_url = "https://question-answer--eden-ai.workload.tenstorrent.com"
        url = f"{base_url}/predictions/question_answer"
        payload = {
            "text": texts[0],
            "question": question,
        }
        try:
            original_response = requests.post(url, json=payload, headers=self.headers)
            original_response.raise_for_status()
        except Exception as exc:
            raise ProviderException(original_response.text)

        original_response = original_response.json()

        # Check for errors
        self.check_for_errors(original_response)

        standardized_response = QuestionAnswerDataClass(
            answers=[original_response["answer"]]
        )
        return ResponseType[QuestionAnswerDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__named_entity_recognition(
        self, text: str
    ) -> ResponseType[NamedEntityRecognitionDataClass]:
        base_url = "https://named-entity-recognition--eden-ai.workload.tenstorrent.com"
        url = f"{base_url}/predictions/named_entity_recognition"
        payload = {
            "text": text,
        }
        try:
            original_response = requests.post(url, json=payload, headers=self.headers)
            original_response.raise_for_status()
        except Exception as exc:
            raise ProviderException(original_response.text)

        original_response = original_response.json()

        # Check for errors
        self.check_for_errors(original_response)

        standardized_response = NamedEntityRecognitionDataClass(
            items=original_response["items"]
        )
        return ResponseType[NamedEntityRecognitionDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__topic_extraction(
        self, text: str
    ) -> ResponseType[TopicExtractionDataClass]:
        base_url = "https://topic-extraction--eden-ai.workload.tenstorrent.com"
        url = f"{base_url}/predictions/topic_extraction"
        payload = {
            "text": text,
        }
        try:
            original_response = requests.post(url, json=payload, headers=self.headers)
            original_response.raise_for_status()
        except Exception as exc:
            raise ProviderException(original_response.text)

        original_response = original_response.json()

        # Check for errors
        self.check_for_errors(original_response)

        standardized_response = TopicExtractionDataClass(
            items=original_response["items"]
        )
        return ResponseType[TopicExtractionDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )
    
    def text__chat(
        self,
        text: str,
        chatbot_global_action: Optional[str],
        previous_history: Optional[List[Dict[str, str]]],
        temperature: float,
        max_tokens: int,
        model: str,
        stream=False,
        # available_tools: Optional[List[dict]] = None,
        # tool_choice: Literal["auto", "required", "none"] = "auto",
        # tool_results: Optional[List[dict]] = None,
    ) -> ResponseType[Union[ChatDataClass, StreamChat]]:
        previous_history = previous_history or []
        # self.check_content_moderation(
        #     text=text,
        #     chatbot_global_action=chatbot_global_action,
        #     previous_history=previous_history,
        # )
        # is_o1_model = "o1-" in model
        messages = []
        for msg in previous_history:
            message = {
                "role": msg.get("role"),
                "content": msg.get("message"),
            }
            # if msg.get("tool_calls"):
            #     message["tool_calls"] = [
            #         {
            #             "id": tool["id"],
            #             "type": "function",
            #             "function": {
            #                 "name": tool["name"],
            #                 "arguments": tool["arguments"],
            #             },
            #         }
            #         for tool in msg["tool_calls"]
            #     ]
            messages.append(message)

        # if text and not tool_results:
        if text:    
            messages.append({"role": "user", "content": text})

        # if tool_results:
        #     for tool in tool_results or []:
        #         tool_call = get_tool_call_from_history_by_id(
        #             tool["id"], previous_history
        #         )
        #         try:
        #             result = json.dumps(tool["result"])
        #         except json.JSONDecodeError:
        #             result = str(result)
        #         messages.append(
        #             {
        #                 "role": "tool",
        #                 "content": result,
        #                 "tool_call_id": tool_call["id"],
        #             }
        #         )

        # if chatbot_global_action and not is_o1_model:
        if chatbot_global_action:
            messages.insert(0, {"role": "system", "content": chatbot_global_action})
        payload = {
            "model": model,
            "temperature": temperature,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        print(payload)


        # if available_tools and not tool_results:
        #     payload["tools"] = convert_tools_to_openai(available_tools)
        #     payload["tool_choice"] = tool_choice
        base_url = "https://vllm-tt-dev-8d232b47.workload.tenstorrent.com/v1"
        client = OpenAI(base_url=base_url)

        try:
            response = client.chat.completions.create(**payload)
        except Exception as exc:
            raise ProviderException(str(exc))

        # Standardize the response
        if stream is False:
            message = response.choices[0].message
            generated_text = message.content
            # original_tool_calls = message.tool_calls or []
            # tool_calls = []
            # for call in original_tool_calls:
            #     tool_calls.append(
            #         ToolCall(
            #             id=call["id"],
            #             name=call["function"]["name"],
            #             arguments=call["function"]["arguments"],
            #         )
            #     )
            messages = [
                # ChatMessageDataClass(role="user", message=text, tools=available_tools),
                ChatMessageDataClass(role="user", message=text),
                ChatMessageDataClass(
                    role="assistant",
                    message=generated_text,
                    # tool_calls=tool_calls,
                ),
            ]
            messages_json = [m.dict() for m in messages]

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
                    provider="tenstorrent",
                )
                for chunk in response
                if chunk
            )

            return ResponseType[StreamChat](
                original_response=None, standardized_response=StreamChat(stream=stream)
            )

    def check_for_errors(self, response):
        if "message" in response:
            raise ProviderException(response["message"])
        