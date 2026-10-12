"""Keep prior release receipts separate from the newly prepared candidate."""
from pathlib import Path
import json,shutil
ROOT=Path(r'H:\SCI2\YR1')
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
p=REPO/'0_admin/CURRENT_PROJECT_STATE.json'
s=json.loads(p.read_text(encoding='utf-8'))
prior_names=['current_public_release_tag','current_public_release_url','current_release_zip_sha256','current_release_zip_bytes','public_repository_head_at_release','public_repository_clean_clone_QA','public_repository_actions_QA']
s['scientific_baseline_publication_receipt']={k:s.pop(k) for k in prior_names if k in s}
s.update(current_editorial_assets_github_publish_pending=True,current_editorial_assets_github_published=False,
         current_public_release_tag=None,current_candidate_release_status='PENDING_CREATE',current_candidate_actions_status='PENDING_PUSH',
         portable_candidate_QA='95/95 PASS local',portable_scientific_replay='38/38 PASS local')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
for script in (ROOT/'2_code/11_manuscript/R7C3H1B_20261013').iterdir():
    if not script.is_file():continue
    for d in [REPO/'2_code/11_manuscript/R7C3H1B',REPO/'5_manuscript/current/R7C3H1B/09_Code',ROOT/'5_manuscript/R7C3H1B_ExactVersionHandoff_20261013/09_Code']:
        shutil.copy2(script,d/script.name)
print('Prior scientific release receipt retained separately; new candidate publication honestly pending')
