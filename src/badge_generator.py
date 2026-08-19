"""Dynamic SVG badge generator — lightweight, only regenerated when values change."""
import os
from pathlib import Path

BADGES_DIR = Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "docs" / "badges"

def _color_for_kp(kp):
    if kp >= 7: return "#ef4444"
    if kp >= 6: return "#f59e0b"
    if kp >= 5: return "#eab308"
    if kp >= 4: return "#22d3ee"
    return "#64748b"

def _color_for_flare(cls):
    if cls.startswith("X"): return "#ef4444"
    if cls.startswith("M"): return "#f59e0b"
    if cls.startswith("C"): return "#22d3ee"
    return "#64748b"

def _storm_label(kp):
    if kp >= 9: return "G5 Extreme"
    if kp >= 8: return "G4 Severe"
    if kp >= 7: return "G3 Strong"
    if kp >= 6: return "G2 Moderate"
    if kp >= 5: return "G1 Minor"
    return "Quiet"

def _aurora_label(kp):
    if kp >= 7: return "High"
    if kp >= 5: return "Moderate"
    if kp >= 4: return "Low"
    return "None"

def _svg(label, value, color, link="https://flarient.com"):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="44" role="img" aria-label="{label}: {value}">\n'
        f'  <title>{label}: {value}</title>\n'
        f'  <a href="{link}" target="_blank" rel="noopener">\n'
        f'    <rect width="200" height="44" rx="6" fill="#0a0620" stroke="{color}" stroke-width="1.5"/>\n'
        f'    <rect width="80" height="44" rx="6" fill="{color}" opacity="0.15"/>\n'
        f'    <text x="40" y="28" text-anchor="middle" fill="#e8eaf2" font-family="monospace" font-size="11" font-weight="bold">{label.upper()}</text>\n'
        f'    <text x="140" y="28" text-anchor="middle" fill="{color}" font-family="monospace" font-size="13" font-weight="bold">{value}</text>\n'
        f'  </a>\n</svg>'
    )

def generate_all_badges(snapshot):
    BADGES_DIR.mkdir(parents=True, exist_ok=True)
    latest_dir = BADGES_DIR / "latest"
    latest_dir.mkdir(exist_ok=True)
    kp = snapshot.get("kp", 0)
    bz = snapshot.get("bz") or 0
    sw = snapshot.get("solar_wind_speed") or 0
    flare = snapshot.get("flare_class", "unknown")
    neo = snapshot.get("neo_count", 0)
    badges = {
        "kp.svg": _svg("Kp", f"{kp:.1f}", _color_for_kp(kp), "https://flarient.com/kp-index"),
        "storm.svg": _svg("Storm", _storm_label(kp), _color_for_kp(kp), "https://flarient.com/storm"),
        "aurora.svg": _svg("Aurora", _aurora_label(kp), _color_for_kp(kp), "https://flarient.com/aurora-forecast"),
        "flare.svg": _svg("Flare", flare, _color_for_flare(flare), "https://flarient.com/solar-flares"),
        "solarwind.svg": _svg("Wind", f"{sw:.0f} km/s", "#22d3ee" if sw > 600 else "#64748b", "https://flarient.com"),
        "bz.svg": _svg("Bz", f"{bz:.1f} nT", "#ef4444" if bz < -10 else "#64748b", "https://flarient.com"),
        "neo.svg": _svg("NEOs", str(neo), "#f59e0b" if neo > 0 else "#64748b", "https://flarient.com/near-earth-objects"),
        "space-weather.svg": _svg("Space Wx", _storm_label(kp), _color_for_kp(kp), "https://flarient.com"),
    }
    for name, svg in badges.items():
        (latest_dir / name).write_text(svg)
    print(f"[BADGE] Generated {len(badges)} badges")
    return list(badges.keys())