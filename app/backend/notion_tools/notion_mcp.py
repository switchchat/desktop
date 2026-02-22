"""Notion MCP client for the assistant project.

This module implements a lightweight Notion client class that can be
used by agents or other backend components. It focuses on a small set
of operations commonly needed by automation:

- search(query)
- get_page(page_id)
- create_page(database_id, properties, children)
- update_page(page_id, properties)
- append_block(page_id, block)

The client expects the Notion integration token in the environment
variable `NOTION_API_KEY`.
"""

from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Optional

import requests


class NotionMCPClient:
    """Small Notion API client tailored for assistant MCP use.

    It intentionally implements a minimal surface so agents can call
    these methods as tools. Methods raise requests.HTTPError on
    non-2xx responses.
    """

    BASE_URL = "https://api.notion.com/v1"

    def __init__(self, api_key: Optional[str] = None, notion_version: str = "2022-06-28") -> None:
        self.api_key = api_key or os.environ.get("NOTION_API_KEY")
        if not self.api_key:
            raise RuntimeError("NOTION_API_KEY not set in environment and no api_key provided")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": notion_version,
            "Content-Type": "application/json",
        }

    # -- Utility -------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.BASE_URL}{path}"

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(self._url(path), headers=self.headers, json=body, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = requests.get(self._url(path), headers=self.headers, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.patch(self._url(path), headers=self.headers, json=body, timeout=20)
        resp.raise_for_status()
        return resp.json()

    # -- API operations -----------------------------------------
    def search(self, query: Optional[str] = None, filter_by: Optional[Dict[str, Any]] = None, page_size: int = 20) -> Dict[str, Any]:
        """Search Notion workspace. Returns raw JSON response."""
        body: Dict[str, Any] = {"page_size": page_size}
        if query:
            body["query"] = query
        if filter_by:
            body["filter"] = filter_by
        return self._post("/search", body)

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Retrieve a Notion page by id."""
        return self._get(f"/pages/{page_id}")

    def create_page(self, parent_database_id: str, properties: Dict[str, Any], children: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create a page in a database. `properties` should follow Notion's property schema."""
        body: Dict[str, Any] = {
            "parent": {"database_id": parent_database_id},
            "properties": properties,
        }
        if children is not None:
            body["children"] = children
        return self._post("/pages", body)

    def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update page properties."""
        return self._patch(f"/pages/{page_id}", {"properties": properties})

    def append_block(self, block_id: str, children: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Append children blocks to a block or page (block_id is the target block)."""
        body = {"children": children}
        return self._patch(f"/blocks/{block_id}/children", body)


def example_usage():
    """Minimal CLI-style demonstration; requires NOTION_API_KEY in env."""
    client = NotionMCPClient()
    print("Search for 'test' results:")
    res = client.search("test")
    print(json.dumps(res, indent=2)[:2000])


if __name__ == "__main__":
    example_usage()
