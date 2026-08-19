"""Distribution compiler — transforms significant events into multiple assets."""
import json, os, datetime
from pathlib import Path
from viral_score import calculate_vis, classify_distribution
from ai_router import generate_summary
from badge_generator import generate_all_badges

REPO_DIR = Path(os.environ.get("GITHUB_WORKSPACE", "."))

def _event_id(event, snapshot):
    date = datetime.date.today().isoformat()
    et = event.get("event_type", "event")
    sev = str(event.get("severity", "")).lower().replace(" ", "-")
    return f"{date}-{et}-{sev}"[:60]

def _flarient_url(event):
    et = event.get("event_type", "")
    if "storm" in et or "kp" in et: return "https://flarient.com/storm"
    if "flare" in et: return "https://flarient.com/solar-flares"
    if "aurora" in et: return "https://flarient.com/aurora-forecast"
    if "neo" in et: return "https://flarient.com/near-earth-objects"
    return "https://flarient.com"

def compile_event(event, snapshot, previous):
    vis, vis_components = calculate_vis(event, snapshot)
    dist_level = classify_distribution(vis)
    if dist_level == "none":
        print(f"[COMPILE] Skipping {event.get('event_type')} — VIS {vis} (none)")
        return None
    public_summary, ai_source = generate_summary(event)
    now = datetime.datetime.now(datetime.timezone.utc)
    event_obj = {
        "event_id": _event_id(event, snapshot),
        "event_type": event.get("event_type"),
        "status": "active",
        "severity": event.get("severity"),
        "novelty": "new",
        "confidence": "moderate",
        "started_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "kp": snapshot.get("kp"),
        "bz": snapshot.get("bz"),
        "solar_wind": snapshot.get("solar_wind_speed"),
        "xray_class": snapshot.get("flare_class") if event.get("event_type") == "solar_flare" else None,
        "data_sources": ["NOAA SWPC", "NASA NeoWS"],
        "previous_state": {k: previous.get(k) for k in ["kp", "bz", "solar_wind_speed", "flare_class"] if k in (previous or {})},
        "current_state": {k: snapshot.get(k) for k in ["kp", "bz", "solar_wind_speed", "flare_class"]},
        "flarient_url": _flarient_url(event),
        "viral_information_score": vis,
        "public_summary": public_summary,
        "technical_summary": event.get("summary", ""),
        "ai_source": ai_source,
    }
    ledger_dir = REPO_DIR / "events" / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}" / event_obj["event_id"]
    ledger_dir.mkdir(parents=True, exist_ok=True)
    (ledger_dir / "event.json").write_text(json.dumps(event_obj, indent=2))
    generate_all_badges(snapshot)
    print(f"[COMPILE] Event {event_obj['event_id']} — VIS {vis} ({dist_level}), AI: {ai_source}")
    return event_obj

def compile_all(events, snapshot, previous):
    compiled = []
    for event in events:
        result = compile_event(event, snapshot, previous)
        if result: compiled.append(result)
    if not compiled: generate_all_badges(snapshot)
    return compiled