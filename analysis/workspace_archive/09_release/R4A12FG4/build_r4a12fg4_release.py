#!/usr/bin/env python3
"""Build the R4A12FG4 reports, state, checksummed release, and catalogs."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import py_compile
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
DATE = "2026-09-13"
STAGE = "R4A12FG4"
REPORT_DIR = ROOT / "7.Report/current/R4A12FG4"
RELEASE_DIR = ROOT / "6_release/current/R4A12FG4"
PACKAGE_NAME = "CMM_R4A12FG4_TenK10K_NK接入与信号门_2026-09-13"
PACKAGE_ROOT = RELEASE_DIR / PACKAGE_NAME
ZIP_PATH = RELEASE_DIR / f"{PACKAGE_NAME}.zip"
VALIDATION_DIR = ROOT / "0_admin/validation/R4A12FG4"
AUDIT_DIR = ROOT / "3_results/00_audit/R4A12FG4"
RESULT_DIR = ROOT / "3_results/01_smoke/R4A12FG4_IL12RB2"
QTL_DIR = ROOT / "1_data/qtl/eqtl/tenk10k/derived/IL12RB2_full/remote_NK"
CODE_INTAKE = ROOT / "2_code/06_intake/tenk10k_il12rb2"
CODE_ANALYSIS = ROOT / "2_code/07_analysis/R4A12FG4"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    temporary.write_text(value.rstrip() + "\n", encoding="utf-8")
    os.replace(temporary, path)


def write_json(path: Path, value: dict) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def append_tsv_if_absent(path: Path, key_value: str, row: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if key_value in text:
        return
    with path.open("a", encoding="utf-8", newline="") as handle:
        handle.write("\t".join(row) + "\n")


def validate_inputs() -> dict:
    package_audit = load_json(VALIDATION_DIR / "R4A12FG3_PACKAGE_INTEGRITY.json")
    intake = load_json(QTL_DIR / "TenK10K_NK_IL12RB2_selective_intake_receipt.json")
    harmonization = load_json(RESULT_DIR / "R4A12FG4_harmonization_gate.json")
    proxy = load_json(AUDIT_DIR / "R4A12FG4_missing_CS_external_proxy_audit.json")
    coloc = load_json(RESULT_DIR / "R4A12FG4_coloc_abf_postgate_diagnostic_summary.json")
    inventory = load_json(AUDIT_DIR / "tenk10k_100kb_remote_zip_inventory.json")
    header_probe = load_json(AUDIT_DIR / "nk_member_header_probe.json")
    assert package_audit["status"] == "PASS_WITH_ACCOUNTING_NOTE"
    assert package_audit["checksum_pass_count"] == 17
    assert package_audit["standalone_pass_count"] == 9
    assert intake["status"] == "PASS_SELECTIVE_MEMBER_INTAKE"
    assert intake["extract"]["target_rows"] == 1366
    assert intake["extract"]["member_crc32_observed"] == "25f9b199"
    assert inventory["member_count"] == 28
    assert "BETA" in header_probe["header"] and "SE" in header_probe["header"]
    assert harmonization["status"] == "HOLD_COVERAGE"
    for release in ("R12", "R13"):
        item = harmonization["releases"][release]["harmonization"]
        assert item["harmonized_variants"] == 891
        assert item["reverse_allele_pairs_excluded"] == 5
        assert item["checks"]["qtl_top_covered"]
        assert item["checks"]["disease_regional_lead_covered"]
        assert item["checks"]["rs6662198_covered"]
    assert proxy["status"] == "CONDITIONAL_PROXY_SUPPORT_FOR_POST_GATE_DIAGNOSTIC"
    assert coloc["R12"]["classification"] == "AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY"
    assert coloc["R13"]["classification"] == "AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY"
    return {
        "package_audit": package_audit,
        "intake": intake,
        "harmonization": harmonization,
        "proxy": proxy,
        "coloc": coloc,
        "inventory": inventory,
        "header_probe": header_probe,
    }


def build_protocol(evidence: dict) -> tuple[Path, Path, Path]:
    base_manifest = ROOT / "0_admin/protocol/current/analysis_manifest_v11.json"
    registry = ROOT / "0_admin/protocol/current/candidate_registry_v11.tsv"
    amendment_path = ROOT / "0_admin/protocol/current/analysis_manifest_v11_amendment_A2_R4A12FG4.json"
    amendment_md_path = ROOT / "0_admin/protocol/current/analysis_manifest_v11_amendment_A2_R4A12FG4.md"
    amendment = {
        "amendment_id": "CMM_R4A12FG4_ANALYSIS_MANIFEST_V11_AMENDMENT_A2",
        "schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_manifest": {
            "path": str(base_manifest),
            "sha256": sha256(base_manifest),
            "candidate_registry_path": str(registry),
            "candidate_registry_sha256": sha256(registry),
        },
        "scope": "Close the bounded FinnGen all-sex IL12RB2 NK-first summary-statistics gate without changing the sex-stratified chr22/SYNGR1 primary branch.",
        "precedence": {
            "primary_project": "CONDITIONAL_GO",
            "primary_branch": "2026 female/male SSc chr22/SYNGR1",
            "primary_input": "NOT_OBTAINED",
            "R4B": "HOLD",
            "C1_count": None,
            "IL12RB2_role": "SECONDARY_ALL_SEX_SENSITIVITY_ONLY",
        },
        "pre_result_exact_coverage_gate": {
            "frozen_in_code_before_harmonization": True,
            "qtl_unique_variants_min": 100,
            "exact_overlap_min": 100,
            "qtl_overlap_fraction_min": 0.80,
            "exact_reference_alignment_fraction_min": 0.99,
            "median_AF_absolute_difference_max": 0.10,
            "p95_AF_absolute_difference_max": 0.20,
            "required_anchors": ["QTL top", "regional disease lead", "rs6662198"],
            "source_CS_requirement": "all members and >=0.95 PIP mass per source credible set",
        },
        "observed_gate": {
            "local_variant_level_qtl": "PASS_1366_ROWS",
            "member_crc32": "PASS_25f9b199",
            "R12_exact_overlap": 891,
            "R13_exact_overlap": 891,
            "qtl_overlap_fraction": 0.6522693997071742,
            "CS1_exact_pip_fraction": 0.7207342839156841,
            "CS2_exact_pip_fraction": 0.979075552970314,
            "status": "HOLD_EXACT_COVERAGE",
        },
        "post_gate_diagnostic": {
            "reason": "The missing CS1 variant rs5022165 (PIP 0.283267) has an exact-overlap same-CS proxy rs11209050 with r2 approximately 1.0 in the frozen 1000G EUR503 panel.",
            "authorization": "Run classic coloc.abf only as an explicitly labelled post-gate diagnostic; do not retroactively pass exact coverage.",
            "priors": {"p1": 1e-4, "p2": 1e-4, "p12": [1e-6, 1e-5, 1e-4]},
            "result": "AMBIGUOUS_AND_PRIOR_SENSITIVE_IN_R12_AND_R13",
            "cannot_satisfy_C1": True,
        },
        "next_stage": {
            "id": "R4A12FG5_EXTERNAL_LD_AND_THREE_CELL_REPLICATION_GATE",
            "goal": "Adjudicate the ambiguous all-sex IL12RB2 signal with a strict external-LD gate and three pre-ranked secondary cells, while keeping source-matched LD and primary sex-stratified SSc as separate requirements.",
        },
    }
    write_json(amendment_path, amendment)
    write_text(
        amendment_md_path,
        """# Analysis Manifest v11 Amendment A2 — R4A12FG4

本修订只关闭 FinnGen all-sex `M13_SYSTSLCE` × TenK10K NK `IL12RB2` 的摘要统计门。主分析仍是 2026 female/male SSc 的 chr22/SYNGR1 路线；`R4B=HOLD`、`C1_count=null`。

真实 NK variant-level eQTL 已接入并通过成员 CRC，但 R12/R13 均仅有 891/1366 个精确重叠，且 CS1 精确覆盖 PIP 比例为 0.7207，所以 exact coverage 保持 HOLD。外部 EUR503 显示缺失高 PIP 变异 rs5022165 与已覆盖 rs11209050 的 `r²≈1.0`，只允许补做明确标记的 post-gate `coloc.abf` 诊断。

该诊断在 `p12=10^-5` 时支持 H4，但在 `p12=10^-6` 时明显下降，R12/R13 均归类为 `AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY`。不得据此升级 C1 或启动 R4B。
""",
    )
    state_path = ROOT / "0_admin/protocol/current/R4A12FG4_state.json"
    state = {
        "stage": "R4A12FG4_TARGETED_TENK10K100KB_INTAKE_NK_FIRST_SIGNAL_GATE",
        "date": DATE,
        "project": "CONDITIONAL_GO",
        "R4B": "HOLD",
        "C1_count": None,
        "primary_2026_female_summary_statistics": "NOT_OBTAINED",
        "primary_2026_male_summary_statistics": "NOT_OBTAINED",
        "primary_scientific_branch": "UNCHANGED_CHR22_SYNGR1_SEX_STRATIFIED",
        "R4A12FG4": {
            "TenK10K_NK_member_intake": "PASS_MEMBER_CRC_AND_EXACT_GENE_EXTRACT",
            "TenK10K_NK_IL12RB2_rows": 1366,
            "R12_exact_overlap": 891,
            "R13_exact_overlap": 891,
            "exact_coverage": "HOLD",
            "external_proxy_diagnostic": "CONDITIONAL_SUPPORT_ONLY",
            "classic_coloc_abf": "POST_GATE_AMBIGUOUS_PRIOR_SENSITIVE",
            "formal_multisignal_coloc": "NOT_RUN_LD_GATE_HOLD",
            "branch_state": "SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED",
        },
        "next_stage": "R4A12FG5_EXTERNAL_LD_AND_THREE_CELL_REPLICATION_GATE",
        "primary_project_trigger_unchanged": "R4A12_BYTE_ARRIVAL_TRIGGERED_HARMONIZATION_AND_COVERAGE_GATE",
        "amendment": {"path": str(amendment_path), "sha256": sha256(amendment_path)},
        "office_rendering": "NOT_APPLICABLE_NO_OFFICE_ARTIFACTS_WPS_RESERVED",
    }
    write_json(state_path, state)
    return amendment_path, amendment_md_path, state_path


def make_coverage_table(evidence: dict) -> Path:
    path = RESULT_DIR / "R4A12FG4_coverage_summary.tsv"
    rows = []
    for release in ("R12", "R13"):
        h = evidence["harmonization"]["releases"][release]["harmonization"]
        rows.append(
            {
                "release": release,
                "qtl_variants": h["qtl_unique_variants"],
                "gwas_region_variants": h["gwas_regional_variants"],
                "exact_overlap": h["harmonized_variants"],
                "qtl_overlap_fraction": h["overlap_fraction_qtl"],
                "reverse_allele_pairs_excluded": h["reverse_allele_pairs_excluded"],
                "AF_absdiff_median": h["af_median_abs_diff"],
                "AF_absdiff_p95": h["af_p95_abs_diff"],
                "CS1_exact_PIP_fraction": h["source_cs"]["1"]["covered_pip_fraction"],
                "CS2_exact_PIP_fraction": h["source_cs"]["2"]["covered_pip_fraction"],
                "anchor_qtl_top": h["checks"]["qtl_top_covered"],
                "anchor_disease_lead": h["checks"]["disease_regional_lead_covered"],
                "anchor_rs6662198": h["checks"]["rs6662198_covered"],
                "status": h["status"],
            }
        )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def build_reports(evidence: dict) -> dict[str, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    r12 = evidence["coloc"]["R12"]["primary_p12_1e_5"]
    r13 = evidence["coloc"]["R13"]["primary_p12_1e_5"]
    reports: dict[str, str] = {
        "00_CMM_R4A12FG4_执行摘要_TenK10K_NK接入与信号门.md": f"""# CMM R4A12FG4 执行摘要：TenK10K NK 接入与信号门

日期：{DATE}

## 最终判定

- 总项目：`CONDITIONAL_GO`
- 正式 R4B：`HOLD`
- `C1_count=null`；2026 female/male SSc 主数据仍未取得
- FinnGen all-sex IL12RB2 分支：`SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED`
- 下一阶段：`R4A12FG5_EXTERNAL_LD_AND_THREE_CELL_REPLICATION_GATE`

## 本轮新证据

TenK10K 16.56 GB 远程 ZIP 的中央目录确认有 28 个细胞文件。本轮没有下载整个归档，而是以 HTTP Range 只取得 NK 成员 556,881,415 个压缩字节；完整 DEFLATE 流展开为 2,272,841,254 字节，成员 CRC32 `25f9b199` PASS。从 15,588,167 行中精确提取 1,366 条 `ENSG00000081985/IL12RB2` 记录。真实表头确认含 `Allele1/Allele2/AF_Allele2/BETA/SE/p.value/N`，其中 SAIGE-QTL 的 BETA 对应 Allele2。

R12 与 R13 各有 891 个 exact GRCh38 REF/ALT 重叠，占 QTL 变异 65.23%；5 个反向等位基因位置因多等位/重复序列歧义被排除。AF 绝对差中位数约 0.02994、P95 约 0.12226，QTL top、rs6662198 和 disease regional lead 全部保留且效应方向一致。

exact coverage 仍未通过：CS1 仅覆盖 11/12 成员、72.07% PIP mass；缺失的 rs5022165 自身 PIP=0.2833。外部 1000G EUR503 显示它与已精确覆盖的 rs11209050 `r²≈1.0`，所以允许一次明确标注的 post-gate 诊断，但 exact coverage 与 source-matched LD 仍保持 HOLD。

`coloc.abf` 结果明显依赖 p12。主 `p12=10^-5` 时 R12 `PP.H4={r12['PP.H4']:.4f}`、R13 `PP.H4={r13['PP.H4']:.4f}`；降至 `10^-6` 时分别为 0.3558 和 0.3311。两版均判定 `AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY`。由于 NK 有两个 source SuSiE signals、精确覆盖不足且 R12/R13 不是独立队列，该结果不能升级 C1，也不能判 IL12RB2 阴性。
""",
        "01_CMM_R4A12FG4_R4A12FG3输入包与远程接入审计.md": """# CMM R4A12FG4：R4A12FG3 输入包与远程接入审计

## 输入包完整性

用户提供的 R4A12FG3 ZIP SHA-256 为 `5919df5762886f0e2256a2ad914e586d693ecb54e7d6de84c9f1e29d7d294175`，ZIP CRC PASS。`checksums.sha256` 的 17/17 个对象全部独立重算 PASS，9 个 standalone 附件与包内对应文件逐字节一致。

包内 `R4A12FG3_release_validation.json` 写成 `checksums_verified=16`，实际 manifest 有 17 行。这是计数错误，不改变内容完整性。原下载脚本直接写最终 `.zip` 路径，缺少 `.part`、远端长度前检、原子晋升和机器可读 receipt；原提取器按任意字段搜索基因、直接写最终输出，且未记录成员 CRC/输出哈希。两者已作为历史快照保存，当前入口已替换。

## Zenodo 独立实测

官方记录 18221260 的 API 返回 `common_all_cis_pvalues_100kb.zip` 大小 16,559,137,990 字节、MD5 `dd54714b2effb91160ac171ccb941534`。HEAD 和 Range 均实测 PASS。通过 ZIP64 尾部中央目录，仅传输少量字节即确定 28 个成员；NK 成员 local header offset=11,749,190,239，压缩大小 556,881,415，展开大小 2,272,841,254，CRC32=`25f9b199`。

1 MiB 局部成员探针直接解压出真实 header，确认 `BETA` 与 `SE` 存在。完整选择性下载随后以 67 个 8 MiB 以内的块、4 个并发连接完成，所有块写 `.part` 后原子改名，支持同命令续传。

## 完整性边界

本轮验证的是完整 NK 成员 CRC，不是整个 16.56 GB ZIP 的 provider MD5。其他 27 个成员没有下载，因此不得宣称整包 MD5 已验证。
""",
        "02_CMM_R4A12FG4_TenK10K_NK_IL12RB2完整QTL验收.md": """# CMM R4A12FG4：TenK10K NK IL12RB2 完整 QTL 验收

## 接入结果

| 项目 | 结果 |
|---|---:|
| 远程归档成员数 | 28 |
| NK 压缩成员字节 | 556,881,415 |
| NK 展开字节 | 2,272,841,254 |
| 完整源文件行数（含表头） | 15,588,167 |
| IL12RB2 精确行数 | 1,366 |
| IL12RB2 坐标范围（GRCh38） | chr1:67,207,429–67,498,705 |
| 成员 CRC32 | `25f9b199` PASS |
| 提取文件 SHA-256 | `3a4f0802507c31d81afdd9842ff256ef48587ccba88310f7760c7ccee9e956fd` |

真实字段为：空索引列、`CHR`、`POS`、`MarkerID`、`Allele1`、`Allele2`、`AC_Allele2`、`AF_Allele2`、`MissingRate`、`BETA`、`SE`、`Tstat`、`var`、`p.value`、`p.value.NA`、`Is.SPA`、`N`、`gene`、`is_snp`。本轮按 `gene` 字段精确匹配 `ENSG00000081985`，不再按任意单元格模糊搜索。

全部目标记录 N=1,925。QTL top 为 `1:67324915:T:C`，BETA=0.470725、SE=0.0201335、P=6.80524×10^-121。rs6662198 对应 `1:67340524:T:C`，QTL BETA=-0.360208、P=2.99088×10^-86。

`Allele2` 是 SAIGE-QTL 的效应等位基因；FinnGen 的 beta 和 AF 对 ALT。因此 harmonization 仅接受 exact REF/ALT。反向等位基因位置不能仅凭交换和翻转 beta 合并，尤其重复序列和多等位位点会造成严重 AF 冲突。
""",
        "03_CMM_R4A12FG4_R12R13_Harmonization覆盖与锚点审计.md": """# CMM R4A12FG4：R12/R13 Harmonization、覆盖与锚点审计

## 冻结门与结果

本轮在读取 harmonization 结果前把 coverage 门写入代码：QTL 与 overlap 均至少 100；QTL exact overlap fraction ≥0.80；exact reference alignment ≥0.99；AF 绝对差中位数 ≤0.10、P95 ≤0.20；QTL top、disease regional lead、rs6662198 必须保留；每个 source CS 全成员且 PIP mass ≥0.95。

R12 与 R13 结果相同：1,366 个 QTL 变异中 891 个 exact overlap（65.23%），5 个 reverse-allele 同位置对象排除。AF 中位差约 0.02994，P95 约 0.12226，三个锚点全部覆盖。门失败来自总体 exact coverage 和 CS1 PIP coverage，不来自 schema、坐标、AF 或锚点。

| Source CS | 成员覆盖 | PIP mass 覆盖 | 判定 |
|---|---:|---:|---|
| CS1 | 11/12 | 0.73106/1.01433 = 72.07% | HOLD |
| CS2 | 3/4 | 0.95485/0.97526 = 97.91% | 成员不全；质量大体保留 |

CS1 缺失 `1:67322669:A:G`（rs5022165，PIP=0.283267），FinnGen 两版区域文件中该位置都不存在。CS2 缺失 `1:67306704:AG:A`（rs3834764，PIP=0.020407）。NCBI Variation Services 完成两个 RefSNP 映射。

外部 1000G EUR503 诊断发现 rs5022165 与同一 CS、已覆盖的 `1:67326053:A:C`（rs11209050）`r²≈1.0`。这说明主要缺失 PIP 很可能有强代理，但不能恢复缺失变异的 disease statistic，也不能替代 TenK10K source-matched LD。exact coverage 状态继续为 HOLD。

三个锚点在 exact allele 下方向一致：QTL top、rs6662198、R12/R13 regional disease lead rs1954118 均同时具有很强 eQTL 和名义/区域疾病信号。这是继续做 LD-aware adjudication 的理由，不是 shared causal 结论。
""",
        "04_CMM_R4A12FG4_colocABF敏感性与最终判定.md": f"""# CMM R4A12FG4：coloc.abf 敏感性与最终判定

## 分析身份

由于 exact coverage 门未通过，本分析标记为 `POST_EXACT_COVERAGE_GATE_SINGLE_CAUSAL_DIAGNOSTIC_ONLY`。使用 891 个 exact GRCh38 REF/ALT 变异，FinnGen R12/R13 为 case-control，TenK10K NK 为 quantitative；QTL sdY 按 coloc 内部同公式由 varbeta、MAF、N 估计为 0.492066。软件为 R 4.6.1、coloc 5.2.3。

## 结果

| Release | p12 | PP.H3 | PP.H4 | H4/(H3+H4) |
|---|---:|---:|---:|---:|
| R12 | 1e-6 | 0.2692 | 0.3558 | 0.5693 |
| R12 | 1e-5 | 0.0641 | 0.8467 | 0.9297 |
| R12 | 1e-4 | 0.0074 | 0.9822 | 0.9925 |
| R13 | 1e-6 | 0.3353 | 0.3311 | 0.4968 |
| R13 | 1e-5 | 0.0843 | 0.8319 | 0.9080 |
| R13 | 1e-4 | 0.0099 | 0.9802 | 0.9900 |

两版 top shared variant 均为 `1:67324915:T:C`，单变异 H4 posterior 约 0.393–0.394。主先验下达到预设 H4 门，但低共享先验下 H4 <0.50 且 H4/(H3+H4) <0.80，因此不能判稳健 shared。

NK source SuSiE 有两个 credible sets，违反把单因果模型当作最终模型的前提；coloc 官方文档也要求 ABF 使用稠密变异图谱。本轮 exact overlap 只有 65.23%，疾病 regional lead P≈2.6–2.8×10^-5，且 R12/R13 是高度重叠的 release 更新而非独立复制。

最终分类：R12 与 R13 均为 `AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY`。保留 IL12RB2 作为需要 LD-aware 判定的 secondary all-sex candidate；不升级 C1、不启动 chromatin layer、不启动 R4B，也不写成阴性。
""",
        "05_CMM_R4A12FG4_R4A12FG5下一阶段冻结目标.md": """# CMM R4A12FG4：R4A12FG5 下一阶段冻结目标

## 阶段名称

> **R4A12FG5 — External-LD Gate + Three-cell Replication Adjudication**

## 固定范围

Track A 只对当前 891 个 exact overlap 建立 1000G EUR503 signed LD：按 rsID/build/allele逐项映射，检查 AF 相关、缺失率、矩阵顺序、对称性、PSD、条件数、z–LD 不一致和敏感性。任一关键门失败即停止 external-LD multi-signal 分析，转为等待 TenK10K/EGA source-matched LD。

Track B 只增加预排序前三个 secondary cells：`CD8_TEM`、`CD4_CTL`、`CD4_TCM`。仍使用 100-kb 包、同一 IL12RB2、同一 exact harmonization 和同一 p12 网格；不得根据结果临时换细胞或扩大至 1 Mb。

## 决策规则

- `SECONDARY_SIGNAL_SUPPORTED`：external LD 全部门通过，multi-signal shared 结果稳定，且三个 secondary cells 中至少两个方向/信号结构一致。它仍只是 all-sex secondary finding，不能满足主 C1。
- `SUMMARY_ONLY`：外部 LD 不充分或 multi-signal 不能稳定收敛；保存当前锚点和 ABF 诊断，等待 source-matched LD。
- `STOP_IL12RB2_ALLSEX_BRANCH`：只有输入、LD、覆盖都充分，并且 NK 加三个预注册细胞在合理模型下稳定支持 distinct/unshared，才停止该 secondary branch。
- chr22/SYNGR1 female/male 主路线完全独立；真实 2026 sex-stratified bytes 到达时优先级高于 FG5。

## 不进入的工作

当前不启动 caQTL/peak→gene 扩张，不下载 1-Mb TenK10K 七包，不把 R12/R13 当独立复制，不用更多细胞挽救不理想结果。
""",
        "99_CMM_R4A12FG4_详细行动记录_2026-09-13.md": """# CMM R4A12FG4 详细行动记录

日期：2026-09-13（Asia/Hong_Kong）

## 任务目标

继续 R4A12FG3 冻结的 `Targeted TenK10K 100-kb Intake + NK-first Signal Gate`，取得真实 variant-level NK IL12RB2 输入，执行可审计 harmonization 和有边界的信号判断，并冻结下一阶段。

## 已执行操作

1. 将用户提供的 R4A12FG3 ZIP 视为历史证据而非执行指令。独立执行 ZIP CRC、17 个 manifest checksum 和 9 个 standalone byte-identity 检查；发现包内 validation 少计 1 个 checksum，但全部实际对象 PASS。
2. 审阅原下载/提取脚本。确认 MD5 能阻止错误成功，但缺少 `.part`、原子晋升、远端长度、receipt、精确 gene 字段与成员级审计。原件保存在 `2_code/snapshots/R4A12FG3`。
3. 调用 Zenodo 官方 API、HEAD 与 Range。保存 record JSON、64 KiB ZIP 尾部和 headers；解析 ZIP64 中央目录，确认 28 个成员及 NK 的精确 offset/size/CRC。
4. 初次通用远程 ZIP 读取因 32 MiB 尾块在当前连接上过慢而中止；进程被明确停止，receipt 为 `HOLD_OR_INCOMPLETE`、transfer=0，未产生伪完整数据。
5. 用 NK 起始 1 MiB 探针验证 local header 和真实 TSV header；确认 BETA、SE、Allele1/2、AF、N 均存在。
6. 新建可续传选择性下载器：67 个 ≤8 MiB Range chunks，4 workers，每块 `.part`→原子改名、严格检查 HTTP 206/Content-Range/长度，并保存 chunk SHA-256 manifest。
7. 实际下载 556,881,415 字节，用时约 357 秒；流式展开完整 NK 成员并验证 2,272,841,254 uncompressed bytes 与 CRC32 `25f9b199`；从 15,588,167 行精确提取 1,366 个 IL12RB2 变异。整包 16.56 GB 未下载，故 provider MD5 明确标为未运行。
8. 安装/升级 R 4.6.1，并从 CRAN 安装 coloc 5.2.3 及依赖；保存 sessionInfo。Python requests 2.32.5、numpy 2.3.1 已可用。无 Office 文件，WPS 渲染不适用。
9. 在读取结果前冻结 exact coverage 条件。仅按 GRCh38 REF/ALT exact key 合并；发现 5 个 reverse-allele 同位置对象具有明显多等位/重复序列歧义，全部排除。
10. R12/R13 各保留 891 个 exact variants，AF 和三个锚点通过，但 overlap fraction=65.23%、CS1 exact PIP=72.07%，coverage 判 HOLD。
11. 通过 NCBI Variation Services 把两个缺失 CS 变异映射到 rs5022165/rs3834764。读取冻结的 1000G EUR503 PLINK BED，发现高 PIP 缺失 rs5022165 与 exact-overlap rs11209050 `r²≈1.0`。该结果只批准 post-gate diagnostic，不改变 exact/source-LD HOLD。
12. 运行 coloc.abf p12={1e-6,1e-5,1e-4}。主先验 H4 约 0.83–0.85，但低 p12 时降至约 0.33–0.36；两版均判 ambiguous。再次通过统一 PowerShell 入口复现。
13. 生成 protocol amendment A2、状态 JSON、本轮报告、release checksums、ZIP 与最终验证；更新 workspace paths 和目录 catalog。

## 关键文件与可复现入口

- 选择性接入：`2_code/06_intake/tenk10k_il12rb2/RUN_R4A12FG4_TENK10K_NK.ps1`
- 信号门复现：`2_code/07_analysis/R4A12FG4/RUN_R4A12FG4_SIGNAL_GATE.ps1 -AllowPostGateDiagnostic`
- 完整 QTL：`1_data/qtl/eqtl/tenk10k/derived/IL12RB2_full/remote_NK/NK_IL12RB2_full_variant_eqtl.tsv`
- 结果：`3_results/01_smoke/R4A12FG4_IL12RB2/`
- 审计：`3_results/00_audit/R4A12FG4/`

## 最终状态

`PROJECT=CONDITIONAL_GO`、`R4B=HOLD`、`C1_count=null`。IL12RB2 all-sex 分支是 `SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED`。下一阶段固定为 R4A12FG5 external-LD + 三细胞复核；主 2026 female/male chr22/SYNGR1 输入一旦到达，立即优先。
""",
    }
    sources = """# Sources checked — 2026-09-13

- TenK10K Zenodo record and file metadata: https://zenodo.org/records/18221260
- TenK10K eQTL manuscript: https://www.medrxiv.org/content/10.1101/2025.03.20.25324352v2.full
- SAIGE-QTL output fields and Allele2 effect direction: https://weizhou0.github.io/SAIGE-QTL-doc/docs/single_step2.html
- FinnGen summary-statistics build/ALT-effect documentation: https://github.com/FINNGEN/finngen-documentation/blob/master/data-download.md
- FinnGen public results page: https://www.finngen.fi/en/access_results
- coloc single-causal ABF vignette: https://chr1swallace.github.io/coloc/articles/a03_enumeration.html
- coloc data/LD requirements: https://chr1swallace.github.io/coloc/articles/a02_data.html
- coloc dense-map FAQ: https://chr1swallace.github.io/coloc/FAQ.html
- NCBI Variation Services SPDI/RefSNP API: https://api.ncbi.nlm.nih.gov/variation/v0/
- 1000 Genomes data collection: https://www.internationalgenome.org/data-portal/data-collection/grch37

本轮网络事实以保存的 API JSON、HTTP headers、Range bytes 和本地哈希为准。网页说明仅用于字段、方法和数据发布身份核对。
"""
    readme = """# R4A12FG4 release

本包包含 TenK10K NK `IL12RB2` 选择性接入、R12/R13 exact harmonization、覆盖门、外部 LD 代理诊断和 post-gate coloc.abf 敏感性结果。

科学状态：`CONDITIONAL_GO / R4B=HOLD / C1_count=null`。IL12RB2 all-sex 分支为 `SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED`。

先读 `00_CMM_R4A12FG4_执行摘要_TenK10K_NK接入与信号门.md`，完整过程见 `99_CMM_R4A12FG4_详细行动记录_2026-09-13.md`。包内 `checksums.sha256` 覆盖除自身以外全部文件。
"""
    reports["SOURCES_CHECKED_2026-09-13.md"] = sources
    reports["README.md"] = readme
    output = {}
    for name, content in reports.items():
        path = REPORT_DIR / name
        write_text(path, content)
        output[name] = path
    return output


def build_release(report_paths: dict[str, Path], protocol_paths: tuple[Path, Path, Path], coverage_table: Path, evidence: dict) -> dict:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    if PACKAGE_ROOT.exists():
        resolved = PACKAGE_ROOT.resolve()
        if resolved.parent != RELEASE_DIR.resolve():
            raise RuntimeError("unsafe package cleanup target")
        shutil.rmtree(PACKAGE_ROOT)
    PACKAGE_ROOT.mkdir()
    for path in report_paths.values():
        shutil.copy2(path, PACKAGE_ROOT / path.name)
    data_dir = PACKAGE_ROOT / "data"
    results_dir = PACKAGE_ROOT / "results"
    scripts_dir = PACKAGE_ROOT / "scripts"
    protocol_dir = PACKAGE_ROOT / "protocol"
    for directory in (data_dir, results_dir, scripts_dir, protocol_dir):
        directory.mkdir()
    data_sources = [
        QTL_DIR / "NK_IL12RB2_full_variant_eqtl.tsv",
        RESULT_DIR / "R12_M13_SYSTSLCE_x_TenK10K_NK_IL12RB2_harmonized.tsv",
        RESULT_DIR / "R13_M13_SYSTSLCE_x_TenK10K_NK_IL12RB2_harmonized.tsv",
        RESULT_DIR / "R4A12FG4_anchor_evidence.tsv",
        coverage_table,
    ]
    for path in data_sources:
        shutil.copy2(path, data_dir / path.name)
    result_sources = [
        QTL_DIR / "TenK10K_NK_IL12RB2_selective_intake_receipt.json",
        AUDIT_DIR / "zenodo_18221260_record.json",
        AUDIT_DIR / "remote_zip_tail_64k.headers.txt",
        AUDIT_DIR / "tenk10k_100kb_remote_zip_inventory.json",
        AUDIT_DIR / "nk_member_header_probe.json",
        AUDIT_DIR / "NK_IL12RB2_CS_NCBI_refsnp_map.json",
        VALIDATION_DIR / "R4A12FG3_PACKAGE_INTEGRITY.json",
        RESULT_DIR / "R4A12FG4_harmonization_gate.json",
        AUDIT_DIR / "R4A12FG4_missing_CS_external_proxy_audit.json",
        RESULT_DIR / "R12_IL12RB2_coloc_abf_postgate_diagnostic.tsv",
        RESULT_DIR / "R13_IL12RB2_coloc_abf_postgate_diagnostic.tsv",
        RESULT_DIR / "R4A12FG4_coloc_abf_postgate_diagnostic_summary.json",
        AUDIT_DIR / "runtime_manifest.json",
        AUDIT_DIR / "R_sessionInfo.txt",
    ]
    for path in result_sources:
        shutil.copy2(path, results_dir / path.name)
    scripts = [
        CODE_INTAKE / "download_extract_tenk10k_nk_resume.py",
        CODE_INTAKE / "RUN_R4A12FG4_TENK10K_NK.ps1",
        CODE_INTAKE / "requirements-r4a12fg4.txt",
        CODE_ANALYSIS / "harmonize_il12rb2_tenk10k_finngen.py",
        CODE_ANALYSIS / "audit_missing_cs_external_ld.py",
        CODE_ANALYSIS / "run_il12rb2_coloc_abf.R",
        CODE_ANALYSIS / "summarize_il12rb2_coloc.py",
        CODE_ANALYSIS / "RUN_R4A12FG4_SIGNAL_GATE.ps1",
        VALIDATION_DIR / "audit_r4a12fg3_package.py",
        AUDIT_DIR / "parse_remote_zip_tail.py",
        AUDIT_DIR / "probe_nk_header.py",
        AUDIT_DIR / "map_nk_cs_variants_to_refsnp.py",
        ROOT / "2_code/09_release/R4A12FG4/build_r4a12fg4_release.py",
    ]
    for path in scripts:
        shutil.copy2(path, scripts_dir / path.name)
    for path in protocol_paths:
        shutil.copy2(path, protocol_dir / path.name)

    release_validation = {
        "schema_version": "CMM_R4A12FG4_RELEASE_VALIDATION_1.0",
        "status": "PASS_WITH_SCIENTIFIC_HOLDS",
        "package_input": {
            "R4A12FG3": "PASS_WITH_ACCOUNTING_NOTE",
            "checksums": "17/17",
            "standalones": "9/9 byte-identical",
        },
        "TenK10K_NK": {
            "member_crc32": "PASS_25f9b199",
            "target_rows": 1366,
            "complete_member_uncompressed_bytes": 2_272_841_254,
        },
        "harmonization": {"R12_exact": 891, "R13_exact": 891, "status": "HOLD_COVERAGE"},
        "post_gate_coloc": {"R12": "AMBIGUOUS", "R13": "AMBIGUOUS"},
        "scientific_state": {"project": "CONDITIONAL_GO", "R4B": "HOLD", "C1_count": None},
        "holds": ["2026 female/male SSc bytes", "exact QTL-GWAS coverage", "source-matched LD", "multi-signal coloc"],
        "office_rendering": "NOT_APPLICABLE_NO_OFFICE_ARTIFACTS_WPS_RESERVED",
    }
    write_json(results_dir / "R4A12FG4_release_validation.json", release_validation)

    checksum_lines = []
    for path in sorted(p for p in PACKAGE_ROOT.rglob("*") if p.is_file()):
        relative = path.relative_to(PACKAGE_ROOT).as_posix()
        if relative == "checksums.sha256":
            continue
        checksum_lines.append(f"{sha256(path)}  {relative}")
    write_text(PACKAGE_ROOT / "checksums.sha256", "\n".join(checksum_lines))
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
        for path in sorted(p for p in PACKAGE_ROOT.rglob("*") if p.is_file()):
            archive.write(path, f"{PACKAGE_NAME}/{path.relative_to(PACKAGE_ROOT).as_posix()}")
    zip_hash = sha256(ZIP_PATH)
    write_text(ZIP_PATH.with_suffix(ZIP_PATH.suffix + ".sha256"), f"{zip_hash}  {ZIP_PATH.name}")
    return {"zip": ZIP_PATH, "zip_sha256": zip_hash, "checksum_count": len(checksum_lines)}


def final_validate(release: dict) -> dict:
    errors = []
    with zipfile.ZipFile(release["zip"]) as archive:
        bad = archive.testzip()
        if bad:
            errors.append(f"ZIP_CRC:{bad}")
        names = archive.namelist()
        manifest_name = f"{PACKAGE_NAME}/checksums.sha256"
        manifest = archive.read(manifest_name).decode("utf-8").splitlines()
        for line in manifest:
            expected, relative = line.split("  ", 1)
            payload = archive.read(f"{PACKAGE_NAME}/{relative}")
            observed = hashlib.sha256(payload).hexdigest()
            if expected != observed:
                errors.append(f"CHECKSUM:{relative}")
    python_files = [
        CODE_INTAKE / "download_extract_tenk10k_nk_resume.py",
        CODE_ANALYSIS / "harmonize_il12rb2_tenk10k_finngen.py",
        CODE_ANALYSIS / "audit_missing_cs_external_ld.py",
        CODE_ANALYSIS / "summarize_il12rb2_coloc.py",
    ]
    compile_errors = []
    for path in python_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as error:
            compile_errors.append(f"{path}:{error}")
    errors.extend(compile_errors)
    result = {
        "schema_version": "CMM_R4A12FG4_FINAL_VALIDATION_1.0",
        "status": "PASS" if not errors else "FAIL",
        "zip": str(release["zip"]),
        "zip_bytes": release["zip"].stat().st_size,
        "zip_sha256": release["zip_sha256"],
        "zip_crc": "PASS" if not any(e.startswith("ZIP_CRC") for e in errors) else "FAIL",
        "zip_file_count": len(names),
        "checksum_manifest_rows": len(manifest),
        "checksum_pass_count": len(manifest) - sum(e.startswith("CHECKSUM") for e in errors),
        "python_compile": "PASS" if not compile_errors else "FAIL",
        "errors": errors,
        "scientific_holds_are_expected": True,
    }
    write_json(VALIDATION_DIR / "R4A12FG4_FINAL_VALIDATION.json", result)
    write_text(
        VALIDATION_DIR / "R4A12FG4_FINAL_VALIDATION.md",
        f"# R4A12FG4 final validation\n\nStatus: `{result['status']}`  \nZIP CRC: `{result['zip_crc']}`  \nChecksums: `{result['checksum_pass_count']}/{result['checksum_manifest_rows']}`  \nPython compile: `{result['python_compile']}`\n",
    )
    return result


def update_workspace(protocol_paths: tuple[Path, Path, Path], release: dict) -> None:
    amendment, _amendment_md, state = protocol_paths
    paths_file = ROOT / "0_admin/workspace_paths.json"
    paths = load_json(paths_file)
    paths.update(
        {
            "release_current": str(RELEASE_DIR),
            "reports_current": str(REPORT_DIR),
            "current_state": str(state),
            "current_protocol_amendment": str(amendment),
            "next_stage": "R4A12FG5_EXTERNAL_LD_AND_THREE_CELL_REPLICATION_GATE",
            "bounded_all_sex_branch": {
                "stage": "R4A12FG4",
                "status": "SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED",
                "exact_overlap": {"R12": 891, "R13": 891},
                "role": "ENGINEERING_AND_SECONDARY_SENSITIVITY",
            },
        }
    )
    write_json(paths_file, paths)

    readme = ROOT / "README_WORKSPACE.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "| 下一阶段 | `R4A12_BYTE_ARRIVAL_TRIGGERED_HARMONIZATION_AND_COVERAGE_GATE` |",
        "| 当前执行下一阶段 | `R4A12FG5_EXTERNAL_LD_AND_THREE_CELL_REPLICATION_GATE` |\n| 主项目数据触发器 | `R4A12_BYTE_ARRIVAL_TRIGGERED_HARMONIZATION_AND_COVERAGE_GATE` |",
    )
    if "## R4A12FG4 当前分支" not in text:
        text += """

## R4A12FG4 当前分支

TenK10K NK IL12RB2 的 1,366 条完整 variant-level eQTL 已取得并通过成员 CRC。FinnGen R12/R13 各有 891 个 exact overlap；coverage 保持 HOLD，post-gate coloc.abf 对先验敏感，分支状态为 `SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED`。当前报告见 `7.Report/current/R4A12FG4`，release 见 `6_release/current/R4A12FG4`。
"""
    write_text(readme, text)

    data_catalog = ROOT / "1_data/catalogs/DATA_CATALOG.tsv"
    qtl = QTL_DIR / "NK_IL12RB2_full_variant_eqtl.tsv"
    append_tsv_if_absent(
        data_catalog,
        "NK_IL12RB2_full_variant_eqtl.tsv",
        ["ZENODO_18221260_SELECTIVE_MEMBER", str(qtl.relative_to(ROOT)).replace("/", "\\"), "tenk10k_NK_IL12RB2_variant_eqtl", str(qtl.stat().st_size), sha256(qtl), "MEMBER_CRC_VERIFIED_DERIVED_EXTRACT", "R4A12FG4"],
    )
    code_catalog = ROOT / "2_code/CODE_CATALOG.tsv"
    for path in [
        CODE_INTAKE / "download_extract_tenk10k_nk_resume.py",
        CODE_INTAKE / "RUN_R4A12FG4_TENK10K_NK.ps1",
        CODE_ANALYSIS / "harmonize_il12rb2_tenk10k_finngen.py",
        CODE_ANALYSIS / "audit_missing_cs_external_ld.py",
        CODE_ANALYSIS / "run_il12rb2_coloc_abf.R",
        CODE_ANALYSIS / "summarize_il12rb2_coloc.py",
        CODE_ANALYSIS / "RUN_R4A12FG4_SIGNAL_GATE.ps1",
        ROOT / "2_code/09_release/R4A12FG4/build_r4a12fg4_release.py",
        CODE_INTAKE / "requirements-r4a12fg4.txt",
    ]:
        relative = str(path.relative_to(ROOT)).replace("/", "\\")
        append_tsv_if_absent(
            code_catalog,
            relative,
            ["GENERATED_R4A12FG4", relative, "ACTIVE_R4A12FG4_RUNTIME", str(path.stat().st_size), sha256(path), "TESTED", "R4A12FG4"],
        )
    stage_catalog = ROOT / "9.Version/STAGE_CATALOG.tsv"
    append_tsv_if_absent(
        stage_catalog,
        "R4A12FG3\t",
        ["R4A12FG3", str((ROOT / "6_release/history/R4A12FG3/imported_2026-09-13")), "18", "24435", "IMPORTED_AND_AUDITED", "HISTORICAL_ADVISORY_INPUT"],
    )
    report_files = [p for p in REPORT_DIR.rglob("*") if p.is_file()]
    append_tsv_if_absent(
        stage_catalog,
        "R4A12FG4\t",
        ["R4A12FG4", str(REPORT_DIR.relative_to(ROOT)).replace("/", "\\"), str(len(report_files)), str(sum(p.stat().st_size for p in report_files)), "REGISTERED_CURRENT_BOUNDED_BRANCH", "SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED"],
    )


def main() -> None:
    evidence = validate_inputs()
    protocol_paths = build_protocol(evidence)
    coverage_table = make_coverage_table(evidence)
    report_paths = build_reports(evidence)
    release = build_release(report_paths, protocol_paths, coverage_table, evidence)
    validation = final_validate(release)
    if validation["status"] != "PASS":
        raise RuntimeError(validation)
    update_workspace(protocol_paths, release)
    print(
        json.dumps(
            {
                "status": "PASS",
                "reports": str(REPORT_DIR),
                "release_zip": str(release["zip"]),
                "release_sha256": release["zip_sha256"],
                "validation": str(VALIDATION_DIR / "R4A12FG4_FINAL_VALIDATION.json"),
                "next_stage": "R4A12FG5_EXTERNAL_LD_AND_THREE_CELL_REPLICATION_GATE",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
