# Task 1 Logs: Project Initialization & Architecture Strategy

## 1. Project Goal
Build a "Cluely-like" invisible desktop assistant for the Cactus Hackathon. The app must run on macOS, use the Cactus AI engine (FunctionGemma, Whisper, VLM), and integrate with the hackathon's required `main.py` logic.

## 2. Architecture Analysis & Decision

### Options Considered
1.  **Electron Frontend + Python Backend**:
    *   **Pros**: Directly imports `main.py` (hackathon submission requirement), fast UI development, cross-platform potential.
    *   **Cons**: Heavier resource usage than native.
2.  **Native Swift App**:
    *   **Pros**: Best performance, native macOS feel.
    *   **Cons**: Requires re-implementing `generate_hybrid` logic in Swift (duplication of work), high complexity for a short timeframe.
3.  **Web Apps (Safari/Chrome PWA)**:
    *   **Pros**: Simple distribution.
    *   **Cons**: **Rejected**. Cannot support critical "Cluely" features due to sandboxing:
        *   No global "Always on Top" floating window.
        *   No "Click-through" transparency.
        *   No silent background screen capture.

### Final Decision: Electron + Python
We chose **Electron + Python** because it is the only viable path to build the specific "invisible overlay" features while satisfying the hackathon's requirement to submit Python logic.

## 3. Implementation Status

### Backend (`app/backend/server.py`)
*   **Framework**: FastAPI.
*   **Integration**: Imports `generate_hybrid` from the root `main.py`.
*   **New Endpoints**:
    *   `POST /chat`: Routes queries to the hybrid agent.
    *   `POST /transcribe`: Handles audio file uploads for Whisper transcription.
    *   `POST /analyze-screen`: Handles screen snapshots for VLM analysis.
*   **Robustness**: Added mock fallbacks for Cactus functions if model weights are missing (enables development without full 50GB model downloads).

### Frontend (`app/frontend/`)
*   **Tech Stack**: Electron, HTML/CSS/JS.
*   **UI**: Dark-themed, semi-transparent overlay designed to float on the desktop.
*   **Features Implemented**:
    *   **Chat Interface**: Real-time message history.
    *   **Audio Capture**: "Hold to Speak" button recording microphone input.
    *   **Screen Capture**: "Eye" button capturing the primary display via `desktopCapturer`.
    *   **Backend Connection**: Auto-spawns the Python server and health-checks connection.

## 4. Distribution & Security Strategy

### Challenge
macOS Gatekeeper requires apps to be signed with a Developer ID and notarized by Apple. This process takes time and costs $99/year.

### Constraints
*   **Time**: ~4 hours remaining.
*   **Risk**: Notarization can fail or take too long, jeopardizing the demo.

### Strategy: "Vibe Coding" / Ad-Hoc
*   **Decision**: **Skip Notarization**.
*   **Build Config**: Configure Electron for **Ad-Hoc Signing** (runnable locally).
*   **Demo Plan**: Run the `.app` on the local machine. If transferring to another machine, use the **Right-Click > Open** bypass to circumvent Gatekeeper quarantine.

## 5. Next Steps
1.  Update `package.json` to disable strict signing requirements.
2.  Build the local `.app` / `.dmg`.
3.  Verify the "invisible" window behavior (transparency, click-through) works in a packaged build.
