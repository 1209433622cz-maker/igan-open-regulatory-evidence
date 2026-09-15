# R7A1C1 dependency record

The HRA target-panel pipeline runs in `Ubuntu-22.04` under WSL because PyPI
does not publish a Windows `pysam` wheel for the workstation's Python 3.13.

Verified on 2026-09-15:

```text
WSL distribution = Ubuntu-22.04
Python = 3.10.12
samtools = 1.13
pysam = 0.23.3
aria2c = 1.37.0 (Windows x64 build1)
```

Installed local wheel:

```text
H:\SCI2\YR1\1_data\software\wheels\pysam-0.23.3-cp310-cp310-manylinux_2_28_x86_64.whl
SHA-256 = a7d6b3dcbf4756bd178e217fa391187edc5793f8f50c3034e585d1e4d282d29b
```

The wheel was fetched from the PyPI file URL recorded in the PyPI 0.23.3 JSON
metadata, then installed without WSL network access:

```powershell
wsl.exe -d Ubuntu-22.04 -- bash -lc "python3 -m pip install --user --no-index /mnt/h/SCI2/YR1/1_data/software/wheels/pysam-0.23.3-cp310-cp310-manylinux_2_28_x86_64.whl"
```

Windows aria2 location:

```text
H:\SCI2\YR1\1_data\software\aria2\aria2-1.37.0\aria2-1.37.0-win-64bit-build1\aria2c.exe
archive SHA-256 = 67d015301eef0b612191212d564c5bb0a14b5b9c4796b76454276a4d28d9b288
```

Run the complete resumable five-donor gate from PowerShell:

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
  '.\2_code\06_intake\r7a1c1\RUN_R7A1C1_HRA008003_TARGET_PANEL_v2.ps1'
```

The runner downloads and validates one donor at a time, uses the provider MD5,
records a local SHA-256, writes the compact called-cell target panel, and then
deletes that donor BAM after successful analysis. Re-running the same command
resumes an interrupted aria2 transfer and skips validated donor summaries.
