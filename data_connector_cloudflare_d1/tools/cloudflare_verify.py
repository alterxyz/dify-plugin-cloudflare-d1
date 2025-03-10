from collections.abc import Generator
from typing import Any

import httpx

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class CloudflareVerify(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            if tool_parameters["a_cloudflare_api_token"]:
                api_token = tool_parameters["a_cloudflare_api_token"]
            else:
                api_token = self.runtime.credentials["cloudflare_api_token"]
        except KeyError:
            api_token = self.runtime.credentials["cloudflare_api_token"]
        result = verify_cloudflare_token(api_token)
        yield self.create_json_message(result)


def verify_cloudflare_token(token):
    """
    Verifies a Cloudflare API token by calling the Cloudflare token verification endpoint.

    Args:
        token (str): The Cloudflare API token to verify.

    Returns:
        dict: A dictionary representing the verification result.
              Returns a dictionary in the format:
              - On successful verification (status active and success true):
                {'success': True, 'message': 'Token is valid and active', 'data': <full cloudflare response>}
              - On unsuccessful verification (status not active or success false):
                {'success': False, 'error': 'Token verification failed: <reason>', 'data': <full cloudflare response>}
              - On HTTP errors during the request:
                {'success': False, 'error': 'HTTP error during token verification: <error message>', 'details': <error details>}
              - On other exceptions during the request:
                {'success': False, 'error': 'Unexpected error during token verification: <error message>', 'details': <exception details>}
    """
    try:
        response = httpx.get(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get("success") and data.get("result", {}).get("status") == "active":
            return {
                "success": True,
                "message": "Token is valid and active",
                "data": data,
            }
        else:
            error_message = "Token verification failed: "
            if not data.get("success"):
                error_message += (
                    f"API request was not successful. Errors: {data.get('errors')}"
                )
            elif data.get("result", {}).get("status") != "active":
                error_message += f"Token status is not active. Status: {data.get('result', {}).get('status')}"
            else:  # Fallback in case of unexpected response structure
                error_message += "Unknown verification failure."
            return {"success": False, "error": error_message, "data": data}

    except httpx.HTTPStatusError as e:
        error_detail = {}
        try:
            # Try to get more details from response body if it's JSON
            error_detail = e.response.json()
        except ValueError:  # If response body is not JSON
            error_detail = {
                "status_code": e.response.status_code,
                "text": e.response.text,
            }
        return {
            "success": False,
            "error": f"HTTP error during token verification: {e}",
            "details": error_detail,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error during token verification: {e}",
            "details": {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
            },
        }
