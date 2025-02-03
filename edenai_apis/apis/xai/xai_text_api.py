from typing import Dict, List, Literal, Optional, Sequence, Union
import requests
from edenai_apis.features import TextInterface
from edenai_apis.features.text.anonymization import AnonymizationDataClass
from edenai_apis.features.text.chat import ChatDataClass
from edenai_apis.features.text.chat.chat_dataclass import (
    StreamChat,
)
from edenai_apis.features.text.code_generation.code_generation_dataclass import (
    CodeGenerationDataClass,
)
from edenai_apis.features.text.custom_classification import (
    CustomClassificationDataClass,
)
from edenai_apis.features.text.custom_named_entity_recognition import (
    CustomNamedEntityRecognitionDataClass,
)
from edenai_apis.features.text.generation import GenerationDataClass
from edenai_apis.features.text.keyword_extraction import KeywordExtractionDataClass
from edenai_apis.features.text.named_entity_recognition.named_entity_recognition_dataclass import (
    NamedEntityRecognitionDataClass,
)
from edenai_apis.features.text.prompt_optimization import (
    PromptDataClass,
    PromptOptimizationDataClass,
)
from edenai_apis.features.text.sentiment_analysis import SentimentAnalysisDataClass
from edenai_apis.features.text.spell_check.spell_check_dataclass import (
    SpellCheckDataClass,
)
from edenai_apis.features.text.summarize import SummarizeDataClass
from edenai_apis.features.text.topic_extraction import TopicExtractionDataClass
from edenai_apis.utils.types import ResponseType
from .helpers import (
    get_openapi_response,
    prompt_optimization_missing_information,
)


class XAiTextApi(TextInterface):
    def text__summarize(
        self, text: str, output_sentences: int, language: str, model: str
    ) -> ResponseType[SummarizeDataClass]:
        url = f"{self.url}/chat/completions"
        prompt = f"""Given the following text, please provide a concise summary in the same language:
        text : {text}
        sumamry : 
        """
        messages = [{"role": "user", "content": prompt}]
        # Build the request
        payload = {
            "model": model,
            "messages": messages,
        }

        response = requests.post(url, json=payload, headers=self.headers)
        original_response = get_openapi_response(response)

        standardized_response = SummarizeDataClass(
            result=original_response["choices"][0]["message"]["content"]
        )

        result = ResponseType[SummarizeDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )
        return result

    def text__anonymization(
        self, text: str, language: str, model: Optional[str] = None
    ) -> ResponseType[AnonymizationDataClass]:
        response = self.llm_client.pii(text=text, model=model)
        return response

    def text__keyword_extraction(
        self, language: str, text: str, model: Optional[str] = None
    ) -> ResponseType[KeywordExtractionDataClass]:
        response = self.llm_client.keyword_extraction(text=text, model=model)
        return response

    def text__sentiment_analysis(
        self, language: str, text: str, model: Optional[str] = None
    ) -> ResponseType[SentimentAnalysisDataClass]:
        response = self.llm_client.sentiment_analysis(text=text, model=model)
        return response

    def text__topic_extraction(
        self, language: str, text: str, model: Optional[str] = None
    ) -> ResponseType[TopicExtractionDataClass]:
        response = self.llm_client.topic_extraction(text=text, model=model)
        return response

    def text__code_generation(
        self,
        instruction: str,
        temperature: float,
        max_tokens: int,
        prompt: str = "",
        model: Optional[str] = None,
    ) -> ResponseType[CodeGenerationDataClass]:
        response = self.llm_client.code_generation(
            instruction=instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        )
        return response

    def text__generation(
        self,
        text: str,
        temperature: float,
        max_tokens: int,
        model: str,
    ) -> ResponseType[GenerationDataClass]:
        url = f"{self.url}/chat/completions"

        payload = {
            "prompt": text,
            "model": model,
            "temperature": temperature,
        }
        if max_tokens != 0:
            payload["max_tokens"] = max_tokens

        response = requests.post(url, json=payload, headers=self.headers)
        original_response = get_openapi_response(response)

        standardized_response = GenerationDataClass(
            generated_text=original_response["choices"][0]["text"]
        )
        return ResponseType[GenerationDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__custom_named_entity_recognition(
        self,
        text: str,
        entities: List[str],
        examples: Optional[List[Dict]] = None,
        model: Optional[str] = None,
    ) -> ResponseType[CustomNamedEntityRecognitionDataClass]:
        response = self.llm_client.custom_named_entity_recognition(
            text=text, model=model, entities=entities, examples=examples
        )
        return response

    def text__custom_classification(
        self,
        texts: List[str],
        labels: List[str],
        examples: List[List[str]],
        model: Optional[str] = None,
    ) -> ResponseType[CustomClassificationDataClass]:
        response = self.llm_client.custom_classification(
            texts=texts, labels=labels, examples=examples, model=model
        )
        return response

    def text__spell_check(
        self, text: str, language: str, model: Optional[str] = None
    ) -> ResponseType[SpellCheckDataClass]:
        response = self.llm_client.spell_check(text=text, model=model)
        return response

    def text__named_entity_recognition(
        self, language: str, text: str, model: Optional[str] = None
    ) -> ResponseType[NamedEntityRecognitionDataClass]:
        response = self.llm_client.named_entity_recognition(text=text, model=model)
        return response

    def text__chat(
        self,
        text: str,
        chatbot_global_action: Optional[str] = None,
        previous_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.0,
        max_tokens: int = 25,
        model: Optional[str] = None,
        stream: bool = False,
        available_tools: Optional[List[dict]] = None,
        tool_choice: Literal["auto", "required", "none"] = "auto",
        tool_results: Optional[List[dict]] = None,
    ) -> ResponseType[Union[ChatDataClass, StreamChat]]:
        response = self.llm_client.chat(
            text=text,
            chatbot_global_action=chatbot_global_action,
            previous_history=previous_history,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            stream=stream,
            available_tools=available_tools,
            tool_choice=tool_choice,
            tool_results=tool_results,
        )
        return response

    def text__prompt_optimization(
        self, text: str, target_provider: str
    ) -> ResponseType[PromptOptimizationDataClass]:
        url = f"{self.url}/chat/completions"
        prompt = construct_prompt_optimization_instruction(text, target_provider)
        messages = [{"role": "user", "content": prompt}]
        messages.insert(
            0,
            {
                "role": "system",
                "content": "Act as a Prompt Optimizer for LLMs, you take a description in input and generate a prompt from it.",
            },
        )
        payload = {
            "model": "grok-base",
            "messages": messages,
            "temperature": 0.2,
            "n": 3,
        }

        response = requests.post(url, json=payload, headers=self.headers)
        original_response = get_openapi_response(response)

        missing_information_call = requests.post(
            url,
            json={
                "model": "grok-base",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt_optimization_missing_information(text),
                    }
                ],
            },
            headers=self.headers,
        )
        missing_information_response = get_openapi_response(missing_information_call)

        # Calculate total tokens consumed
        total_tokens_missing_information = missing_information_response["usage"][
            "total_tokens"
        ]
        original_response["usage"][
            "missing_information_tokens"
        ] = total_tokens_missing_information
        original_response["usage"]["total_tokens"] += total_tokens_missing_information

        # Standardize the response
        prompts: Sequence[PromptDataClass] = []

        for generated_prompt in original_response["choices"]:
            prompts.append(
                PromptDataClass(text=generated_prompt["message"]["content"].strip('"'))
            )

        standardized_response = PromptOptimizationDataClass(
            missing_information=missing_information_response["choices"][0]["message"][
                "content"
            ],
            items=prompts,
        )

        return ResponseType[PromptOptimizationDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )
