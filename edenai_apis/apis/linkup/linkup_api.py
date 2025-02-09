from edenai_apis.features.provider.provider_interface import ProviderInterface
from edenai_apis.loaders.loaders import load_provider, ProviderDataEnum
from linkup import LinkupClient
from typing import Dict
from edenai_apis.apis.linkup.linkup_search import LinkupSearch
from edenai_apis.apis.linkup.linkup_answer import LinkupAnswer


class LinkupApi(ProviderInterface, LinkupSearch, LinkupAnswer):


    provider_name = "linkup"

    def __init__(self, api_keys: Dict = {}):
        self.api_settings = load_provider(
            ProviderDataEnum.KEY, self.provider_name, api_keys=api_keys
        )
        self.client = LinkupClient(api_key=self.api_settings["api_key"])
