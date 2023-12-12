from utils.parsing import NoRaiseBaseModel
from pydantic import BaseModel

class AnonymizationAsyncDataClass(NoRaiseBaseModel):
    document: str
    document_url : str
