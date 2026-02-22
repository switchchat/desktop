Notion MCP client

This module provides a lightweight Notion client suitable for assistant agents and backend code.

Files (moved into `notion_tools/`):
- `notion_tools/notion_mcp.py` - main client class `NotionMCPClient`.
- `notion_tools/notion_demo.py` - small CLI demo that runs a basic search. Requires `NOTION_API_KEY` env var.
- `notion_tools/notion_tools.py` - function-call (MCP) tool wrappers exposing JSON-schema definitions and a `call_tool` dispatcher for agents.

HTTP Endpoints

- `POST /notion/search` - body: `{query, page_size}` -> forwards to Notion search
- `GET  /notion/page/{page_id}` - returns page JSON
- `POST /notion/page` - create page in a database, body: `{database_id, properties, children?}`
- `PATCH /notion/page/{page_id}` - update page properties
- `PATCH /notion/blocks/{block_id}/append` - append children blocks
- `GET /notion/tools/schemas` - returns JSON function schemas for LLM function-calling

Usage:

1. Install requests if not present:

```bash
pip install requests
```

2. Set your Notion integration token:

```bash
export NOTION_API_KEY="secret_..."
```

3. Run the demo from the package directory:

```bash
cd assistant/app/backend/notion_tools
python3 notion_demo.py
```

Notes:
- This client aims to be minimal and explicit; adapt property payloads to your Notion database schema.
