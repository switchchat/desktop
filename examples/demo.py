
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_response(label, res):
    print(f"\n=== {label} ===")
    if res.status_code != 200:
        print(f"Error {res.status_code}: {res.text}")
        return

    data = res.json()
    print(json.dumps(data, indent=2))

def main():
    print("Checking server health...")
    try:
        res = requests.get(f"{BASE_URL}/health")
        if res.status_code != 200:
            print("Server not healthy!")
            return
        print("Server is up!")
    except Exception as e:
        print(f"Could not connect: {e}")
        return

    # 1. Weather check (local tool call via FunctionGemma)
    print("\n--- Demo 1: Weather Check (Local Tool) ---")
    payload = {
        "messages": [{"role": "user", "content": "What is the weather in San Francisco?"}],
        # Tools will be injected by backend if empty
        "tools": [] 
    }
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    print_response("Weather Check", res)

    # 2. Notion Search (using real Notion tools if configured)
    print("\n--- Demo 2: Notion Search ---")
    payload = {
        "messages": [{"role": "user", "content": "Search for 'meeting notes' in Notion."}],
        "tools": []
    }
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    print_response("Notion Search", res)

    # 3. Slack Message (using real Slack tools if configured)
    print("\n--- Demo 3: Slack Message ---")
    payload = {
        "messages": [{"role": "user", "content": "Send a message to #general saying 'Hello from Nova!'"}],
        "tools": []
    }
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    print_response("Slack Message", res)

if __name__ == "__main__":
    main()
