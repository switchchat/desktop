# Task 2 Logs: App Integration, Real AI, and Packaging Fixes

## 1. Context & Objectives
The primary goal was to transition the Cluely (Cactus) app from a mock state to a fully functional "Real AI" application. This involved fixing the "Offline" status, enabling local and cloud-based inference, resolving transcription errors, and ensuring the packaged Electron app runs correctly.

**Key Objectives:**
-   **Fix "Offline" Status:** Ensure the Python backend starts successfully within the Electron app.
-   **Enable Real AI:** Integrate `libcactus` for on-device inference (FunctionGemma) and Whisper transcription.
-   **Hybrid Inference:** Implement a fallback mechanism to Gemini Cloud when local confidence is low.
-   **Fix Errors:** Resolve `spawn ENOENT`, `Failed to fetch`, and API key permissions (403).
-   **Packaging:** Rebuild the Electron app to include all necessary binaries and scripts.

## 2. Discussion & Issues Identified

### 2.1. Backend Startup Failures ("Offline" Status)
-   **Issue:** The Electron app reported "Offline" because the Python backend failed to start or crashed immediately.
-   **Root Cause:**
    -   Missing native library (`libcactus.dylib`).
    -   Python version mismatch (system default vs. required 3.11).
    -   Incorrect relative paths for model weights in `server.py`.

### 2.2. Transcription & Inference Errors
-   **Issue:** "Transcription failed: Failed to fetch" and generic 500 errors.
-   **Root Cause:**
    -   `server.py` was crashing due to unhandled exceptions when loading models.
    -   Model paths were pointing to non-existent directories.

### 2.3. Python Spawn Error (Packaged App)
-   **Issue:** `Uncaught Exception: Error: spawn python3.11 ENOENT`
-   **Root Cause:** The packaged Electron app could not find `python3.11` in the system PATH because `spawn` was called with a bare command name, and the environment in the packaged app differs from the terminal.

### 2.4. Gemini API Key Leak & 403 Error
-   **Issue:** Hybrid inference failed with `403 PERMISSION_DENIED`.
-   **Root Cause:** The hardcoded API key in `main.py` was flagged as leaked by Google and disabled.

### 2.5. FunctionGemma Formatting
-   **Issue:** On-device function calling was suboptimal.
-   **Root Cause:** The prompt passed to `cactus_complete` lacked the specific control tokens (`<start_function_declaration>`, `<start_of_turn>`, etc.) required by FunctionGemma for accurate tool use.

## 3. Plan & Alignment

### 3.1. Alignment with User
-   **API Key:** User provided a new, valid Gemini API key (`AIzaSyDP...`) to replace the leaked one.
-   **Rebuild:** User explicitly requested a rebuild of the Electron app after fixes.
-   **Documentation:** User requested review of FunctionGemma best practices.

### 3.2. Execution Plan
1.  **Fix Python Path:** Implement a robust `findPython()` function in `main.js` to locate the Python 3.11 executable via absolute paths.
2.  **Fix Model Paths:** Update `server.py` to point to the correct locations for Whisper and FunctionGemma weights.
3.  **Update `main.py`:**
    -   Replace the leaked API key.
    -   Implement full FunctionGemma prompt formatting (control tokens) to improve local accuracy.
4.  **Rebuild App:** Run `electron-builder` (via `npm run dist`) to package the changes.

## 4. Implementation Details

### 4.1. Python Path Detection ([main.js](file:///Users/yaksheng/projects/cactus-hackathon-cluely/app/frontend/main.js))
Implemented `findPython()` to check common installation paths for Python 3.11 (Homebrew, Python.org framework) before falling back to `python3`.

```javascript
function findPython() {
  const possiblePaths = [
    '/opt/homebrew/bin/python3.11',
    '/usr/local/bin/python3.11',
    '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11',
    'python3.11',
    'python3'
  ];
  // ... checks existence ...
}
```

### 4.2. FunctionGemma Prompting ([main.py](file:///Users/yaksheng/projects/cactus-hackathon-cluely/app/frontend/python_backend/main.py))
Rewrote `generate_cactus` to manually construct the prompt using official control tokens. This ensures the model understands tool definitions and user turns.

```python
prompt = "<start_of_turn>user\nYou are a helpful assistant with access to the following tools:\n"
for tool in tools:
    prompt += "<start_function_declaration>\n"
    prompt += json.dumps(tool) + "\n"
    prompt += "<end_function_declaration>\n"
prompt += user_content.strip() + "<end_of_turn>\n<start_of_turn>model\n"
```

### 4.3. API Key Update ([main.py](file:///Users/yaksheng/projects/cactus-hackathon-cluely/app/frontend/python_backend/main.py))
Updated `generate_cloud` to use the new API key, resolving the 403 error.

```python
api_key = "AIzaSy..." # Updated key (redacted)
```

### 4.4. App Rebuild
Ran `npm run dist` in `app/frontend`.
-   **Output:** `dist/mac-arm64/cluely-clone.app` (and DMG/Zip).
-   **Status:** Build successful. Asar packing was disabled to ensure Python files and binaries are accessible.

## 5. Current Status
-   **App Status:** Online.
-   **Inference:** Hybrid mode active. Local inference uses formatted prompts; cloud fallback uses the valid API key.
-   **Packaging:** App rebuilt and ready for testing.
