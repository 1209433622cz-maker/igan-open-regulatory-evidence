"""Resolve historical file paths without rewriting frozen evidence rows."""
import json
from pathlib import Path
ROOT=Path(r"H:\SCI2\YR1")
PLAN=ROOT/"0_admin/navigation/R7C3E_20261012/organization_plan.json"
def resolve_workspace_path(path):
    raw=str(path).replace("\\","/")
    prefix=ROOT.as_posix()+"/"
    rel=raw[len(prefix):] if raw.lower().startswith(prefix.lower()) else raw
    mapping={x["source"].lower():x["destination"] for x in json.loads(PLAN.read_text(encoding="utf-8"))["candidates"] if x["decision"].startswith("MOVE")}
    return ROOT/mapping.get(rel.lower(),rel)
