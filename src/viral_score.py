"""Viral Information Score (VIS) — weighted score determining distribution level."""
import json, os
from pathlib import Path

WEIGHTS_PATH = Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "config" / "vis_weights.json"

def load_weights():
    if WEIGHTS_PATH.exists(): return json.loads(WEIGHTS_PATH.read_text())
    return {}

def _component_scores(event, snapshot):
    scores = {}
    sev = event.get("significance", "minor")
    scores["scientific_importance"] = {"minor":30,"moderate":50,"elevated":60,"strong":75,"major":85,"severe":95,"extreme":100}.get(sev, 30)
    scores["novelty"] = 80 if event.get("novelty", "new") == "new" else 40
    et = event.get("event_type", "")
    scores["visual_potential"] = 80 if "aurora" in et or "storm" in et or "flare" in et else 40
    scores["human_relevance"] = 80 if "storm" in et or "aurora" in et or "kp" in et else 50
    prev = event.get("previous_value"); curr = event.get("current_value")
    if isinstance(curr, (int, float)) and isinstance(prev, (int, float)) and prev != 0:
        scores["forecast_surprise"] = min(abs((curr - prev) / max(abs(prev), 1)) * 100, 100)
    else: scores["forecast_surprise"] = 50
    scores["human_ai_disagreement"] = event.get("disagreement_score", 0) or 0
    if event.get("event_type") == "kp_threshold": scores["magnitude"] = min((curr or 0) * 11, 100)
    elif event.get("event_type") == "solar_wind_threshold": scores["magnitude"] = min((curr or 0) / 10, 100)
    elif event.get("event_type") == "bz_threshold": scores["magnitude"] = min(abs(curr or 0) * 5, 100)
    else: scores["magnitude"] = 50
    sev_str = str(event.get("severity", ""))
    scores["rarity"] = 90 if any(x in sev_str for x in ["G4", "G5", "X"]) else 50
    scores["recency"] = 90
    scores["location_relevance"] = 30
    return scores

def calculate_vis(event, snapshot):
    weights = load_weights()
    components = _component_scores(event, snapshot)
    total_weight = sum(weights.get(k, 0) for k in components)
    if total_weight == 0: return 50, components
    weighted_sum = sum(components[k] * weights.get(k, 0) for k in components)
    vis = round(weighted_sum / total_weight)
    return min(max(vis, 0), 100), components

def classify_distribution(vis):
    weights = load_weights()
    for level, (lo, hi) in weights.get("distribution_levels", {}).items():
        if lo <= vis <= hi: return level
    return "none"