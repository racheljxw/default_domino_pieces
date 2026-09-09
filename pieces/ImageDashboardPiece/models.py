from pydantic import BaseModel, Field
from typing import List, Optional


class FilterResult(BaseModel):
    """One entry from ImageFilterPiece's output. Defined here so this Piece stays self-contained."""
    url: str = Field(
        description="The URL this entry corresponds to."
    )
    status: str = Field(
        description='Filtering outcome: "success" or "failed".'
    )
    filtered_image: Optional[str] = Field(
        default=None,
        description="Filtered image as a base64 encoded PNG string. Set when status is 'success'."
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message. Set when status is 'failed'."
    )


class InputModel(BaseModel):
    results: List[FilterResult] = Field(
        description="The full results list from ImageFilterPiece.",
        json_schema_extra={
            "from_upstream": "always"
        }
    )


class OutputModel(BaseModel):
    dashboard_file_path: str = Field(
        default="",
        description="Path to the generated self-contained HTML dashboard file in shared storage."
    )
