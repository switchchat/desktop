# Nova - Hybrid AI Desktop Assistant

**Nova** is an intelligent, privacy-preserving desktop assistant that leverages hybrid AI to enhance your workflow. By combining the speed and privacy of on-device inference (**Cactus + FunctionGemma**) with the reasoning capabilities of the cloud (**Gemini**), Nova provides real-time assistance without compromising user data.

## Features

-   **Privacy-First Analysis**: Your voice and queries are processed locally on your device by default. Sensitive information never leaves your machine unless complex reasoning is required.
-   **Hybrid Intelligence**: Seamlessly switches between a lightweight local model (**FunctionGemma 270M**) for speed and a powerful cloud model (**Gemini 3.0 Flash**) for complex tasks.
-   **Invisible Overlay**: A transparent, click-through interface built with Electron that floats above your windows, providing assistance without breaking your flow.
-   **System Control**: Deep integration with your desktop to control music, set timers, and manage tools via the **Model Context Protocol (MCP)**.
-   **Optimized for Apple Silicon**: Built on the **Cactus engine**, delivering blazing fast inference speeds on M-series chips.

## Technologies Used

-   **On-Device AI**: Google FunctionGemma (270M parameters), Whisper (Small), LFM2-VL (Vision) running on Cactus.
-   **Cloud AI**: Google Gemini 3.0 Flash for fallback reasoning.
-   **Backend**: Python, FastAPI, Uvicorn.
-   **Frontend**: Electron, React, Tailwind CSS.
-   **Tooling**: cactus-python SDK, google-genai SDK, MCP (Model Context Protocol).

## Project Structure

```text
├── app/                    # 📦 The Application Wrapper
│   ├── backend/            # 🧠 The Brain (FastAPI Server)
│   │   ├── server.py       # API Entry point
│   │   ├── notion_tools/   # Notion MCP Client
│   │   └── slack_tools/    # Slack MCP Client
│   └── frontend/           # 👁️ The Eyes (Electron Overlay)
│       ├── src/            # React UI
│       └── main.js         # Window Management
├── src/                    # ⚡️ The Core Logic
│   └── main.py             # Hybrid Routing Algorithm
├── scripts/                # 🛠️ Utilities
│   ├── benchmark.py        # Performance Evaluation
│   └── sync_backend.py     # Deployment Sync
└── docs/                   # 📚 Documentation
```

## System Architecture

Nova operates on a three-tier architecture designed for minimal latency and maximum privacy:

1.  **Presentation Layer**: The **Electron Frontend** provides an "invisible" overlay that captures user interactions (voice, text, screen content) and renders non-intrusive responses.
2.  **Application Layer**: The **Python Backend** receives events, manages the application state, and orchestrates tool execution via the Model Context Protocol (MCP).
3.  **Intelligence Layer**: The **Hybrid Router** (`src/main.py`) determines the best execution path:
    -   **Local Path**: Uses **FunctionGemma** via Cactus for fast, private inference (typical latency: 50-100ms). Used for system controls, music, and simple queries.
    -   **Cloud Path**: Falls back to **Gemini 3.0 Flash** when the local model's confidence is low or the task requires broad world knowledge (typical latency: 500ms+).

## Our Approach

The core innovation in Nova is its **Hybrid Routing Strategy**. Instead of relying solely on the cloud (slow, privacy-invasive) or solely on the edge (limited reasoning), we implemented a dynamic router:

-   **Confidence-Based Routing**: We utilize the confidence scores returned by the Cactus engine. If the local model is confident, we use its result immediately.
-   **Latency Optimization**: By prioritizing the local model, we achieve near-instantaneous feedback for common tasks, essential for a real-time voice assistant.
-   **Graceful Fallback**: If the local model struggles or returns a low-confidence score, the system seamlessly delegates the task to Gemini Cloud, ensuring high accuracy even for ambiguous inputs.

## Getting Started

### Prerequisites

-   **macOS** with Apple Silicon (M1/M2/M3/M4).
-   **Python 3.10+**.
-   **Node.js v16+**.
-   **Google Gemini API Key**.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/switchchat/desktop.git
    cd desktop
    ```

2.  **Setup Cactus**:
    Follow the [Cactus installation guide](https://github.com/cactus-compute/cactus) to build the `libcactus` bindings.

3.  **Install Dependencies**:
    ```bash
    pip install google-genai requests fastapi uvicorn notion-client slack-sdk
    cd app/frontend && npm install
    ```

4.  **Run Nova**:
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<p align="center">
  Built with 🌵 <b>Cactus</b> and 🧠 <b>Google DeepMind</b>
</p>