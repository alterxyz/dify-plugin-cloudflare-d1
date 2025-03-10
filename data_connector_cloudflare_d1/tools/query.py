from collections.abc import Generator
from typing import Any, Dict, List

import httpx
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DataConnectorCloudflareD1Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        account_id = self.runtime.credentials["cloudflare_account_id"]
        api_token = self.runtime.credentials["cloudflare_api_token"]
        database_id = tool_parameters["database_id"]
        sql_query = tool_parameters["query"]

        result = query_cloudflare_d1(
            account_id, database_id, api_token, sql_query, []
        )
        yield self.create_json_message(result)


def query_cloudflare_d1(
    account_id: str,
    database_id: str,
    api_token: str,
    sql_query: str,
    params: List[Any]
) -> Dict[str, Any]:
    """
    Execute a query on the Cloudflare D1 database.

    Args:
        account_id: Cloudflare account ID.
        database_id: D1 database ID.
        api_token: Cloudflare API Bearer Token.
        sql_query: SQL query to be executed (using ? as a placeholder).
        params: List of SQL query parameters.

    Returns:
        If the request is successful, returns the JSON response data (dict).
        If the request fails, returns a dictionary with error details.
    """
    # Parameter validation
    if not account_id:
        return {"error": "invalid_parameter", "metadata": "account_id cannot be empty"}
    if not database_id:
        return {"error": "invalid_parameter", "metadata": "database_id cannot be empty"}
    if not sql_query:
        return {"error": "invalid_parameter", "metadata": "sql_query cannot be empty"}

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    data = {"sql": sql_query, "params": params}

    try:
        response = httpx.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    except httpx.HTTPError as e:
        try:
            error_data = e.response.json()
            errors = error_data.get("errors", [])
            if errors:
                error_details = [
                    {"code": error.get("code"),
                     "message": error.get("message")}
                    for error in errors
                ]
                return {
                    "error": "cloudflare_d1_error",
                    "metadata": {
                        "http_status": e.response.status_code,
                        "details": error_details,
                        "raw_response": error_data,
                    },
                }
            else:
                return {
                    "error": "http_request_error",
                    "metadata": {
                        "http_status": e.response.status_code,
                        "detail": str(e),
                        "response_text": e.response.text,
                    },
                }
        except json.JSONDecodeError:
            return {
                "error": "http_request_error",
                "metadata": {
                    "http_status": e.response.status_code,
                    "detail": str(e),
                    "response_text": e.response.text,
                },
            }
    except json.JSONDecodeError as e:
        return {"error": "json_decode_error", "metadata": str(e)}
    except Exception as e:
        return {"error": "other_error", "metadata": str(e)}
