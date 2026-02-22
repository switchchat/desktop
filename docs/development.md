# Development Guide

This guide is for developers contributing to Nova or participating in the hackathon. It covers the project structure, testing workflows, and how to extend the application.

## Project Structure

```text
/
├── app/                  # Application code
│   ├── backend/          # Python backend (FastAPI) source
│   └── frontend/         # Electron frontend source
├── cactus/               # Cactus AI Engine (C++ core & bindings)
├── scripts/              # Utility scripts
│   ├── benchmark.py      # Hackathon benchmark tool
│   └── submit.py         # Leaderboard submission tool
├── src/                  # Core Python Logic (Hackathon Submission)
│   └── main.py           # Main hybrid agent logic
└── tests/                # Unit and integration tests
```

## Hackathon Workflow

The primary goal for the hackathon is to optimize `src/main.py`.

1.  **Modify Logic**: Edit `src/main.py` to improve the `generate_hybrid` function. Focus on better prompt engineering for the local model and smarter routing heuristics.
2.  **Benchmark**: Run `python scripts/benchmark.py` to score your changes locally.
3.  **Test in App**: Run the backend and frontend to see how your changes affect the real user experience.
4.  **Submit**: Run `python scripts/submit.py` to upload your score.

## Adding New Tools (MCP)

Nova uses the **Model Context Protocol (MCP)** to integrate external tools. To add a new tool (e.g., Jira):

1.  **Create a Tool Module**: Create a new directory `app/backend/jira_tools/`.
2.  **Implement Client**: Write a client class that wraps the service's API.
3.  **Define Schemas**: Create JSON schemas describing the tools available to the LLM.
4.  **Register**: Update `app/backend/server.py` to import your new module and inject the tools into the `/chat` endpoint.

## Testing

We use `pytest` for testing backend logic.

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_mcp_integration.py
```

## Packaging for Release

To build the standalone application:

1.  **Sync Backend**: Run the script to prepare the python backend for packaging.
    ```bash
    python scripts/sync_backend.py
    ```

2.  **Build Electron App**:
    ```bash
    cd app/frontend
    npm run dist
    ```
    This will create a `.dmg` (macOS) or `.zip` file in `app/frontend/dist/`.

## Debugging

- **Backend Logs**: The backend logs to stdout. When running via Electron, logs may be captured in the Electron console or a log file in `tmp`.
- **Frontend Logs**: Use the Developer Tools in the Electron window (`Cmd+Option+I`).
- **Cactus Debugging**: Set `_DIAG = True` in `src/main.py` to see detailed inference logs.
