"""Function-call (MCP) tool wrappers for Slack operations.

Provides JSON-schema tool definitions and a `call_tool(name, args)`
dispatcher that calls `SlackMCPClient` methods. Intended for LLM
function-calling integrations.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .slack_mcp import SlackMCPClient
from .schemas import all_schemas


class SlackTools:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self._client_instance: Optional[SlackMCPClient] = None
        self._api_key = api_key

    def _client(self) -> SlackMCPClient:
        if self._client_instance is None:
            self._client_instance = SlackMCPClient(api_key=self._api_key)
        return self._client_instance

    def tool_schemas(self) -> List[Dict[str, Any]]:
        return all_schemas()

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            client = self._client()
        except Exception as exc:
            return {"ok": False, "error": f"Slack client init error: {exc}"}

        try:
            if name == "slack_post_message":
                return {"ok": True, "data": client.post_message(arguments["channel"], arguments.get("text"), arguments.get("blocks"), arguments.get("thread_ts"))}
            if name == "slack_list_conversations":
                return {"ok": True, "data": client.list_conversations(arguments.get("types", "public_channel,private_channel,im,mpim"), arguments.get("limit", 100))}
            if name == "slack_get_history":
                return {"ok": True, "data": client.get_conversation_history(arguments["channel"], arguments.get("limit", 100))}
            if name == "slack_upload_file":
                return {"ok": True, "data": client.upload_file(arguments["channels"], arguments["file_path"], arguments.get("filename"), arguments.get("initial_comment"))}
            return {"ok": False, "error": f"Unknown tool: {name}"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


slack_tools = SlackTools()
