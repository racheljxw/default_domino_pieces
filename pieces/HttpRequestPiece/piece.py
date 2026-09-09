from domino.base_piece import BasePiece
from .models import InputModel, OutputModel, FetchResult
import requests
import base64
import json


REQUEST_TIMEOUT_SECONDS = 10


class HttpRequestPiece(BasePiece):
    def piece_function(self, input_data: InputModel):

        method = input_data.method

        headers = {}
        if input_data.bearer_token:
            headers['Authorization'] = f'Bearer {input_data.bearer_token}'

        # Prepare the request body once, shared by all URLs (POST/PUT only).
        # An invalid body is a configuration error, not a per-URL failure, so it hard-fails here.
        body_data = None
        if method in ["POST", "PUT"]:
            try:
                body_data = json.loads(input_data.body_json_data)
            except json.JSONDecodeError:
                raise Exception("Invalid JSON data in the request body.")

        results = []
        for url in input_data.urls:
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json=body_data, timeout=REQUEST_TIMEOUT_SECONDS)
                elif method == "PUT":
                    response = requests.put(url, headers=headers, json=body_data, timeout=REQUEST_TIMEOUT_SECONDS)
                elif method == "DELETE":
                    response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
                else:
                    raise Exception(f"Unsupported HTTP method: {method}")

                response.raise_for_status()

                base64_content = base64.b64encode(response.content).decode('utf-8')
                results.append(FetchResult(
                    url=url,
                    status="success",
                    base64_content=base64_content,
                ))
            except requests.RequestException as e:
                self.logger.info(f"Request to {url} failed: {e}")
                results.append(FetchResult(
                    url=url,
                    status="failed",
                    error=str(e),
                ))

        n_failed = sum(1 for r in results if r.status == "failed")
        self.logger.info(f"Fetched {len(results)} URL(s): {len(results) - n_failed} succeeded, {n_failed} failed.")

        return OutputModel(results=results)
