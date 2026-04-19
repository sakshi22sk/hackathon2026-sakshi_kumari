import json
from datetime import datetime

LOG_FILE = "logs/audit_log.json"

def log_event(ticket_id, step, data):
    entry = {
        "timestamp": str(datetime.now()),
        "ticket_id": ticket_id,
        "step": step,
        "data": data
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")