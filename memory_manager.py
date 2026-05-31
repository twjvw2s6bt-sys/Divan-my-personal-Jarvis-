import json
import os

MEMORY_PATH = "memory/memory.json"

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return {}
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def memory_to_prompt(memory):
    return f"""
User profile:
- Tone preference: {memory.get('tone', 'direct')}
- Known weaknesses: {', '.join(memory.get('weaknesses', [])) or 'none yet'}
- Goals: {', '.join(memory.get('goals', []))}
"""

def add_session_summary(memory, summary):
    history = memory.get("session_history", [])
    history.append(summary)
    memory["session_history"] = history[-5:]  # keep last 5 sessions
    save_memory(memory)
