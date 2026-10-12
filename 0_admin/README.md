# Project administration, scope and identity

- [Current state](CURRENT_PROJECT_STATE.json): PBC remains GO; R7C3G is the latest editorial review candidate.
- [Eight-directory map](docs/EIGHT_FOLDER_MAP.md) and [evidence/reuse guide](docs/CURRENT_EVIDENCE_AND_REUSE.md).
- [Exact path migration](audit/r7c3g1/PATH_MIGRATION_AND_PRESERVATION.tsv): all old tracked file bytes survive at their mapped locations.
- `protocols/` preserves scientific freezes; new repository layout does not change their scope.
- `history/root_before_R7C3G1/` retains old README, manifests, citation and data/reproduction statements verbatim. Old IgAN descriptions here are historical, not the current PBC contract.
- `environment/` and `workspace_support/` retain stage environments and historical support scripts. This repository does not package installed runtimes or secrets.

Frozen stage documents retain their original local/repository paths. Use the migration table rather than editing scientific provenance. Historical tags and Releases retain the old tree. Git history has not been rewritten.
