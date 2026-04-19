import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory", "memory.json")

def update_memory(ticket_id, data):
    try:
        with open(MEMORY_FILE) as f:
            memory = json.load(f)
    except:
        memory = {}

    memory[ticket_id] = data

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)