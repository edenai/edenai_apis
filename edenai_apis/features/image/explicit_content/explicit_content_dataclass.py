from utils.parsing import NoRaiseBaseModel
from typing import Sequence, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictStr,
    field_validator,
    field_serializer,
    FieldSerializationInfo,
)

from edenai_apis.features.image.explicit_content.category import CategoryType
from edenai_apis.features.image.explicit_content.subcategory import (
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


class ExplicitItem(NoRaiseBaseModel):
    label: StrictStr
    likelihood: int
    likelihood_score: float
    category: CategoryType
    subcategory: SubCategoryType

    model_config = ConfigDict(use_enum_values=True)

    @field_serializer("subcategory", mode="plain", when_used="always")
    def serialize_subcategory(self, value: SubCategoryType, _: FieldSerializationInfo):
        return value.value


class ExplicitContentDataClass(NoRaiseBaseModel):
    nsfw_likelihood: int
    nsfw_likelihood_score: float
    items: Sequence[ExplicitItem] = Field(default_factory=list)

    @field_validator("nsfw_likelihood")
    def check_min_max(cls, v):
        if not 0 <= v <= 5:
            raise ValueError("Value should be between 0 and 5")
        return v

    @staticmethod
    def calculate_nsfw_likelihood(items: Sequence[ExplicitItem]):
        if len(items) == 0:
            return 0
        safe_labels = ("safe", "sfw")
        return max([item.likelihood for item in items if item.label not in safe_labels])

    @staticmethod
    def calculate_nsfw_likelihood_score(items: Sequence[ExplicitItem]):
        if len(items) == 0:
            return 0
        safe_labels = ("safe", "sfw")
        return max(
            [item.likelihood_score for item in items if item.label not in safe_labels]
        )

    @field_validator("nsfw_likelihood_score")
    def check_min_max_score(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Value should be between 0 and 1")
        return v
