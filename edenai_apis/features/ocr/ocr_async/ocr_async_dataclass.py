import enum
from typing import Callable, Optional, Sequence, List

from pydantic import Field, field_validator
from utils.parsing import NoRaiseBaseModel


class BoundingBoxEnum(enum.Enum):
    """Enum for the keys of the bounding box JSON object

    Attributes:
        LEFT (int): Index of the left coordinate of the bounding box
        TOP (int): Index of the top coordinate of the bounding box
        WIDTH (int): Index of the width of the bounding box
        HEIGHT (int): Index of the height of the bounding box
    """

    LEFT = 0
    TOP = 1
    WIDTH = 2
    HEIGHT = 3


class BoundingBoxCornerEnum(enum.Enum):
    """Enum for the corners of the bounding box

    Attributes:
        TOP_LEFT (int): Index of the top left corner of the bounding box
        TOP_RIGHT (int): Index of the top right corner of the bounding box
        BOTTOM_LEFT (int): Index of the bottom left corner of the bounding box
        BOTTOM_RIGHT (int): Index of the bottom right corner of the bounding box
    """

    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3


class CoordinateEnum(enum.Enum):
    """Enum for the keys of the coordinate JSON object

    Attributes:
        X (int): Index of the X coordinate of the bounding box
        Y (int): Index of the Y coordinate of the bounding box
    """

    X = 0
    Y = 1


class BoundingBox(NoRaiseBaseModel):
    """Bounding box of a word in the image


    Attributes:
        left (float): Left coordinate of the bounding box
        top (float): Top coordinate of the bounding box
        width (float): Width of the bounding box
        height (float): Height of the bounding box
        text (str): Text detected in the bounding box

    Constructor:
        from_json (classmethod): Create a new instance of BoundingBox from a JSON object
        from_normalized_vertices (classmethod): Create a new instance of BoundingBox from normalized vertices
    """

    left: float = Field(description="Left coordinate of the bounding box")
    top: float = Field(description="Top coordinate of the bounding box")
    width: float = Field(description="Width of the bounding box")
    height: float = Field(description="Height of the bounding box")

    @field_validator("left", "top", "width", "height", mode="before")
    def convert_to_float(cls, value):
        """Convert the value to float

        Args:
            value (Any): Value to convert

        Returns:
            float: Converted value
        """
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"Value {value} cannot be converted to float") from exc

    @classmethod
    def from_json(
        cls,
        bounding_box: dict,
        modifiers: Callable = lambda x: x,
        keys: Sequence[str] = ["left", "top", "width", "height"],
    ):
        """Create a new instance of BoundingBox from a JSON object
        Args:
            bounding_box (dict): JSON object representing the bounding box
            modifiers (callable): Function to apply to the keys of the JSON object (default: lambda x: x).
            keys (Sequence[str]): Keys of the JSON object (default: ["left", "top", "width", "height"])

        Returns:
            BoundingBox: BoundingBox created from the JSON object
        """
        return cls(
            left=bounding_box[modifiers(keys[BoundingBoxEnum.LEFT.value])],
            top=bounding_box[modifiers(keys[BoundingBoxEnum.TOP.value])],
            width=bounding_box[modifiers(keys[BoundingBoxEnum.WIDTH.value])],
            height=bounding_box[modifiers(keys[BoundingBoxEnum.HEIGHT.value])],
        )

    @classmethod
    def from_normalized_vertices(
        cls,
        normalized_vertices: list,
        coordinate_keys: Sequence[str] = ["x", "y"],
        corner_position_keys: Sequence[int] = [0, 1, 2, 3],
    ):
        """Create a new instance of BoundingBox from a list of normalized vertices

        Args:
            normalized_vertices (list): List of normalized vertices
            coordinate_keys (Sequence[str | int]): Keys of the JSON object (default: ["x", "y"]).
            corner_position_keys (Sequence[int | str]): Keys of the JSON object (default: [0, 1, 2, 3]).

        Returns:
            BoundingBox: BoundingBox created from the list of normalized vertices.

        Dependencies:
            BoundingBox.from_json
        """
        boxes = {}

        # x_key and y_key are the coordinate keys of the normalized vertices after applying the modifiers
        x_key = coordinate_keys[CoordinateEnum.X.value]
        y_key = coordinate_keys[CoordinateEnum.Y.value]

        top_left_key = corner_position_keys[BoundingBoxCornerEnum.TOP_LEFT.value]
        top_right_key = corner_position_keys[BoundingBoxCornerEnum.TOP_RIGHT.value]
        bottom_left_key = corner_position_keys[BoundingBoxCornerEnum.BOTTOM_LEFT.value]

        xleft = normalized_vertices[top_left_key][x_key]
        xright = normalized_vertices[top_right_key][x_key]
        ytop = normalized_vertices[top_left_key][y_key]
        ybottom = normalized_vertices[bottom_left_key][y_key]

        boxes = {
            "left": xleft,
            "top": ytop,
            "width": xright - xleft,
            "height": ybottom - ytop,
        }

        return cls.from_json(boxes)


class Word(NoRaiseBaseModel):
    """Word of a document

    Attributes:
        text (str): Text detected in the word
        bounding_boxes (Sequence[BoundingBox]): Bounding boxes of the words in the word
        confidence (float): Confidence score of the word
    """

    text: str = Field(description="Text detected in the word")
    bounding_box: BoundingBox = Field(
        description="Bounding boxes of the words in the word"
    )
    confidence: Optional[float] = Field(..., description="Confidence score of the word")

    @field_validator("confidence")
    def round_confidence(cls, v):
        """Round confidence to 2 decimals"""
        if v is not None:
            return round(v, 2)
        return v


class Line(NoRaiseBaseModel):
    """Line of a document

    Attributes:
        text (str): Text detected in the line
        bounding_boxes (Sequence[BoundingBox]): Bounding boxes of the words in the line
        words (Sequence[Word]): List of words of the line
        confidence (float): Confidence of the line
    """

    text: str = Field(description="Text detected in the line")
    words: Sequence[Word] = Field(default_factory=list, description="List of words")
    bounding_box: BoundingBox = Field(
        description="Bounding boxes of the words in the line"
    )
    confidence: Optional[float] = Field(..., description="Confidence of the line")

    @field_validator("confidence")
    @classmethod
    def round_confidence(cls, v):
        """Round confidence to 2 decimals"""
        if v is not None:
            return round(v, 2)
        return v


class Page(NoRaiseBaseModel):
    """Page of a document

    Attributes:
        lines (Sequence[Line]): List of lines of the page
    """

    lines: Sequence[Line] = Field(default_factory=list, description="List of lines")


class OcrAsyncDataClass(NoRaiseBaseModel):
    """OCR Async Data Class

    Attributes:
        pages (Sequence[Page]): Pages of the document
    """

    raw_text: str
    pages: List[Page] = Field(default_factory=list, description="List of pages")
    number_of_pages: Optional[int] = Field(
        description="Number of pages in the document",
    )
