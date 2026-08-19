#!/usr/bin/env python3
"""Flarient Constellation — main orchestrator."""
import json, os, sys, subprocess, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data_sources import fetch_all
from state_detector import detect_changes
from significance_engine import check_significance
from distribution_compiler import compile_all

def log(msg): print(f"[CONSTELLATION] {msg}", flush=True)

def main():
    log(f"=== Flarient Constellation — {datetime.datetime.now(datetime.timezone.utc).isoformat()} ===")
    snapshot = fetch_all()
    if not snapshot:
        log("ERROR: Failed to fetch data — skipping cycle")
        sys.exit(0)
    changed_fields, previous, state_changed = detect_changes(snapshot)
    if not state_changed:
        log("No state changes detected — exiting")
        sys.exit(0)
    log(f"Changed fields: {changed_fields}")
    events = check_significance(snapshot, changed_fields, previous)
    if not events:
        log("Changes detected but none significant — updating badges only")
        from badge_generator import generate_all_badges
        generate_all_badges(snapshot)
        _commit("Update badges (state changed, no significant events)")
        sys.exit(0)
    log(f"Significant events: {len(events)}")
    compiled = compile_all(events, snapshot, previous)
    log(f"Compiled events: {len(compiled)}")
    _commit(f"Constellation: {len(compiled)} significant event(s)")
    log("=== Cycle complete ===")

def _commit(message):
    try:
        env = os.environ.copy()
        subprocess.run(["git", "config", "user.name", "Flarient Constellation Bot"], env=env, check=True)
        subprocess.run(["git", "config", "user.email", "constellation@flarient.com"], env=env, check=True)
        subprocess.run(["git", "add", "-A"], env=env, check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], env=env)
        if result.returncode == 0: log("No changes to commit"); return
        subprocess.run(["git", "commit", "-m", message], env=env, check=True)
        subprocess.run(["git", "push"], env=env, check=True)
        log("Changes committed and pushed")
    except Exception as e: log(f"Commit failed: {e}")

if __name__ == "__main__": main()