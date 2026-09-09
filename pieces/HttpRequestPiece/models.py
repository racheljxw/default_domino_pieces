from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class MethodTypes(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class FetchResult(BaseModel):
    url: str = Field(
        description="The URL this entry corresponds to."
    )
    status: str = Field(
        description='Outcome of the request: "success" or "failed".'
    )
    base64_content: Optional[str] = Field(
        default=None,
        description="Response content as a base64 encoded string. Set when status is 'success'."
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message. Set when status is 'failed'."
    )


class InputModel(BaseModel):
    urls: List[str] = Field(
        default=[],
        description="List of URLs to make requests to. Each URL produces one entry in the output."
    )
    method: MethodTypes = Field(
        default=MethodTypes.GET,
        description="HTTP method to use for every request."
    )
    bearer_token: Optional[str] = Field(
        default=None,
        description="Bearer token to use for authentication."
    )
    body_json_data: str = Field(
        default="""{
    "key_1": "value_1",
    "key_2": "value_2"
}
""",
        description="JSON data to send in the request body. Used for POST and PUT requests.",
        json_schema_extra={
            'widget': "codeeditor-json",
        }
    )


class OutputModel(BaseModel):
    results: List[FetchResult] = Field(
        default=[],
        description='One entry per input URL, in the same order, whether the request succeeded or failed.'
    )
