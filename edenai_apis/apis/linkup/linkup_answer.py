from edenai_apis.utils.exception import ProviderException
from linkup import LinkupClient
from typing import Optional, List

class LinkupAnswer:

    def __init__(self):
        self.client = LinkupClient()

    def text__question_answer(
        self,
        query: str,
        depth: str,
        examples_context: Optional[str] = None,
        examples: Optional[List[List[str]]] = None,
        model: Optional[str] = None,
        texts: Optional[List[str]] = None,
        similarity_metric: Optional[str] = None,
    ):
        try:
            return self.client.search(
                query=query,
                depth=depth,
                output_type="sourcedAnswer")
        except Exception as e:
            print("DEBUG - Exception occurred:", str(e))
            raise ProviderException(f"Error during Linkup API call: {str(e)}")
