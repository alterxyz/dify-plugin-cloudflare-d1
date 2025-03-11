from collections.abc import Generator
from typing import Any

from cloudflare_d1 import cloudflare_d1_query

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DataConnectorCloudflareD1Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        account_id = self.runtime.credentials["cloudflare_account_id"]
        api_token = self.runtime.credentials["cloudflare_api_token"]
        database_id = tool_parameters["database_id"]
        sql_query = tool_parameters["query"]

        result = cloudflare_d1_query(
            account_id, database_id, api_token, sql_query, []
        )
        yield self.create_json_message(result)
