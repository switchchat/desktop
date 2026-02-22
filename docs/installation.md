# Installation Guide

This guide covers the comprehensive setup process for Nova, including the core Cactus engine (required for the hackathon) and the full desktop application.

## Prerequisites

- **Operating System**: macOS 12+ (Required for Cactus engine optimization).
- **Hardware**: Apple Silicon (M1/M2/M3) recommended for optimal performance.
- **Software**:
  - Python 3.10 or higher
  - Node.js v16+ & npm
  - `git`
  - `make` / `cmake` (for building bindings)

## Part 1: Core Cactus Setup (Hackathon Base)

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/cactus-compute/cactus
    cd cactus
    ```

2.  **Initialize Environment**
    Run the setup script to configure the environment variables and paths:
    ```bash
    source ./setup
    cd ..
    ```
    *Note: You may need to add `source /path/to/cactus/setup` to your `.zshrc` or `.bashrc` for persistence.*

3.  **Build Cactus**
    Compile the Python bindings for the engine:
    ```bash
    cactus build --python
    ```

4.  **Download Models**
    Download the quantized models required for local inference:
    ```bash
    # FunctionGemma (Logic/Tools)
    cactus download google/functiongemma-270m-it --reconvert
    
    # Whisper (Speech-to-Text)
    cactus download openai/whisper-small --reconvert
    ```

5.  **Configure Cloud Fallback**
    - Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/api-keys).
    - Export the key:
      ```bash
      export GEMINI_API_KEY="your-key-here"
      ```

## Part 2: Application Setup

### Backend Setup

The backend handles AI logic and tool execution.

1.  **Install Python Dependencies**
    ```bash
    pip install google-genai requests fastapi uvicorn notion-client slack-sdk
    ```

2.  **Configure Tool Keys (Optional)**
    If you plan to use Notion or Slack integrations:
    ```bash
    export NOTION_API_KEY="your-notion-secret"
    export SLACK_BOT_TOKEN="your-slack-token"
    ```

### Frontend Setup

The frontend provides the invisible UI.

1.  **Navigate to Frontend Directory**
    ```bash
    cd app/frontend
    ```

2.  **Install Node Dependencies**
    ```bash
    npm install
    ```

3.  **Build React Assets**
    ```bash
    npm run build
    ```

## Verification

To verify your installation:

1.  **Run the Benchmark**:
    ```bash
    python scripts/benchmark.py
    ```
    *Success: You should see a table of scores and latencies.*

2.  **Start the Server**:
    ```bash
    python app/backend/server.py
    ```
    *Success: Server should start on port 8000 without errors.*
