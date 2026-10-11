#!/usr/bin/env python3
"""Build the frozen R6A1 report set and R6A2 protocol."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "3_results/00_audit/R6A1"
RESULT = ROOT / "3_results/04_integration/R6A1"
CURRENT = ROOT / "7.Report/current/R6A1"
ROUND = ROOT / "7.Report/rounds/R6A1"
ADMIN = ROOT / "0_admin/protocol/current"
for folder in (CURRENT, ROUND, ADMIN):
    folder.mkdir(parents=True, exist_ok=True)

state = json.loads((AUDIT / "R6A1_final_gate_adjudication.json").read_text(encoding="utf-8"))
gwas = json.loads((AUDIT / "IgAN_GWAS_schema_loci_serumIgA_audit.json").read_text(encoding="utf-8"))
qtl = json.loads((AUDIT / "IgAN_QTL_testability_positive_control_audit.json").read_text(encoding="utf-8"))
kidney = json.loads((AUDIT / "IgAN_kidney_tissue_byte_metadata_detectability_audit.json").read_text(encoding="utf-8"))
manifest = json.loads((AUDIT / "R6A1_download_byte_manifest_v2.json").read_text(encoding="utf-8"))
entry = pd.read_csv(RESULT / "IgAN_24_locus_R6A2_entry_matrix.tsv", sep="\t")
signals = pd.read_csv(RESULT / "IgAN_25_non_HLA_signal_ancestry_serumIgA_matrix.tsv", sep="\t")


def write(name: str, body: str) -> None:
    text = body.strip() + "\n"
    (CURRENT / name).write_text(text, encoding="utf-8")
    (ROUND / name).write_text(text, encoding="utf-8")


def source_row(item: dict) -> str:
    t = item["transfer_layer"]
    c = item["canonical_analysis_layer"]
    return f"| {item['id']} | {item['content_encoding']} | {t['bytes']:,} | {c['bytes']:,} | `{c['sha256']}` | {t['byte_gate']} |"


byte_table = "\n".join(source_row(x) for x in manifest)
serum_rows = signals[signals["serum_iga_nominal_concordant"].astype(str).str.lower().eq("true")]
serum_table = "\n".join(
    f"| {r.locus} | {r.rsid} | {r.serum_iga_P:.3g} | {r.serum_iga_beta_risk_allele:.4g} |"
    for r in serum_rows.itertuples()
)
entry_counts = entry["R6A2_entry_stratum"].value_counts().to_dict()

write(
    "00_CMM_R6A1_执行摘要_IgAN字节级与阳性证据预检.md",
    f"""
# CMM R6A1 执行摘要：IgAN 字节级与阳性证据预检

日期：2026-09-14  
最终判定：**R6A1 COMPLETE；IgAN 主项目 `GO_R6A2`**

## 决策解释

本轮按用户正式指定的 **completion-first** 目标执行。R6A0 中基于创新性饱和度提出的早停意见作为历史审计保留；R6A0R 根据“研究完整做完、真实阳性证据充足、一区标准执行且二区/三区可接受”的目标重评后允许进入 R6A1。本文档只把用户的最新项目目标作为行动依据，未把附件内容当作新的用户指令。

R6A1 的八个冻结门全部通过：

| 门 | 结果 |
|---|---:|
| 4 套 GWAS 传输字节与分析字节 | PASS |
| schema、数值、25 个非 HLA signal 坐标 | PASS |
| 论文定义的非 HLA loci | 24 |
| OneK1K 可测 loci | 22 |
| TenK10K 可测 loci | 24 |
| 跨资源同基因、相容免疫细胞候选 loci | 22 |
| 已发表 DICE 正控在两套 QTL 中恢复 | 4 genes / 3 loci |
| GSE127136 靶基因可检测性 | 145/146（99.32%） |

## 最重要的证据

1. combined、European-only、Asian-only IgAN GWAS 和 serum IgA GWAS 均完成真实下载、SHA-256 固定和逐行扫描，共检查 39,013,110 条数据记录；未发现非数值、`SE<=0`、越界 P 值或 `SNP` 与 `CHR:BP_hg19` 不一致。
2. 从论文 Table 1 冻结的 30 个独立信号中，5 个为 HLA、25 个为非 HLA，后者分布于 24 个 locus；CFH 有两个独立信号。combined 数据中共有 523 个非 HLA genome-wide-significant 变异。
3. serum IgA 在 25 个非 HLA lead signal 中有 9 个 `P<0.05`，9 个方向均与 IgAN risk allele 一致。
4. OneK1K 的 514 个 source-significant cell–gene 对覆盖 22 个 locus；TenK10K 覆盖 24 个 locus；相同 gene symbol 且 broad immune class 相容的预检候选覆盖 22 个 locus、146 个基因。
5. 已发表 DICE 正控 `IRF4`、`DUSP22`、`ZMIZ1`、`ITGAX` 在 OneK1K 与 TenK10K 中都恢复为可测试候选，形成 R6A2 的三个方法正控 locus：`IRF4/DUSP22`、`ZMIZ1`、`ITGAM/ITGAX`。

## 结论边界

R6A1 证明的是：数据真实存在、结构可计算、阳性正控可进入 signal-level 验证、组织层能检测主要候选。它**没有产生新的疾病–eQTL 共定位阳性**，也不能凭 source QTL 显著性指定 causal gene。

## 下一阶段

进入 **R6A2 — IgAN Regulatory Landscape：正控先行的全 24-locus 信号级分析**。先在三个正控 locus 验证 harmonization 与 coloc 回收能力，再按同一冻结规则扩到全部 24 个非 HLA locus。只有具体 cell–gene 通过稳健 H4 或可解析 H3/H4 门，才构建对应 source LD；TenK10K 只复核预先触发的相同 gene/cell-class 组合。
""",
)

write(
    "01_CMM_R6A1_GWAS字节_Schema与非HLA位点审计.md",
    f"""
# CMM R6A1：GWAS 字节、Schema 与非 HLA 位点审计

## 字节对象

官方页面未提供校验和，因此本轮保留 HTTP 传输层与 canonical 分析层，并生成本地 MD5/SHA-256。European-only IgAN 与 serum IgA 的服务器响应使用 Brotli；原始响应以 `.br` 保存，解压后的纯文本作为分析层，二者不能混为一个文件。

| 对象 | 传输编码 | 传输 bytes | canonical bytes | canonical SHA-256 | 门 |
|---|---|---:|---:|---|---|
{byte_table}

## 全文件扫描

| 数据集 | 行数 | 字段 | 非法数值 | `SE<=0` | P 越界 | SNP/坐标不符 | 25 个 lead 坐标 |
|---|---:|---|---:|---:|---:|---:|---:|
| combined | 10,021,045 | `SNP CHR BP_hg19 A1 A2 BETA SE P` | 0 | 0 | 0 | 0 | 25/25 |
| European | 9,094,951 | 同上 | 0 | 0 | 0 | 0 | 25/25 |
| Asian | 7,666,659 | 同上 | 0 | 0 | 0 | 0 | 25/25 |
| serum IgA | 12,230,455 | 同上 | 0 | 0 | 0 | 0 | 25/25 |

`A1` 是 effect allele；build 为 GRCh37/hg19。BETA、SE、P 齐全，满足 coloc.abf 与 effect-direction audit 的输入要求。

## 信号与 locus 计数

论文 Table 1 给出 30 个独立信号：5 HLA + 25 非 HLA。25 个非 HLA 信号对应 24 个 locus，因为 CFH 有两个独立信号。

combined 文件重算得到 523 个非 HLA `P<5e-8` 变异。单纯按相邻 GWS 变异间距 1 Mb 聚类会得到 25 个簇，因为 CFH 的一个远端尾部变异 `1:197921246` 与 CFH lead 相距 1,234,328 bp。本轮保留该工程诊断，不为了复现论文数量而偷偷改变聚类法；再以论文定义 locus、±1.5 Mb 锚定后，523/523 均归入 24 个已发表 locus。

## 跨 build 核验

24/24 locus lead 均经 NCBI RefSNP placement 找到 GRCh38 坐标，且 GRCh37 与论文坐标一致。`rs751081288` 已 retired 并 merge 到 `rs57707137`，normalized placement 相对旧坐标存在 1 bp shift，已在 cross-build manifest 中显式记录。`rs1865097` 只接受 assembled chromosome placement，排除了 scaffold placement。

## 判定

`GWAS_BYTE_SCHEMA_LOCUS_GATE = PASS`。
""",
)

write(
    "02_CMM_R6A1_OneK1K_TenK10K可测性与正控恢复.md",
    f"""
# CMM R6A1：OneK1K / TenK10K 可测性与正控恢复

## 冻结定义

- locus window：匹配 build 的已发表非 HLA lead ±1 Mb。
- OneK1K source-positive：source q-value `<0.05`，且 source top eQTL 位于窗口内。
- TenK10K source-positive：cell 内 gene-level ACAT P 经 BH FDR `<0.05`，或 source SuSiE credible-set member 位于窗口内。
- cross-resource candidate：同一 locus、同一 GENCODE gene symbol、broad immune class 相容。

这三个定义都是**预检候选定义**，不是 disease-QTL colocalization。

## 资源完整性

- OneK1K top-QTL ZIP：CRC PASS，308 个科学数据成员；full ±1 Mb cis-eQTL 与 980-donor PLINK genotype 已在工作区。
- TenK10K gene-level ZIP：CRC PASS，28/28 cell types。
- TenK10K SuSiE ZIP：CRC PASS，28/28 cell types。
- GENCODE v50：相关 812 个 Ensembl ID 中 804 个映射到 symbol；8 个未映射项保留，不做猜测式基因名替换。

## 结果

| 项目 | 数量 |
|---|---:|
| OneK1K source-significant cell–gene | {qtl['OneK1K']['source_significant_cell_gene_pairs_in_loci']} |
| OneK1K source-significant genes | {qtl['OneK1K']['source_significant_genes']} |
| OneK1K testable loci | {qtl['OneK1K']['testable_loci']}/24 |
| TenK10K ACAT-FDR cell–gene | {qtl['TenK10K']['ACAT_FDR_cell_gene_pairs_in_loci']} |
| TenK10K SuSiE gene–cell | {qtl['TenK10K']['SuSiE_gene_cell_pairs_in_loci']} |
| TenK10K testable loci | {qtl['TenK10K']['testable_loci']}/24 |
| cross-resource compatible cell–gene pairings | {qtl['cross_resource']['compatible_cell_gene_pairs']} |
| cross-resource genes | {qtl['cross_resource']['genes']} |
| cross-resource loci | {qtl['cross_resource']['loci']}/24 |

CFH 与 IGH 在 OneK1K source-significant 层为 0，但 TenK10K 可测，因此列为 resource-asymmetric，不解释为生物学阴性。OneK1K public BIM 在 19/24 个 locus 有精确 lead position；其余 locus 仍有充分区域变异，后续必须用 harmonized regional variants，而不能因 exact lead 缺失直接判失败。

## 已发表正控

来自论文 DICE 分析的 14 个 gene–locus 正控中，4 个在两套资源和相容 broad cell class 中同时恢复：

| locus | gene |
|---|---|
| IRF4/DUSP22 | IRF4 |
| IRF4/DUSP22 | DUSP22 |
| ZMIZ1 | ZMIZ1 |
| ITGAM/ITGAX | ITGAX |

它们属于 R6A2 的方法 benchmark。只有 R6A2 在真实疾病 GWAS 与新 QTL 之间重算 signal-level 证据后，才能说是否在 OneK1K/TenK10K 中复现共定位。

`QTL_TESTABILITY_AND_CONTROL_ELIGIBILITY_GATE = PASS`。
""",
)

write(
    "03_CMM_R6A1_serumIgA与跨祖源支持.md",
    f"""
# CMM R6A1：serum IgA 与跨祖源支持

## Serum IgA

25 个非 HLA lead signal 中 9 个 serum IgA `P<0.05`，且 9 个 effect 均与 IgAN risk allele 同向：

| locus | lead | serum IgA P | risk-allele beta |
|---|---|---:|---:|
{serum_table}

这构成 disease-related trait support；它不是多重校正后的独立 serum-IgA locus 声明，也不是 mediation 证据。R6A2 的 `B_TRAIT_CONCORDANT_CROSS_RESOURCE` 分层只用它排序，不改变共定位阈值。

## European 与 Asian 分层

- 25/25 lead 在 European-only 中 risk-allele beta 同向；24/25 nominal `P<0.05`，3/25 达 `P<5e-8`。
- 25/25 lead 在 Asian-only 中 risk-allele beta 同向；25/25 nominal `P<0.05`，7/25 达 `P<5e-8`。

这些数据允许在 R6A2 检查 combined shared signal 是否同时得到两个祖源层的方向支持。不同祖源的 LD 与统计功效不同，因此不能把未达 genome-wide significance 简化为 replication failure，也不能把 trans-ancestry combined 的 H4 直接当作 European-QTL 的 ancestry-matched 结果。

`TRAIT_AND_ANCESTRY_SUPPORT_GATE = PASS`。
""",
)

write(
    "04_CMM_R6A1_肾组织字节与目标可检测性.md",
    f"""
# CMM R6A1：肾组织字节与目标可检测性

## GSE127136

- processed count matrix：15,703,242 bytes；SHA-256 `{kidney['GSE127136']['counts_sha256']}`。
- 24,153 genes × 3,620 cells；3,620/3,620 matrix cell titles 与 GEO SOFT metadata 精确匹配。
- kidney donors：13 IgAN + 6 kidney-cancer/paracancer controls。
- peripheral monocyte donors：5 IgAN + 5 normal，属于不同 compartment，不能并入肾组织对照。
- 146 个跨资源候选 gene 中检测到 145 个（99.32%）；22/22 个跨资源候选 locus 至少有一个可检测 gene。

该数据可做组织定位和 donor-level pseudobulk，但目前 metadata 缺少可直接复用的完整 kidney cell-cluster label。R6A2 必须先恢复或重建细胞注释，然后以 donor 为生物学重复，不能把 3,620 个细胞当作独立样本。

## GSE286184 / GSE286186

- GSE286184 Xenium：22 samples，其中 IgAN 4、Control 3、DKD 6、MCD 4、MN 5；RAW tar 声明 335,585,280 bytes。本项目把 4 个 IgAN 空间样本用于 localization，禁止单独冒充充分的 disease-control inference。
- GSE286186 SuperSeries：59 个 sample records；其 file list 与 series metadata 已验收，RAW tar 声明 3,452,221,440 bytes。本轮不下载大 RAW；R6A2 先拆分 snRNA 与 Xenium subseries、冻结 diagnosis/covariate 后再取所需对象。

`KIDNEY_TARGET_DETECTABILITY_GATE = PASS`。
""",
)

protocol = """
# R6A2 冻结协议：IgAN Regulatory Landscape

版本：v1.0（2026-09-14）

## 目标

在 24 个已发表非 HLA IgAN locus 中，使用公开 GWAS、OneK1K、TenK10K 和公开肾组织数据识别可复现的 cell–gene shared signals，并给出有边界的 locus 分类。R6A2 不以“做出阳性”为优化目标。

## 冻结输入

1. primary disease：Kiryluk 2023 combined IgAN GWAS，GRCh37。
2. ancestry support：European-only、Asian-only IgAN GWAS。
3. related trait：serum IgA GWAS，只作方向与相关性状支持。
4. molecular discovery：OneK1K full cis-eQTL；只使用 source-significant 514 个 cell–gene 组合组成的冻结发现全集，并加回已发表 benchmark gene（若将来发现其在过滤中被漏掉）。
5. independent molecular replication：TenK10K；必须在 discovery trigger 前冻结同 gene 与相容 cell class。
6. tissue：GSE127136 donor-level kidney localization/pseudobulk；GSE286184 只作空间定位；GSE286186 拆分 subseries 后再决定用途。

## 执行顺序

### R6A2A：方法正控门

先分析三个 locus：`IRF4/DUSP22`、`ZMIZ1`、`ITGAM/ITGAX`。目标是检验 build/allele、窗口、variant overlap 与 coloc 实现能否恢复已发表正控结构。至少 2/3 locus 获得方向合理、覆盖充分且可解释的 signal-level 支持才进入全景扫描；否则只允许一次有记录的 harmonization/窗口故障排查。

### R6A2B：全 24-locus 单信号预筛

- 24 locus 全部保留；CFH 两个独立信号分别保留 signal ID。
- OneK1K 22 个可测 locus 运行完整冻结 cell–gene 集；combined 为 primary，European/Asian 作支持。
- coloc.abf 只作 single-causal smoke；固定 `p1=p2=1e-4`、`p12=1e-6/1e-5/1e-4`。
- robust trigger：默认 `PP.H4>=0.80` 且 `H4/(H3+H4)>=0.80`，先验变化下不由 H3 主导。
- ambiguity trigger：H3/H4 混合且有足够区域覆盖，问题可被 source LD 和多信号分解回答。

### R6A2C：targeted source LD 与多信号裁决

只为触发的具体 OneK1K cell–gene 构建 source LD，使用该细胞真实 active donor 集，不得用全体 genotype donors 替代。需要疾病侧 LD 时，按 ancestry 选择公开 reference，并把 mismatch 风险单独报告。禁止对全部组合批量建 LD 后择优。

### R6A2D：TenK10K 独立复核

只复核触发前已登记的同 gene、相容 cell class。source credible set、覆盖差异和 build/allele 必须分别验收。TenK10K 中另一个更强 gene 不能替代原 trigger。

### R6A2E：肾组织定位

GSE127136 使用 donor-level pseudobulk；先冻结 kidney cell annotation、donor、disease state 与 covariates。GSE286184 只做空间定位。组织表达用于定位已通过遗传门的 gene/cell，不可反向挑选最显著基因再回填遗传故事。

## 证据层级

- Tier A：稳健 disease–OneK shared signal + 多信号裁决通过 + TenK 相同 gene/cell-class 复核 + kidney 可检测/定位。
- Tier B：稳健 discovery shared signal + 技术覆盖充分 + kidney 支持；TenK 无法充分检验或产生有解释的资源差异。
- Tier C：QTL 可测但 shared signal 未通过、H3 favored，或证据不足。
- Resource-asymmetric：OneK 缺失但 TenK 可测，禁止与 Tier C 混同。

## 项目出口

- `GO_MANUSCRIPT_SCALE`：Tier A/B locus ≥3，且至少 2 个为 Tier A 或具有独立 molecular replication。
- `CONDITIONAL_GO`：Tier A/B locus =2；只允许完成已冻结组织与稳健性分析后再判断。
- `NO_GO_REGULATORY_LANDSCAPE`：完整 24-locus 后 Tier A/B <2，或正控门 2/3 无法恢复且技术原因不能解决。

所有阈值按 locus 计数；同一 locus 的多个 gene/cell 不得重复充数。
"""
(ADMIN / "R6A2_IgAN_regulatory_landscape_protocol.md").write_text(protocol.strip() + "\n", encoding="utf-8")

write(
    "05_CMM_R6A1_GO-NOGO与R6A2冻结目标.md",
    f"""
# CMM R6A1：GO/NO-GO 与 R6A2 冻结目标

## R6A1 门控

八项门全部通过，机器可读状态见 `R6A1_final_gate_adjudication.json`。

```text
IgAN_MAIN_PROJECT = GO
R6A1 = COMPLETE
R6A2 = GO

PUBLISHED_NON_HLA_LOCI = 24
ONEK1K_TESTABLE_LOCI = 22
TENK10K_TESTABLE_LOCI = 24
CROSS_RESOURCE_CANDIDATE_LOCI = 22
SERUM_IGA_NOMINAL_CONCORDANT_SIGNALS = 9
PUBLISHED_CONTROL_RECOVERY = 4 genes / 3 loci
KIDNEY_DETECTABILITY = PASS

NEW_COLOC_POSITIVE_CLAIMS = 0
MANUSCRIPT_SCALE_ANALYSIS = HOLD_UNTIL_R6A2_GATE
```

## R6A2 的首批顺序

1. benchmark positive-control：`IRF4/DUSP22`、`ZMIZ1`、`ITGAM/ITGAX`。
2. trait-concordant cross-resource：除已重叠的 IRF4 locus 外，`TNFSF4/18`、`REL`、`TNFSF8/15`、`REEP3`、`OVOL1/RELA`、`TNFSF12/13`、`TNFRSF13B`、`LIF/OSM`。
3. 其余 cross-resource testable locus。
4. CFH、IGH 作为 resource-asymmetric 特殊层，不强行制造 OneK1K 复制。

排序只决定计算顺序，不决定论文结论。最终必须完成 24-locus universe，不能在首个阳性出现后停止，也不能把多个同 locus gene 计成多个独立阳性。

## 下一阶段唯一合法目标

**R6A2A — 三个已发表正控 locus 的真实 signal-level recovery gate。**

完成 build/allele harmonization、区域变异重叠、coloc.abf 预筛和必要时的 targeted source-LD。若至少 2/3 正控 locus 在技术覆盖充分条件下得到可解释 signal-level 支持，则继续 R6A2B 全 24-locus；否则先修复方法，不直接扫描全景。
""",
)

write(
    "99_CMM_R6A1_详细行动记录_2026-09-14.md",
    """
# CMM R6A1 详细行动记录

日期：2026-09-14  
阶段：R6A1 — IgAN Byte-Level + Positive-Evidence Preflight  
状态：**COMPLETE / GO_R6A2**

## 1. 本轮目标与决策继承

用户明确要求正式进入 R6A1，并要求每轮产出详细行动记录。输入的 R6A0 与 R6A0R 对 IgAN 的建议冲突：前者从 novelty saturation 出发建议停，后者按 completion-first 目标建议继续。本轮采用用户最新明确选择的 R6A0R 目标，但保留两份原始记录和 SHA-256，避免改写历史。

- R6A0：`87ee4d5c44c83f5b4d093cb1dd875a8b212c5fafa144d44a12f1fca7b2267bfe`
- R6A0R：`53de2ae77ec89ec54abe658571340448d37b3d48a59f9372f2beccc6f344efe6`

## 2. 官方数据入口与实际下载

从 Columbia IgAN GWAS portal 获取 combined、European-only、Asian-only IgAN summary statistics 和 serum IgA summary statistics；从论文补充材料固定 30 个独立 lead；从 NCBI GEO 获取 GSE127136 processed counts 与 SOFT、GSE286184/GSE286186 file list 和 series metadata；复用已经验收的 OneK1K 与 TenK10K 公共 QTL 字节。

服务器未提供官方 checksum，本轮记录 URL、HTTP transfer length、transfer-layer MD5/SHA-256、canonical-layer MD5/SHA-256。发现 European-only 与 serum IgA 的 HTTP 响应为 Brotli 编码；把响应字节保留为 `.br`，再生成可逐行读取的 canonical `.txt`。这一纠偏避免把压缩字节误判为损坏文本。

## 3. GWAS 全量审计

逐行扫描四个文件，共 39,013,110 行。核验 header、数值解析、SE、P、SNP/CHR:BP 一致性、25 个非 HLA lead 坐标。四个文件均 PASS。

按论文定义重建 30 signals = 5 HLA + 25 non-HLA；25 non-HLA signals = 24 loci。combined 中非 HLA GWS 变异 523 个。纯 1 Mb gap 聚类得到 25 个簇，追踪到 CFH distal tail；未篡改算法来追求 24，而是增加论文 locus anchor 层，523 个变异全部归入 24 个 published locus。

## 4. Variant identity 与 cross-build

用 NCBI RefSNP API 核对 24 个 locus lead。24/24 获得 GRCh38 assembled-chromosome placement，GRCh37 与论文坐标一致。显式记录 retired/merged rsID 和 1-bp normalized shift；排除 scaffold placement。

## 5. OneK1K / TenK10K 可测性扫描

扫描 OneK1K 308 个 top-QTL 科学成员；扫描 TenK10K 28 个 gene-level 文件和 28 个 SuSiE 文件。安装并使用 GENCODE v50 映射 Ensembl ID；812 个相关 ID 映射 804 个，未映射项未强行命名。

结果：OneK1K 514 source-significant cell–gene、211 genes、22 loci；TenK10K 4,469 ACAT-FDR cell–gene、2,861 SuSiE gene–cell、24 loci；跨资源相容候选 1,189 pairings、146 genes、22 loci。

对论文 DICE 正控进行 screening-level recovery：IRF4、DUSP22、ZMIZ1、ITGAX 在两套 QTL 资源与相容 broad cell class 中恢复。没有把这一结果写成新共定位。

## 6. Trait 与组织正证据

serum IgA 在 25 lead signals 中有 9 个 nominal 且全部 risk-direction concordant。European 和 Asian 分层的 25 个 lead 均方向同向。

GSE127136 processed matrix 完整读入：24,153 genes × 3,620 cells；metadata 3,620/3,620 精确匹配。把 kidney 与 peripheral-monocyte compartment 分开后，kidney 为 13 IgAN + 6 cancer/paracancer controls，peripheral monocyte 为 5 IgAN + 5 normal。跨资源候选 genes 检测到 145/146，22/22 candidate loci 均有可检测 gene。

GSE286184 和 GSE286186 只完成 metadata/file-list 级验收，大 RAW 延后至 R6A2，并冻结用途边界。

## 7. 环境变化

为正确处理官方 Brotli 响应与 HTML/XML 解析，安装：

```text
brotli 1.2.0
lxml 6.1.3
beautifulsoup4 4.15.0
soupsieve
```

本轮只生成 Markdown、TSV、JSON、PNG/PDF 和 ZIP；没有 Office 文档，因此无需调用 WPS 后台渲染，也未使用 LibreOffice。

## 8. 质量控制

- 四个 GWAS：真实字节、hash、schema、全行数与 signal coordinate PASS。
- QTL ZIP：CRC PASS；成员数 PASS。
- NCBI RefSNP：24/24 assembled chromosome placement PASS。
- GEO counts ↔ metadata：3,620/3,620 exact cell-title set match。
- Python：全脚本 `py_compile`。
- JSON：全审计文件可解析。
- 图：PNG 视觉检查完成，PDF 同源输出。
- release：只包含脚本、报告、审计和派生小文件；不复制约 1.9 GB 原始 GWAS 与既有 10.34 GB OneK1K raw eQTL。

## 9. 本轮判定

R6A0R 预设的八个门全部通过，因此：

```text
R6A1 = COMPLETE
IgAN_MAIN_PROJECT = GO
NEXT_STAGE = R6A2A_POSITIVE_CONTROL_SIGNAL_RECOVERY
```

仍冻结：新共定位阳性 0；causal gene 0；manuscript-scale analysis HOLD。

## 10. 下一阶段

R6A2A 只先跑 IRF4/DUSP22、ZMIZ1、ITGAM/ITGAX 三个 benchmark locus 的真实 signal-level recovery。至少 2/3 通过覆盖充分、方向合理和共定位门后，才扩展到全部 24 个 locus。任何 source LD 都限定于已触发的 cell–gene，不能批量生成后择优。
""",
)

write(
    "README.md",
    """
# R6A1 report set

本目录记录 IgAN byte-level、GWAS schema/locus、OneK1K/TenK10K testability、published positive-control eligibility、serum-IgA support 和 kidney target detectability 的完整预检。

阅读顺序：`00` → `01` → `02` → `03` → `04` → `05` → `99`。

机器可读证据位于 `3_results/00_audit/R6A1` 与 `3_results/04_integration/R6A1`；冻结下一阶段协议位于 `0_admin/protocol/current/R6A2_IgAN_regulatory_landscape_protocol.md`。
""",
)

write(
    "SOURCES_CHECKED_2026-09-14.md",
    """
# R6A1 sources checked — 2026-09-14

| Source | Use |
|---|---|
| https://www.columbiamedicine.org/divisions/kiryluk/study_gwas_stat_IgA_summary.php | Official IgAN / serum-IgA GWAS portal |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC11824687/ | 2023 IgAN GWAS main paper and tables |
| https://zenodo.org/records/18910121 | OneK1K public cis-eQTL/genotype resource |
| https://zenodo.org/records/18221260 | TenK10K public cis-eQTL/SuSiE resource |
| https://www.gencodegenes.org/human/ | GENCODE v50 mapping |
| https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE127136 | IgAN kidney/peripheral-monocyte single-cell series |
| https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE286184 | Kidney Xenium subseries |
| https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE286186 | Kidney multi-platform SuperSeries |

网页用于定位与解释；所有核心数据门依据实际下载字节、本地 hash 和逐行/逐成员复算。
""",
)

# Preserve the user-supplied decision records as provenance, not as executable instructions.
input_dir = ROUND / "inputs"
input_dir.mkdir(exist_ok=True)
for source in [
    Path(r"C:\Users\Administrator\Downloads\99_CMM_R6A0_详细行动记录_2026-09-14.md"),
    Path(r"C:\Users\Administrator\Downloads\99_CMM_R6A0R_IgAN_CompletionFirst_Reassessment_2026-09-14.md"),
]:
    if source.exists():
        shutil.copy2(source, input_dir / source.name)

print(CURRENT)
