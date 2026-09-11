"""Apply a pending recommendation after an external human approval step."""
import json
from pathlib import Path

approved=Path("config/approved.json")
pending=Path("config/pending_recommendation.json")
if not pending.exists(): raise SystemExit("No pending recommendation found.")
rec=json.loads(pending.read_text()); cfg=json.loads(approved.read_text())
for key in ("model","temperature","max_tokens"):
    if rec.get(key) is not None: cfg[key]=rec[key]
cfg.setdefault("prompts",{}).update(rec.get("prompt_changes",{})); cfg.setdefault("routing",{}).update(rec.get("routing_changes",{}))
approved.write_text(json.dumps(cfg,indent=2)); print("Approved configuration written.")
