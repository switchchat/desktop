# System Architecture

## Overview

Nova is designed as a **Hybrid AI Desktop Assistant**. It bridges the gap between high-performance local inference (using the Cactus engine) and high-intelligence cloud reasoning (using Gemini 3.0 Flash). The architecture is split into a lightweight **Electron Frontend** for UI/UX and a robust **Python Backend** for logic and AI processing.

```mermaid
graph TD
    User[User Interaction] -->|Voice/Input| Electron[Electron Frontend]
    User -->|Screen Content| Electron
    
    Electron -->|HTTP /transcribe| Backend[Python Backend]
    Electron -->|HTTP /chat| Backend
    Electron -->|HTTP /analyze-screen| Backend
    
    subgraph "Python Backend (FastAPI)"
        Server[Server.py]
        Router[Hybrid Router (src/main.py)]
        MCP[MCP Client Manager]
        
        Server --> Router
        Server --> MCP
        
        subgraph "Cactus Engine (Local)"
            FG[FunctionGemma]
            Whisper[Whisper (Audio)]
            VLM[LFM2-VL (Vision)]
        end
        
        subgraph "Cloud Services"
            Gemini[Gemini 3.0 Flash API]
        end
        
        Router -->|Low Confidence/Complex| Gemini
        Router -->|High Confidence/Simple| FG
        
        MCP -->|Connect| Notion[Notion API]
        MCP -->|Connect| Slack[Slack API]
    end
    
    Backend -->|JSON Response| Electron
```

## 1. Backend (Python)

The backend (`app/backend/`) is the brain of Nova. It is a FastAPI application that serves as the host for the Cactus AI engine and the hackathon logic.

### Key Components

- **Hybrid Router (`src/main.py`)**: 
    - This is the core logic for the hackathon.
    - **Responsibility**: Analyzes user queries to determine the optimal model.
    - **Logic**: It attempts to solve the query using the local FunctionGemma model first. If the model's confidence is low or if the query requires complex reasoning (detected via heuristics), it falls back to the cloud-based Gemini 3.0 Flash model.
    
- **Cactus Integration**:
    - **Inference**: Uses `libcactus` bindings to run quantized models locally.
    - **Models**:
        - `functiongemma-270m-it`: For instruction following and tool calling.
        - `whisper-small`: For near-instant speech-to-text.
        - `lfm2-vl-450m`: For analyzing screen content.

- **MCP Client Manager**:
    - Implements the [Model Context Protocol](https://modelcontextprotocol.io/).
    - Manages connections to external tools (Notion, Slack) via standard transports (Stdio, SSE).
    - dynamically injects available tools into the AI model's context window.

## 2. Frontend (Electron)

The frontend (`app/frontend/`) is built with Electron and React. It provides the "invisible" user experience.

### Key Features

- **Overlay Window**: 
    - A frameless, transparent window that sits always-on-top.
    - **Click-through**: Ignores mouse events when displaying only suggestions, allowing the user to work "through" the assistant.
    - **Interactivity**: Becomes clickable when the user engages with a suggestion or button.

- **Input Capture**:
    - **Audio**: Uses the Web Audio API to stream microphone data to the backend for transcription.
    - **Desktop Capture**: Uses Electron's `desktopCapturer` API to take snapshots of the user's screen context when requested.

## 3. Data Flow

1.  **Capture**: User speaks a command or triggers the assistant. Frontend captures audio/text.
2.  **Transcribe (if voice)**: Audio is sent to `/transcribe`. Local Whisper model converts it to text.
3.  **Process**: Text is sent to `/chat` along with current screen context (if enabled).
4.  **Route**: The `Hybrid Router` evaluates the request:
    - *Is it a simple command (e.g., "Set timer")?* -> **Local Model**.
    - *Is it a complex query (e.g., "Summarize this PDF")?* -> **Cloud Model**.
5.  **Execute**: If the model decides to call a tool (e.g., `notion_search`), the Backend executes it via the MCP Client.
6.  **Response**: The final answer (or tool result) is sent back to the Frontend.
7.  **Display**: The Frontend renders the response on the overlay.

## 4. Hackathon Integration

The project structure is specifically designed for the Cactus Hackathon:

- **`src/main.py`**: This file contains the `generate_hybrid` function. This is the **only** file submitted to the leaderboard.
- **`app/`**: The rest of the application (Electron + FastAPI) wraps this logic to create a usable product.
- **Benefit**: Improvements made to the app's intelligence directly translate to a better score on the leaderboard, as they share the exact same source file.
