"""Review staged public paths and create a manifest of canonical index blobs."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
REPO=Path(sys.argv[1])
paths=[p for p in subprocess.check_output(['git','-C',str(REPO),'ls-files','-z']).decode('utf-8').split('\0') if p and p!='MANIFEST.sha256']
changed=[p for p in subprocess.check_output(['git','-C',str(REPO),'diff','--cached','--name-only','-z']).decode('utf-8').split('\0') if p]
secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|AKIA[A-Z0-9]{16}')
bad=[];large=[];private=[]
for rel in changed:
    p=REPO/rel
    if not p.exists():raise RuntimeError('Unreviewed staged deletion: '+rel)
    if p.stat().st_size>10*1024*1024:large.append(rel)
    if p.suffix.lower() in {'.bed','.bim','.fam','.bam','.cram','.vcf','.bcf','.pem','.key'} or p.name in {'.env','credentials.json'}:private.append(rel)
    if secret.search(p.read_bytes()):bad.append(rel)
assert not bad and not large and not private,dict(secret_paths=bad,large=large,private=private)
proc=subprocess.Popen(['git','-C',str(REPO),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
lines=[]
try:
    for rel in sorted(paths):
        proc.stdin.write((':'+rel+'\n').encode('utf-8'));proc.stdin.flush()
        fields=proc.stdout.readline().decode().strip().split();assert len(fields)==3 and fields[1]=='blob',rel
        b=proc.stdout.read(int(fields[2]));proc.stdout.read(1)
        lines.append(hashlib.sha256(b).hexdigest()+'  '+rel)
finally:proc.stdin.close();proc.wait()
(REPO/'MANIFEST.sha256').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(status='PASS',staged_reviewed_paths=len(changed),index_blob_manifest=len(lines),secret_matches=0,files_above_10MiB=0,individual_data_paths=0)))
