from utils.parsing import NoRaiseBaseModel
import datetime
import json
import os
from enum import Enum
from typing import Any, List, Optional, Sequence, Union

from dateutil import parser
from pydantic import (
    BaseModel,
    Field,
    StrictStr,
    field_validator,
)


def format_date(value: Any) -> Union[str, None]:
    """
    try returning a string date from value.
    format: YYYY-MM-DD
    """
    if not value:
        return None
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    try:
        value = parser.parse(value)
    except parser.ParserError:
        return None

    return value.strftime("%Y-%m-%d")


class Country(NoRaiseBaseModel):
    name: Optional[StrictStr]
    alpha2: Optional[StrictStr]
    alpha3: Optional[StrictStr]
    confidence: Optional[float] = None

    @staticmethod
    def default():
        return Country(name=None, alpha2=None, alpha3=None, confidence=None)


class InfoCountry(Enum):
    NAME = "name"
    ALPHA2 = "alpha2"
    ALPHA3 = "alpha3"


def get_info_country(key: InfoCountry, value: StrictStr) -> Optional[Country]:
    feature_path = os.path.dirname(os.path.dirname(__file__))

    if not value or not key:
        return None

    with open(
        f"{feature_path}/identity_parser/countries.json", "r", encoding="utf-8"
    ) as f:
        countries = json.load(f)
        country_idx = next(
            (
                index
                for (index, country) in enumerate(countries)
                if country[key.value].lower() == value.lower()
            ),
            None,
        )
        if country_idx:
            return countries[country_idx]
    return None


class ItemIdentityParserDataClass(NoRaiseBaseModel):
    value: Optional[StrictStr] = None
    confidence: Optional[float] = None


class InfosIdentityParserDataClass(NoRaiseBaseModel):
    last_name: ItemIdentityParserDataClass
    given_names: List[ItemIdentityParserDataClass] = Field(default_factory=list)
    birth_place: ItemIdentityParserDataClass
    birth_date: ItemIdentityParserDataClass
    issuance_date: ItemIdentityParserDataClass
    expire_date: ItemIdentityParserDataClass
    document_id: ItemIdentityParserDataClass
    issuing_state: ItemIdentityParserDataClass
    address: ItemIdentityParserDataClass
    age: ItemIdentityParserDataClass
    country: Optional[Country]
    document_type: ItemIdentityParserDataClass
    gender: ItemIdentityParserDataClass
    image_id: Sequence[ItemIdentityParserDataClass] = Field(default_factory=list)
    image_signature: Sequence[ItemIdentityParserDataClass] = Field(default_factory=list)
    mrz: ItemIdentityParserDataClass
    nationality: ItemIdentityParserDataClass

    @field_validator("last_name")
    def to_uppercase(cls, value):
        value.value = value.value.upper() if value.value else None
        return value

    @field_validator("birth_place", "nationality", "issuing_state", "document_type")
    def to_title(cls, value):
        value.value = value.value.title() if value.value else None
        return value

    @field_validator("given_names")
    def given_names_to_title(cls, value):
        for v in value:
            v.value = v.value.title() if v.value else None
        return value

    @field_validator("expire_date", "issuance_date", "birth_date")
    def date_validator(cls, value):
        if not value.value:
            return {"value": None, "confidence": None}
        try:
            datetime.datetime.strptime(value.value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return value

    @staticmethod
    def default():
        return InfosIdentityParserDataClass(
            last_name=ItemIdentityParserDataClass(),
            birth_place=ItemIdentityParserDataClass(),
            birth_date=ItemIdentityParserDataClass(),
            issuance_date=ItemIdentityParserDataClass(),
            expire_date=ItemIdentityParserDataClass(),
            document_id=ItemIdentityParserDataClass(),
            issuing_state=ItemIdentityParserDataClass(),
            address=ItemIdentityParserDataClass(),
            age=ItemIdentityParserDataClass(),
            country=Country.default(),
            document_type=ItemIdentityParserDataClass(),
            gender=ItemIdentityParserDataClass(),
            mrz=ItemIdentityParserDataClass(),
            nationality=ItemIdentityParserDataClass(),
        )


class IdentityParserDataClass(NoRaiseBaseModel):
    extracted_data: Sequence[InfosIdentityParserDataClass] = Field(default_factory=list)
