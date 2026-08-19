"""State change detector — compares current data against previous state.
Most runs should detect no changes and exit immediately.
"""
import json, hashlib, os
from pathlib import Path

STATE_FILE = Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "state" / "current_state.json"

def _hash_state(state):
    meaningful = {
        "kp": round(state.get("kp") or 0, 1),
        "bz": round(state.get("bz") or 0, 1) if state.get("bz") else None,
        "solar_wind_speed": round(state.get("solar_wind_speed") or 0) if state.get("solar_wind_speed") else None,
        "flare_class": state.get("flare_class"),
        "neo_count": state.get("neo_count"),
    }
    return hashlib.sha256(json.dumps(meaningful, sort_keys=True).encode()).hexdigest()

def load_state():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except: pass
    return {}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def detect_changes(current):
    previous = load_state()
    prev_hash = previous.get("_state_hash")
    curr_hash = _hash_state(current)
    if prev_hash == curr_hash:
        return [], previous, False
    changed = []
    for key in ["kp", "bz", "solar_wind_speed", "flare_class", "neo_count"]:
        if previous.get(key) != current.get(key):
            changed.append(key)
    current["_state_hash"] = curr_hash
    save_state(current)
    return changed, previous, True