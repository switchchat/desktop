# Usage Guide

This guide explains how to use the Nova desktop assistant and how to leverage its features for the hackathon.

## Running the Application

The application requires both the Python backend and the Electron frontend to be running.

### 1. Start the Backend
Open a terminal in the project root:

```bash
# Set your API keys first
export GEMINI_API_KEY="your-key"

# Start the server
python app/backend/server.py
```

You will see logs indicating the server is running at `http://127.0.0.1:8000`.

### 2. Start the Frontend
Open a **new terminal** window:

```bash
cd app/frontend
npm start
```

This will launch the Nova application. You will see two windows:
1.  **Control Panel**: The main window for logs, settings, and manual chat.
2.  **Overlay**: A floating, transparent bar (initially empty or showing a greeting).

## Using Nova

### Voice Commands 🗣️
1.  Click the **Microphone** icon on the overlay or Control Panel.
2.  Speak your command (e.g., *"What is the weather in Tokyo?"*).
3.  Nova will transcribe your speech locally using Whisper and then process the query.

### Screen Analysis 👁️
1.  Click the **Eye** icon.
2.  Nova will take a snapshot of your current screen.
3.  Ask a question about what's on your screen (e.g., *"Summarize this email"*).

### Using Tools 🛠️

Nova can interact with external apps if you have configured the API keys.

- **Notion**: *"Search for meeting notes about the Q1 roadmap."*
- **Slack**: *"Send a message to #general saying I'll be late."*
- **System**: *"Set a timer for 10 minutes."*

## Hackathon Workflow

For the Cactus x Google DeepMind Hackathon, your mission is to optimize the AI routing logic.

### The Challenge
Optimize `src/main.py` to:
1.  Maximize the use of the **Local Model** (FunctionGemma).
 57.  **Cloud Model**: Gemini 3.0 Flash (smarter, but adds latency and cost).
2.  Maintain high **Accuracy** (correct tool calls).
3.  Minimize **Latency**.

### Benchmarking
Test your logic against the standard evaluation set:

```bash
python scripts/benchmark.py
```

### Submitting
Upload your score to the leaderboard:

```bash
python scripts/submit.py --team "YourTeamName" --location "YourCity"
```
