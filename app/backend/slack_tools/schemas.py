"""JSON Schema definitions for Slack MCP tools.

These schemas are intended to be returned by the server's
`/slack/tools/schemas` endpoint for LLM function-calling.
"""

from __future__ import annotations

from typing import Any, Dict, List


SLACK_POST_MESSAGE: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "slack_post_message",
        "description": "Post a message to a Slack channel or thread.",
        "parameters": {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Slack channel ID (e.g., C01234567) or @user"},
                "text": {"type": "string", "description": "Fallback plain-text message"},
                "blocks": {"type": "array", "items": {"type": "object"}, "description": "Optional Slack Block Kit blocks"},
                "thread_ts": {"type": "string", "description": "Timestamp of parent message to post in a thread"},
            },
            "required": ["channel"],
        },
    },
}

SLACK_LIST_CONVERSATIONS: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "slack_list_conversations",
        "description": "List Slack conversations (channels, IMs).",
        "parameters": {
            "type": "object",
            "properties": {
                "types": {"type": "string", "description": "Comma-separated conversation types (public_channel,private_channel,im,mpim)"},
                "limit": {"type": "integer", "description": "Maximum results to return"},
            },
        },
    },
}

SLACK_GET_HISTORY: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "slack_get_history",
        "description": "Get recent message history for a channel.",
        "parameters": {
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["channel"],
        },
    },
}

SLACK_UPLOAD_FILE: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "slack_upload_file",
        "description": "Upload a file to channels. The server expects the file to be uploaded via multipart or accessible on disk.",
        "parameters": {
            "type": "object",
            "properties": {
                "channels": {"type": "array", "items": {"type": "string"}},
                "file_path": {"type": "string", "description": "Local path on server or pre-fetched temporary file path"},
                "filename": {"type": "string"},
                "initial_comment": {"type": "string"},
            },
            "required": ["channels", "file_path"],
        },
    },
}


def all_schemas() -> List[Dict[str, Any]]:
    return [SLACK_POST_MESSAGE, SLACK_LIST_CONVERSATIONS, SLACK_GET_HISTORY, SLACK_UPLOAD_FILE]
