from pathlib import Path
import csv, hashlib, json, re, shutil, zipfile
from lxml import etree
from docx import Document

ROOT = Path(r'H:\SCI2\YR1')
SRC = ROOT / '5_manuscript/R7C3H_StatisticalReproducibilityClosure_20261013'
OUT = ROOT / '5_manuscript/R7C3H1B_ExactVersionHandoff_20261013'
WORK = ROOT / '5_analysis/R7C3H1B_20261013'
SCIENTIFIC_TAG = 'r7c3h0-statistical-reproducibility-closure-2026-10-13'
REPO_URL = 'https://github.com/1209433622cz-maker/igan-open-regulatory-evidence'
OLD = REPO_URL + '/tree/r7c3f-full-audit-rebuilt-submission-2026-10-12'
NEW = REPO_URL + '/tree/' + SCIENTIFIC_TAG
PIN = '4fb58180c23af48e337e9a14e4073d9071e44d16'
TENK_REL = '3_results/r7a1c/R7A1C_FCRL3_TenK_Bintermediate_coloc.tsv'
REPO = ROOT / '0_admin/repositories/igan-open-regulatory-evidence_REBUILD_20261012'

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

assert not OUT.exists(), 'Inspect existing destination before repeating preparation.'
for d in ['01_Manuscript','02_Figures','03_Supplement','04_Cover','05_Source_Data','06_QA','07_Reports','08_Protocol','09_Code']:
    (OUT / d).mkdir(parents=True)
WORK.mkdir(parents=True, exist_ok=True)
baseline = [{'relative': p.relative_to(SRC).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(SRC.rglob('*')) if p.is_file()]
assert len(baseline) == 115
(OUT / '06_QA/BASELINE_INPUT_IDENTITY.json').write_text(json.dumps(baseline, indent=2), encoding='utf-8')
changes = []
source_docx = SRC / '01_Manuscript/Manuscript_ExpertRebuilt.docx'
source_md = SRC / '01_Manuscript/Manuscript_ExpertRebuilt.md'
target_docx = OUT / '01_Manuscript/Manuscript_SubmissionCandidate.docx'
doc = Document(source_docx)
data_text = next(p.text for p in doc.paragraphs if p.text.startswith('PBC summary statistics are available'))
data_add = (' The exact scientific release is ' + REPO_URL + '/releases/tag/' + SCIENTIFIC_TAG +
            '. Source Data 1-3 provide the primary aggregate tables, bounded external evidence and disease sample-size robustness records, respectively.')
edits = [
    ('FCRL3_TenK_cross_reference', 'low-prior H4/[H3+H4]=0.9217; Figure 5b)', 'low-prior H4/[H3+H4]=0.9217; Figure 3d)', 1),
    ('exact_scientific_code_release', OLD, NEW, 2),
    ('data_release_and_three_source_archives', data_text, data_text + data_add, 1),
]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def replace_nodes(paragraph, old, new):
    nodes = paragraph.xpath('.//w:t', namespaces=NS)
    texts = [n.text or '' for n in nodes]
    joined = ''.join(texts)
    if old not in joined: return 0
    count = joined.count(old)
    # Replacements across runs preserve formatting outside the changed span.
    for _ in range(count):
        texts = [n.text or '' for n in nodes]
        joined = ''.join(texts)
        start = joined.index(old); end = start + len(old)
        offset = 0; inserted = False
        for n, value in zip(nodes, texts):
            left, right = offset, offset + len(value); offset = right
            if right <= start or left >= end: continue
            pre = value[:max(0, start-left)]
            post = value[max(0, end-left):] if end < right else ''
            n.text = pre + (new if not inserted else '') + post
            n.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            inserted = True
    return count

with zipfile.ZipFile(source_docx) as z:
    xml = etree.fromstring(z.read('word/document.xml'))
    for label, old, new, expected in edits:
        n = sum(replace_nodes(p, old, new) for p in xml.xpath('.//w:p', namespaces=NS))
        assert n == expected, (label, n, expected)
        changes.append(dict(change=label, before=old, after=new, occurrences=n))
    with zipfile.ZipFile(target_docx, 'w', compression=zipfile.ZIP_DEFLATED) as dest:
        for entry in z.infolist():
            data = z.read(entry.filename)
            if entry.filename == 'word/document.xml':
                data = etree.tostring(xml, xml_declaration=True, encoding='UTF-8', standalone=True)
            elif entry.filename.endswith('.rels'):
                data = data.replace(OLD.encode(), NEW.encode())
            dest.writestr(entry, data)
md = source_md.read_text(encoding='utf-8-sig')
for label, old, new, expected in edits:
    assert md.count(old) == expected, (label, md.count(old))
    md = md.replace(old, new)
(OUT / '01_Manuscript/Manuscript_SubmissionCandidate.md').write_text(md, encoding='utf-8')
for folder in ['02_Figures','03_Supplement','05_Source_Data']:
    for p in sorted((SRC / folder).glob('*')):
        if p.is_file(): shutil.copy2(p, OUT / folder / p.name)
for ext in ['docx', 'pdf']:
    shutil.copy2(SRC / f'04_Cover/Cover_Letter_ExpertRebuilt_DRAFT.{ext}', OUT / f'04_Cover/Cover_Letter_SubmissionCandidate.{ext}')
for name in ['FIGURE_VALUES.json', 'CLAIM_EVIDENCE_LEDGER.tsv', 'R7C3H_FIGURE_BYTE_IDENTITY.tsv']:
    p = SRC / '06_QA' / name
    if p.exists(): shutil.copy2(p, OUT / '06_QA' / ('BASELINE_' + name))
with open(SRC / '06_QA/PANEL_EVIDENCE_MAP.tsv', encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f, delimiter='\t'); fields = reader.fieldnames; panels = list(reader)
target_row = next(r for r in panels if r['figure'] == '3' and r['panel'] == 'd')
local = Path(target_row['source_member'])
assert sha(local) == sha(REPO / TENK_REL)
old_locator = target_row['source_member']
target_row['source_member'] = REPO_URL + '/blob/' + PIN + '/' + TENK_REL
with open(OUT / '06_QA/PANEL_EVIDENCE_MAP.tsv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fields, delimiter='\t'); writer.writeheader(); writer.writerows(panels)
changes.append(dict(change='Figure_3d_public_source_locator', before=old_locator, after=target_row['source_member'], source_sha256=sha(local)))
shutil.copy2(local, OUT / '05_Source_Data/R7A1C_FCRL3_TenK_Bintermediate_coloc.tsv')
(OUT / '06_QA/EDITORIAL_CHANGE_LEDGER.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
review = {
    'stage': 'R7C3H1B_EXACT_VERSION_HANDOFF', 'scientific_source_tag': SCIENTIFIC_TAG,
    'status': 'CANDIDATE_PREPARED_PENDING_DOCUMENT_QA', 'scientific_results_changed': False,
    'figures_changed': False, 'author_identity_previously_confirmed': True,
    'fresh_exact_version_author_approval': 'PENDING', 'publisher_portal_proof': 'PENDING',
    'journal_submission': 'NOT_EXECUTED', 'zenodo_DOI': 'NOT_ESTABLISHED',
    'scope': 'Bounded editorial navigation changes; no biological refit or new candidate selection.'
}
(OUT / '08_Protocol/HANDOFF_STATE.json').write_text(json.dumps(review, indent=2), encoding='utf-8')
print(json.dumps({'status': 'PREPARED', 'changes': len(changes), 'baseline_files': len(baseline), 'main_docx_sha256': sha(target_docx)}))
