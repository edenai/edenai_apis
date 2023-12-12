from utils.parsing import NoRaiseBaseModel
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr


class BoundixBoxOCRTable(NoRaiseBaseModel):
    left: Optional[float]
    top: Optional[float]
    width: Optional[float]
    height: Optional[float]


class Cell(NoRaiseBaseModel):
    text: Optional[StrictStr]
    row_index: Optional[int]
    col_index: Optional[int]
    row_span: Optional[int]
    col_span: Optional[int]
    confidence: Optional[float]
    bounding_box: BoundixBoxOCRTable
    is_header: bool = False


class Row(NoRaiseBaseModel):
    cells: List[Cell] = Field(default_factory=list)


class Table(NoRaiseBaseModel):
    rows: List[Row] = Field(default_factory=list)
    num_rows: Optional[int]
    num_cols: Optional[int]


class Page(NoRaiseBaseModel):
    tables: List[Table] = Field(default_factory=list)


class OcrTablesAsyncDataClass(NoRaiseBaseModel):
    pages: List[Page] = Field(default_factory=list)
    num_pages: Optional[int]
