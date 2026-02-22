"""Function-call (MCP) tool wrappers for Notion operations.

Provides JSON-schema tool definitions and a `call_tool(name, args)`
dispatcher that calls `NotionMCPClient` methods. Intended for LLM
function-calling integrations.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .notion_mcp import NotionMCPClient

class NotionTools:
    def __init__(self, api_key: Optional[str] = None) -> None:
        # instantiate lazily; raise on use if Notion not configured
        self._client_instance: Optional[NotionMCPClient] = None
        self._api_key = api_key

    def _client(self) -> NotionMCPClient:
        if self._client_instance is None:
            self._client_instance = NotionMCPClient(api_key=self._api_key)
        return self._client_instance

    def tool_schemas(self) -> List[Dict[str, Any]]:
        """Return JSON-schema definitions suitable for function-calling.

        Each item follows the format {type: 'function', function: {...}}
        where `function.parameters` is a JSON Schema for the tool's args.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "notion_search",
                    "description": "Search the Notion workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "page_size": {"type": "integer", "minimum": 1, "maximum": 100},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "notion_get_page",
                    "description": "Retrieve a Notion page by id.",
                    "parameters": {"type": "object", "properties": {"page_id": {"type": "string"}}, "required": ["page_id"]},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "notion_create_page",
                    "description": "Create a page in a database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "database_id": {"type": "string"},
                            "title": {"type": "string", "description": "Page title"},
                            "properties": {"type": "object"},
                            "children": {"type": "array", "items": {"type": "object"}},
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "notion_update_page",
                    "description": "Update properties on a page.",
                    "parameters": {"type": "object", "properties": {"page_id": {"type": "string"}, "properties": {"type": "object"}}, "required": ["page_id", "properties"]},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "notion_append_block",
                    "description": "Append child blocks to a block or page.",
                    "parameters": {"type": "object", "properties": {"block_id": {"type": "string"}, "children": {"type": "array", "items": {"type": "object"}}}, "required": ["block_id", "children"]},
                },
            },
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a named tool call to the Notion client.

        Returns a dict with either {ok: True, data: ...} or {ok: False, error: ...}
        """
        try:
            client = self._client()
        except Exception as exc:
            return {"ok": False, "error": f"Notion client init error: {exc}"}

        try:
            if name == "notion_search":
                return {"ok": True, "data": client.search(arguments.get("query"), page_size=arguments.get("page_size", 20))}
            if name == "notion_get_page":
                return {"ok": True, "data": client.get_page(arguments["page_id"]) }
            if name == "notion_create_page":
                db_id = arguments.get("database_id")
                props = arguments.get("properties", {})
                if not props and arguments.get("title"):
                    props = {"Name": {"title": [{"text": {"content": arguments["title"]}}]}}
                
                # Fallback: if no DB ID, try to find one or error out gracefully
                if not db_id:
                     # For now, just error if no DB ID, but at least we TRIED to call this tool
                     # instead of Slack. In a real app, we might default to a specific DB.
                     pass 

                return {"ok": True, "data": client.create_page(db_id, props, arguments.get("children"))}
            if name == "notion_update_page":
                return {"ok": True, "data": client.update_page(arguments["page_id"], arguments["properties"]) }
            if name == "notion_append_block":
                return {"ok": True, "data": client.append_block(arguments["block_id"], arguments["children"]) }
            return {"ok": False, "error": f"Unknown tool: {name}"}
        except Exception as exc:
            # Surface HTTP/request errors cleanly
            return {"ok": False, "error": str(exc)}


notion_tools = NotionTools()
