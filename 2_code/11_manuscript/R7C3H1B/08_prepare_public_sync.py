"""Stage reviewed candidate and RP v5 into the existing public checkout.

Preserves prior versions and all previously tracked scientific files.
Does not commit, push, create a DOI or submit the manuscript.
"""
from pathlib import Path
import json,shutil,subprocess
ROOT=Path(r'H:\SCI2\YR1')
REPO=ROOT/'0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'
SRC=ROOT/'5_manuscript/R7C3H1B_ExactVersionHandoff_20261013'
DEST=REPO/'5_manuscript/current/R7C3H1B'
assert subprocess.check_output(['git','-C',str(REPO),'status','--porcelain']).strip()==b'', 'Preserve existing uncommitted work'
assert not DEST.exists(), 'New public candidate must not overwrite an existing version'
shutil.copytree(SRC,DEST)
for p in (ROOT/'2_code/11_manuscript/R7C3H1B_20261013').glob('*.py'):
    target=REPO/'2_code/11_manuscript/R7C3H1B'/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
for p in (ROOT/'2_code/11_manuscript/R7C3H1B_20261013').glob('*.ps1'):shutil.copy2(p,REPO/'2_code/11_manuscript/R7C3H1B'/p.name)
RP=ROOT/'9.Version/research_plans/PBC/RP_v5_20261013'
for p in RP.iterdir():
    if not p.is_file() or p.name in ['RPv5_RAW_DATA_METADATA_INVENTORY.tsv','RPv5_PDF_TEXT.txt']:continue
    t=REPO/'0_admin/research_plans/RP_v5_20261013'/p.name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
for p in (ROOT/'7.Report/rounds/R7C3H1B_20261013').glob('*.md'):
    t=REPO/'7.Report/rounds/r7c3h1b'/p.name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
public_state=json.loads((REPO/'0_admin/CURRENT_PROJECT_STATE.json').read_text(encoding='utf-8'))
public_state['previous_scientific_stage']=public_state['stage']
public_state.update(stage='R7C3H1B_EXACT_VERSION_HANDOFF',RP='v5',current_editorial_candidate='R7C3H1B',
    document_package_QA='43/43 PASS',WPS='Main 25 + SI 6 + unchanged cover 1 = 32/32 visual pages',
    next='R7C3H1C_EXACT_AUTHOR_APPROVAL_AND_PUBLISHER_PORTAL_PROOF',NEXT='R7C3H1C_EXACT_AUTHOR_APPROVAL_AND_PUBLISHER_PORTAL_PROOF',
    current_scientific_source_tag='r7c3h0-statistical-reproducibility-closure-2026-10-13',
    candidate_release_tag='r7c3h1b-exact-version-handoff-2026-10-13',candidate_publication_status='CANDIDATE_CHECKOUT_PREPARED_PENDING_PUSH',
    baseline='R7C3H immutable source retained',scientific_results_changed=False)
(REPO/'0_admin/CURRENT_PROJECT_STATE.json').write_text(json.dumps(public_state,indent=2,ensure_ascii=False),encoding='utf-8')
readme=REPO/'README.md';s=readme.read_text(encoding='utf-8')
s=s.replace('Current project: **PBC, RP v4**. Latest exact-version candidate: **R7C3H**,','Current project: **PBC, RP v5**. Latest exact-version candidate: **R7C3H1B**,')
s=s.replace('| Editable current main manuscript | [DOCX](5_manuscript/current/R7C3H/01_Manuscript/Manuscript_ExpertRebuilt.docx) / [25-page WPS PDF](5_manuscript/current/R7C3H/01_Manuscript/Manuscript_ExpertRebuilt.pdf) |','| Editable current main manuscript | [DOCX](5_manuscript/current/R7C3H1B/01_Manuscript/Manuscript_SubmissionCandidate.docx) / [25-page WPS PDF](5_manuscript/current/R7C3H1B/01_Manuscript/Manuscript_SubmissionCandidate.pdf) |\n| Exact-file author handoff | [Start here](5_manuscript/current/R7C3H1B/START_HERE_精确版本审阅.md) / [13-file SHA-256 list](5_manuscript/current/R7C3H1B/06_QA/UPLOAD_CANDIDATE_MANIFEST.tsv) |\n| Detailed current research plan | [RP v5 DOCX](0_admin/research_plans/RP_v5_20261013/PBC_研究计划书_RP_v5_20261013.docx) / [58-page WPS PDF](0_admin/research_plans/RP_v5_20261013/PBC_研究计划书_RP_v5_20261013.pdf) |')
s=s.replace('**PBC = GO. R7C3H is complete and awaits exact-version author reconfirmation and publisher-generated PDF proof**','**PBC = GO. R7C3H1B local handoff and QA are complete; exact-version author reconfirmation and publisher-generated PDF proof remain pending**')
s=s.replace('## Scientific question and narrative','## Exact-version handoff\n\nR7C3H1B fixes the FCRL3 TenK Figure 3d pointer, pins scientific code/data links to R7C3H0, and replaces raw exponent/support notation and the two LD definitions with native Word formatting. Figure masters, workbook and all three Source Data ZIPs are unchanged. The SI wording and values are unchanged, with native notation and a new WPS export. Local QA is **43/43**, visual review **32/32 pages**, and the single upload candidate list contains **13 files**. Author identity/declaration confirmation is retained; approval of this exact candidate and actual portal proof are pending. [Round report](7.Report/rounds/r7c3h1b/99_R7C3H1B_详细行动记录_20261013.md).\n\nRP v5 is a detailed evidence plan, not an authorization to submit. Its earlier abstract count is superseded by the explicit R7C3H1B counting receipt: 126 whitespace words, 129 compound-aware tokens, or 148 conservative alphanumeric pieces; the abstract itself was not edited.\n\n## Scientific question and narrative')
readme.write_text(s,encoding='utf-8')
repro=REPO/'REPRODUCIBILITY.md';s=repro.read_text(encoding='utf-8').replace('RP v4 / R7C3H','RP v5 / R7C3H1B')
s+='\n## Current exact-file candidate\n\n`R7C3H1B` retains the frozen scientific R7C3H0 tag. Run the standard-library byte/aggregate checker after the existing scientific replay:\n\n```powershell\npython 2_code/11_manuscript/R7C3H1B/07_verify_public_handoff.py\n```\n\nThis checks the 13-file upload manifest, immutable source ZIPs and figure bytes, native equation presence, navigation and local proof identities. It does not reproduce human WPS review, generate a publisher proof or sign author declarations.\n'
repro.write_text(s,encoding='utf-8')
workflow=REPO/'.github/workflows/portable-reproducibility.yml'
s=workflow.read_text(encoding='utf-8')
s+='\n      - name: Verify exact-file R7C3H1B handoff\n        run: python 2_code/11_manuscript/R7C3H1B/07_verify_public_handoff.py\n'
workflow.write_text(s,encoding='utf-8')
print('Prepared reviewed R7C3H1B and RP v5; old scientific tree preserved')
