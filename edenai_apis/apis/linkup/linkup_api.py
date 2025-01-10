from edenai_apis.features.provider.provider_interface import ProviderInterface
from edenai_apis.loaders.loaders import load_provider, ProviderDataEnum
from edenai_apis.utils.exception import ProviderException
from linkup import LinkupClient
from typing import Dict, List, Optional
from pydantic import BaseModel

class SearchResult(BaseModel):
    type: str
    name: Optional[str]
    url: Optional[str]
    content: Optional[str]

class StandardizedResponse(BaseModel):
    results: List[SearchResult]

class ApiResponse(BaseModel):
    original_response: Dict
    standardized_response: StandardizedResponse

class LinkupApi(ProviderInterface):
    provider_name = "linkup"

    def __init__(self, api_keys: Dict = {}):
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_keys
        )
        self.client = LinkupClient(api_key=self.api_settings["api_key"])

    def text__search(
        self,
        query: str,
        output_type: str = "searchResults",
        depth: str = "standard",
        structured_output_schema: Optional[dict] = None,
        model: Optional[str] = None,
        texts: Optional[List[str]] = None,
        similarity_metric: str = "cosine",
    ):
        try:
            if model and ":" in model:
                params = model.split(":")
                if len(params) >= 1:
                    output_type = params[0]
                if len(params) >= 2:
                    depth = params[1]

            payload = {
                "query": query,
                "depth": depth,
                "output_type": output_type,
            }

            if output_type == "structured" and structured_output_schema:
                payload["structured_output_schema"] = structured_output_schema

            response = self.client.search(**payload)

            print("DEBUG - Response:", response)

            if output_type in ["searchResults", "sourcedAnswer"]:
                sources = getattr(response, "sources", getattr(response, "results", []))
                if not isinstance(sources, list):
                    raise ProviderException("Invalid format for response.sources; expected a list.")

                standardized_response = StandardizedResponse(
                    results=[
                        SearchResult(
                            type="text",
                            name=getattr(source, "name", None),
                            url=getattr(source, "url", None),
                            content=getattr(source, "snippet", None),
                        )
                        for source in sources
                    ]
                )

                return ApiResponse(
                    original_response={
                        "answer": getattr(response, "answer", None),
                        "sources": sources,
                    },
                    standardized_response=standardized_response,
                )

            elif output_type == "structured":
                structured_data = getattr(response, "structured_data", response)
                if not isinstance(structured_data, dict):
                    raise ProviderException("Response does not contain valid 'structured_data'.")

                return ApiResponse(
                    original_response=structured_data,
                    standardized_response=StandardizedResponse(
                        results=[
                            SearchResult(
                                type="structured",
                                name=structured_data.get("name"),
                                url=structured_data.get("url"),
                                content=structured_data.get("content"),
                            )
                        ]
                    ),
                )

            else:
                raise ProviderException(f"Unsupported output_type: {output_type}")
        except Exception as e:
            print("DEBUG - Exception occurred:", str(e))
            raise ProviderException(f"Error during Linkup API call: {str(e)}")
