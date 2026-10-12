"""Verify the whole current public tree using canonical Git blobs, no extra packages."""
from pathlib import Path
import hashlib, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
def main():
    manifest=subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:MANIFEST.sha256']).decode('utf-8')
    rows=[line.split('  ',1) for line in manifest.splitlines() if line.strip()]
    tracked=set(subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-rz','--name-only','HEAD']).decode('utf-8').split('\0'))-{''}
    expected={p for h,p in rows}
    assert tracked==expected|{'MANIFEST.sha256'}, 'Manifest coverage must equal all tracked files except itself'
    proc=subprocess.Popen(['git','-C',str(ROOT),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        for digest,path in rows:
            proc.stdin.write(('HEAD:'+path+'\n').encode('utf-8'));proc.stdin.flush()
            head=proc.stdout.readline().decode().strip().split()
            assert len(head)==3 and head[1]=='blob', 'Missing Git blob: '+path
            body=proc.stdout.read(int(head[2]));proc.stdout.read(1)
            assert hashlib.sha256(body).hexdigest()==digest, 'SHA-256 mismatch: '+path
    finally:
        proc.stdin.close();proc.wait()
    required={'0_admin','1_data','2_code','3_results','4_figures','5_manuscript','6_release','7.Report'}
    roots={p.split('/')[0] for p in tracked if '/' in p}
    assert required.issubset(roots), 'Missing required directory roots'
    assert roots.issubset(required|{'.github'}), 'Unexpected directory roots'
    print(f'PASS {len(rows)}/{len(rows)} canonical Git-blob SHA-256; eight required roots plus optional .github automation; exact manifest coverage')
if __name__=='__main__':main()
