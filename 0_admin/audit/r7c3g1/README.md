# Public tree audit scope

`MANIFEST.sha256` at repository root covers every tracked file except itself. Run the canonical Git-blob verifier on current HEAD; this is the authoritative whole-tree identity check.

`PUBLIC_FILE_CATALOG.tsv` provides roles, sizes and hashes for content files. To avoid self-reference it excludes itself, the whole-tree manifest and `DIRECTORY_SIZE_SUMMARY.tsv`; all three are covered by the whole-tree manifest. `DIRECTORY_SIZE_SUMMARY.tsv` includes its own converged size and all files except the root manifest, whose byte length can be read directly.

The preservation table maps all 2,335 pre-existing tracked files to unchanged identities. Frozen historical navigation retains original paths; current links are tested separately. The remote receipt identifies an independently fetched content commit. Later main commits append audit metadata; the external local final receipt records the last HEAD, avoiding a commit hash referencing itself.
