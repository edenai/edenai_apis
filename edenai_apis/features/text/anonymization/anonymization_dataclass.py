from utils.parsing import NoRaiseBaseModel
from typing import Dict, Optional, Sequence, Union
from pydantic import BaseModel, ConfigDict, Field, FieldSerializationInfo, field_serializer, field_validator, model_validator

from edenai_apis.features.text.anonymization.category import (
    CategoryType,
)
from edenai_apis.features.text.anonymization.subcategory import (
    FinancialInformationSubCategoryType,
    PersonalInformationSubCategoryType,
    IdentificationNumbersSubCategoryType,
    MiscellaneousSubCategoryType,
    OrganizationSubCategoryType,
    DateAndTimeSubCategoryType,
    LocationInformationSubCategoryType,
    OtherSubCategoryType,
)
from typing import Dict, Optional, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, FieldSerializationInfo, field_serializer, field_validator, \
    model_validator

from edenai_apis.features.text.anonymization.category import (
    CategoryType,
)
from edenai_apis.features.text.anonymization.subcategory import (
    FinancialInformationSubCategoryType,
    PersonalInformationSubCategoryType,
    IdentificationNumbersSubCategoryType,
    MiscellaneousSubCategoryType,
    OrganizationSubCategoryType,
    DateAndTimeSubCategoryType,
    LocationInformationSubCategoryType,
    OtherSubCategoryType,
)

SubCategoryType = Union[
    FinancialInformationSubCategoryType,
    PersonalInformationSubCategoryType,
    IdentificationNumbersSubCategoryType,
    MiscellaneousSubCategoryType,
    OrganizationSubCategoryType,
    DateAndTimeSubCategoryType,
    LocationInformationSubCategoryType,
    OtherSubCategoryType,
]


class AnonymizationEntity(NoRaiseBaseModel):
    """This model represents an entity extracted from the text.

    Attributes:
        offset (int): The offset of the entity in the text.
        length (int): The lenght of the entity in the text.
        category (CategoryType): The category of the entity.
        subcategory (SubCategoryType): The subcategory of the entity.
        original_label (str): The original label of the entity.
        content (str): The content of the entity.
    """

    offset: int = Field(..., ge=0)
    length: int = Field(..., gt=0)
    category: CategoryType
    subcategory: SubCategoryType
    original_label: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    confidence_score: Optional[float] = Field(..., ge=0, le=1)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("content", mode="before")
    @classmethod
    def content_must_be_str(cls, v):
        if not isinstance(v, str):
            raise TypeError("entity must be a string")
        return v

    @field_validator("original_label", mode="before")
    @classmethod
    def original_label_must_be_str(cls, v):
        if not isinstance(v, str):
            raise TypeError("original_label must be a string")
        return v

    @model_validator(mode="after")
    def content_length_must_be_equal_to_length(self):
        if len(self.content) != self.length:
            raise ValueError("content length must be equal to length")
        return self

    @field_validator("confidence_score")
    @classmethod
    def round_confidence_score(cls, v):
        if v is not None:
            return round(v, 3)
        return v

    @field_serializer('subcategory', mode="plain", when_used="always")
    def serialize_subcategory(self, value: SubCategoryType, _: FieldSerializationInfo):
        return value.value


class AnonymizationDataClass(NoRaiseBaseModel):
    """This model represents the response from the API.

    Attributes:
        result (str): The anonymized text.
        entities (List[AnonymizationEntity]): The entities extracted from the text.
    """

    result: str
    entities: Sequence[AnonymizationEntity] = Field(default_factory=list)

    @field_validator("result", mode="before")
    def result_must_be_str(cls, v):
        if not isinstance(v, str):
            raise TypeError("result must be a string")
        return v

    @staticmethod
    def direct_response(api_response: Dict):
        return api_response["result"]
