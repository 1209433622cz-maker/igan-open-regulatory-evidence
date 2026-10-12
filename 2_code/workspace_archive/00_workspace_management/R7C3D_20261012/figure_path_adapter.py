"""Resolve historical immutable figure paths through the recorded move manifest.

No scientific record is rewritten. Non-figure paths are returned unchanged.
"""
import json
from pathlib import Path

def resolve_legacy_figure(root, relative):
    root=Path(root)
    value=str(relative).replace('\\','/')
    registry=root/'0_admin/figure_registry/R7C3D_20261012/classification_plan.json'
    if value.startswith('4_figures/') and registry.exists():
        rows=json.loads(registry.read_text(encoding='utf-8'))
        matching=[r for r in rows if r['old_relative']==value and r['kind'].startswith('ORIGINAL_')]
        if len(matching)==1:return root/matching[0]['new_relative']
        if len(matching)>1:raise RuntimeError('Ambiguous figure path')
    return root/value
