#!/usr/bin/env python3
"""Selectively fetch the frozen TenK10K B_intermediate member and extract FCRL3.

Each HTTP range is resume-safe and hashed.  A member is accepted only after its
ZIP local header, raw-DEFLATE EOF, uncompressed byte count, CRC32, row shape,
and exact gene filter have all passed.  The full 16.56-GB archive is not fetched.
"""
from __future__ import annotations

import argparse, binascii, concurrent.futures, hashlib, json, math, os, struct, threading, time, zlib
from datetime import datetime, timezone
from pathlib import Path
import requests

SOURCE_RECORD = "https://zenodo.org/records/18221260"
SOURCE_URL = "https://zenodo.org/api/records/18221260/files/common_all_cis_pvalues_100kb.zip/content"
ARCHIVE_SIZE = 16_559_137_990
ARCHIVE_MD5 = "dd54714b2effb91160ac171ccb941534"
TARGET_GENE = "ENSG00000160856"
REQUIRED = {"CHR","POS","MarkerID","Allele1","Allele2","AF_Allele2","BETA","SE","p.value","N","gene"}
MEMBERS = {
 "B_intermediate": {
     "name":"B_intermediate_common_all_cis_raw_pvalues.tsv",
     "local_header_offset":605710861,
     "compressed_size":591715279,
     "uncompressed_size":2392868507,
     "crc32":"3c73842b"
 },
}

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(4<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    # Completion callbacks run concurrently.  A thread-specific temporary name
    # prevents two callbacks from replacing the same .part file on Windows.
    tmp=path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.part")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for attempt in range(20):
        try:
            os.replace(tmp,path); return
        except PermissionError:
            time.sleep(min(2.0,0.05*(attempt+1)))
    # Some Windows indexers briefly deny replacement of the destination.  A
    # final direct write keeps the receipt current; member CRC remains the data
    # integrity authority and will still fail closed.
    path.write_bytes(tmp.read_bytes())
    try: tmp.unlink()
    except OSError: pass

def fetch_range(url: str, start: int, end: int, dest: Path, retries: int) -> dict:
    expected=end-start+1; part=dest.with_name(dest.name+".part"); last=None
    for attempt in range(1,retries+1):
        try:
            if part.exists(): part.unlink()
            began=time.monotonic(); h=hashlib.sha256(); observed=0
            with requests.get(url,headers={"Range":f"bytes={start}-{end}","Accept-Encoding":"identity",
                 "User-Agent":"CMM-R7A1C1-FCRL3-selective/1.0"},timeout=(30,600),stream=True) as r:
                if r.status_code!=206: raise RuntimeError(f"expected HTTP 206, got {r.status_code}")
                cr=f"bytes {start}-{end}/{ARCHIVE_SIZE}"
                if r.headers.get("Content-Range")!=cr: raise RuntimeError(f"Content-Range mismatch: {r.headers.get('Content-Range')!r}")
                dest.parent.mkdir(parents=True,exist_ok=True)
                with part.open("wb") as f:
                    for b in r.iter_content(1<<20):
                        if b: f.write(b); h.update(b); observed+=len(b)
            if observed!=expected: raise RuntimeError(f"range length {observed} != {expected}")
            os.replace(part,dest)
            return {"status":"DOWNLOADED","start":start,"end":end,"bytes":observed,
                    "sha256":h.hexdigest(),"attempt":attempt,"seconds":round(time.monotonic()-began,3)}
        except Exception as e:
            last=e
            if part.exists(): part.unlink()
            if attempt<retries: time.sleep(min(60,2**(attempt-1)))
    raise RuntimeError(f"range {start}-{end} failed after {retries} attempts: {last}")

def validate_header(cell: str, meta: dict, url: str, cache: Path, retries: int) -> dict:
    probe=cache/cell/"local_header_probe.bin"
    if not probe.exists() or probe.stat().st_size!=512:
        fetch_range(url,meta["local_header_offset"],meta["local_header_offset"]+511,probe,retries)
    b=probe.read_bytes()
    if b[:4]!=b"PK\x03\x04": raise RuntimeError(f"{cell}: bad local-header signature")
    _,version,flags,method,_,_,crc,csize,usize,nlen,xlen=struct.unpack_from("<IHHHHHIIIHH",b,0)
    name=b[30:30+nlen].decode("utf-8" if flags&0x800 else "cp437")
    observed={"name":name,"version_needed":version,"flag_bits":flags,"method":method,
              "crc32":f"{crc:08x}","compressed_size":csize,"uncompressed_size":usize,
              "local_header_offset":meta["local_header_offset"],
              "data_offset":meta["local_header_offset"]+30+nlen+xlen}
    for k in ("name","crc32","compressed_size","uncompressed_size"):
        if str(observed[k])!=str(meta[k]): raise RuntimeError(f"{cell}: {k} mismatch")
    if method!=8: raise RuntimeError(f"{cell}: unsupported compression method {method}")
    return observed

def download_chunks(cell: str, meta: dict, header: dict, url: str, cache: Path,
                    chunk_bytes: int, workers: int, retries: int) -> tuple[list[Path],dict]:
    cdir=cache/cell; cdir.mkdir(parents=True,exist_ok=True)
    count=math.ceil(meta["compressed_size"]/chunk_bytes); info=[None]*count; pending=[]
    for i in range(count):
        rel=i*chunk_bytes; n=min(chunk_bytes,meta["compressed_size"]-rel)
        start=header["data_offset"]+rel; end=start+n-1; p=cdir/f"chunk_{i:04d}.bin"
        if p.exists() and p.stat().st_size==n:
            info[i]={"status":"REUSED_BY_EXACT_SIZE","start":start,"end":end,"bytes":n,"sha256":sha256_file(p)}
        else:
            if p.exists(): p.unlink()
            pending.append((i,start,end,p))
    manifest=cdir/"chunks_manifest.json"; began=time.monotonic(); manifest_lock=threading.Lock()
    def task(s):
        i,start,end,p=s; return i,fetch_range(url,start,end,p,retries)
    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futures=[ex.submit(task,s) for s in pending]
            for f in concurrent.futures.as_completed(futures):
                i,res=f.result(); info[i]=res
                with manifest_lock:
                    atomic_json(manifest,{"schema_version":"CMM_TENK10K_CHUNKS_2.0","cell":cell,
                        "completed":sum(x is not None for x in info),"chunk_count":count,"chunks":info})
                print(f"{cell} chunks={sum(x is not None for x in info)}/{count}",flush=True)
    if not all(info): raise RuntimeError(f"{cell}: incomplete chunk set")
    summary={"chunk_bytes":chunk_bytes,"chunk_count":count,"workers":workers,
             "network_bytes_this_run":sum(x["bytes"] for x in info if x["status"]=="DOWNLOADED"),
             "elapsed_seconds":round(time.monotonic()-began,3),"chunks":info}
    atomic_json(manifest,{"schema_version":"CMM_TENK10K_CHUNKS_2.0","cell":cell,**summary})
    return [cdir/f"chunk_{i:04d}.bin" for i in range(count)],summary

def extract(cell: str, meta: dict, chunks: list[Path], output: Path) -> dict:
    output.parent.mkdir(parents=True,exist_ok=True); part=output.with_name(output.name+".part")
    if part.exists(): part.unlink()
    dec=zlib.decompressobj(-15); crc=ubytes=lines=targets=malformed=0; buf=b""; header=None; gi=None
    with part.open("wb") as out:
        for cp in chunks:
            data=dec.decompress(cp.read_bytes()); crc=binascii.crc32(data,crc); ubytes+=len(data); buf+=data
            records=buf.split(b"\n"); buf=records.pop()
            for raw in records:
                lines+=1; raw=raw.rstrip(b"\r")
                if header is None:
                    header=raw.decode("utf-8-sig").split("\t"); missing=REQUIRED-set(header)
                    if missing: raise RuntimeError(f"{cell}: missing fields {sorted(missing)}")
                    gi=header.index("gene"); out.write(("\t".join(header)+"\tsource_zip_member\tsource_line\n").encode()); continue
                fields=raw.split(b"\t")
                if len(fields)!=len(header): malformed+=1; continue
                if fields[gi].decode("utf-8","strict")==TARGET_GENE:
                    out.write(raw+b"\t"+meta["name"].encode()+b"\t"+str(lines).encode()+b"\n"); targets+=1
        tail=dec.flush(); crc=binascii.crc32(tail,crc); ubytes+=len(tail); buf+=tail
        if buf:
            lines+=1; raw=buf.rstrip(b"\r"); fields=raw.split(b"\t")
            if header is None or len(fields)!=len(header): malformed+=1
            elif fields[gi].decode("utf-8","strict")==TARGET_GENE:
                out.write(raw+b"\t"+meta["name"].encode()+b"\t"+str(lines).encode()+b"\n"); targets+=1
    crc &= 0xffffffff
    if not dec.eof or dec.unused_data: raise RuntimeError(f"{cell}: invalid DEFLATE EOF")
    if ubytes!=meta["uncompressed_size"]: raise RuntimeError(f"{cell}: uncompressed byte mismatch")
    if f"{crc:08x}"!=meta["crc32"]: raise RuntimeError(f"{cell}: CRC32 mismatch")
    if malformed: raise RuntimeError(f"{cell}: {malformed} malformed rows")
    if targets==0: raise RuntimeError(f"{cell}: zero exact target-gene rows")
    os.replace(part,output)
    return {"status":"PASS_MEMBER_CRC_AND_EXACT_GENE_EXTRACT","cell":cell,"target_rows":targets,
            "source_lines_including_header":lines,"uncompressed_bytes":ubytes,"crc32":f"{crc:08x}",
            "extract_path":str(output),"extract_bytes":output.stat().st_size,"extract_sha256":sha256_file(output)}

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--out-dir",type=Path,required=True); p.add_argument("--cache-dir",type=Path,required=True)
    p.add_argument("--cells",default="B_intermediate"); p.add_argument("--url",default=SOURCE_URL)
    p.add_argument("--chunk-mib",type=int,default=8); p.add_argument("--workers",type=int,default=6); p.add_argument("--retries",type=int,default=6)
    a=p.parse_args(); cells=[x.strip() for x in a.cells.split(",") if x.strip()]
    if cells != ["B_intermediate"]: raise SystemExit("only the pre-registered B_intermediate cell is allowed")
    if not 1<=a.workers<=12 or not 1<=a.chunk_mib<=64: raise SystemExit("invalid worker/chunk setting")
    a.out_dir.mkdir(parents=True,exist_ok=True); receipts=[]; began=time.monotonic()
    overall={"schema_version":"CMM_TENK10K_FCRL3_B_INTERMEDIATE_INTAKE_1.0","created_at_utc":datetime.now(timezone.utc).isoformat(),
             "status":"RUNNING","source":{"record":SOURCE_RECORD,"url":a.url,"archive_size":ARCHIVE_SIZE,
             "provider_md5":ARCHIVE_MD5,"provider_md5_verification":"NOT_RUN_SELECTIVE_MEMBERS_ONLY"},
             "target":{"gene_id":TARGET_GENE,"cells":cells}}
    all_receipt=a.out_dir/"TenK10K_B_intermediate_FCRL3_selective_intake_receipt.json"; atomic_json(all_receipt,overall)
    try:
        for cell in cells:
            meta=MEMBERS[cell]; member_receipt=a.out_dir/f"TenK10K_{cell}_FCRL3_selective_intake_receipt.json"
            existing_output=a.out_dir/f"{cell}_FCRL3_full_variant_eqtl.tsv"
            if member_receipt.exists() and existing_output.exists():
                old=json.loads(member_receipt.read_text(encoding="utf-8")); ex=old.get("extract",{})
                if (ex.get("status")=="PASS_MEMBER_CRC_AND_EXACT_GENE_EXTRACT" and
                    ex.get("crc32")==meta["crc32"] and ex.get("uncompressed_bytes")==meta["uncompressed_size"] and
                    ex.get("target_rows",0)>0 and ex.get("extract_sha256")==sha256_file(existing_output)):
                    receipts.append(old); print(f"{cell} reused=PASS_VERIFIED_EXISTING_EXTRACT",flush=True); continue
            header=validate_header(cell,meta,a.url,a.cache_dir,a.retries)
            chunks,transfer=download_chunks(cell,meta,header,a.url,a.cache_dir,a.chunk_mib<<20,a.workers,a.retries)
            result=extract(cell,meta,chunks,a.out_dir/f"{cell}_FCRL3_full_variant_eqtl.tsv")
            rec={"member_header":header,"transfer":transfer,"extract":result}; receipts.append(rec)
            atomic_json(member_receipt,rec)
        overall.update({"status":"PASS_FCRL3_B_INTERMEDIATE_MEMBER_INTAKE","members":receipts})
        return 0
    except Exception as e:
        overall.update({"status":"HOLD_INCOMPLETE","members":receipts,"error":f"{type(e).__name__}: {e}"})
        return 2
    finally:
        overall["elapsed_seconds"]=round(time.monotonic()-began,3); atomic_json(all_receipt,overall)
        print(json.dumps({"status":overall["status"],"receipt":str(all_receipt),"error":overall.get("error")},indent=2),flush=True)

if __name__=="__main__": raise SystemExit(main())
