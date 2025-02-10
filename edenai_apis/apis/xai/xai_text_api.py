import itertools
import json
import asyncio
import os
from time import sleep
from typing import Dict, List, Literal, Optional, Sequence, Union
from edenai_apis.apis.openai.helpers import construct_prompt_optimization_instruction
from edenai_apis.features.text.chat.helpers import get_tool_call_from_history_by_id

from openai import OpenAI

import requests
from pydantic_core._pydantic_core import ValidationError

from edenai_apis.features import TextInterface
from edenai_apis.features.text.anonymization import AnonymizationDataClass
from edenai_apis.features.text.anonymization.anonymization_dataclass import (
    AnonymizationEntity,
)
from edenai_apis.features.text.anonymization.category import CategoryType
from edenai_apis.features.text.chat import ChatDataClass, ChatMessageDataClass
from edenai_apis.features.text.chat.chat_dataclass import (
    StreamChat,
    ChatStreamResponse,
    ToolCall,
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
from edenai_apis.features.text.embeddings import EmbeddingDataClass, EmbeddingsDataClass
from edenai_apis.features.text.generation import GenerationDataClass
from edenai_apis.features.text.keyword_extraction import KeywordExtractionDataClass
from edenai_apis.features.text.keyword_extraction.keyword_extraction_dataclass import (
    InfosKeywordExtractionDataClass,
)
from edenai_apis.features.text.moderation import ModerationDataClass, TextModerationItem
from edenai_apis.features.text.moderation.category import (
    CategoryType as CategoryTypeModeration,
)
from edenai_apis.features.text.named_entity_recognition.named_entity_recognition_dataclass import (
    NamedEntityRecognitionDataClass,
)
from edenai_apis.features.text.prompt_optimization import (
    PromptDataClass,
    PromptOptimizationDataClass,
)
from edenai_apis.features.text.question_answer import QuestionAnswerDataClass
from edenai_apis.features.text.search.search_dataclass import InfosSearchDataClass, SearchDataClass
from edenai_apis.features.text.sentiment_analysis import SentimentAnalysisDataClass
from edenai_apis.features.text.spell_check.spell_check_dataclass import (
    SpellCheckDataClass,
)
from edenai_apis.features.text.summarize import SummarizeDataClass
from edenai_apis.features.text.topic_extraction import TopicExtractionDataClass
from edenai_apis.utils.conversion import (
    closest_above_value,
    find_all_occurrence,
)
from edenai_apis.utils.exception import ProviderException
from edenai_apis.utils.metrics import METRICS
from edenai_apis.utils.types import ResponseType
from .helpers import (
    construct_anonymization_context,
    convert_tools_to_openai,
    get_openapi_response,
    prompt_optimization_missing_information,
)


class XAiTextApi(TextInterface):

    def __assistant_text(
        self, name, instruction, message_text, example_file, dataclass
    ):

        with open(os.path.join(os.path.dirname(__file__), example_file), "r") as f:
            output_response = json.load(f)["standardized_response"]

        assistant = self.client.beta.assistants.create(
            response_format={"type": "json_object"},
            model="grok-beta",
            name=name,
            instructions="{} You return a json output shaped like the following with the exact same structure and the exact same keys but the values would change : \n {} \n\n You should follow this pydantic dataclass schema {}".format(
                instruction, output_response, dataclass.schema()
            ),
        )
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message_text,
                        }
                    ],
                }
            ]
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        while run.status != "completed":
            sleep(1)

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        usage = run.to_dict()["usage"]
        original_response = messages.to_dict()
        original_response["usage"] = usage

        try:
            standardized_response = json.loads(
                json.loads(messages.data[0].content[0].json())["text"]["value"]
            )
        except json.JSONDecodeError as exc:
            raise ProviderException(
                "An error occurred while parsing the response."
            ) from exc

        return original_response, standardized_response

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
    
    # def text__embeddings(
    #     self, texts: List[str], model: str
    # ) -> ResponseType[EmbeddingsDataClass]:
    #     url = f"{self.url}/embeddings"
    #     payload = {
    #         "input": texts,
    #         "model": model[1],
    #     }

    #     response = requests.post(url, json=payload, headers=self.headers)
    #     original_response = get_openapi_response(response)

    #     items: Sequence[EmbeddingsDataClass] = []
    #     embeddings = original_response["data"]

    #     for embedding in embeddings:
    #         items.append(EmbeddingDataClass(embedding=embedding["embedding"]))

    #     standardized_response = EmbeddingsDataClass(items=items)

    #     return ResponseType[EmbeddingsDataClass](
    #         original_response=original_response,
    #         standardized_response=standardized_response,
    #     )
    
    # def text__search(
    #     self,
    #     texts: List[str],
    #     query: str,
    #     similarity_metric: Literal[
    #         "cosine", "hamming", "manhattan", "euclidean"
    #     ] = "cosine",
    #     model: str = None,
    # ) -> ResponseType[SearchDataClass]:
    #     if model is None:
    #         model = "v1"

    #     # Import the function
    #     function_score = METRICS[similarity_metric]

    #     # Embed the texts & query
    #     texts_embed_response = XAiTextApi.text__embeddings(
    #         self, texts=texts, model=model
    #     ).original_response
    #     query_embed_response = XAiTextApi.text__embeddings(
    #         self, texts=[query], model=model
    #     ).original_response

    #     # Extract Tokens consumed
    #     texts_usage = texts_embed_response.get("usage").get("total_tokens")
    #     query_usage = query_embed_response.get("usage").get("total_tokens")

    #     # Extracts embeddings from texts & query
    #     texts_embed = [item["embedding"] for item in texts_embed_response.get("data")]
    #     query_embed = query_embed_response["data"][0]["embedding"]

    #     items = []
    #     # Calculate score for each text index
    #     for index, text in enumerate(texts_embed):
    #         score = function_score(query_embed, text)
    #         items.append(
    #             InfosSearchDataClass(
    #                 object="search_result", document=index, score=score
    #             )
    #         )

    #     # Sort items by score in descending order
    #     sorted_items = sorted(items, key=lambda x: x.score, reverse=True)

    #     # Build the original response
    #     original_response = {
    #         "texts_embeddings": texts_embed_response,
    #         "embeddings_query": query_embed_response,
    #         "usage": {"total_tokens": texts_usage + query_usage},
    #     }

    #     result = ResponseType[SearchDataClass](
    #         original_response=original_response,
    #         standardized_response=SearchDataClass(items=sorted_items),
    #     )
    #     return result

    # def text__question_answer(
    #     self,
    #     texts: List[str],
    #     question: str,
    #     temperature: float,
    #     examples_context: str,
    #     examples: List[List[str]],
    #     model: Optional[str],
    # ) -> ResponseType[QuestionAnswerDataClass]:
    #     url = f"{self.url}/chat/completions"
    #     # With search get the top document with the question & construct the context
    #     document = self.text__search(texts, question).model_dump()
    #     context = document["standardized_response"]["items"][0]["document"]
    #     prompt_questions = [
    #         "\nQ:" + example[0] + "\nA:" + example[1] for example in examples
    #     ]
    #     prompts = [
    #         examples_context
    #         + "\n\n"
    #         + "".join(prompt_questions)
    #         + "\n\n"
    #         + texts[context]
    #         + "\nQ:"
    #         + question
    #         + "\nA:"
    #     ]
    #     payload = {
    #         "model": self.model,
    #         "prompt": prompts,
    #         "max_tokens": 100,
    #         "temperature": temperature,
    #         "top_p": 1,
    #         "frequency_penalty": 0,
    #         "presence_penalty": 0,
    #     }
    #     response = requests.post(url, json=payload, headers=self.headers)
    #     original_response = get_openapi_response(response)

    #     answers = []
    #     for choice in original_response["choices"]:
    #         answer = choice["text"]
    #         answers.append(answer)
    #     standardized_response = QuestionAnswerDataClass(answers=answers)

    #     result = ResponseType[QuestionAnswerDataClass](
    #         original_response=original_response,
    #         standardized_response=standardized_response,
    #     )
    #     return result

    def text__anonymization(
        self, text: str, language: str
    ) -> ResponseType[AnonymizationDataClass]:
        prompt = construct_anonymization_context(text)
        json_output = '{{"redactedText" : "...", "entities": [{{content: entity, label: category, confidence_score: confidence score, offset: start_offset}}]}}'
        messages = [{"role": "user", "content": prompt}]
        messages.insert(
            0,
            {
                "role": "system",
                "content": f"""Act as a PII system that takes a text input containing personally identifiable information (PII) and generates an anonymized version of the text, 
                you return a JSON object in this format : {json_output}""",
            },
        )
        # Build the request
        payload = {
            "response_format": {"type": "json_object"},
            "model": "grok-beta",
            "messages": messages,
        }
        url = f"{self.url}/chat/completions"
        response = requests.post(url, json=payload, headers=self.headers)
        original_response = get_openapi_response(response)
        pii_data = original_response["choices"][0]["message"]["content"]
        try:
            data_dict = json.loads(rf"{pii_data}")
        except json.JSONDecodeError:
            raise ProviderException("An error occurred while parsing the response.")
        new_text = text
        entities: Sequence[AnonymizationEntity] = []
        for entity in data_dict.get("entities", []):
            classificator = CategoryType.choose_category_subcategory(
                entity.get("label")
            )
            offset = closest_above_value(
                find_all_occurrence(text, entity.get("content", "")),
                entity.get("offset", 0),
            )
            length = len(entity.get("content", ""))
            try:
                entities.append(
                    AnonymizationEntity(
                        offset=offset,
                        length=length,
                        content=entity.get("content"),
                        original_label=entity.get("label"),
                        category=classificator["category"],
                        subcategory=classificator["subcategory"],
                        confidence_score=entity.get("confidence_score"),
                    )
                )
            except ValidationError as exc:
                raise ProviderException(
                    "An error occurred while parsing the response."
                ) from exc
            tmp_new_text = new_text[0:offset] + "*" * length
            tmp_new_text += new_text[offset + length :]
            new_text = tmp_new_text

        standardized_response = AnonymizationDataClass(
            result=new_text, entities=entities
        )
        return ResponseType[AnonymizationDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

    def text__keyword_extraction(
        self, language: str, text: str
    ) -> ResponseType[KeywordExtractionDataClass]:

        original_response, result = self.__assistant_text(
            name="Keywoord Extraction",
            instruction="You are an Keyword Extract model. You extract keywords from a text input.",
            message_text=text,
            example_file="outputs/text/keyword_extraction_output.json",
            dataclass=KeywordExtractionDataClass,
        )

        return ResponseType[KeywordExtractionDataClass](
            original_response=original_response,
            standardized_response=result,
        )

    def text__sentiment_analysis(
        self, language: str, text: str
    ) -> ResponseType[SentimentAnalysisDataClass]:

        original_response, result = self.__assistant_text(
            name="Sentiment Analysis",
            instruction="You are a Text Sentiment Analysis model. You extract the sentiment of a textual input.",
            message_text=text,
            example_file="outputs/text/sentiment_analysis_output.json",
            dataclass=SentimentAnalysisDataClass,
        )

        return ResponseType[SentimentAnalysisDataClass](
            original_response=original_response, standardized_response=result
        )

    def text__topic_extraction(
        self, language: str, text: str
    ) -> ResponseType[TopicExtractionDataClass]:

        original_response, result = self.__assistant_text(
            name="Topic Extraction",
            instruction="You are a Text Topic Exstraction Model. You extract the main topic of a textual input.",
            message_text=text,
            example_file="outputs/text/topic_extraction_output.json",
            dataclass=TopicExtractionDataClass,
        )

        return ResponseType[TopicExtractionDataClass](
            original_response=original_response,
            standardized_response=result,
        )

    def text__code_generation(
        self, instruction: str, temperature: float, max_tokens: int, prompt: str = ""
    ) -> ResponseType[CodeGenerationDataClass]:
        url = f"{self.url}/chat/completions"
        model = "grok-beta"

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Be helpful for code generation",
            },
            {"role": "user", "content": instruction},
        ]
        if prompt:
            messages.insert(1, {"role": "user", "content": prompt})

        payload = {
            "model": model,
            "temperature": temperature,
            "messages": messages,
            "max_completion_tokens": max_tokens,
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
        except requests.exceptions.ChunkedEncodingError:
            raise ProviderException("Connection closed with provider", 400)
        original_response = get_openapi_response(response)

        standardized_response = CodeGenerationDataClass(
            generated_text=original_response["choices"][0]["message"]["content"]
        )
        return ResponseType[CodeGenerationDataClass](
            original_response=original_response,
            standardized_response=standardized_response,
        )

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
        self, text: str, entities: List[str], examples: Optional[List[Dict]] = None
    ) -> ResponseType[CustomNamedEntityRecognitionDataClass]:

        original_response, result = self.__assistant_text(
            name="Custom NER",
            instruction="You are a Named Entity Extraction Model. Given a list of Entities Types and a text input, you should extract extract all entities of the given entities types.",
            message_text="""
                Entities to look for : 
                {}

                ======
                text : 

                {}
                """.format(
                entities, text
            ),
            example_file="outputs/text/custom_named_entity_recognition_output.json",
            dataclass=CustomNamedEntityRecognitionDataClass,
        )

        return ResponseType[CustomNamedEntityRecognitionDataClass](
            original_response=original_response,
            standardized_response=result,
        )

    def text__custom_classification(
        self, texts: List[str], labels: List[str], examples: List[List[str]]
    ) -> ResponseType[CustomClassificationDataClass]:

        original_response, result = self.__assistant_text(
            name="Custom classification",
            instruction="You are a Text Classification Model. Given a list of possible labels and a list of texts, you should classify each text by giving it one label.",
            message_text="""
                Possible Labels : 
                {}

                ======
                List of texts : 

                {}
                """.format(
                labels, texts
            ),
            example_file="outputs/text/custom_classification_output.json",
            dataclass=CustomClassificationDataClass,
        )

        return ResponseType[CustomClassificationDataClass](
            original_response=original_response, standardized_response=result
        )

    def text__spell_check(
        self, text: str, language: str
    ) -> ResponseType[SpellCheckDataClass]:

        original_response, result = self.__assistant_text(
            name="Spell Check",
            instruction="You are a Spell Checking model. You analyze a text input and proficiently detect and correct any grammar, syntax, spelling or other types of errors.",
            message_text=text,
            example_file="outputs/text/spell_check_output.json",
            dataclass=SpellCheckDataClass,
        )

        return ResponseType[SpellCheckDataClass](
            original_response=original_response,
            standardized_response=result,
        )

    def text__named_entity_recognition(
        self, language: str, text: str
    ) -> ResponseType[NamedEntityRecognitionDataClass]:

        original_response, result = self.__assistant_text(
            name="NER",
            instruction="You are a Named Entity Extraction Model. Given an input text you should extract extract all entities in it.",
            message_text=text,
            example_file="outputs/text/named_entity_recognition_output.json",
            dataclass=NamedEntityRecognitionDataClass,
        )

        return ResponseType[NamedEntityRecognitionDataClass](
            original_response=original_response, standardized_response=result
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
            "model": model,
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
                    provider="openai",
                )
                for chunk in response
                if chunk
            )

            return ResponseType[StreamChat](
                original_response=None, standardized_response=StreamChat(stream=stream)
            )

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
