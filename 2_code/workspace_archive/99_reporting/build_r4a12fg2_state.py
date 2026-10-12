#!/usr/bin/env python3
"""Build the R4A12FG2 protocol amendment and machine-readable state."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    protocol = root / "0_admin/protocol/current"
    base_manifest = protocol / "analysis_manifest_v11.json"
    base_state = protocol / "R4A11_state.json"
    registry = protocol / "candidate_registry_v11.tsv"
    descriptive_path = root / "3_results/00_audit/R4A12FG2/R4A12FG2_IL12RB2_TenK10K_FinnGen_descriptive_audit.json"
    object_receipt_path = root / "3_results/00_audit/R4A12FG2/R4A12FG2_manifest_object_receipt.json"
    p0_paths = {
        release: root / f"3_results/00_audit/R4A12FG2/{release}_IL12RB2_P0.json"
        for release in ("R12", "R13")
    }
    base = json.loads(base_manifest.read_text(encoding="utf-8"))
    descriptive = json.loads(descriptive_path.read_text(encoding="utf-8"))
    object_receipt = json.loads(object_receipt_path.read_text(encoding="utf-8"))
    p0 = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in p0_paths.items()}
    generated = datetime.now(timezone.utc).isoformat()
    local_date = datetime.now().astimezone().date().isoformat()

    amendment = {
        "amendment_id": "CMM_R4A12FG2_ANALYSIS_MANIFEST_V11_AMENDMENT_A1",
        "schema_version": "1.0.0",
        "generated_at_utc": generated,
        "base_manifest": {
            "id": base["manifest_id"],
            "path": str(base_manifest),
            "sha256": sha256(base_manifest),
            "candidate_registry_path": str(registry),
            "candidate_registry_sha256": sha256(registry),
        },
        "scope": "Add a bounded FinnGen all-sex IL12RB2 engineering/sensitivity branch while preserving the frozen 2026 sex-stratified chr22/SYNGR1 primary analysis.",
        "precedence": {
            "base_primary_science_unchanged": True,
            "primary_disease_anchor": "2026 multi-cohort female/male SSc GWAS",
            "primary_gene": "SYNGR1",
            "R4B": "HOLD",
            "C1_count": None,
            "IL12RB2_candidate_registry_membership": False,
            "rule": "This amendment authorizes only the named all-sex branch. It cannot promote IL12RB2 into the frozen chr22 candidate competition or substitute FinnGen all-sex results for the 2026 female/male primary estimand.",
        },
        "reason_for_amendment": {
            "old_operational_state": "R4A12 waited for target 2026 female/male bytes.",
            "new_evidence": "Official FinnGen R12/R13 public manifests and indexed regional M13_SYSTSLCE bytes are available and can support a bounded IL12RB2 input/feasibility audit while the primary bytes remain unavailable.",
            "change": "Add R4A12FG2/R4A12FG3 as a secondary branch; do not change the primary estimand or claim boundary.",
        },
        "r4a11cd_reconciliation": {
            "R4A11C_role": "HISTORICAL_ADVISORY_INPUT",
            "R4A11D_role": "HISTORICAL_ADVISORY_INPUT_WITH_CORRECTIONS",
            "R12_M13_SYSTSLCE_cases": {
                "R4A11D_reported": 881,
                "official_public_analysis_manifest": 854,
                "adopted": 854,
                "explanation": "Risteys phenotype count is not the public GWAS analysis N.",
            },
            "R13_M13_SYSTSLCE_cases": {"reported": 883, "official_public_analysis_manifest": 883, "adopted": 883},
            "R12_R13_relationship": "CROSS_RELEASE_STABILITY_NOT_INDEPENDENT_REPLICATION",
            "H6_v2_1_applicability": "TARGET_2026_SEX_STRATIFIED_INPUT_ONLY; FinnGen all-sex uses P0-FG.",
            "native_finemap_boundary": "FinnGen native fine-mapping is generated for genome-wide significant regions; the IL12RB2 regional lead is not genome-wide significant in R12 or R13, so a native IL12RB2 credible set is not presumed.",
        },
        "branch": {
            "id": "R4A12FG2_FINNGEN_ALL_SEX_IL12RB2",
            "role": "ENGINEERING_AND_SECONDARY_SENSITIVITY",
            "disease_endpoint": "M13_SYSTSLCE",
            "releases": {"R13": "LATEST_ALL_SEX_INPUT", "R12": "MULTIOME_RELEASE_BRIDGE"},
            "region_grch38": "1:66840524-67840524",
            "anchor": "rs6662198 / 1:67340524:T:C",
            "input_states": {
                "R12_public_manifest": "OBTAINED",
                "R13_public_manifest": "OBTAINED",
                "target_objects_head": "PASS_12_OF_12",
                "R12_region": "OBTAINED_REMOTE_TABIX_REQUERY_HASH_IDENTICAL",
                "R13_region": "OBTAINED_REMOTE_TABIX_REQUERY_HASH_IDENTICAL",
                "R12_full_GWAS_object": "NOT_DOWNLOADED",
                "R13_full_GWAS_object": "NOT_DOWNLOADED",
                "R12_sex_specific_drop_list": "ACCESS_BLOCKED_403_NO_ACTIVE_FINNGEN_GCLOUD_ACCOUNT",
                "R13_sex_specific_release": "NOT_OFFICIALLY_DOCUMENTED_IN_CHECKED_RELEASE_NOTES",
                "TenK10K_IL12RB2_gene_level_and_CS": "OBTAINED",
                "TenK10K_IL12RB2_complete_variant_beta_SE": "NOT_OBTAINED",
                "matched_LD": "NOT_OBTAINED",
                "variant_INFO_annotation": "NOT_MATERIALIZED_FOR_REGION",
            },
            "P0_FG": {key: value["status"] for key, value in p0.items()},
            "scientific_outputs": {
                "regional_association": "DESCRIPTIVE_ONLY",
                "cross_release_comparison": descriptive["cross_release"]["interpretation"],
                "formal_finemapping": "NOT_RUN",
                "formal_coloc": "NOT_RUN",
                "SMR_HEIDI": "NOT_RUN",
                "C1": "NOT_APPLICABLE_TO_THIS_BRANCH_AND_NOT_UPDATED",
            },
        },
        "next_stage": {
            "id": "R4A12FG3_MOLECULAR_QTL_AND_LD_FEASIBILITY_GATE",
            "goal": "Obtain complete variant-level IL12RB2 molecular QTL statistics and compatible LD/INFO/reference inputs, then decide whether a bounded all-sex coloc is technically testable.",
            "go_requirements": [
                "Complete variant-level QTL beta/SE or source signal likelihood inputs with exact GRCh38 alleles",
                "Adequate disease-QTL exact-key coverage and retained QTL credible-set mass",
                "Matched/source-compatible signed LD if multi-signal fine-mapping is required",
                "Frozen INFO/QC and normalization policy with reference identity",
            ],
            "failure_state": "UNTESTABLE_OR_UNINFORMATIVE; never a negative IL12RB2 or SSc conclusion",
            "primary_project_trigger_unchanged": base["next_stage"],
        },
        "evidence": {
            "object_receipt": {"path": str(object_receipt_path), "sha256": sha256(object_receipt_path), "status": object_receipt["status"]},
            "descriptive_audit": {"path": str(descriptive_path), "sha256": sha256(descriptive_path), "status": descriptive["status"]},
            "P0": {key: {"path": str(path), "sha256": sha256(path), "status": p0[key]["status"]} for key, path in p0_paths.items()},
        },
    }
    amendment_path = protocol / "analysis_manifest_v11_amendment_A1_R4A12FG2.json"
    amendment_path.write_text(json.dumps(amendment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    state = {
        "stage": "R4A12FG2",
        "date": local_date,
        "execution_window": "2026-09-12_to_2026-09-13_Asia_Hong_Kong",
        "generated_at_utc": generated,
        "project": "CONDITIONAL_GO",
        "R4B": "HOLD",
        "C1_count": None,
        "primary_2026_female_summary_statistics": "NOT_OBTAINED",
        "primary_2026_male_summary_statistics": "NOT_OBTAINED",
        "primary_scientific_branch": "UNCHANGED_CHR22_SYNGR1_SEX_STRATIFIED",
        "R4A12FG2": {
            "status": "PASS_REGIONAL_INPUT_AND_DESCRIPTIVE_SMOKE_GATE",
            "R12_M13_SYSTSLCE_region": "PASS_P0_FG",
            "R13_M13_SYSTSLCE_region": "PASS_P0_FG",
            "cross_release": descriptive["cross_release"]["interpretation"],
            "formal_disease_molecular_coloc": "NOT_TESTED",
            "full_GWAS_archives": "NOT_DOWNLOADED_SCRIPT_READY",
        },
        "next_stage": amendment["next_stage"]["id"],
        "next_stage_goal": amendment["next_stage"]["goal"],
        "primary_project_trigger_unchanged": base["next_stage"],
        "amendment": {"path": str(amendment_path), "sha256": sha256(amendment_path)},
        "office_rendering": "NOT_APPLICABLE_NO_OFFICE_ARTIFACTS_WPS_RESERVED",
    }
    state_path = protocol / "R4A12FG2_state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = f"""# Analysis Manifest v11 Amendment A1 — R4A12FG2

生成时间（UTC）：`{generated}`

本补充只授权一个有边界的 FinnGen all-sex IL12RB2 工程/敏感性分支。2026 female/male SSc → chr22/SYNGR1 仍是项目主线，`PROJECT=CONDITIONAL_GO`、`R4B=HOLD`、`C1_count=null` 均未改变。

## 本轮纠偏

- R12 `M13_SYSTSLCE` public GWAS analysis N 采用官方 manifest 的 **854 cases / 484,260 controls**；Risteys 的 881 不能写成该公开 GWAS 文件的分析 N。
- R12/R13 样本高度嵌套，跨版本一致性只记为 `CROSS_RELEASE_STABILITY_NOT_INDEPENDENT_REPLICATION`。
- H6 v2.1 保持专用于 2026 sex-stratified 输入；FinnGen all-sex 区域使用独立 P0-FG。
- IL12RB2 不加入 chr22 冻结 20-gene registry，不替代 SYNGR1，也不能更新 C1。

## 下一阶段

`{amendment['next_stage']['id']}`：取得完整 variant-level molecular QTL、相容 LD、INFO/QC 与参考基因组身份，先判断正式 all-sex coloc 是否可测试。任何输入或技术门失败均写 `UNTESTABLE/UNINFORMATIVE`。
"""
    (protocol / "analysis_manifest_v11_amendment_A1_R4A12FG2.md").write_text(md, encoding="utf-8")
    print(json.dumps({"amendment": str(amendment_path), "state": str(state_path), "status": state["R4A12FG2"]["status"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
