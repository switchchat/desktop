# Task 6 Logs: Real MCP Client Integration (Notion Focus)

## 1. Objective
Transition the Cluely backend from using **Mock MCP Servers** to a **Real MCP Client Architecture**. The goal is to enable FunctionGemma/Gemini to dynamically discover and execute tools from official MCP servers (Atlassian, Slack, Notion) without hardcoding tool logic in our backend.

## 2. Architecture Shift
*   **Old Approach**: A local `mcp_server.py` with hardcoded mock tools (`create_jira_ticket`, etc.).
*   **New Approach**: 
    *   **Strict Client Role**: The Python backend acts *only* as an MCP Client.
    *   **Remote Connections**: Connects to external MCP servers via standard protocols (SSE, Streamable HTTP, or Stdio subprocesses).
    *   **Dynamic Discovery**: Tools are fetched at runtime (`list_tools`) and injected into the AI model's context.

## 3. Implementation Details

### 3.1. MCP Client Manager (`mcp_client.py`)
Created a robust `MCPManager` class capable of handling multiple concurrent connections.
*   **Transports Supported**:
    *   `sse`: Server-Sent Events (standard for many hosted servers).
    *   `http`: Streamable HTTP (JSON-RPC over HTTP).
    *   `stdio`: Subprocess execution (used for local adapters like `npx`).
*   **Key Features**:
    *   Auto-connection on startup.
    *   Tool caching and aggregation.
    *   `get_status()` endpoint for health checks.

### 3.2. Server Integration (`server.py`)
*   Modified `lifespan` to initialize `MCPManager` on startup.
*   Updated `/chat` endpoint to:
    1.  Fetch real tools from `mcp_manager`.
    2.  Merge them with any local tools.
    3.  Pass them to `generate_hybrid`.
    4.  Intercept model function calls, execute them via `mcp_manager`, and return results.

### 3.3. Schema Sanitization (`main.py`)
*   **Issue**: Official MCP servers (like Notion) often return complex JSON schemas (e.g., arrays without explicit `items` types, nested objects without properties) that cause **Gemini 2.5** to throw `400 INVALID_ARGUMENT` errors.
*   **Fix**: Implemented `_sanitize_schema` function.
    *   Recursively traverses tool schemas.
    *   Defaults missing types to `STRING`.
    *   Adds default `items: {"type": "STRING"}` for untyped arrays.
    *   Ensures compatibility between MCP specs and Gemini's strict requirements.

## 4. Notion MCP Integration

### 4.1. Challenge: Hosted vs. Local Adapter
We initially attempted to connect to the hosted endpoint `https://mcp.notion.com/mcp` via HTTP/SSE.
*   **Failure**: Authentication handshake issues and protocol mismatches with the hosted proxy.
*   **Pivot**: Switched to the **Stdio Transport** using the official Node.js adapter.
    *   Command: `npx -y @notionhq/notion-mcp-server`
    *   Auth: Injected `NOTION_TOKEN` via environment variables.

### 4.2. Current Configuration
*   **Enabled**: Notion (via Stdio/npx).
*   **Disabled**: Atlassian and Slack (commented out for focused testing).
*   **Credentials**: Using provided integration token `ntn_...`.

## 5. Verification
*   **Test Query**: "Search for pages about planning in Notion"
*   **Model Action**: Gemini correctly selected the `API-post-search` tool.
*   **Execution**: The backend forwarded the call to the `npx` subprocess.
*   **Result**: Received a valid JSON response from Notion (empty list `[]`, confirming successful authentication and API access).

## 6. Files Created/Modified
*   `app/frontend/python_backend/mcp_client.py`: Core client logic.
*   `app/frontend/python_backend/server.py`: Integration with FastAPI.
*   `app/frontend/python_backend/main.py`: Schema sanitization logic.
*   `tests/test_mcp_integration.py`: Integration testing script.

## 7. Next Steps
*   Enable Atlassian and Slack integrations when tokens are available.
*   Build a Frontend UI to allow users to input their own MCP tokens.
*   Visualize connection status in the app.
