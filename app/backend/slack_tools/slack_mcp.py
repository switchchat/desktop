"""Slack MCP client for the assistant project.

Lightweight wrapper around Slack Web API for use as MCP tools.

Environment variable `SLACK_BOT_TOKEN` is used for authentication when
no token is provided to the constructor.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


class SlackMCPClient:
    """Small Slack Web API client used by agent tools.

    Methods raise requests.HTTPError on non-2xx responses.
    """

    BASE_URL = "https://slack.com/api"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("SLACK_BOT_TOKEN")
        if not self.api_key:
            raise RuntimeError("SLACK_BOT_TOKEN not set in environment and no api_key provided")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

    # -- helpers ------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.BASE_URL}{path}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = requests.get(self._url(path), headers=self.headers, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        headers = dict(self.headers)
        headers["Content-Type"] = "application/json; charset=utf-8"
        resp = requests.post(self._url(path), headers=headers, json=body, timeout=20)
        resp.raise_for_status()
        return resp.json()

    # -- API operations -----------------------------------------
    def post_message(self, channel: str, text: Optional[str] = None, blocks: Optional[List[Dict[str, Any]]] = None, thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Post a message to a channel or thread."""
        body: Dict[str, Any] = {"channel": channel}
        if text is not None:
            body["text"] = text
        if blocks is not None:
            body["blocks"] = blocks
        if thread_ts is not None:
            body["thread_ts"] = thread_ts
        return self._post("/chat.postMessage", body)

    def list_conversations(self, types: str = "public_channel,private_channel,im,mpim", limit: int = 100) -> Dict[str, Any]:
        """List conversations. `types` matches Slack API `types` param."""
        params = {"types": types, "limit": limit}
        return self._get("/conversations.list", params=params)

    def get_conversation_history(self, channel: str, limit: int = 100) -> Dict[str, Any]:
        """Get message history for a channel."""
        params = {"channel": channel, "limit": limit}
        return self._get("/conversations.history", params=params)

    def upload_file(self, channels: List[str], file_path: str, filename: Optional[str] = None, initial_comment: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to one or more channels. Uses multipart/form-data."""
        url = self._url("/files.upload")
        headers = dict(self.headers)
        # multipart requests must not set Content-Type here
        data: Dict[str, Any] = {"channels": ",".join(channels)}
        if filename:
            data["filename"] = filename
        if initial_comment:
            data["initial_comment"] = initial_comment

        with open(file_path, "rb") as f:
            files = {"file": (filename or file_path, f)}
            resp = requests.post(url, headers=headers, data=data, files=files, timeout=60)
        resp.raise_for_status()
        return resp.json()


def example_usage() -> None:
    client = SlackMCPClient()
    print("Listing conversations:")
    print(client.list_conversations())


if __name__ == "__main__":
    example_usage()
