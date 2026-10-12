# Local workspace audit and reversible organization

Runtime paths: `0_admin/tooling`, `0_admin/skills/qiteng_runtime_v03242`, `0_admin/repositories/igan-open-regulatory-evidence`. Exact old-path scripts remain in local `9.Version/workspace_reorganization/R7C3C_20261012/original_path_dependent_code` and old release tags. No statistical threshold or formula was changed by runtime adapters.

`01_full_audit.py --label <new_snapshot>` inventories and freshly hashes regular workspace files, preserving explicit semantic scan depth. Do not infer biological validity from hashes or status words in archived records. `03_organize_workspace.py` is a one-time migration; its preflight refuses absent sources or occupied targets. `ROLLBACK_ORGANIZATION.py` defaults to dry-run and requires `--execute` for restoration. Other builders retain frozen stage output locations; rerun only in a separate workspace or deliberately selected new version.

The public data manifest contains pointers; retrieve raw inputs from original providers. No genotype, donor pseudobulk, raw LD or complete local content inventory is distributed by these scripts. No email, journal submission or Zenodo publication is executed.
