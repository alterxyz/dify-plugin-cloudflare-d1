from typing import Dict, Any, List, Optional
from collections.abc import Generator

import httpx
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class QueryAdvanced(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            account_id = tool_parameters["account_id"]
        except KeyError:
            account_id = self.runtime.credentials["cloudflare_account_id"]
        try:
            api_token = tool_parameters["api_token"]
        except KeyError:
            api_token = self.runtime.credentials["cloudflare_api_token"]

        database_id = tool_parameters["database_id"]
        sql_query = tool_parameters["query"]
        try:
            params = tool_parameters["params"]
        except KeyError:
            params = ""

        result = query_cloudflare_d1(
            account_id, database_id, api_token, sql_query, params
        )

        if "error" in result:
            error_message = f"Cloudflare D1 Query Error: {result['error']}. "
            if "metadata" in result:
                metadata = result["metadata"]
                error_message += "Details: "
                if "http_status" in metadata:
                    error_message += f"HTTP Status: {metadata['http_status']}, "
                if "detail" in metadata:
                    error_message += f"Detail: {metadata['detail']}, "
                if "response_payload" in metadata:
                    error_message += f"Response Payload: {metadata['response_payload']}"
                if "details" in metadata: # For cloudflare_d1_error original structure
                    error_message += f"D1 Error Details: {metadata['details']}"
                if "raw_response" in metadata: # For cloudflare_d1_error original structure
                    error_message += f"Raw Response: {metadata['raw_response']}"

            raise Exception(error_message) # Raise exception if there's an error

        yield self.create_json_message(result) # Only yield message if successful


def query_cloudflare_d1(
    account_id: str,
    database_id: str,
    api_token: str,
    sql_query: str,
    params: Optional[str]
) -> Dict[str, Any]:
    """
    Execute a query on the Cloudflare D1 database.

    Args:
        account_id: Cloudflare account ID.
        database_id: D1 database ID.
        api_token: Cloudflare API Bearer Token.
        sql_query: SQL query to be executed (using ? as a placeholder).
        params: JSON array string of SQL query parameters, e.g., '["value1", "value2"]'.
                If no parameters are needed, pass None or an empty string.

    Returns:
        If the request is successful, returns a dictionary with "success": True and the result in "metadata".
        If the request fails, returns a dictionary with "error" and error details in "metadata".
    """
    # Parameter validation
    if not account_id:
        return {"error": "invalid_parameter", "metadata": "account_id cannot be empty"}
    if not database_id:
        return {"error": "invalid_parameter", "metadata": "database_id cannot be empty"}
    if not sql_query:
        return {"error": "invalid_parameter", "metadata": "sql_query cannot be empty"}

    query_params: List[Any] = []

    if params:
        try:
            query_params = json.loads(params)
            if not isinstance(query_params, list):
                return {"error": "invalid_parameter", "metadata": "params must be a JSON array string, e.g., '[\"value1\", \"value2\"]'"}
        except json.JSONDecodeError as e:
            return {"error": "invalid_parameter", "metadata": f"params is not a valid JSON string: {str(e)}"}

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    data = {"sql": sql_query, "params": query_params}

    try:
        response = httpx.post(url, headers=headers, json=data)
        response.raise_for_status()
        return {
            "success": True,
            "metadata": response.json()
        }

    except httpx.HTTPError as e:  # Simplified HTTPError handling
        try:
            error_data = e.response.json()  # Attempt to get JSON, even if it fails
        except json.JSONDecodeError:
            # Fallback if not JSON
            error_data = {"response_text": e.response.text}

        return {
            "error": "http_request_error",
            "metadata": {
                "http_status": e.response.status_code,
                "detail": str(e),
                # Include the entire payload (JSON or text)
                "response_payload": error_data
            },
        }
    except json.JSONDecodeError as e:
        return {"error": "json_decode_error", "metadata": str(e)}
    except Exception as e:
        return {"error": "other_error", "metadata": str(e)}
