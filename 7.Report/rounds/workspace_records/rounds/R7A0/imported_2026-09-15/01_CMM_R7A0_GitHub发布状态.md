# R7A0 GitHub publication state

Date: 2026-09-15

Repository: `1209433622cz-maker/igan-open-regulatory-evidence`

Remote read verification succeeded. The last remotely verified commit before this R7A0 package was:

`5be29034298192b1772dbf75696294ec8e276529`

The current GitHub connector has read access but returned `403 Resource not accessible by integration` for write operations in this round. Therefore R7A0 remote publication is **not claimed complete from this chat**.

A safe local synchronization script is included:

`code/SYNC_R7A0_TO_GITHUB.ps1`

It requires local `main == origin/main`, runs `git diff --check`, rejects >10 MB public files, commits only the frozen small R7A0 report/protocol/result/manifest paths, pushes with the user's existing local Git credentials, and verifies remote HEAD after push.
