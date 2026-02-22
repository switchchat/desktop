
import sys
import os
import json
import tempfile
import shutil
import time
import traceback

# Debug logging for packaged app (before imports)
LOG_FILE = os.path.join(tempfile.gettempdir(), "nova_backend.log")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.ctime()}: {msg}\n")

try:
    log("Backend starting...")
    log(f"CWD: {os.getcwd()}")
    
    # Add project root to sys.path
    # server.py is in app/frontend/python_backend/
    # root is app/frontend/ (where src/ and cactus/ live)
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log(f"PROJECT_ROOT: {PROJECT_ROOT}")
    
    if PROJECT_ROOT not in sys.path:
        sys.path.append(PROJECT_ROOT)
        log(f"Added {PROJECT_ROOT} to sys.path")

    # Ensure cactus python src is in path
    # app/frontend/cactus/python/src
    CACTUS_PYTHON_SRC = os.path.join(PROJECT_ROOT, "cactus/python/src")
    log(f"CACTUS_PYTHON_SRC: {CACTUS_PYTHON_SRC}")
    
    if CACTUS_PYTHON_SRC not in sys.path:
        sys.path.insert(0, CACTUS_PYTHON_SRC)
        log(f"Added {CACTUS_PYTHON_SRC} to sys.path")
        
    log(f"Final sys.path: {sys.path}")

    from fastapi import FastAPI, HTTPException, UploadFile, File, Body
    from pydantic import BaseModel
    from typing import List, Dict, Any, Optional

    # Notion client + tools
    try:
        from notion_tools.notion_mcp import NotionMCPClient
        from notion_tools.notion_tools import notion_tools
        from notion_tools.schemas import get_schemas as get_notion_schemas
        log("Notion tools loaded")
    except Exception as e:
        log(f"Notion tools failed: {e}")
        NotionMCPClient = None
        notion_tools = None
        get_notion_schemas = None

    # Slack client + tools
    try:
        from slack_tools import SlackMCPClient, slack_tools
        log("Slack tools loaded")
    except Exception as e:
        log(f"Slack tools failed: {e}")
        SlackMCPClient = None
        slack_tools = None

    # Import core logic
    try:
        log("Importing src.main...")
        from src.main import generate_hybrid
        log("src.main imported")
        
        log("Importing cactus...")
        from cactus import cactus_init, cactus_destroy, cactus_transcribe, cactus_image_embed, cactus_complete
        log("cactus imported")
    except ImportError as e:
        log(f"CRITICAL IMPORT ERROR: {e}")
        log(traceback.format_exc())
        raise RuntimeError(f"Failed to import core modules: {e}")

except Exception as e:
    log(f"CRITICAL STARTUP ERROR: {e}")
    log(traceback.format_exc())
    raise

app = FastAPI()

# Global model handles (lazy loaded)
whisper_model = None
vlm_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        # In a real app, you'd check if weights exist
        try:
            whisper_model = cactus_init("cactus/weights/whisper-small")
        except Exception as e:
            print(f"Failed to init whisper: {e}")
            return None
    return whisper_model

def get_vlm_model():
    global vlm_model
    if vlm_model is None:
        try:
            vlm_model = cactus_init("cactus/weights/lfm2-vl-450m")
        except Exception as e:
            print(f"Failed to init VLM: {e}")
            return None
    return vlm_model

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = []
    confidence_threshold: float = 0.7

# ---------------------------------------------------------------------------
# Standard System Tools
# ---------------------------------------------------------------------------
SYSTEM_TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name or location"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "set_alarm",
        "description": "Set an alarm for a specific time",
        "parameters": {
            "type": "object",
            "properties": {
                "hour": {"type": "integer", "description": "Hour (0-23)"},
                "minute": {"type": "integer", "description": "Minute (0-59)"}
            },
            "required": ["hour", "minute"]
        }
    },
    {
        "name": "set_timer",
        "description": "Set a countdown timer",
        "parameters": {
            "type": "object",
            "properties": {
                "minutes": {"type": "integer", "description": "Duration in minutes"}
            },
            "required": ["minutes"]
        }
    },
    {
        "name": "play_music",
        "description": "Play a song or music genre",
        "parameters": {
            "type": "object",
            "properties": {
                "song": {"type": "string", "description": "Song title, artist, or genre"}
            },
            "required": ["song"]
        }
    },
    {
        "name": "create_reminder",
        "description": "Create a reminder for a task",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Reminder content/title"},
                "time": {"type": "string", "description": "Time string (e.g. '5 PM', 'tomorrow')"}
            },
            "required": ["title", "time"]
        }
    },
    {
        "name": "search_contacts",
        "description": "Search for a contact",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name to search for"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "send_message",
        "description": "Send a text message",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Name or phone number"},
                "message": {"type": "string", "description": "Message content"}
            },
            "required": ["recipient", "message"]
        }
    }
]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Inject available tools if none provided or merge them
        current_tools = request.tools or []
        
        # 1. Add Standard System Tools (ALWAYS)
        existing_names = {t["name"] for t in current_tools}
        for tool in SYSTEM_TOOLS:
            if tool["name"] not in existing_names:
                current_tools.append(tool)
                existing_names.add(tool["name"])
        
        # Add Notion tools if available
        if notion_tools:
            try:
                notion_schemas = notion_tools.tool_schemas()
                # Avoid duplicates by name
                existing_names = {t["name"] for t in current_tools}
                for tool_wrapper in notion_schemas:
                    # tool_schemas returns {type: function, function: {...}}
                    # We need the inner function dict
                    tool = tool_wrapper.get("function", tool_wrapper)
                    if tool["name"] not in existing_names:
                        current_tools.append(tool)
            except Exception as e:
                print(f"Error loading Notion tools: {e}")

        # Add Slack tools if available
        if slack_tools:
            try:
                slack_schemas = slack_tools.tool_schemas()
                existing_names = {t["name"] for t in current_tools}
                for tool_wrapper in slack_schemas:
                    tool = tool_wrapper.get("function", tool_wrapper)
                    if tool["name"] not in existing_names:
                        current_tools.append(tool)
            except Exception as e:
                print(f"Error loading Slack tools: {e}")

        # Call the hackathon logic
        result = generate_hybrid(
            request.messages, 
            current_tools, 
            confidence_threshold=request.confidence_threshold
        )
        
        # Add available tools to the result for frontend visibility
        result["available_tools"] = [t["name"] for t in current_tools]

        # Execute tools if present
        execution_results = []
        if "function_calls" in result and result["function_calls"]:
            print(f"Executing {len(result['function_calls'])} tools...")
            for call in result["function_calls"]:
                name = call.get("name")
                args = call.get("arguments", {})
                
                tool_result = {"ok": False, "error": "Unknown tool or client not available"}
                
                if name.startswith("notion_") and notion_tools:
                    tool_result = notion_tools.call_tool(name, args)
                elif name.startswith("slack_") and slack_tools:
                    tool_result = slack_tools.call_tool(name, args)
                
                # Tag with name for context
                tool_result["tool"] = name
                execution_results.append(tool_result)
            
            result["execution_results"] = execution_results
            
            # Append execution summary to response
            successes = [r for r in execution_results if r.get("ok")]
            if successes:
                summary = f"\n\nExecuted {len(successes)} action(s) successfully."
                if not result.get("response"):
                    result["response"] = "Actions processed." + summary
                else:
                    result["response"] += summary
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_path = temp_audio.name
        
        model = get_whisper_model()
        if model:
            # Use real cactus transcribe
            response_str = cactus_transcribe(model, temp_path)
            response = json.loads(response_str)
            text = response.get("response", "")
        else:
            # Mock if model load failed
            text = "Mock transcription (Whisper model not loaded)"
            
        os.remove(temp_path)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-screen")
async def analyze_screen(file: UploadFile = File(...), prompt: str = "Describe this image"):
    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
            shutil.copyfileobj(file.file, temp_img)
            temp_path = temp_img.name
            
        model = get_vlm_model()
        if model:
            # For VLM, we usually treat it as a completion with image context
            # But the provided API only showed cactus_image_embed.
            # Assuming there's a way to do VLM chat or we use embeddings.
            # The docs showed: model = cactus_init("weights/lfm2-vl-450m")
            # And then cactus_complete(model, messages).
            # We might need to attach the image path to the message?
            # The docs didn't explicitly show VLM chat syntax, but usually it's in the message content.
            # Let's assume standard VLM format or just return a placeholder for now.
            
            # If the API supports image paths in content:
            # messages = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": temp_path}}]}]
            # But cactus C API might be different. 
            # Given the docs, let's just assume we can get an embedding or run a simple prompt.
            
            # Mocking a description for now as VLM specific syntax isn't fully clear in provided snippets
            description = "Screen analysis not fully implemented (VLM syntax TBD)"
        else:
            description = "Mock screen analysis (VLM model not loaded)"
            
        os.remove(temp_path)
        return {"description": description}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------- Notion endpoints ---------------------------------


def get_notion_client() -> NotionMCPClient:
    if NotionMCPClient is None:
        raise RuntimeError("Notion client not available (missing module or dependency)")
    try:
        return NotionMCPClient()
    except Exception as exc:
        raise RuntimeError(f"Failed to init Notion client: {exc}")


def get_slack_client() -> SlackMCPClient:
    if SlackMCPClient is None:
        raise RuntimeError("Slack client not available (missing module or dependency)")
    try:
        return SlackMCPClient()
    except Exception as exc:
        raise RuntimeError(f"Failed to init Slack client: {exc}")


class NotionSearchRequest(BaseModel):
    query: Optional[str] = None
    page_size: Optional[int] = 20


@app.post("/notion/search")
async def notion_search(req: NotionSearchRequest):
    try:
        client = get_notion_client()
        res = client.search(req.query, page_size=req.page_size or 20)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notion/page/{page_id}")
async def notion_get_page(page_id: str):
    try:
        client = get_notion_client()
        res = client.get_page(page_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NotionCreateRequest(BaseModel):
    database_id: str
    properties: Dict[str, Any]
    children: Optional[List[Dict[str, Any]]] = None


@app.post("/notion/page")
async def notion_create_page(body: NotionCreateRequest):
    try:
        client = get_notion_client()
        res = client.create_page(body.database_id, body.properties, body.children)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NotionUpdateRequest(BaseModel):
    properties: Dict[str, Any]


@app.patch("/notion/page/{page_id}")
async def notion_update_page(page_id: str, body: NotionUpdateRequest):
    try:
        client = get_notion_client()
        res = client.update_page(page_id, body.properties)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NotionAppendRequest(BaseModel):
    children: List[Dict[str, Any]]


@app.patch("/notion/blocks/{block_id}/append")
async def notion_append_block(block_id: str, body: NotionAppendRequest):
    try:
        client = get_notion_client()
        res = client.append_block(block_id, body.children)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notion/tools/schemas")
async def notion_tool_schemas():
    """Return function-call schemas for LLM agents to consume."""
    # Prefer packaged JSON schemas when available
    if get_notion_schemas is not None:
        try:
            return {"schemas": get_notion_schemas()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    if notion_tools is None:
        raise HTTPException(status_code=500, detail="Notion tools module not available")
    try:
        return {"schemas": notion_tools.tool_schemas()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- Slack endpoints ---------------------------------


class SlackPostRequest(BaseModel):
    channel: str
    text: Optional[str] = None
    blocks: Optional[List[Dict[str, Any]]] = None
    thread_ts: Optional[str] = None


@app.post("/slack/post_message")
async def slack_post_message(body: SlackPostRequest):
    try:
        client = get_slack_client()
        res = client.post_message(body.channel, body.text, body.blocks, body.thread_ts)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/slack/conversations")
async def slack_list_conversations(types: Optional[str] = "public_channel,private_channel,im,mpim", limit: int = 100):
    try:
        client = get_slack_client()
        res = client.list_conversations(types=types, limit=limit)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/slack/history/{channel}")
async def slack_get_history(channel: str, limit: int = 100):
    try:
        client = get_slack_client()
        res = client.get_conversation_history(channel, limit=limit)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SlackUploadForm(BaseModel):
    channels: List[str]
    initial_comment: Optional[str] = None


@app.post("/slack/upload")
async def slack_upload_file(channels: List[str] = Body(...), file: UploadFile = File(...), initial_comment: Optional[str] = Body(None)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tempf:
            shutil.copyfileobj(file.file, tempf)
            temp_path = tempf.name

        client = get_slack_client()
        res = client.upload_file(channels, temp_path, filename=file.filename, initial_comment=initial_comment)
        os.remove(temp_path)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/slack/tools/schemas")
async def slack_tool_schemas():
    if slack_tools is None:
        raise HTTPException(status_code=500, detail="Slack tools module not available")
    try:
        return {"schemas": slack_tools.tool_schemas()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import traceback
    
    # Setup logging to a file for debugging packaged app
    log_file = os.path.join(tempfile.gettempdir(), "nova_backend.log")
    try:
        with open(log_file, "w") as f:
            f.write(f"Starting backend at {time.ctime()}\n")
            f.write(f"CWD: {os.getcwd()}\n")
            f.write(f"sys.path: {sys.path}\n")
            
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"\nCRITICAL ERROR: {e}\n")
            f.write(traceback.format_exc())
        raise
