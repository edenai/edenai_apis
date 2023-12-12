from utils.parsing import NoRaiseBaseModel
from enum import Enum
from typing import Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, FieldSerializationInfo, field_serializer

from edenai_apis.features.text.moderation.category import (
    CategoryType,
)
from edenai_apis.features.text.moderation.subcategory import (
    ToxicSubCategoryType,
    ContentSubCategoryType,
    SexualSubCategoryType,
    ViolenceSubCategoryType,
    DrugAndAlcoholSubCategoryType,
    FinanceSubCategoryType,
    HateAndExtremismSubCategoryType,
    SafeSubCategoryType,
    OtherSubCategoryType,
)

SubCategoryType = Union[
    ToxicSubCategoryType,
    ContentSubCategoryType,
    SexualSubCategoryType,
    ViolenceSubCategoryType,
    DrugAndAlcoholSubCategoryType,
    FinanceSubCategoryType,
    HateAndExtremismSubCategoryType,
    SafeSubCategoryType,
    OtherSubCategoryType,
]
class TextModerationCategoriesMicrosoftEnum(Enum):
    Category1 = "sexually explicit"
    Category2 = "sexually suggestive"
    Category3 = "offensive"


class TextModerationItem(NoRaiseBaseModel):
    label: StrictStr
    likelihood: int
    category: CategoryType
    subcategory: SubCategoryType
    likelihood_score: float

    model_config = ConfigDict(use_enum_values=True)
    @field_serializer('subcategory', mode="plain", when_used="always")
    def serialize_subcategory(self, value: SubCategoryType, _: FieldSerializationInfo):
        return value.value

class ModerationDataClass(NoRaiseBaseModel):
    nsfw_likelihood: int
    items: Sequence[TextModerationItem] = Field(default_factory=list)
    nsfw_likelihood_score : float

    @field_validator("nsfw_likelihood")
    @classmethod
    def check_min_max(cls, value):
        if not 0 <= value <= 5:
            raise ValueError("Likelihood walue should be between 0 and 5")
        return value


    @staticmethod
    def calculate_nsfw_likelihood(items: Sequence[TextModerationItem]):
        if len(items) == 0:
            return 0
        return max([item.likelihood for item in items])

    @field_validator("nsfw_likelihood_score")
    @classmethod
    def check_min_max_score(cls, value):
        if not 0 <= value <= 1:
            raise ValueError("Likelihood walue should be between 0 and 1")
        return value

    @staticmethod
    def calculate_nsfw_likelihood_score(items: Sequence[TextModerationItem]):
        if len(items) == 0:
            return 0
        return max([item.likelihood_score for item in items])
