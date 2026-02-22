# Task 4: Workspace Organization

## Objective
Organize the workspace to improve code structure and maintainability, moving core logic to a dedicated `src/` directory and utility scripts to a `scripts/` directory.

## Context
The project was initially structured with all Python files at the root level. This organization was functional but not ideal for a larger project or for maintaining a clear separation between core logic, utility scripts, and application components.

## Plan
1.  Create a `src/` directory to house the core hackathon logic (`main.py`).
2.  Create a `scripts/` directory for utility scripts (`benchmark.py`, `submit.py`).
3.  Update all import paths and references to reflect the new structure.
4.  Ensure the application (both the hackathon scripts and the Electron app backend) continues to function correctly.

## Implementation

### 1. Directory Creation
- Created `src/` and `scripts/` directories at the project root.

### 2. File Relocation
- Moved `main.py` to `src/main.py`.
- Moved `benchmark.py` to `scripts/benchmark.py`.
- Moved `submit.py` to `scripts/submit.py`.
- Created `src/__init__.py` to make `src` a Python package.

### 3. Path Updates

#### `src/main.py`
- Updated `_get_gemini_api_key()` to look for the `.env` file in the project root (`os.path.dirname(os.path.dirname(__file__))`) instead of the `src/` directory.

#### `scripts/benchmark.py`
- Added the project root to `sys.path` to allow importing from `src`.
- Updated import: `from src.main import generate_hybrid`.

#### `scripts/submit.py`
- Updated the file path in the `submit()` function to read `src/main.py` instead of `main.py`.

#### `app/backend/server.py`
- Updated import: `from src.main import generate_hybrid`.
- Updated fallback error message to reference `src.main`.

### 4. Documentation Updates

#### `README.md`
- Updated instructions to reference `src/main.py`, `scripts/benchmark.py`, and `scripts/submit.py`.

#### `ARCHITECTURE.md`
- Updated the directory structure diagram to reflect the new layout.
- Updated the hackathon integration note to reference `src/main.py`.

#### `ARCHITECTURE_COMPARISON.md`
- Updated references to `main.py` to `src/main.py` throughout the document.

## Verification
- Successfully ran `python scripts/benchmark.py` (noting that the benchmark itself hit API rate limits, which is expected and not related to the reorganization).
- Confirmed that the backend server (`app/backend/server.py`) can still import the necessary functions.

## Result
The workspace is now organized with a clear separation of concerns:

```
/Users/yaksheng/projects/cactus-hackathon-cluely/
├── app/
│   ├── backend/
│   │   └── server.py
│   └── frontend/
│       └── ... (Electron app files)
├── assets/
├── scripts/
│   ├── benchmark.py
│   └── submit.py
├── src/
│   ├── __init__.py
│   └── main.py
├── task-list/
└── ... (config files, docs, etc.)
```

This structure improves maintainability and aligns with common Python project conventions. The core logic is isolated in `src/`, utility scripts are in `scripts/`, and the application components are in `app/`.