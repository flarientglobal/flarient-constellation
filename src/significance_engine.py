"""Event significance engine — deterministic threshold-based detection. No LLM calls."""
import json, os
from pathlib import Path

CONFIG_PATH = Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "config" / "significance_thresholds.json"

def load_config():
    if CONFIG_PATH.exists(): return json.loads(CONFIG_PATH.read_text())
    return {}

def check_significance(snapshot, changed_fields, previous):
    config = load_config()
    events = []
    curr_kp = snapshot.get("kp", 0)
    prev_kp = (previous or {}).get("kp", 0)
    for t in config.get("kp_thresholds", []):
        if curr_kp >= t["value"] and prev_kp < t["value"]:
            events.append({"event_type": "kp_threshold", "severity": t["label"], "current_value": curr_kp, "previous_value": prev_kp, "significance": t["significance"], "summary": f"Kp crossed {t['label']} ({prev_kp} -> {curr_kp})"})
    curr_bz = snapshot.get("bz") or 0
    prev_bz = (previous or {}).get("bz") or 0
    for t in config.get("bz_thresholds", []):
        if curr_bz <= t["value"] and prev_bz > t["value"]:
            events.append({"event_type": "bz_threshold", "current_value": curr_bz, "previous_value": prev_bz, "significance": t["significance"], "summary": f"Bz dropped below {t['value']} nT ({prev_bz} -> {curr_bz})"})
    curr_sw = snapshot.get("solar_wind_speed") or 0
    prev_sw = (previous or {}).get("solar_wind_speed") or 0
    for t in config.get("solar_wind_thresholds", []):
        if curr_sw >= t["value"] and prev_sw < t["value"]:
            events.append({"event_type": "solar_wind_threshold", "current_value": curr_sw, "previous_value": prev_sw, "significance": t["significance"], "summary": f"Solar wind crossed {t['value']} km/s ({prev_sw} -> {curr_sw})"})
    curr_flare = snapshot.get("flare_class", "unknown")
    prev_flare = (previous or {}).get("flare_class", "unknown")
    for t in config.get("flare_thresholds", []):
        if curr_flare.startswith(t["class"]) and not prev_flare.startswith(t["class"]):
            events.append({"event_type": "solar_flare", "severity": curr_flare, "current_value": curr_flare, "previous_value": prev_flare, "significance": t["significance"], "summary": f"{t['class']}-class flare: {curr_flare}"})
    neo_cfg = config.get("neo_thresholds", {})
    for obj in snapshot.get("neo_objects", []):
        diam = obj.get("diameter_m", 0)
        dist_ld = obj.get("miss_distance_km", 999999999) / 384400
        if diam >= neo_cfg.get("min_diameter_m", 50) and dist_ld <= neo_cfg.get("max_miss_distance_ld", 10):
            events.append({"event_type": "neo_approach", "severity": "hazardous" if obj.get("is_hazardous") else "notable", "current_value": obj, "significance": "major" if obj.get("is_hazardous") else "moderate", "summary": f"NEO {obj.get('name', '?')}: {diam}m, {dist_ld:.1f} LD"})
    return events