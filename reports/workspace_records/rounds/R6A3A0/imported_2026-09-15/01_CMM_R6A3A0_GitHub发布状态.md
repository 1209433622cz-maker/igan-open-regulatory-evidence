# R6A3A0 GitHub publication state

Date: 2026-09-14

Repository: `1209433622cz-maker/igan-open-regulatory-evidence`

## Read verification

The repository is public and the default branch is `main`.

The last remotely verified HEAD before this R6A3A0 package was:

`3ea533f02efe27d192e2f02fcdfc84d4f4f98548`

## Write status from this chat

The GitHub connector returned:

`403 Resource not accessible by integration`

for write operations. Therefore **R6A3A0 files have not been claimed as remotely published from this chat**.

This is a publication-layer limitation, not a scientific-analysis failure.

## Safe local synchronization

The execution package contains:

`analysis/r6a3a/SYNC_R6A3A0_TO_GITHUB.ps1`

It:
- copies only the pre-approved public R6A3A code/protocol/report/state/manifest paths;
- aborts if a repository file exceeds 10 MB;
- scans common token/private-key/password patterns;
- requires local `main` to match `origin/main` before commit;
- commits and pushes using the user's already-configured local Git credential;
- verifies final remote `main` equals local HEAD.

Example:

```powershell
Set-Location 'H:\SCI2\YR1'
pwsh -File '.\2_code\06_intake\igan_r6a3a\SYNC_R6A3A0_TO_GITHUB.ps1' `
  -RepoPath 'H:\SCI2\YR1\9.Version\public_repro\igan-open-regulatory-evidence'
```

If the clone is elsewhere, pass its actual path.
