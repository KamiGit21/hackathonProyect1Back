# app/events.py
import json
from datetime import datetime

def emit_event(name: str, payload: dict):
    print(f"[EVENT] {name} @ {datetime.utcnow().isoformat()}Z :: {json.dumps(payload, ensure_ascii=False)}")
