from pydantic import BaseModel, Field
from typing import List, Optional


class FetchResult(BaseModel):
    """One entry from HttpRequestPiece's output. Defined here so this Piece stays self-contained."""
    url: str = Field(
        description="The URL this entry corresponds to."
    )
    status: str = Field(
        description='Upstream fetch outcome: "success" or "failed".'
    )
    base64_content: Optional[str] = Field(
        default=None,
        description="Fetched content as a base64 encoded string. Set when status is 'success'."
    )
    error: Optional[str] = Field(
        default=None,
        description="Upstream error message. Set when status is 'failed'."
    )


class FilterResult(BaseModel):
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
    results: List[FetchResult] = Field(
        description="The full results list from HttpRequestPiece. One filtered entry is produced per URL.",
        json_schema_extra={
            "from_upstream": "always"
        }
    )
    sepia: bool = Field(
        default=False,
        description='Apply sepia effect.',
    )
    black_and_white: bool = Field(
        default=False,
        description='Apply black and white effect.',
    )
    brightness: bool = Field(
        default=False,
        description='Apply brightness effect.',
    )
    darkness: bool = Field(
        default=False,
        description='Apply darkness effect.',
    )
    contrast: bool = Field(
        default=False,
        description='Apply contrast effect.',
    )
    red: bool = Field(
        default=False,
        description='Apply red effect.',
    )
    green: bool = Field(
        default=False,
        description='Apply green effect.',
    )
    blue: bool = Field(
        default=False,
        description='Apply blue effect.',
    )
    cool: bool = Field(
        default=False,
        description='Apply cool effect.',
    )
    warm: bool = Field(
        default=False,
        description='Apply warm effect.',
    )


class OutputModel(BaseModel):
    results: List[FilterResult] = Field(
        default=[],
        description='One entry per input URL, in the same order, whether filtering succeeded or failed.'
    )
