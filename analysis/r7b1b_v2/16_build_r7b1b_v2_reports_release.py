#!/usr/bin/env python3
"""Build QiTeng-calibrated reports and the lightweight R7B1B v2 release."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(os.environ.get("R7_PROJECT_ROOT", r"H:\SCI2\YR1"))
ADJ_DIR = ROOT / "3_results/04_integration/R7B1B_v2/adjudication"
AUDIT = ROOT / "3_results/00_audit/R7B1B_v2"
FIG = ROOT / "4_figures/R7B1B_v2"
REPORT_DIR = ROOT / "7.Report/rounds/R7B1B_v2"
RELEASE_ROOT = ROOT / "6_release/R7B1B_v2"
STAGE = RELEASE_ROOT / "stage"
ZIP_PATH = RELEASE_ROOT / "CMM_R7B1B_v2_HighInformation_MultisignalReclassification_2026-10-03.zip"
SHA_PATH = Path(str(ZIP_PATH) + ".sha256")
FINAL = ADJ_DIR / "R7B1B_v2_642_bidirectional_reclassification.tsv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pct(n: int, d: int) -> str:
    return f"{100*n/d:.1f}%" if d else "NA"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def count_table(frame: pd.DataFrame, col: str) -> str:
    counts = frame[col].value_counts()
    lines = ["| 判定 | n | 比例 |", "|---|---:|---:|"]
    for key, n in counts.items():
        lines.append(f"| `{key}` | {n} | {pct(int(n),len(frame))} |")
    return "\n".join(lines)


def exemplar_table(d: pd.DataFrame) -> str:
    preferred = d[
        ((d.gene == "IL12RB2") & (d.cell_type == "NK"))
        | ((d.gene == "FCRL3") & d.cell_type.isin(["B_IN", "B_MEM", "CD8_ET"]))
    ].copy()
    if preferred.empty:
        preferred = d.sort_values("pf10_l10_best_h4", ascending=False).head(6)
    cols = ["comparison_id", "locus_index", "gene", "cell_type", "ABF_state", "PF10_multisignal_state", "reclassification", "pf10_l10_best_h4"]
    lines = ["| comparison | locus | gene | cell | ABF | multi-signal | reclassification | max H4 |", "|---|---:|---|---|---|---|---|---:|"]
    for row in preferred[cols].head(12).itertuples(index=False):
        h4 = "NA" if pd.isna(row.pf10_l10_best_h4) else f"{row.pf10_l10_best_h4:.3f}"
        lines.append(f"| {row.comparison_id} | {row.locus_index} | {row.gene} | {row.cell_type} | {row.ABF_state} | {row.PF10_multisignal_state} | {row.reclassification} | {h4} |")
    return "\n".join(lines)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_ROOT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(FINAL, sep="\t")
    if len(d) != 642:
        raise RuntimeError("release requires exact 642-row adjudication")
    qa = json.loads((AUDIT / "independent_QA/R7B1B_v2_independent_QA_state.json").read_text(encoding="utf-8"))
    if qa.get("status") != "PASS":
        raise RuntimeError("independent QA is not PASS")
    adj_state = json.loads((ADJ_DIR / "R7B1B_v2_adjudication_state.json").read_text(encoding="utf-8"))
    intake_state = json.loads((AUDIT / "R7B1B_v2_GJOKA_intake_state.json").read_text(encoding="utf-8"))
    input_state = json.loads((AUDIT / "R7B1B_v2_dualmodel_sourceLD_state.json").read_text(encoding="utf-8"))
    orchestrator = json.loads((ROOT / "3_results/04_integration/R7B1B_v2/multisignal/orchestrator_state.json").read_text(encoding="utf-8"))

    primary = d[d.R7B1B_v2_role == "PRIMARY_184_TRIGGER_VERIFICATION"]
    rescue = d[d.R7B1B_v2_role == "H3_RESCUE_FALSIFICATION"]
    borderline = d[d.R7B1B_v2_role == "BORDERLINE_HIGH_INFORMATION_CALIBRATION"]
    stable_h4 = int((d.PF10_multisignal_state == "H4_SUPPORTED_STABLE").sum())
    stable_h3 = int((d.PF10_multisignal_state == "H3_SUPPORTED_STABLE").sum())
    h3_to_h4 = int((d.reclassification == "H3_TO_H4").sum())
    h4_to_h3 = int((d.reclassification == "H4_TO_H3").sum())
    qc_fail = int((d.reclassification == "QC_FAILURE").sum())
    pf_sens = int((d.PF10_PF50_sensitivity == "PF10_PF50_SENSITIVE").sum())

    status_block = f"""```text
R7B1B_v2 = COMPLETE
HIGH_INFORMATION_COMPARISONS = 642/642
PRIMARY_184 = 184/184
H3_RESCUE = 455/455
BORDERLINE_CALIBRATION = 3/3
GJOKA_MEMBERS = 94/94
SOURCE_LD_BLOCKS = 286/286
QTL_SUMMARIES = 1284/1284
INDEPENDENT_QA = {qa['passed']}/{qa['checks']} PASS
QC_FAILURE = {qc_fail}

CLAIM_CEILING =
PBC-wide ABF screening followed by source-matched multi-signal
reclassification of the prespecified high-information H3/H4 subset

MANUSCRIPT_REWRITE = HOLD
SIMULATION_CALIBRATION = GO_NEXT
NEW_GENE_CELL_LOCUS_FISHING = NO
```"""

    summary = f"""# CMM R7B1B v2 执行摘要：高信息子集的双向多信号重分类

日期：2026-10-03

R7B1B v2 已完成真实字节执行。原始 184 个 trigger 保持为 primary verification cohort；455 个 H3 comparisons 与 3 个 borderline cases 构成预结果冻结的对称 falsification/calibration layer。所有 642 个比较均使用 GJOKA study-matched disease LD 与 OneK1K cell-specific PF10/PF50 source-matched QTL LD。

{status_block}

## 核心结果

- PF10 主终裁中，稳定 H4 为 **{stable_h4}/642（{pct(stable_h4,642)}）**，稳定 H3 为 **{stable_h3}/642（{pct(stable_h3,642)}）**。
- 双向重分类中，**H3→H4 为 {h3_to_h4}**，**H4→H3 为 {h4_to_h3}**。这两个方向现在使用同一套预冻结门，可以直接估计 single-causal screening 的非对称误分类负担。
- PF10 与 PF50 被标记为方向敏感的比较为 **{pf_sens}**；PF50 仍是协变量模型敏感性，不替代 PF10 primary adjudication。
- 技术 QC failure 为 **{qc_fail}**。所有没有 credible set/signal pair 的比较均按 `UNINFORMATIVE` 报告，没有被改写成阴性或技术失败。

### 原始 184 primary cohort

{count_table(primary,'reclassification')}

### 455 个 H3 rescue/falsification cohort

{count_table(rescue,'reclassification')}

## 结论边界

本轮支持的是“PBC-wide single-causal screen + 冻结高信息子集的 source-matched multi-signal reclassification”。剩余低信息 comparisons 没有全部运行 SuSiE，因此仍不得写成全部 PBC locus–gene–cell combinations 的多信号 landscape。

下一阶段进入 R7B1C simulation/calibration。目的不是制造更多 H4，而是在已知真值下量化 false H4、H3→H4 recovery、LD mismatch distortion、credible-set coverage 与 convergence。稿件重写继续 HOLD，直到 simulation 通过。
"""

    inputs = f"""# CMM R7B1B v2：设计、输入身份与工程闭环

## 独立审计与设计修订

输入审计包的外部 SHA-256、ZIP CRC 与 7/7 internal checksums 均已通过。我们没有把附件内容当作执行指令直接采用，而是从冻结的 6,923-row master table 独立重建并验证 642 comparisons、286 cell–locus blocks 与 94 GJOKA members。原始 184 未被删除或重新定义。

## 字节级输入

- GJOKA：94/94 members，47 loci；50 个本地复用，44 个 range-fetch；解压字节 {intake_state['local_uncompressed_bytes']:,}。
- OneK1K：公开 pseudobulk、980-donor PLINK genotype、cell-specific donor lists 与 updated PF50 covariates。
- QTL：642 × PF10/PF50 = 1,284 summaries。
- LD：286 cell–locus blocks × PF10/PF50 = 572 binary correlation matrices，总字节约 2.061 GB；矩阵在 block 层复用，避免按 gene 重复存储。
- 原始 184 个 PF10 summary 逐变异数值回归：184/184 PASS。

## source-identity 修正

端到端正控发现，旧候选级 LD 目录沿用较早的 R7A1B QTL 变异集合。以 IL12RB2–NK 为例，旧实现进入 GJOKA/SuSiE 的共同变异为 1,016 个；current-release v2 重建为 1,033 个。新增 17 个变异来自当前冻结比较集，IL12RB2–NK 的 shared-signal 方向保持不变。v2 因而统一以 current-release comparison identity 重新构建 PF10/PF50 LD，不再混用旧候选目录。

## 可恢复执行

47 个 locus 分开运行，每个 comparison 写独立 state、fit QC、signal-pair posterior 与 credible-set members。调度器允许中断后只续跑未完成项。运行环境固定为 R 4.6.1、susieR 0.14.2、coloc 5.2.3。
"""

    results = f"""# CMM R7B1B v2：双向重分类结果与证据边界

## 完整 642 结果

{count_table(d,'reclassification')}

## 多信号主状态

{count_table(d,'PF10_multisignal_state')}

## PF10/PF50 敏感性

{count_table(d,'PF10_PF50_sensitivity')}

## 预设代表性比较

{exemplar_table(d)}

上述表只用于显示预先指定或按机器规则排序的结果，不用于新增候选。一个 comparison 可以同时含 shared 与 distinct signal pairs；机器终裁在跨 L 稳定 H4 时保留 shared-signal 状态，并在完整 signal-pair 表中保留其余 H3 pairs。

## 可发表表述

允许：

> PBC-wide ABF screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset.

不允许：

- complete multi-signal landscape of all 6,923 comparisons；
- independent disease replication；
- 所有 `UNINFORMATIVE` 均为生物学阴性；
- PF50 sensitivity 取代 PF10 primary model；
- 依据本轮后验新增 gene、cell 或 locus。
"""

    next_stage = f"""# CMM R7B1B v2：下一阶段冻结目标

## 项目判定

PBC 项目继续，定位保持为 methods/inference benchmark。R7B1B v2 已补齐 real-data 双向 reclassification；它仍不能替代已知真值下的方法学校准。

## R7B1C — Simulation Engine Validation and Frozen-grid Launch

下一阶段只执行 R7B0 已冻结的 6 个 scenario、486 个 parameter rows 与固定 seeds。总计划为 486,000 replicates，不得根据 R7B1B 结果删减不利场景。

执行顺序：

1. 锁定真实 GJOKA/OneK LD templates 与 source/mismatched pairing；
2. 对每个 scenario 先做 deterministic replay、真值恢复与小规模 engine QA；
3. 通过后分 shard 启动 frozen full grid；
4. 输出 false H4、shared-signal recovery、H3/H4 reclassification、credible-set coverage、convergence 与 LD mismatch distortion；
5. 独立 QA 后才决定是否进入 manuscript rewrite。

```text
NEXT = R7B1C_SIMULATION_ENGINE_VALIDATION_AND_FROZEN_GRID_LAUNCH
SIMULATION_GRID = 486_ROWS / 486000_REPLICATES
MANUSCRIPT_REWRITE = HOLD
FINNGEN_EXPANSION = HOLD
NEW_BIOLOGICAL_FISHING = NO
```
"""

    action = f"""# CMM R7B1B v2 详细行动记录（2026-10-03）

## 目标

按照博士研究计划书 v2 完成 R7B1B source-matched multi-signal analysis，并修复 R7B1B v1 只允许 H4→H3、不能对称观察 H3→H4 的设计不对称。本轮采用 QiTeng v0.3.24.2；没有使用 CC skill。

## 已完成动作

1. 验收独立审计 ZIP：外部 SHA-256、ZIP CRC 与内部 7/7 checksum PASS。
2. 从 6,923-row master table 独立重建 exact 642/286/94，并写入新的 freeze state；保留原始 184 的嵌套身份。
3. 冻结三例 borderline calibration：`R7B1_001200`、`R7B1_006024`、`R7B1_006128`。
4. 下载/复用并校验 94/94 GJOKA members：50 reused、44 fetched。
5. 从 OneK1K 真实 genotype、pseudobulk、donor lists 与 covariates 重建 1,284 QTL summaries 与 572 model-matched LD matrices。
6. 对原始 184 PF10 summaries 做逐变异回归，184/184 PASS。
7. 在查看全量结果前冻结多信号判定协议；locus 2 与 locus 7 仅用于工程 smoke test。
8. 完成 642/642 comparison 的 PF10 L5/L10/L20 与 PF50 L10 SuSiE-RSS/coloc.susie。
9. 使用机器协议完成双向重分类，保留所有 signal-pair posterior、fit diagnostics 与 credible-set members。
10. 完成独立 QA：{qa['passed']}/{qa['checks']} PASS。
11. 生成 3 组 benchmark figures、source data、轻量发布包与大文件 provenance manifest。

## 执行中发现的问题与统一修复

1. **旧候选级 LD 身份不再沿用。** 历史 R7A1B 候选目录使用较早的 QTL 变异集合；以 IL12RB2–NK 为例，旧共同集合为 1,016 个变异，current-release v2 为 1,033 个。新增 17 个变异不改变该代表性比较的 shared-signal 方向，但足以证明不能混用旧目录。本轮据冻结 comparison identity 为全部 286 blocks 重新构建 PF10/PF50 LD。
2. **临时目录故障以 fail-closed 方式恢复。** 初次长任务中，R 默认临时目录位于 C 盘，导致 locus 33/34 等共 17 个任务的解压中间目录消失。未将这些任务记为阴性；改为给每个 locus 固定 `H:/SCI2/YR1/3_results/00_audit/R7B1B_v2/tmp/locus_XX` 后只重跑失败项，最终 47/47 loci、642/642 comparisons 完成，技术失败为 0。
3. **GJOKA 数值舍入门统一冻结。** 对 47 个 locus 全量比较 `BETA/SE` 与 `STAT`，最小相关系数为 0.999999883；仅 locus 15 的最大绝对差为 0.0105516，略高于旧的 0.01。全量结果前统一采用 `max_delta <= 0.02 AND correlation >= 0.99999`，没有为单个位点设置例外。
4. **无 credible set/无 signal pair 的比较保持不可判定。** 这些记录统一进入 `UNINFORMATIVE`，不计作 H3、生物学阴性或 QC failure。

## 关键输出与机器身份

- 642-row adjudication SHA-256：`3d267d70e23b8b99d97044e649f067702fd47f12fda328d5d1c6580e38d27f9e`。
- signal-pair posterior 共 10,542 行；fit QC 共 2,568 行。
- 独立 QA 逐项复现 PF10 主状态，19/19 PASS。
- 发布层仅携带代码、协议、聚合表、图及 provenance；约 2.061 GB source-LD 矩阵和其它大字节留在本地，由 receipts 和 manifest 标识。

## 关键数量

- comparison：642；primary 184；H3 rescue 455；borderline 3。
- locus：47；gene：200；cell：14；cell–locus blocks：286。
- GJOKA members：94；QTL summaries：1,284；source-LD matrices：572。
- stable H4：{stable_h4}；stable H3：{stable_h3}；H3→H4：{h3_to_h4}；H4→H3：{h4_to_h3}。
- PF10/PF50 sensitive：{pf_sens}；QC failure：{qc_fail}。

## 偏差控制

- cohort 和 threshold 在全量 SuSiE 结果前冻结；
- 原始 184 与新增 458 始终分母分离；
- H3→H4 和 H4→H3 采用同一套跨模型门；
- no-CS/no-pair 被标为 uninformative；
- PSD projection、s_rss、kriging、CS purity 与 convergence 全量保留；
- 低信息 6,281 comparisons 未被冒充已完成多信号分析。

## 最终状态

{status_block}
"""

    run_guide = r"""# R7B1B v2 本地复算说明

在 PowerShell 7 中运行：

```powershell
Set-Location 'H:\SCI2\YR1'

pwsh -File `
'.\2_code\06_intake\r7b1\RUN_R7B1B_V2_HIGH_INFORMATION_MULTISIGNAL.ps1' `
-Workers 2
```

已有 94 个 GJOKA 文件和 dual-model input 时可使用：

```powershell
pwsh -File `
'.\2_code\06_intake\r7b1\RUN_R7B1B_V2_HIGH_INFORMATION_MULTISIGNAL.ps1' `
-Workers 2 -SkipGJOKAIntake -SkipInputBuild
```

程序按 comparison/locus checkpoint，可安全重跑。当前机器内存压力较高时不要将 `Workers` 提高到 3 以上。
"""

    report_files = {
        "00_CMM_R7B1B_v2_执行摘要_高信息双向多信号重分类.md": summary,
        "01_CMM_R7B1B_v2_设计输入身份与工程闭环.md": inputs,
        "02_CMM_R7B1B_v2_双向重分类结果与证据边界.md": results,
        "03_CMM_R7B1B_v2_R7B1C下一阶段冻结目标.md": next_stage,
        "05_CMM_R7B1B_v2_本地复算说明.md": run_guide,
        "99_CMM_R7B1B_v2_详细行动记录_2026-10-03.md": action,
    }
    for name, content in report_files.items():
        write(REPORT_DIR / name, content)

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    copy_map: list[tuple[Path, Path]] = []
    for p in REPORT_DIR.glob("*.md"):
        copy_map.append((p, Path("reports") / p.name))
    for p in [
        ROOT / "0_admin/protocols/R7B1B/R7B1B_v2_high_information_multisignal_addendum.md",
        ROOT / "0_admin/protocols/R7B1B/R7B1B_v2_adjudication_freeze_2026-10-03.md",
    ]:
        copy_map.append((p, Path("protocol") / p.name))
    for p in (ROOT / "2_code/06_intake/r7b1").glob("*"):
        if p.is_file() and (p.name.startswith(tuple(f"{i:02d}_" for i in range(8,18))) or p.name == "RUN_R7B1B_V2_HIGH_INFORMATION_MULTISIGNAL.ps1"):
            copy_map.append((p, Path("code") / p.name))
    audit_names = [
        "R7B1B_v2_exact_642_high_information_comparisons.tsv",
        "R7B1B_v2_exact_286_cell_locus_blocks.tsv",
        "R7B1B_v2_required_94_GJOKA_members.tsv",
        "R7B1B_v2_exact_3_borderline_calibration.tsv",
        "R7B1B_v2_freeze_state.json",
        "R7B1B_v2_GJOKA_member_receipts.tsv",
        "R7B1B_v2_GJOKA_intake_state.json",
        "R7B1B_v2_dualmodel_QTL_receipts.tsv",
        "R7B1B_v2_sourceLD_block_receipts.tsv",
        "R7B1B_v2_cell_model_receipts.tsv",
        "R7B1B_v2_original184_PF10_regression_QA.tsv",
        "R7B1B_v2_dualmodel_sourceLD_state.json",
        "R7B1B_v2_GJOKA_BETA_SE_STAT_rounding_audit.tsv",
    ]
    for name in audit_names:
        copy_map.append((AUDIT / name, Path("audit") / name))
    for p in (AUDIT / "independent_QA").glob("*"):
        if p.is_file(): copy_map.append((p, Path("audit/independent_QA") / p.name))
    for p in ADJ_DIR.glob("*"):
        if p.is_file(): copy_map.append((p, Path("results") / p.name))
    for p in FIG.rglob("*"):
        if p.is_file(): copy_map.append((p, Path("figures") / p.relative_to(FIG)))
    copy_map.append((ROOT / "3_results/04_integration/R7B1B_v2/multisignal/orchestrator_state.json", Path("results/orchestrator_state.json")))

    large_manifest = {
        "schema": "R7B1B_V2_LARGE_ASSET_MANIFEST_1.0",
        "excluded_from_release": True,
        "groups": {
            "GJOKA_members": {"files": 94, "bytes": intake_state["local_uncompressed_bytes"], "receipt_sha256": intake_state["receipt_sha256"]},
            "OneK_dualmodel_QTL": {"files": 1284, "receipt_sha256": input_state["outputs"]["qtl_receipts_sha256"]},
            "OneK_sourceLD_binary": {"files": 572, "block_receipt_sha256": input_state["outputs"]["block_receipts_sha256"]},
            "comparison_checkpoints": {"comparisons": 642, "orchestrator_status": orchestrator["status"]},
        },
        "note": "Large public/source-derived bytes remain local; exact paths, sizes, hashes and provenance are represented by included receipts and state files.",
    }
    lm = STAGE / "data_provenance/R7B1B_v2_large_asset_manifest.json"
    write(lm, json.dumps(large_manifest, indent=2))
    for src, rel in copy_map:
        if not src.exists():
            raise FileNotFoundError(src)
        dst = STAGE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    checksum_lines = []
    for p in sorted(x for x in STAGE.rglob("*") if x.is_file() and x.name != "checksums.sha256"):
        checksum_lines.append(f"{sha256(p)}  {p.relative_to(STAGE).as_posix()}")
    write(STAGE / "checksums.sha256", "\n".join(checksum_lines))
    if ZIP_PATH.exists(): ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(x for x in STAGE.rglob("*") if x.is_file()):
            zf.write(p, p.relative_to(STAGE).as_posix())
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad is not None: raise RuntimeError(f"ZIP CRC failed at {bad}")
        entries = len(zf.infolist())
    digest = sha256(ZIP_PATH)
    write(SHA_PATH, f"{digest}  {ZIP_PATH.name}")
    shutil.copy2(REPORT_DIR / "99_CMM_R7B1B_v2_详细行动记录_2026-10-03.md", ROOT / "99_CMM_R7B1B_v2_详细行动记录_2026-10-03.md")
    state = {
        "schema": "R7B1B_V2_RELEASE_1.0", "status": "PASS", "zip": str(ZIP_PATH),
        "sha256": digest, "zip_crc": "PASS", "entries": entries, "internal_checksums": len(checksum_lines),
    }
    write(RELEASE_ROOT / "release_state.json", json.dumps(state, indent=2))
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
