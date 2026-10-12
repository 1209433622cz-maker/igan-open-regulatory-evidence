"""Physical-file integrity review, with explicit limits for large compressed data."""
from pathlib import Path
import csv, json, zipfile, gzip, time, importlib.util, sys
from collections import Counter
ROOT=Path(r'H:\SCI2\YR1');OUT=ROOT/'5_analysis/R7C3F_GitHubRebuild_FullAudit_Submission_20261012'
def ex(p):return '\\\\?\\'+str(p.resolve())
def main():
    rows=list(csv.DictReader((OUT/'ALL_FILES_FRESH_SHA256.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    retry='--retry-npy' in sys.argv
    checks=[]
    if retry:
        checks=[r for r in csv.DictReader((OUT/'FULL_FORMAT_CHECKS_LOCAL.tsv').open(encoding='utf-8-sig'),delimiter='\t') if Path(r['path']).suffix.lower()!='.npy']
        rows=[r for r in rows if r['extension']=='.npy']
    start=time.time();last=start
    for r in rows:
        ext=r['extension'];p=ROOT/r['relative_path'];state='';detail=''
        try:
            if ext in ['.zip','.docx','.xlsx','.pptx','.docm','.xlsm']:
                with zipfile.ZipFile(ex(p)) as z:
                    bad=z.testzip();state='PASS_FULL_ARCHIVE_CRC' if bad is None else 'FAIL';detail='members='+str(len(z.infolist()))+';expanded_bytes='+str(sum(i.file_size for i in z.infolist()))
            elif ext=='.gz':
                if int(r['size_bytes'])<=64*1024**2:
                    with gzip.open(ex(p),'rb') as f:
                        while f.read(8*1024**2):pass
                    state='PASS_FULL_GZIP_STREAM_CRC'
                else:state='LIMIT_FULL_SHA256_ONLY';detail='Large compressed input: full original-byte SHA was computed; full decompression/CRC is not asserted.'
            elif ext=='.bed':
                with open(ex(p),'rb') as f:magic=f.read(3)
                state='PASS_PLINK_SNP_MAJOR_MAGIC' if magic==b'\x6c\x1b\x01' else 'REVIEW_UNEXPECTED_PLINK_MAGIC';detail='Header identity only; genotype/donor row counts remain in source intake receipts.'
            elif ext=='.npy':
                import numpy as np
                with open(ex(p),'rb') as f:
                    version=np.lib.format.read_magic(f)
                    if version==(1,0):shape,fortran,dtype=np.lib.format.read_array_header_1_0(f)
                    elif version==(2,0):shape,fortran,dtype=np.lib.format.read_array_header_2_0(f)
                    else:raise ValueError('NPY version needs a separate public-API reader: '+str(version))
                    header=f.tell()
                import math
                expected=header+math.prod(shape)*dtype.itemsize
                state='PASS_NPY_HEADER_AND_PAYLOAD_SIZE' if expected==int(r['size_bytes']) and not dtype.hasobject else 'REVIEW_NPY_OBJECT_OR_SIZE'
                detail=f'shape={shape};dtype={dtype};header_bytes={header}'
        except Exception as e:state='FAIL_OR_PARSER_LIMITATION';detail=type(e).__name__+':'+str(e)[:240]
        if state:checks.append({'path':r['relative_path'],'bytes':r['size_bytes'],'sha256':r['sha256'],'check':state,'detail':detail})
        if time.time()-last>20:print(json.dumps({'format_files':len(checks),'seconds':round(time.time()-start)}),flush=True);last=time.time()
    with (OUT/'FULL_FORMAT_CHECKS_LOCAL.tsv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,delimiter='\t',fieldnames=['path','bytes','sha256','check','detail']);w.writeheader();w.writerows(checks)
    counts=dict(Counter(r['check'] for r in checks));state={'counts':counts,'review_findings':sum(not r['check'].startswith(('PASS_','LIMIT_')) for r in checks),'elapsed_seconds':round(time.time()-start,2),'scope':'All original snapshot archive members CRC-checked; gzip <=64MiB fully decompressed, larger gzip identity-only; PLINK/NPY headers not scientific-model validation. No raw-file mutation.','retry_npy_only':retry,'repair':'Replaced removed NumPy private API with public version-specific header readers; original scientific NPY bytes untouched.' if retry else ''}
    (OUT/'FULL_FORMAT_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(state,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
