#!/usr/bin/env python3
"""Write the R7C1 scientific adjudication and action-record reports."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
WORK = ROOT / "5_manuscript/R7C1_IL12RB2_ExternalValidation_ManuscriptFork"
REPORTS = WORK / "reports"
MANUSCRIPT = WORK / "manuscript/R7C1_HumanGenomics_IL12RB2_external_validation_fork.md"
DOCX = WORK / "manuscript/R7C1_HumanGenomics_IL12RB2_external_validation_fork.docx"
PDF = WORK / "manuscript/R7C1_HumanGenomics_IL12RB2_external_validation_fork_WPS.pdf"
FIG4 = WORK / "figures/Figure4_IL12RB2_external_evidence.png"
ADD3 = WORK / "supplement/Additional_file_3_R7C1_External_Validation_Data.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(name: str, body: str) -> None:
    (REPORTS / name).write_text(body.strip() + "\n", encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    hashes = {
        "manuscript_md": sha256(MANUSCRIPT),
        "manuscript_docx": sha256(DOCX),
        "manuscript_wps_pdf": sha256(PDF),
        "figure4_png": sha256(FIG4),
        "additional_file_3": sha256(ADD3),
    }

    write("00_CMM_R7C1_执行摘要_外部验证与稿件分支终裁.md", f"""
# R7C1 执行摘要：IL12RB2 外部验证模块与稿件分支终裁

## 最终裁决

```text
PBC_PRIMARY_PROJECT = GO
R7B4B2_Q2_BASELINE = FROZEN_BYTE_IDENTICAL
R7C1 = PASS_WITH_BOUNDED_SCIENTIFIC_UPGRADE

IL12RB2_NK_EXTERNAL_DISEASE_STUDY_SUPPORT = PASS
SOURCE_CS_AUDIT = PASS_2_OF_2
CHROMATIN_TRIANGLE = PASS_WITHOUT_DIRECT_MEDIATION
OMIX001122 = DESCRIPTIVE_ONLY

NEW_GENE_LOCUS_CELL_FISHING = NO
FULL_642_RERUN = NO
NEW_BIOLOGICAL_ANALYSIS_REQUIRED = NO

NEXT = R7C2_Q1_TARGET_JOURNAL_REALITY_CHECK_AND_DUAL_TRACK_SUBMISSION_PACKAGE
```

R7C1 已把 R7C0 的预设外部证据正式整合进新的英文稿分支，同时保持作者批准的 R7B4B2 Human Genomics 稿件逐字节不变。升级成立的原因不是发现了新的候选基因，而是 IL12RB2–NK 的核心关联现在获得了三个互补层面的支持：原 OneK source-matched 多信号证据、FinnGen R13 不同疾病研究系统中的单因果验证与 source-CS 审计、以及 PBC–eQTL / PBC–caQTL / peak–gene 三角信号一致性。

升级后的证据等级仍为稳健关联，而非机制证明。FinnGen R13 与发现 GWAS 的个体级完全不重叠无法由公开元数据证实；外部验证没有重建第二套 source-LD 多信号模型；直接 eQTL–caQTL 后验和介导估计缺失；OMIX001122 只有一个 PBC 和一个对照矩阵。因此稿件没有使用“独立人群复制”“完整级联”或“介导”表述。

## 关键结果

- FinnGen R12/R13 疾病可信集：19 与 17 个成员；R13 的 17 个成员全部位于 R12 集合中，Jaccard=0.895，PIP 相关 r=0.833。
- FinnGen R13 × OneK NK/IL12RB2：1,175 个 harmonized variants；PP.H4 分别为 0.9772、0.9977、0.9998（p12=10^-6、10^-5、10^-4）。
- OneK QTL source CS 的 2/2 成员均位于 FinnGen R13 疾病 CS。
- 固定 27 基因 CASCADE 审计：22 个有相关广义细胞 eQTL 覆盖，只有 IL12RB2 返回 PBC–eQTL 共定位。
- l1.NK：PBC–IL12RB2 eQTL PP.H4=0.9703；PBC–linked-peak caQTL PP.H4=0.9695；peak–gene link beta=0.141，距 TSS 239 bp。
- OMIX001122 仅支持 IL12RB2/FCRL3 的描述性可检测性，不支持病例对照、供者复制或空间定位推断。

## 交付身份

- Manuscript MD SHA-256: `{hashes['manuscript_md']}`
- Manuscript DOCX SHA-256: `{hashes['manuscript_docx']}`
- WPS PDF SHA-256: `{hashes['manuscript_wps_pdf']}`
- Figure 4 PNG SHA-256: `{hashes['figure4_png']}`
- Additional file 3 SHA-256: `{hashes['additional_file_3']}`
""")

    write("01_CMM_R7C1_数字与来源一致性审计.md", """
# R7C1 数字与来源一致性审计

## 审计方法

每一个 R7C1 新增数字均与 R7C0 冻结 TSV/JSON 机器表进行双向核对。审计不从报告文字反推数字，也不将 Figure 4 的标签作为独立数据源。

## 通过项目

1. FinnGen R12/R13 疾病 CS 身份、大小、交集、Jaccard、lead variant 和 PIP 相关值与 `R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json` 一致。
2. 三档 p12 下的 PP.H4 与 H4/(H3+H4) 与 `R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv` 一致。
3. OneK QTL CS 的 2/2 disease-CS coverage 与 source-CS 成员表一致。
4. 固定 27 基因、22 个相关细胞 eQTL coverage 和唯一 IL12RB2 disease-coloc 结果与 CASCADE 固定表一致。
5. disease–eQTL、disease–caQTL、credible-set sizes、peak–gene beta 与 TSS 距离均与 chromatin adjudication JSON 一致。
6. OMIX 的两个公开矩阵、样本身份和描述性限制与 byte-level QC 表一致。
7. 引用 1–25 连续，正文引用范围 1–25，25/25 均被引用。

## 机器结果

`R7C1_machine_hostile_QA.json`：38/38 PASS，0 FAIL。

R7B4B2 基线 MD、DOCX、WPS PDF 的 SHA-256 分别继续匹配冻结值；R7C1 没有覆盖这些文件。
""")

    write("02_CMM_R7C1_敌意审稿与claim边界.md", """
# R7C1 敌意审稿与 claim 边界

## 统计遗传学审稿视角

最强攻击点是 FinnGen R13 的 795 个病例不足以承担“完全独立、等强度复制”的表述，而且公开信息不能证明与发现 GWAS 在个体层面零重叠。稿件已统一使用 `different disease study system` 和 `external disease-study validation`，并明确保留 overlap 不可证明、样本量较小和 single-causal 模型限制。

第二个攻击点是把 source-CS 交集当作第二套 multi-signal 共定位。稿件明确区分：OneK discovery 层拥有 source-matched LD 和多信号推断；FinnGen R13 层是 single-causal ABF 加 source-CS 审计。没有把两者合并成同一统计层级。

## 调控基因组学审稿视角

最强攻击点是从两个 disease-sharing 边推导 eQTL→caQTL 介导。稿件保留了 direct eQTL–caQTL posterior unavailable，并把结果命名为 triangular signal coherence。虽然 eQTL CS 与 caQTL CS 都是疾病 CS 的子集，但集合重叠不能替代直接 posterior 或方向性介导模型。

固定 CASCADE 审计只覆盖预先冻结的 27 个基因，不能写成全基因组或所有 PBC 位点的多模态扫描。只有 IL12RB2 通过 disease-coloc 层，这一结果支持模块特异性，但不证明 IL12RB2 是唯一效应基因。

## 空间与组织审稿视角

OMIX001122 的公开处理包只有一个 PBC 和一个对照矩阵，没有供者级复制、组织图像坐标或 spot annotation。它不能承担空间验证、病例对照差异或新机制发现。稿件只保留 target detectability，并继续以 HRA008003 五对五 donor-level null enrichment 作为主要组织边界。

## 新颖性判断

R7C1 仍不声称首次发现 IL12RB2。新增价值是把一个已被优先化的基因放入来源匹配、多信号、不同疾病研究系统、可信集和染色质边界共同约束的可靠性框架。该升级能够提高稿件完整性，但尚不足以把文章自动定级为 SCI 一区；期刊层级必须在 R7C2 依据真实 scope、编辑门槛和竞争稿件重新裁决。
""")

    write("03_CMM_R7C1_WPS与发布工程质控.md", f"""
# R7C1 WPS 与发布工程质控

## 文档构建

- DOCX 由冻结 R7B4B2 Markdown 分支构建，包含 6 个图对象、连续页码与连续行号。
- PDF 使用 WPS Writer COM 后台导出，未使用 LibreOffice。
- WPS PDF 共 32 页，Producer/Creator 元数据包含 WPS 标识。
- 32/32 页均以 150 dpi 渲染为 PNG，并通过 8 张四页 contact sheet 完成视觉检查。

## 视觉结果

未发现图像缺失、跨页裁切、文字重叠、超出页边距、图注错配、异常空白页或 Supplementary Table S11 遗失。新的 Figure 4 在最终版面中可读，四个 panel 与图注含义一致。

## 补充包

Additional file 3 含 25 个 ZIP entries，CRC PASS，并带内部 SHA-256 manifest。第三方 raw archive、个体基因型、BAM、pseudobulk 和权限受限资源未被重新分发。

## 文件哈希

- DOCX: `{hashes['manuscript_docx']}`
- WPS PDF: `{hashes['manuscript_wps_pdf']}`
- Figure 4 PNG: `{hashes['figure4_png']}`
- Additional file 3: `{hashes['additional_file_3']}`
""")

    write("04_CMM_R7C1_R7C2下一阶段冻结目标.md", """
# R7C1 → R7C2 下一阶段冻结目标

## 当前状态

```text
R7C1 = COMPLETE_PASS
R7C1_MODULE = RETAIN
R7B4B2_Q2_BASELINE = RETAIN_UNCHANGED
Q1_UPGRADE_TRACK = GO_TO_JOURNAL_FIT_GATE
NEW_BIOLOGICAL_ANALYSIS_REQUIRED = NO
```

## R7C2 唯一目标

`R7C2 — Q1 Target-Journal Reality Check + Dual-Track Submission Package`

R7C2 不再增加基因、位点、细胞或组学层。它只完成：

1. 实时核对候选 SCI 一区期刊的官方 scope、article type、字数、图表、数据代码、AI disclosure、预印本、APC 和投稿文件要求；
2. 用当前证据上限对候选期刊执行编辑拒稿风险审计；
3. 判断 R7C1 是否足以支持一次合理的一期刊升级尝试；
4. 若通过，制作一套目标期刊专用稿件、cover letter、upload map 和 checklist；
5. 若未通过，立即回到已完成的 R7B4B2 Human Genomics 路线，不再追加生物学分析。

## 退出规则

- `Q1_FIT_PASS`：目标期刊明确接收以人类基因组学、统计遗传可靠性和疾病调控归因为核心的计算研究，当前证据链与其编辑门槛相符。
- `Q1_FIT_FAIL_Q2_BASELINE_GO`：如果期刊要求广泛跨疾病方法验证、直接功能机制或更大独立队列，则不为了期刊补做无边界分析，直接采用 R7B4B2/Q2 方案。
- `PROJECT_REDESIGN`：只有发现足以推翻核心方法或数据身份的不可修复问题才触发；R7C1 没有发现此类问题。
""")

    write("99_CMM_R7C1_详细行动记录_2026-10-11.md", f"""
# R7C1 详细行动记录（2026-10-11）

## 1. 任务

按照 RP v4 继续执行已冻结的 `R7C1_IL12RB2_EXTERNAL_VALIDATION_MODULE_AND_MANUSCRIPT_FORK`。要求保留 R7B4B2 投稿基线、只整合预设 IL12RB2–NK 外部证据、完成英文稿、WPS 渲染、敌意审稿、发布工程和下一阶段裁决。写作使用 QiTeng Academic Writing Skill v0.3.24.2，不使用 CC skill。

## 2. 权威与基线

已读取 QiTeng `VERSION_REGISTRY.json` 与 Runtime Core。当前 authority 为 v0.3.24.2；采用 QITENG_Q1、Original Research、claim governor、Methods–Results mirror、hostile-review 和 next-test 规则。

R7B4B2 冻结基线重新核验：

- Markdown SHA-256 `39c3164e572d7957859de71815856cd7b61cb7865caea00ffeb3078ede7a3638`
- DOCX SHA-256 `8dec3207ec695aded22a50ad0646c0b016df27fb28eb333fbd70ca7c35039ff7`
- WPS PDF SHA-256 `c7f55e24936b29add40621ff2b4dd57c28664fb0663ff9a049a810d2e9ab4786`

三者在本轮结束时仍完全匹配。

## 3. Figure 4 重构

旧 Figure 4 的“PBC–caQTL sharing 未建立”已经被 R7C0 的预设 full-region CASCADE 查询所取代。R7C1 在新目录中重建 Figure 4：

- A：FinnGen R12/R13 disease-CS stability；
- B：FinnGen R13 × OneK NK/IL12RB2 三档先验后验；
- C：固定 27 基因 CASCADE coverage；
- D：disease–eQTL、disease–caQTL、peak–gene 三角与缺失 direct eQTL–caQTL posterior。

图标题和 panel B 均避免“独立 cohort”表述；OMIX 边界置于 panel D。

## 4. 英文稿整合

在 R7B4B2 文本基础上形成独立 R7C1 分支。修改范围限于 Abstract、Background 任务句、三段新增 Methods、IL12RB2 Results、Discussion、limitations、next tests、Conclusion、Data availability、References、Figure 4 legend 和 Additional file 3。

新增 Methods：

1. different-disease-study validation and source-CS audit；
2. source-integrated chromatin evidence；
3. descriptive spatial-transcriptomic boundary。

新增 Results 严格报告 1,175 variants、三档 posterior、2/2 source-CS coverage、27→22→1 CASCADE 漏斗、两个 disease-sharing edges 与 239 bp peak–gene link。直接 eQTL–caQTL posterior、participant-level zero overlap 和介导均保留为未证实。

## 5. Supplementary Data

构建 `Additional_file_3_R7C1_External_Validation_Data.zip`，含疾病 CS、外部 coloc、source-CS、固定 CASCADE、chromatin triangle、OMIX QC、source ledger、final state 与 independent QA，共 25 entries。CRC PASS；内部 manifest 存在。

## 6. WPS 文档工程

DOCX 使用 Times New Roman 11 pt、双倍行距、连续行号、页码和六个内嵌图件。WPS Writer 以后台 COM 导出 32 页 PDF。全部 32 页以 150 dpi 渲染并通过 8 张 contact sheets 逐页检查。未使用 LibreOffice。

## 7. 机器与敌意 QA

`R7C1_machine_hostile_QA` 最终为 38/38 PASS。审计覆盖：

- 基线字节不变；
- 每个新增数字与冻结表一致；
- 禁止 independence/mediation/cascade 过度表述；
- 引用 1–25 连续且全部被引用；
- 6/6 图对象、页码、行号；
- WPS 元数据、32/32 页渲染；
- Additional file 3 CRC 与 manifest；
- Figure 4 和读者-facing supplement inventory。

## 8. 结果身份

- Markdown SHA-256: `{hashes['manuscript_md']}`
- DOCX SHA-256: `{hashes['manuscript_docx']}`
- WPS PDF SHA-256: `{hashes['manuscript_wps_pdf']}`
- Figure 4 PNG SHA-256: `{hashes['figure4_png']}`
- Additional file 3 SHA-256: `{hashes['additional_file_3']}`

## 9. 科学终裁

R7C1 通过。升级稿比 R7B4B2 多了一项真实、不同疾病研究系统的 IL12RB2–NK 验证，并补齐了有边界的染色质三角；这足以进入一次正式的 Q1 期刊适配现实检查。它仍不是完整机制论文，也没有充分依据直接放弃已完成的 Q2 基线。

## 10. 下一阶段

冻结为 `R7C2_Q1_TARGET_JOURNAL_REALITY_CHECK_AND_DUAL_TRACK_SUBMISSION_PACKAGE`。R7C2 不运行新的生物学分析；若 Q1 fit 不通过，立即采用 R7B4B2 Human Genomics 投稿路线。

## 11. 发布工程

最终发布包包含 manuscript、6 组图件、3 个 Additional files、协议、代码、结果状态、QA 与本轮报告。ZIP CRC 通过；内部 manifest 覆盖除 manifest 自身外的 48/48 个文件。外部 ZIP SHA-256 由发布目录中的同名 `.sha256` 文件和 `R7C1_release_state.json` 记录，避免在归档内部形成自引用哈希。
""")

    final_state = {
        "stage": "R7C1_IL12RB2_EXTERNAL_VALIDATION_MODULE_AND_MANUSCRIPT_FORK",
        "date": str(date(2026, 10, 11)),
        "R7C1": "COMPLETE_PASS_WITH_BOUNDED_SCIENTIFIC_UPGRADE",
        "PBC_PRIMARY_PROJECT": "GO",
        "R7B4B2_Q2_BASELINE": "FROZEN_BYTE_IDENTICAL_SUBMISSION_READY",
        "IL12RB2_external_disease_study": "PASS_FINNGEN_R13_X_ONEK_SINGLE_CAUSAL_WITH_SOURCE_CS",
        "chromatin": "PASS_TRIANGULAR_SIGNAL_COHERENCE_WITHOUT_DIRECT_MEDIATION",
        "OMIX001122": "DESCRIPTIVE_ONLY_NOT_INDEPENDENT_SPATIAL_VALIDATION",
        "new_biological_analysis_required": False,
        "new_gene_locus_cell_fishing": False,
        "full_642_rerun": False,
        "qa": {"pass": 38, "fail": 0, "total": 38},
        "wps_pdf_pages": 32,
        "hashes": hashes,
        "NEXT": "R7C2_Q1_TARGET_JOURNAL_REALITY_CHECK_AND_DUAL_TRACK_SUBMISSION_PACKAGE",
        "R7C2_exit_rule": "Attempt a Q1-specific package only if current official scope and editor-facing novelty fit pass; otherwise submit the unchanged Q2 baseline without additional biological analysis.",
    }
    (WORK / "results/R7C1_final_state.json").write_text(json.dumps(final_state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(final_state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
