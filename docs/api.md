# API Reference

This document details the API endpoints provided by the Nova backend server and the core Python SDK methods available for the hackathon logic.

## Backend HTTP API

The backend runs a FastAPI server, typically accessible at `http://127.0.0.1:8000`.

### Chat & Inference

#### `POST /chat`
Process a user message and generate a response using the hybrid AI engine.

- **Endpoint**: `/chat`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "messages": [
      {
        "role": "user", 
        "content": "What is the weather?"
      }
    ],
    "tools": [ ... ],       // Optional: Custom tool definitions
    "confidence_threshold": 0.7 // Optional: Threshold for cloud fallback
  }
  ```
- **Response**:
  ```json
  {
    "response": "The weather is sunny.",
    "function_calls": [],
    "source": "on-device",  // or "cloud (fallback)"
    "confidence": 0.95
  }
  ```

#### `POST /transcribe`
Transcribe audio data using the local Whisper model.

- **Endpoint**: `/transcribe`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
    - `file`: The audio file (WAV/MP3).
- **Response**:
  ```json
  {
    "text": "Hello world"
  }
  ```

#### `POST /analyze-screen`
Analyze a screenshot to provide context or answer questions about the screen content.

- **Endpoint**: `/analyze-screen`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
    - `file`: The image file (PNG/JPG).
    - `prompt`: "Describe this image" (Optional).
- **Response**:
  ```json
  {
    "description": "A screenshot of a code editor showing Python code..."
  }
  ```

---

## Cactus SDK Reference

These functions are available in the `cactus` python module for use in `src/main.py`.

### Initialization & Cleanup

#### `cactus_init(model_path, corpus_dir=None)`
Initialize a model handle.
- **model_path** (str): Absolute or relative path to the model weights.
- **corpus_dir** (str, optional): Directory containing text files for RAG.
- **Returns**: A model handle object.

#### `cactus_destroy(model)`
Free the memory associated with a model handle.
- **model**: The model handle to destroy.

### Generation

#### `cactus_complete(model, messages, **options)`
Generate a completion or chat response.

- **Parameters**:
    - `model`: The model handle.
    - `messages`: List of dicts `{"role": "...", "content": "..."}`.
- **Options**:
    - `tools` (list): Tool definitions (JSON schema) for function calling.
    - `temperature` (float): Sampling temperature (default 0.7).
    - `max_tokens` (int): Limit generation length (default 512).
    - `force_tools` (bool): If True, forces the model to generate a tool call.
- **Returns**: A JSON string containing the raw model response.

### Utilities

#### `cactus_transcribe(model, audio_path)`
Transcribe an audio file.
- **model**: Handle to a Whisper model.
- **audio_path**: Path to the audio file.
- **Returns**: JSON string `{"text": "..."}`.

---

## Tool Integrations (MCP)

Nova implements the Model Context Protocol to interface with external tools.

### Notion Tools (`app/backend/notion_tools`)

- **`POST /notion/search`**: Search Notion pages.
- **`GET /notion/page/{page_id}`**: Retrieve page content.
- **`POST /notion/page`**: Create a new page.
- **`GET /notion/tools/schemas`**: Get JSON schemas for LLM usage.

### Slack Tools (`app/backend/slack_tools`)

- **`POST /slack/post_message`**: Send a message to a channel.
- **`GET /slack/history/{channel}`**: Read channel history.
- **`GET /slack/tools/schemas`**: Get JSON schemas for LLM usage.
