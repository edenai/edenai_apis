import logging
from typing import Any, List, Optional, TypeVar, Union

from pydantic import BaseModel, ValidationError

T = TypeVar("T")


def extract(
    obj: Union[dict, list],
    path: List[Union[str, int]],
    fallback: T = None,
    type_validator: Optional[type] = None,
) -> Union[Any, T]:
    """
    Extract a value from a dict given a path & optional fallback + type validator

    Args:
        obj (dict): object to extract value from
        path (List[str | int]): list of keys/indexed representing the path of the value to extract (eg: obj['result'][0] will be ['result', 0])
        fallback (T), optional: fallback value if something goes wrong while trying to get extract value
        type_validator (type), optional: expected type of extracted value, if they are different, we return the fallback

    Returns:
        Any | T: extracted value of Any type or fallback type

    Example:
      Extract a value from an object
      >>> obj = {"one": {"two": [0, "result", 0]}}
      >>> extract(obj, ["one", "two", 1])
      "result"

      Get fallback Value if extraction failed
      >>> obj = {"one": {"two": [0, "result", 0]}}
      >>> extract(obj, ["one", "two", 3], fallback="FALLBACK_VALUE")
      "FALLBACK_VALUE"

      Simple type validation, return fallback if validation fails
      >>> obj = {"one": {"two": [0, "result", 0]}}
      >>> extract(obj, ["one", "two", 3], fallback="FALLBACK_VALUE", type_validator=int)
      "FALLBACK_VALUE"
    """
    result = obj
    try:
        for key in path:
            result = result[key]  # type: ignore
    except (KeyError, IndexError, TypeError) as exc:
        logging.warning(
            f"{exc.__class__.__name__}: {exc} while trying to extract {path} of object {obj}, returning fallback: {fallback}"
        )
        return fallback

    if type_validator is not None and type(result) != type_validator:
        logging.warning(
            f"Object {result} of type {type(result)} is not of expected type: {type_validator}, returning fallback: {fallback}"
        )
        return fallback

    return result


class NoRaiseBaseModel(BaseModel):
    """
    Catch ValidationError from pydantic BaseModel,
    set the invalid fields at `None` and log the error instead of raising it
    """

    __pydantic_extra__ = None
    __pydantic_private__ = None

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except ValidationError as pve:
            for error in pve.errors():
                name = str(error["loc"][0])
                logging.error(
                    "Pydantic ValidationError in %s: %s",
                    str(self.__class__.__qualname__),
                    str(error),
                )
                data[name] = None

            fields_set = set(data.keys())
            for key, value in self.model_construct(fields_set, **data).__dict__.items():
                self.__dict__[key] = value
