#!/usr/bin/env python3
"""Build the frozen R5A2A2 reports, state, and R5A2A3 protocol from audits."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
REPORT_DIR = ROOT / "7.Report/current/R5A2A2"
ROUND_DIR = ROOT / "7.Report/rounds/R5A2A2"
AUDIT_DIR = ROOT / "3_results/00_audit/R5A2A2"
QTL_DIR = ROOT / "3_results/03_qtl/R5A2A2"
GWAS_DIR = ROOT / "3_results/01_gwas/R5A2A2"
INTEGRATION_DIR = ROOT / "3_results/04_integration/R5A2A2"
PROTOCOL_DIR = ROOT / "0_admin/protocol/current"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def markdown_table(rows: list[list[object]], headers: list[str]) -> str:
    def clean(value: object) -> str:
        if isinstance(value, float):
            return f"{value:.6g}"
        return str(value).replace("|", "\\|")
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(clean(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ROUND_DIR.mkdir(parents=True, exist_ok=True)

    archive = read_json(AUDIT_DIR / "OneK1K_archive_intake_audit.json")
    genotype = read_json(AUDIT_DIR / "OneK1K_genotype_extraction_audit.json")
    qtl = read_json(AUDIT_DIR / "OneK1K_chr18_schema_usability_audit.json")
    gwas = read_json(AUDIT_DIR / "MG_GRCh37_chr18_harmonization_audit.json")
    readiness = read_json(AUDIT_DIR / "OneK1K_chr18_coloc_input_readiness.json")
    sample_manifest = pd.read_csv(QTL_DIR / "OneK1K_chr18_cell_sample_manifest.tsv", sep="\t")
    gene_summary = pd.read_csv(QTL_DIR / "OneK1K_chr18_cell_gene_summary.tsv", sep="\t")
    overlap = pd.read_csv(INTEGRATION_DIR / "OneK1K_chr18_coloc_input_manifest.tsv", sep="\t")

    gene_best = gene_summary.loc[gene_summary.groupby("phenotype_id")["top_pval_nominal"].idxmin()].copy()
    gene_best = gene_best.sort_values("top_pval_nominal")
    gene_best_rows = [[
        row.phenotype_id,
        row.cell_type,
        int(row.n_expression_donors),
        row.top_variant,
        float(row.top_pval_nominal),
        float(row.top_slope_A1),
        int((gene_summary.phenotype_id == row.phenotype_id).sum()),
    ] for row in gene_best.itertuples()]
    gene_best_table = markdown_table(
        gene_best_rows,
        ["archive phenotype", "最佳 cell", "N", "窗口 top eQTL", "P", "A1 slope", "可检验 cells"],
    )

    sample_rows = [[
        row.cell_type, int(row.expression_analysis_donors), int(row.covariate_rows),
        bool(row.first_five_expression_NA_masks_identical), bool(row.sample_interface_pass),
    ] for row in sample_manifest.itertuples()]
    sample_table = markdown_table(sample_rows, ["cell", "实际表达 donors", "covariate 行", "NA mask 稳定", "接口"])

    gwas_rows = []
    lead_rows = []
    for result in gwas["traits"]:
        counts = result["counts"]
        lead = result["lead_rs7239261"]
        gwas_rows.append([
            result["accession"], result["trait"], f"{result['source_bytes']:,}",
            f"{counts['all_data_rows']:,}", f"{counts['fixed_window_rows']:,}",
            f"{counts['position_in_OneK1K_BIM']:,}", f"{counts['inference_eligible_rows']:,}",
            f"{counts['inference_excluded_rows']:,}", result["md5_pass"],
        ])
        lead_rows.append([
            result["trait"], lead["GWAS_effect_allele"], lead["BIM_A1_effect_allele"],
            float(lead["odds_ratio_GWAS_effect"]), float(lead["beta_logOR_A1"]),
            float(lead["standard_error"]), float(lead["p_value"]), float(lead["EAF_A1"]),
            float(lead["oneK1K_AF_A1_980"]), float(lead["frequency_difference"]),
        ])
    gwas_table = markdown_table(gwas_rows, [
        "accession", "trait", "bytes", "全文件行", "窗口行", "BIM 匹配", "可推断", "排除", "MD5",
    ])
    lead_table = markdown_table(lead_rows, [
        "trait", "GWAS EA", "OneK A1", "OR", "beta_A1", "SE", "P", "EAF_A1", "OneK AF_A1", "|ΔAF|",
    ])

    overlap_gene = overlap.groupby("phenotype_id").agg(
        cells=("cell_type", "size"),
        min_shared=("EOMG_LOMG_shared_with_qtl", "min"),
        max_shared=("EOMG_LOMG_shared_with_qtl", "max"),
        all_pass=("ABF_input_gate_pass", "all"),
    ).reset_index().sort_values("phenotype_id")
    overlap_table = markdown_table(
        [[r.phenotype_id, int(r.cells), int(r.min_shared), int(r.max_shared), bool(r.all_pass)] for r in overlap_gene.itertuples()],
        ["phenotype", "cells", "每对最少 EOMG∩LOMG∩QTL", "最多", "ABF 输入门"],
    )

    write(REPORT_DIR / "00_CMM_R5A2A2_执行摘要_OneK1K_chr18输入闭环.md", f"""
# CMM R5A2A2 执行摘要：OneK1K chr18 输入闭环

日期：2026-09-14  
项目：Myasthenia gravis，EOMG vs LOMG  
阶段状态：`R5A2A2_COMPLETE_INPUT_GATE_PASS`  
下一阶段：`R5A2A3_CHR18_COLOC_ABF_SMOKE_AND_LD_TRIGGER = GO`

## 最终判定

R5A2A2 已把 chr18 / rs7239261 从“文件已经下载”推进到“可以启动信号级检验”的状态。OneK1K 10.34 GB raw cis-eQTL、980-donor genotype、pseudobulk 样本接口，以及 MG overall、EOMG、LOMG 三套同 build 疾病统计量全部通过字节、结构、等位基因和区域共同覆盖门。

关键输入规模如下：

- raw eQTL archive：`10,344,009,571` bytes，官方 MD5 `e42239480f40abd21f221c0d77c82cc3` 与实际值一致；
- 14 个 chr18 Parquet 共 `8,959,978` 个 QTL pairs；固定 chr18:59,005,046–61,005,046 区域有 `241,650` pairs、8 个 archive phenotype、71 个 cell–gene 组合；
- 三套 GRCh37 GWAS 分别得到 `3,854`、`4,153`、`2,596` 个可推断的 OneK1K BIM 匹配变异；三套共同变异为 `2,497`；
- 71/71 个 cell–gene 组合均有至少 `1,124` 个 EOMG∩LOMG∩QTL 共同变异，并且 rs7239261 在所有必要输入中存在。

因此，`INPUT_CLOSURE = PASS`，`SAMPLE_INTERFACE = PASS`，`ALLELE_INTERFACE = PASS`，`ABF_INPUT_GATE = PASS`。MG 主项目保持 `CONDITIONAL GO`。

## 科学边界

本轮没有执行 disease–eQTL colocalization，因此没有产生效应基因结论。PIGN/Mono_NC、KIAA1468/Mono_NC、ZCCHC2/CD4_NC 等只是窗口内最小 nominal eQTL P 的排序；rs7239261 本身在候选基因中的 eQTL P 也不能替代区域共享信号检验。TNFRSF11A 只在 5 个细胞类型中有可用表型，其他细胞的缺失属于不可测试，不能写成阴性。

下一阶段先对 3 个疾病表型 × 71 个 cell–gene 组合运行冻结的 coloc.abf smoke gate。LOMG 是主检验，overall MG 是疾病信号复核，EOMG 是亚型对照。只有出现共享信号或可解决的 H3/H4 歧义，才为相应 cell–gene 生成 source-matched LD 并进入多信号分析；否则 chr18 在充分覆盖下失败，并按既定顺序只转 chr5。
""")

    write(REPORT_DIR / "01_CMM_R5A2A2_OneK1K_10GB归档与基因型字节审计.md", f"""
# CMM R5A2A2：OneK1K 10 GB 归档与基因型字节审计

## raw cis-eQTL archive

- 文件：`1_data/qtl/OneK1K/OneK1K_TensorQTL_raw_eQTL_summary.tar.gz`
- bytes：`10,344,009,571`
- MD5：`e42239480f40abd21f221c0d77c82cc3`，与 Zenodo 官方记录一致；
- SHA-256：`63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea`；
- tar members：622；其中科学成员 311、AppleDouble metadata 311；
- 科学 Parquet：308，即 14 cells × 22 chromosomes；
- 真实 chr18 Parquet：14/14，外加 README 与 BIM，共提取 16 个对象、408,104,922 bytes。

AppleDouble 成员只从科学成员选择中排除；完整 archive 仍被顺序读取并参与哈希。这个处理不改变原文件，也没有把 metadata 文件误当成第二份 QTL 数据。

## genotype

OneK1K genotype ZIP 的官方 MD5 已在 R5A2A 通过。本轮把 3 个真实 PLINK 成员解出到规范数据目录：BED/BIM/FAM 合计 `1,461,094,883` bytes；FAM 为 980 个唯一 donors，BIM 为 5,326,925 个唯一 variant IDs，BED magic 表明 SNP-major PLINK v1。

raw eQTL archive 内的 `plink_merged.bim` 与 genotype ZIP 的 BIM 逐字节相同，大小 `155,979,658` bytes，SHA-256 `6e28edad34d5930ca99f7be873e4684a885e26433d13ddba3d970bb8f8ad0bb6`。这使 Parquet `variant_id`、BIM 顺序和 BED offset 构成同一可验证接口。

## 代码级方向定义

官方 OneK1K TensorQTL 脚本通过 `PlinkReader` 载入 PLINK，TensorQTL 当前 `genotypeio.py` 明确执行 `self.bed = 2 - self.bed`。结合 3,655 个跨 14 cells 的 BED 重算，本轮确认：

- Parquet `af` 与 `slope` 对应 BIM `A1`；
- `ma_count` 与 `ma_samples` 对应较小频率等位基因；当 A1 AF>0.5 时，它们对应 A2，而不是 A1；
- 3,655/3,655 行的 minor allele count、carrier count 和 A1 AF 均精确复现。

因此下游效应统一方向冻结为 OneK1K BIM A1。
""")

    write(REPORT_DIR / "02_CMM_R5A2A2_样本接口_ParquetSchema与等位基因审计.md", f"""
# CMM R5A2A2：样本接口、Parquet schema 与等位基因审计

## schema

14 个 chr18 Parquet 的 schema 完全一致：`phenotype_id:string`、`variant_id:string`、`tss_distance:int32`、`af:float`、`ma_samples:int32`、`ma_count:int32`、`pval_nominal:double`、`slope:float`、`slope_se:float`。每个文件只有一个 row group；统计量范围、有限性、正 SE、variant–BIM 映射和 phenotype TSS 一致性全部通过。

## 样本接口的纠正

更新版 covariate 文件不能单独定义每个 cell 的实际 QTL donors。例如 CD4_SOX4 有 857 行 covariate，但 raw QTL 的计数只对应 295 donors；Plasma 为 795 对 253。继续把 covariate 全部行当作 LD 样本会产生错误频率和 LD。

本轮从官方 pseudobulk mean matrices 的 donor 列读取每个 cell 的非 `NA` mask，并检查前 5 个基因的 mask 完全一致。得到的 active donor 集合全部存在于 FAM 和相应 covariate 文件；用这些 donor 重新读取 BED 后，QTL 的 `af/ma_count/ma_samples` 精确复现。因此 cell-specific source LD 的样本列表已经明确。

{sample_table}

`pseudobulk_matrix_columns` 中还包括非 donor 标识列，所以报告的“实际表达 donors”以非 NA donor ID 为准。
""")

    write(REPORT_DIR / "03_CMM_R5A2A2_chr18区域基因与QTL可测性.md", f"""
# CMM R5A2A2：chr18 区域基因与 QTL 可测性

固定区域为 GRCh37 chr18:59,005,046–61,005,046，以 rs7239261 `18:60005046:A:C` 为中心。14 个 cell 文件共提供 8,959,978 个 chr18 QTL pairs；区域提取后为 241,650 pairs、8 个 archive phenotype、71 个 cell–gene 组合。

{gene_best_table}

表中每个基因只展示跨 cells 最小 nominal P 的组合，用于确认存在可分析的区域形状，不用于指定疾病效应基因。KIAA1468 是源 archive 使用的 phenotype 名称；后续报告可同时标注当前基因符号 RELCH，但机器键保持 KIAA1468，避免静默改名。

TNFRSF11A 出现在 CD4_NC、CD8_ET、CD8_NC、NK、NK_R 五个细胞类型。它在其他细胞没有 phenotype 行，因此那些组合不进入失败计数。rs7239261 在所有 71 个已存在的 cell–gene 组合中都有 QTL 记录，但单点 nominal 关联普遍不足以判断共享因果信号。
""")

    write(REPORT_DIR / "04_CMM_R5A2A2_MG_GRCh37协调与共定位准备度.md", f"""
# CMM R5A2A2：MG GRCh37 协调与共定位准备度

## 原始疾病输入

为避免把 GRCh38 harmonised GWAS 再映射回 OneK1K GRCh37，本轮下载 GWAS Catalog 的 original GRCh37 TSV，并逐文件完整扫描。三项字节数和官方 MD5 均通过。

{gwas_table}

协调规则固定为同一 GRCh37 染色体与唯一位置连接，再用 allele set 定向到 BIM A1。非回文 SNP 可直接处理 exact、swap 或 reverse-complement；回文 SNP 只有在一个频率方向至少比另一个近 0.10 且与 OneK AF 相差不超过 0.20 时才保留。其余回文歧义、allele mismatch 和 |ΔAF|>0.20 均排除。

LOMG 原始窗口有 7 个重复位置，来自不同 indel/多等位记录；与 OneK BIM allele set 匹配后的结果没有重复 variant_id。它们被保留在审计计数中，但不构成推断输入失败。

## rs7239261 锚点复核

{lead_table}

三套原始 GWAS 的 effect allele 均为 A，与 OneK BIM A1 一致。此前 GRCh38 harmonised 表使用 ALT C，因此 beta 符号相反但生物学方向一致。LOMG 的 A1 正效应等价于先前 C 的 beta=-0.2591；EOMG 接近零，overall MG 为强疾病信号。

## cell–gene 共同覆盖

三套疾病数据有 2,497 个共同可推断变异。每个 cell–gene 单独与 EOMG 和 LOMG 相交后：

{overlap_table}

71/71 组合达到预设的至少 500 个 EOMG∩LOMG∩QTL 共同变异，实际范围为 1,124–2,562。该结果只证明 coloc 输入足够，并不证明任何组合存在 H4 共享信号。
""")

    write(REPORT_DIR / "05_CMM_R5A2A2_R5A2A3下一阶段冻结目标.md", """
# CMM R5A2A2：R5A2A3 下一阶段冻结目标

下一阶段固定为 `R5A2A3_CHR18_COLOC_ABF_SMOKE_AND_LD_TRIGGER`。

## 分析矩阵

- 疾病侧：LOMG 为主检验，overall MG 为疾病信号复核，EOMG 为亚型对照；
- QTL 侧：当前 71 个真实存在的 OneK1K cell–gene 组合；
- 坐标与方向：GRCh37 chr18:59,005,046–61,005,046，所有 beta/EAF 定向至 OneK BIM A1；
- 第一层：3 × 71 个 coloc.abf 单信号 smoke tests；
- 第二层：只对共享信号或 H3/H4 可解决歧义的组合建立 cell-specific source LD，并进入条件化或 SuSiE；
- 第三层：只有 OneK1K 信号门通过后才接入 TenK10K 做独立 molecular replication。

## 冻结阈值

每个比较至少 500 个共同变异。默认先验为 `p1=1e-4`、`p2=1e-4`、`p12=1e-5`，同时固定检查 `p12=1e-6` 与 `1e-4`。必须报告 PP.H0–H4、H4/(H3+H4)、共同变异数、两侧区域最小 P 与最大单变异 H4 贡献。

- `PASS_ROBUST_SHARED_SIGNAL`：默认 PP.H4≥0.80，H4/(H3+H4)≥0.80，且先验敏感性不把结论翻转为 H3；
- `HOLD_LD_REQUIRED`：H3+H4 较高但 H3/H4 无法分解，或单信号假设受多峰结构影响；
- `FAIL_SUFFICIENT_COVERAGE`：疾病和 QTL 均有区域信息、共同覆盖充分，但 H4 在冻结先验范围内持续低；
- `UNINFORMATIVE`：某一侧缺乏区域信号，不解释为反向生物学证据。

## 决策顺序

若 LOMG 在至少一个 gene/cell 出现稳健 H4，并且 overall MG 支持同一信号，进入该组合的 source-LD 和 TenK10K 复制。EOMG 是否支持同一信号用于解释共享效应与 LOMG 富集，不要求人为制造 EOMG 阴性。

若没有稳健 H4，但存在明确 H3/H4 歧义，只构建触发组合的 LD，不为全部 71 组合生成大矩阵。若 chr18 在充分覆盖下全部失败，冻结 chr18 为 `FAIL_PRIMARY_LOCUS`，下一轮只测试 chr5 / rs6861227；不调用 chr2 或 chr8 补故事。
""")

    write(REPORT_DIR / "99_CMM_R5A2A2_详细行动记录_2026-09-14.md", f"""
# CMM R5A2A2 详细行动记录：OneK1K chr18 字节、样本、等位基因与推断输入闭环

日期：2026-09-14  
执行状态：`COMPLETE`  
最终判定：`R5A2A2_INPUT_GATE_PASS`  
下一阶段：`R5A2A3_CHR18_COLOC_ABF_SMOKE_AND_LD_TRIGGER`

## 一、目标与继承边界

本轮承接 R5A2A 的 chr18 / rs7239261 首位点排序和用户完成的 10.34 GB 分片下载。任务是验证实际 archive，而不是接受下载日志本身；并把 raw eQTL、genotype、样本、GRCh37 疾病统计量变成可审计的同一分析接口。SSc 继续保持冻结归档，开放数据硬约束不变，TenK10K 仍受顺序门控。

## 二、10.34 GB raw eQTL 单次流式审计

新建 `audit_and_extract_onek_chr18_archive.py`，顺序读取完整 gzip tar，同时计算 MD5/SHA-256、检查每个 member，并只提取 14 个真实 chr18 Parquet、README 与 BIM。结果为 622 members，其中 311 个科学成员和 311 个 AppleDouble metadata；308 个科学 Parquet 精确对应 14×22。压缩文件所有 `10,344,009,571` bytes 均被读取，官方 MD5 和 archive member gate 通过。

## 三、genotype 科学成员提取

新建 `extract_onek_genotype_scientific_members.py`，从已验收 ZIP 中提取真实 BED/BIM/FAM，忽略 `__MACOSX/._*` 科学选择干扰，同时保留完整 ZIP CRC 结论。提取合计 `1,461,094,883` bytes。archive BIM 与 genotype BIM 逐字节相同；rs7239261 位于 BIM zero-based index 4,904,698，GRCh37 `18:60005046`，A1=A、A2=C。

## 四、Parquet schema 与区域提取

新建 `audit_extract_onek_chr18_usability.py`，逐 cell 检查 schema、row group、统计范围、variant–BIM、TSS 和 lead 覆盖，并提取固定区域。14 个文件共 8,959,978 pairs，区域为 241,650 pairs、8 个 phenotype、71 个 cell–gene 组合。所有 schema 与数据规则通过。

## 五、两次关键接口纠错

### 5.1 covariate 行不是 cell-specific QTL 样本

直接使用 covariate 行时，CD4_SOX4、Plasma 等细胞的 BED 计数与 QTL `ma_count` 不符。继续检查官方 pseudobulk matrix 后发现，每个 cell 实际分析 donors 是 header 中首批基因均非 NA 的列。前 5 个基因的 NA mask 在 14 个 cell 内各自稳定；非 NA donors 全部存在于 FAM 和 covariates。用这些样本重算后完全一致。

### 5.2 ma_count 是 minor allele count，不恒等于 A1 count

首次检查有 12/3,655 行 `ma_count` 不一致，但 `af` 全部复现。定位后确认这些行的 A1 AF>0.5；TensorQTL 的 `ma_count/ma_samples` 记录 minor allele，而 `slope/af` 仍对应 A1。修正检查规则后，3,655/3,655 行的 count、carrier 与 AF 全部通过。这个修正避免了错误翻转 QTL slope。

## 六、GRCh37 MG GWAS 下载与完整扫描

为消除 liftover，本轮取得 GWAS Catalog 三套 original GRCh37 TSV。下载采用可恢复分段方法，三套文件均以官方 byte count 和 MD5 验收。新建 `extract_harmonize_mg_grch37_chr18.py`，完整扫描合计 21,035,433 行，而不是假定文件坐标有序。

{gwas_table}

等位基因按同 build 位置与 BIM allele set 严格连接，log(OR) 和 EAF 统一到 A1。回文 SNP 使用 OneK 980-donor AF 消歧；19、45、11 个条目分别因歧义或 allele mismatch 被排除。三套 rs7239261 均精确存在且频率差在门槛内。

LOMG 原文件在窗口内出现 7 个重复位置。逐条检查确认是不同 indel/多等位记录；最终 BIM-matched 输出没有重复位置。脚本门控从“任何原始位置重复即失败”纠正为“推断输出不得有重复 variant”，同时在 audit 中保留两个计数。

## 七、推断输入矩阵

新建 `build_chr18_coloc_input_manifest.py`，将 241,650 条 QTL 与三套 eligible GWAS 分别相交。三套疾病数据共同变异为 2,497；71/71 个 cell–gene 组合通过至少 500 个 EOMG∩LOMG∩QTL 共同变异和 lead 完整性门，实际共同数范围 1,124–2,562。TNFRSF11A 可测试细胞固定为 CD4_NC、CD8_ET、CD8_NC、NK、NK_R。

## 八、最终状态

`OneK1K_archive_gate=PASS`、`genotype_interface=PASS`、`cell_sample_interface=PASS`、`A1_effect_semantics=PASS`、`MG_GRCh37_harmonization=PASS`、`chr18_coloc_input_gate=PASS`。

本轮只完成输入闭环。所有 top eQTL 排序仍是 nominal molecular evidence，不能写成 disease–gene 共定位或因果基因。MG 主项目继续 `CONDITIONAL_GO`，但大规模单细胞和论文主图继续 HOLD。

## 九、下一阶段

R5A2A3 运行 213 个冻结 coloc.abf smoke tests。只对稳健 H4 或 H3/H4 歧义组合生成 cell-specific OneK source LD；随后才能决定 TenK10K 下载/复制。若 chr18 在充分覆盖下失败，转 chr5 一次，不扩张到无边界候选。

## 十、本轮新增主要文件

- `2_code/06_intake/mg_r5a2a2/`：核心接入、提取、协调、readiness、测试、报告与发布脚本；
- `3_results/00_audit/R5A2A2/`：archive、genotype、schema、GWAS、coloc readiness 审计；
- `3_results/01_gwas/R5A2A2/`：三套 GRCh37 chr18 A1-aligned 区域表与 manifest；
- `3_results/03_qtl/R5A2A2/`：区域 QTL、样本列表、schema 与 gene summary；
- `3_results/04_integration/R5A2A2/`：71 个 cell–gene 推断输入清单；
- `0_admin/protocol/current/`：R5A2A2 状态与 R5A2A3 冻结协议；
- `7.Report/current/R5A2A2/`：本轮全套报告与详细行动记录。
""")

    write(REPORT_DIR / "SOURCES_CHECKED_2026-09-14.md", """
# R5A2A2 核验来源

| 来源 | 本轮用途 | 官方入口 |
|---|---|---|
| OneK1K Zenodo v2 | raw eQTL、genotype、pseudobulk、covariate 的文件大小与 MD5 | https://zenodo.org/records/18910121 |
| OneK1K 官方分析代码 | TensorQTL 载入方式、MAF 门和分析调用 | https://github.com/powellgenomicslab/sc-veQTL/blob/main/TensorQTL_cis/eQTL_OneK1K_cell_5_mean_mx.py |
| TensorQTL 官方代码 | PLINK dosage/A1 转换定义 | https://github.com/broadinstitute/tensorqtl/blob/master/tensorqtl/genotypeio.py |
| GWAS Catalog GCST90432156 | MG overall study 与 original summary statistics | https://www.ebi.ac.uk/gwas/studies/GCST90432156 |
| GWAS Catalog GCST90432157 | EOMG study 与 original summary statistics | https://www.ebi.ac.uk/gwas/studies/GCST90432157 |
| GWAS Catalog GCST90432158 | LOMG study 与 original summary statistics | https://www.ebi.ac.uk/gwas/studies/GCST90432158 |
| Braun et al. 2024 | EOMG/LOMG 定义、样本与疾病结果语境 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11560923/ |

网页说明只用于来源定义。字节、schema、样本和区域数值均来自本地文件的独立读取与重算。
""")

    write(REPORT_DIR / "README.md", """
# R5A2A2 报告入口

建议阅读顺序：

1. `00_CMM_R5A2A2_执行摘要_OneK1K_chr18输入闭环.md`
2. `01_CMM_R5A2A2_OneK1K_10GB归档与基因型字节审计.md`
3. `02_CMM_R5A2A2_样本接口_ParquetSchema与等位基因审计.md`
4. `03_CMM_R5A2A2_chr18区域基因与QTL可测性.md`
5. `04_CMM_R5A2A2_MG_GRCh37协调与共定位准备度.md`
6. `05_CMM_R5A2A2_R5A2A3下一阶段冻结目标.md`
7. `99_CMM_R5A2A2_详细行动记录_2026-09-14.md`

冻结状态：`R5A2A2_INPUT_GATE_PASS`；下一阶段 `R5A2A3_CHR18_COLOC_ABF_SMOKE_AND_LD_TRIGGER = GO`。本轮尚未执行 disease–eQTL 共定位。
""")

    state = {
        "schema_version": "1.0",
        "adjudicated_at": "2026-09-14",
        "project": "MYASTHENIA_GRAVIS",
        "axis": "EOMG_VS_LOMG",
        "stage": "R5A2A2_CHR18_INPUT_USABILITY_GATE",
        "status": "COMPLETE_INPUT_GATE_PASS",
        "constraints": {"open_data_only": True, "permission_required_data": False, "author_request_data": False},
        "gates": {
            "OneK1K_raw_eQTL_archive": "PASS_10344009571_BYTES_MD5_MATCH",
            "OneK1K_chr18_parquets": "PASS_14_CELLS_8959978_PAIRS",
            "OneK1K_cell_sample_interface": "PASS_PSEUDOBULK_NON_NA_DONORS",
            "OneK1K_A1_effect_semantics": "PASS_3655_OF_3655_BED_RECALCULATIONS",
            "MG_original_GRCh37_bytes": "PASS_ALL_3_MD5_MATCH",
            "MG_chr18_harmonization": "PASS_3854_4153_2596_ELIGIBLE_VARIANTS",
            "chr18_coloc_input": "PASS_71_OF_71_CELL_GENE_PAIRS",
            "disease_eQTL_colocalization": "NOT_RUN",
            "source_matched_LD": "READY_SAMPLE_INTERFACE;NOT_BUILT",
            "TenK10K_replication": "DEFERRED_UNTIL_R5A2A3_SIGNAL_GATE",
        },
        "fixed_region": {"build": "GRCh37", "chromosome": 18, "start": 59005046, "end": 61005046, "lead": "rs7239261"},
        "testable_scope": {
            "cells": 14,
            "genes": sorted(gene_summary["phenotype_id"].unique().tolist()),
            "cell_gene_pairs": 71,
            "QTL_pairs": 241650,
            "all_three_GWAS_shared_variants": 2497,
            "minimum_EOMG_LOMG_QTL_overlap": 1124,
        },
        "current_decision": {
            "MG_main_project": "CONDITIONAL_GO",
            "R5A2A2_input_closure": "PASS",
            "R5A2A3_coloc_ABF_smoke": "GO",
            "LD_generation": "TRIGGERED_ONLY_BY_H4_OR_H3_H4_AMBIGUITY",
            "TenK10K_large_download": "DEFERRED",
            "manuscript_scale_analysis": "HOLD",
            "IgAN_fallback": "NOT_TRIGGERED",
        },
        "next_stage": "R5A2A3_CHR18_COLOC_ABF_SMOKE_AND_LD_TRIGGER",
        "next_stage_stop_rule": "If chr18 fails with adequate regional disease and QTL coverage, test chr5 only; do not rescue with chr2 or chr8.",
    }
    write(PROTOCOL_DIR / "R5A2A2_MG_chr18_usability_state.json", json.dumps(state, indent=2, ensure_ascii=False))

    protocol = (REPORT_DIR / "05_CMM_R5A2A2_R5A2A3下一阶段冻结目标.md").read_text(encoding="utf-8")
    write(PROTOCOL_DIR / "R5A2A3_MG_chr18_coloc_smoke_protocol.md", protocol)

    for source in REPORT_DIR.glob("*.md"):
        write(ROUND_DIR / source.name, source.read_text(encoding="utf-8"))

    print(json.dumps({
        "report_dir": str(REPORT_DIR),
        "reports": len(list(REPORT_DIR.glob("*.md"))),
        "state": str(PROTOCOL_DIR / "R5A2A2_MG_chr18_usability_state.json"),
        "next_protocol": str(PROTOCOL_DIR / "R5A2A3_MG_chr18_coloc_smoke_protocol.md"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
