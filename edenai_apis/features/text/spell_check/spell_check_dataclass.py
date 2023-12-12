from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence, List

from pydantic import BaseModel, Field


class SuggestionItem(NoRaiseBaseModel):
    """
    Represents a suggestion for a misspelled word.

    Args:
        suggestion (str): The suggested text.
        score (float, optional): The score of the suggested text (between 0 and 1).

    Raises:
        ValueError: If the score is not between 0 and 1.

    Returns:
        SuggestionItem: An instance of the SuggestionItem class.
    """

    suggestion: str
    score: Optional[float] = Field(ge=0, le=1)


class SpellCheckItem(NoRaiseBaseModel):
    """Represents a spell check item with suggestions.

    Args:
        text (str): The text to spell check.
        type (str, optional): The type of the text.
        offset (int): The offset of the text.
        length (int): The length of the text.
        suggestions (Sequence[SuggestionItem], optional): The list of suggestions for the misspelled text.

    Raises:
        ValueError: If the offset or length is not positive.

    Returns:
        SpellCheckItem: An instance of the SpellCheckItem class.
    """

    text: str
    type: Optional[str]
    offset: int = Field(ge=0)
    length: int = Field(ge=0)
    suggestions: List[SuggestionItem] = Field(default_factory=list)


class SpellCheckDataClass(NoRaiseBaseModel):
    """
    Represents a spell check model with a list of spell check items.

    Args:
        text (str): The text to spell check.
        items (Sequence[SpellCheckItem], optional): The list of spell check items.

    Returns:
        SpellCheckDataClass: An instance of the SpellCheckDataClass class.
    """

    text: str
    items: Sequence[SpellCheckItem] = Field(default_factory=list)
