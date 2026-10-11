"""Verify the frozen public-tree SHA-256 against canonical Git blobs."""
from pathlib import Path
import hashlib, subprocess
ROOT=Path(__file__).resolve().parents[2]
def main():
    manifest=subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:MANIFEST.sha256']).decode('utf-8')
    passed=0
    proc=subprocess.Popen(['git','-C',str(ROOT),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    for line in manifest.splitlines():
        if not line.strip():continue
        expected,path=line.split('  ',1)
        proc.stdin.write(('HEAD:'+path+'\n').encode('utf-8'));proc.stdin.flush()
        header=proc.stdout.readline().decode().strip().split()
        if len(header)!=3 or header[1]!='blob':raise SystemExit('MISSING '+path)
        b=proc.stdout.read(int(header[2]));proc.stdout.read(1)
        actual=hashlib.sha256(b).hexdigest()
        if actual!=expected:raise SystemExit('FAIL '+path)
        passed+=1
    proc.stdin.close();proc.wait()
    print(f'PASS {passed}/{passed} canonical Git-blob checksums')
if __name__=='__main__':main()
