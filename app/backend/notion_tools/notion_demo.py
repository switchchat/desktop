"""Simple demo harness for NotionMCPClient."""

from __future__ import annotations

import os
import json
from .notion_mcp import NotionMCPClient


def main():
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        print("Set NOTION_API_KEY in environment to run the demo.")
        return

    client = NotionMCPClient()
    print("Searching for 'assistant'...")
    res = client.search("assistant")
    print(json.dumps(res, indent=2)[:2000])


if __name__ == '__main__':
    main()
