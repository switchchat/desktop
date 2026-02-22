# Task 7: Tool Calling Fixes & Execution Implementation

## 1. Initial Analysis & Test Planning
We started by reviewing the workspace to understand the hybrid architecture of Nova (Python backend + Electron frontend). We identified that the core logic resides in `src/main.py` (heuristic routing) and `app/backend/server.py` (API server).

We devised a set of questions to test Nova's capabilities:
- **Basic**: Simple single-tool lookups (e.g., "Search Notion for 'Project Alpha'").
- **Extraction**: Testing regex heuristics for specific params like time and content.
- **Multi-step**: Testing the "SPLIT" logic in `generate_hybrid`.
- **Fallback**: forcing cloud fallback for complex queries.

## 2. Fixing Tool Selection & Argument Extraction
The user provided evidence (via OCR of a screenshot) that Nova was failing to extract arguments correctly:
- `notion_search` truncated queries to single words.
- `slack_post_message` received the entire user query as the channel name.
- `notion_create_page` was never selected due to strict schema requirements.

### Changes Implemented
1.  **Enhanced Argument Extraction (`src/main.py`)**:
    *   Updated `_extract_from_schema` to treat `query` parameters as "content" fields, allowing them to capture full phrases instead of just proper nouns.
    *   Added a **Blacklist** for sensitive parameters (e.g., `channel`, `id`, `database_id`) to prevent them from being filled with leftover garbage text.
    *   Added specific heuristics for **Slack Channels** (requiring `#` or `@` prefixes) to prevent false positives.

2.  **Simplified Notion Schema (`app/backend/notion_tools/notion_tools.py`)**:
    *   Modified `notion_create_page` schema to accept a simple `title` argument instead of requiring complex `properties` and `database_id` objects.
    *   Updated the tool handler to automatically construct the required Notion `properties` structure from the simple `title`.

### Verification
We created and ran `tests/repro_issue.py`, confirming that:
- "Search for 'Project Alpha'" -> `query="Project Alpha"` (Correct)
- "Create a task..." -> `notion_create_page(title=...)` (Correct tool selected)
- "Post to #general" -> `channel="#general"` (Correct extraction)

## 3. Implementing Tool Execution
The user noted that tools were being *selected* but not *executed*.

### Changes Implemented
1.  **Server Execution Logic (`app/backend/server.py`)**:
    *   Updated the `/chat` endpoint to intercept `function_calls` returned by `generate_hybrid`.
    *   Added logic to immediately execute these calls using `notion_tools.call_tool` and `slack_tools.call_tool`.
    *   Appended execution results and a natural language summary to the response.

2.  **Bug Fixes in Tool Wrappers**:
    *   Fixed a critical shadowing bug in `notion_tools.py` and `slack_tools.py` where `self._client` (attribute) conflicted with `self._client()` (method), causing `TypeError: 'NoneType' object is not callable`. Renamed attribute to `self._client_instance`.

### Verification
We created `tests/test_execution.py` which simulated API requests. Logs confirmed that the server now attempts to execute tools (evidenced by "API Key missing" errors, proving the execution path is active).

## 4. Rebuilding the Electron App
To deploy these changes, we had to ensure the Electron frontend (which bundles its own Python backend) was using the updated code.

### Process
1.  **Sync Script**: Created `scripts/sync_backend.py` to copy the updated:
    *   `app/backend/server.py`
    *   `app/backend/notion_tools/`
    *   `app/backend/slack_tools/`
    *   `src/main.py`
    ...into `app/frontend/python_backend/` and `app/frontend/src/`.
2.  **Build**: Ran `npm install && npm run dist` in `app/frontend`.

### Outcome
The app was successfully rebuilt. The artifacts in `app/frontend/dist/` now contain the fixed logic for tool extraction, execution, and reliable backend performance.
