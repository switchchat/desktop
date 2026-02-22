# Nova - Intelligent Invisible Desktop Assistant

<div align="center">
  <img src="assets/banner.png" alt="Nova Banner" width="100%" style="border-radius: 10px;">
  
  <p align="center">
    <b>Hybrid AI Intelligence • Invisible Interface • On-Device First</b>
  </p>

  <p align="center">
    Built for the <b>Cactus x Google DeepMind Hackathon</b>
  </p>
</div>

**Nova** is a next-generation desktop assistant that reimagines how we interact with AI. Instead of a chat window that breaks your flow, Nova exists as an "invisible" layer over your desktop—always present but never intrusive. 

It leverages **Cactus Compute** to run powerful AI models locally on your Mac, seamlessly handing off to the cloud only when necessary.

## Features

- **🧠 Hybrid Intelligence**: Automatically routes queries between **FunctionGemma** (local, fast, private) and **Gemini Flash** (cloud, reasoning-heavy) based on complexity.
- **� Invisible Overlay**: A transparent, click-through interface built with Electron that floats above your windows.
- **⚡️ On-Device First**: Powered by **Cactus Compute**, running Whisper (speech) and FunctionGemma (logic) locally for near-zero latency.
- **�️ Extensible Tool Use**: Implements the **Model Context Protocol (MCP)** to connect with external apps like **Notion** and **Slack**.
- **👁️ Multimodal**: Understands your voice via Whisper and sees your screen via Vision Language Models (VLM).

## Technologies Used

- **AI Engine**: [Cactus Compute](https://github.com/cactus-compute/cactus) (running `functiongemma-270m-it`, `whisper-small`, `lfm2-vl-450m`)
- **Cloud Fallback**: [Google Gemini API](https://ai.google.dev/) (google-genai)
- **Backend**: Python, FastAPI, Pydantic
- **Frontend**: Electron, React, Tailwind CSS
- **Protocols**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## Project Structure

```text
├── app/
│   ├── backend/           # Python Intelligence Server
│   │   ├── notion_tools/  # Notion MCP Client
│   │   ├── slack_tools/   # Slack MCP Client
│   │   └── server.py      # FastAPI entry point
│   └── frontend/          # Electron Overlay App
│       ├── src/           # React UI components
│       └── main.js        # Window management logic
├── cactus/                # Cactus Engine (C++ core & bindings)
├── src/                   # Core Hybrid Logic (The "Brain")
│   └── main.py            # Hybrid routing algorithm
├── scripts/               # Hackathon Utilities
│   ├── benchmark.py       # Performance scoring
│   └── submit.py          # Leaderboard submission
└── docs/                  # Documentation
```

## System Architecture & Approach

Nova was built with a specific philosophy: **Local for speed, Cloud for power.**

### 1. The Hybrid Engine (`src/main.py`)
At the heart of Nova is a smart router that sits between the user and the models. This was our primary focus for the hackathon challenge.
- **Local Path**: When a user asks for a specific action ("Set a timer for 10 minutes", "Play Jazz"), Nova uses **FunctionGemma** running on **Cactus**. This ensures the request is handled instantly and privately, without leaving the device.
- **Cloud Path**: If the request requires broad world knowledge or complex reasoning ("Summarize this article and email it to the team"), the router detects the intent and forwards it to **Gemini Flash**.
- **Result**: We achieve the responsiveness of a native tool with the intelligence of a large language model.

### 2. Cactus Compute Integration
We utilized **Cactus** to bring efficient AI inference to the desktop.
- **LibCactus**: We use the Python bindings to load quantized models directly into memory. This avoids the overhead of running heavy local servers like Ollama.
- **Whisper**: Integrated directly into the backend for real-time speech-to-text.
- **VLM**: We use Cactus's vision capabilities to embed screen snapshots, giving the AI "eyes" to understand the user's context.

### 3. Model Context Protocol (MCP)
To make Nova truly useful, it needs to interact with the world. We implemented a custom MCP client that decouples the tool logic from the AI model.
- **Dynamic Discovery**: Nova queries available tools (Notion, Slack) at runtime.
- **Standardized Execution**: Whether the tool runs locally (e.g., system timer) or remotely (e.g., Notion API), the AI interacts with it using a unified schema.

## Key Lessons Learned

- **Latency Matters**: For voice interfaces, even a 500ms delay feels sluggish. Running tool selection locally with FunctionGemma drastically improved the "snappiness" of the assistant compared to cloud-only solutions.
- **Prompt Engineering for Small Models**: FunctionGemma (270M) is surprisingly capable but requires strict prompt formatting. We learned to use specific control tokens (`<start_function_declaration>`) to get reliable structured output.
- **Electron + Python**: Packaging a full Python environment with native C++ bindings inside an Electron app is complex but necessary for a standalone distribution.

## Getting Started

### Prerequisites
- **macOS** (Apple Silicon recommended)
- **Node.js** (v16+)
- **Python** (3.10+)
- **Google Gemini API Key**

### Quick Start

1.  **Clone & Setup**:
    ```bash
    git clone https://github.com/cactus-compute/cactus
    cd cactus
    source ./setup
    cactus build --python
    ```

2.  **Install Dependencies**:
    ```bash
    pip install google-genai requests fastapi uvicorn notion-client slack-sdk
    cd app/frontend && npm install
    ```

3.  **Run Nova**:
    *   **Backend** (Terminal 1):
        ```bash
        export GEMINI_API_KEY="your-key"
        python app/backend/server.py
        ```
    *   **Frontend** (Terminal 2):
        ```bash
        cd app/frontend && npm start
        ```

> For detailed setup instructions, see [docs/installation.md](docs/installation.md).

## Documentation

- [**System Architecture**](docs/architecture.md)
- [**API Reference**](docs/api.md)
- [**Usage Guide**](docs/usage.md)
- [**Hackathon Logs**](docs/logs/)
