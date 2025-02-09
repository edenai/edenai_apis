from edenai_apis.utils.exception import ProviderException
from linkup import LinkupClient
from typing import Optional, List


class LinkupSearch:

    def __init__(self):
        self.client = LinkupClient()
    
    def text__search(
        self,
        query: str,
        depth: str,
        model: Optional[str] = None,
        texts: Optional[List[str]] = None,
        similarity_metric: str= "cosine"
    ):
        try:
            result = self.client.search(
                query=query,
                depth=depth,
                output_type="searchResults")
            return result
        except Exception as e:
            raise ProviderException(f"Error during Linkup API call: {str(e)}")
