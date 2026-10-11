"""Sort catalogue display and refresh navigation only; no scientific file writes."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(r'H:\SCI2\YR1')
CODE=ROOT/'2_code/00_workspace_management/R7C3D_20261012'
REG=ROOT/'0_admin/figure_registry/R7C3D_20261012'
spec=importlib.util.spec_from_file_location('classification',CODE/'03_classify_figures.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
rows=json.loads((REG/'classification_plan.json').read_text(encoding='utf-8'))
groups=json.loads((REG/'figure_content_catalogue.json').read_text(encoding='utf-8'))
groups.sort(key=lambda g:(g['fig_family'],0 if g['status'].startswith('CURRENT') else 1,g['files'][0]))
module.dump(REG/'figure_content_catalogue.json',groups)
module.generate_navigation(rows,groups)
print('Catalogue sorted by Fig1–Fig8, current before historical; scientific files untouched.')
