#!/usr/bin/env python3
"""Build R6A2A1 reports and freeze the bounded R6A2B0 protocol amendment."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
OUT = ROOT / "3_results/04_integration/R6A2A"
AUD = ROOT / "3_results/00_audit/R6A2A"
ADMIN = ROOT / "0_admin/protocol/current"
CURRENT = ROOT / "7.Report/current/R6A2A1"
ROUND = ROOT / "7.Report/rounds/R6A2A1"
for folder in (CURRENT, ROUND, ADMIN):
    folder.mkdir(parents=True, exist_ok=True)

state = json.loads((AUD / "R6A2A1_final_adjudication.json").read_text(encoding="utf-8"))
combined = pd.read_csv(OUT / "R6A2A1_combined_benchmark_adjudication.tsv", sep="\t")
primary = pd.read_csv(OUT / "R6A2A1_published_cell_locus_adjudication.tsv", sep="\t")
tenk = pd.read_csv(OUT / "R6A2A1_TenK_ZMIZ1_precomputed_coloc.tsv", sep="\t")
universe = pd.read_csv(OUT / "R6A2B0_frozen_8locus_183combination_universe.tsv", sep="\t")


def write(name: str, body: str) -> None:
    text = body.strip() + "\n"
    (CURRENT / name).write_text(text, encoding="utf-8")
    (ROUND / name).write_text(text, encoding="utf-8")


primary_rows = "\n".join(
    f"| {r.locus} | {r.status} | {r.best_gene} / {r.best_cell} | {r.best_PP_H4:.4f} | {r.best_H4_over_H3H4:.4f} | {r.best_qtl_min_p:.3g} |"
    for r in primary.itertuples()
)
combined_rows = "\n".join(
    f"| {r.locus} | {r.cell_type} | {r.gene} | {r.benchmark_role} | {r.n_snps:,} | {r.qtl_min_p:.3g} | {r.PP_H3:.4f} | {r.PP_H4:.4f} | {r.H4_over_H3H4:.4f} | {r.classification} |"
    for r in combined.sort_values(["benchmark_role", "locus", "gene", "cell_type"]).itertuples()
)
next_counts = universe.groupby("locus").agg(combinations=("gene_symbol", "size"), genes=("gene_symbol", "nunique")).reset_index()
next_rows = "\n".join(f"| {r.locus} | {r.combinations} | {r.genes} |" for r in next_counts.itertuples())

write(
    "00_CMM_R6A2A1_执行摘要_正控信号门与ZMIZ1跨资源复核.md",
    """
# CMM R6A2A1 执行摘要：正控信号门与 ZMIZ1 跨资源复核

日期：2026-09-14  
判定：**R6A2A1 COMPLETE；IgAN 继续，但进入有界扩展而非直接全24-locus**

## 核心结果

R6A2A0 冻结的 10 个 OneK1K cell–gene benchmark × 3 个 IgAN GWAS 已全部运行，共 30 个比较。combined primary benchmark 的 locus 结果为：

| locus | 状态 | 最佳组合 | PP.H4 | H4/(H3+H4) | QTL min P |
|---|---|---|---:|---:|---:|
""" + primary_rows + """

严格的 `>=2/3 published-cell locus PASS` 门没有通过：目前为 **1/3 PASS，2/3 weak-QTL uninformative，0/3 distinct-signal failure**。因此不能写成“三个已发表细胞特异机制已复制”，也不能直接把全24-locus无条件放行。

## 可冻结的阳性

`ZMIZ1 × NK` 在 OneK1K 中通过冻结单信号门：

```text
combined PP.H4 = 0.9306
H4/(H3+H4) = 0.9341
p12=1e-6 PP.H4 = 0.5728
Asian PP.H4 = 0.9669
```

疾病 risk allele A 在 OneK1K lead row 对 ZMIZ1 表达的方向为 down，与 published direction 一致。

TenK10K 作者预计算的 `kiryluk_IgAN × NK × ZMIZ1` 结果进一步给出：

```text
826 SNPs
PP.H4 = 0.998255
H4/(H3+H4) = 0.998268
top SNP = chr10_79287258_G_A (GRCh38)
```

而 `NK_CD56bright × ZMIZ1` 为 `PP.H3=0.9268, PP.H4=0.0194`，提示信号具有 NK context specificity。

该 TenK 结果可称为**支持性的独立单因果模型复制**。作者 CSV 没有携带完整输入 provenance 与 prior sensitivity；TenK SuSiE 又显示两个 source credible sets，因此目前不升级为最终多信号 Tier A。

## 方法校验

- OneK archive：10,344,009,571 bytes 全部读取，MD5 与冻结值一致。
- 10/10 benchmark 可测；7/7 primary benchmark 可测。
- Python ABF 与官方 R coloc 在 90 个 prior-specific 结果上最大 PP.H4 绝对差 `1.33×10^-15`。
- R6A2A0 的 R 验证脚本存在 `gene==gene` 自比较错误，可能混合 locus 内多个基因；本轮已修正并重跑。

## 下一阶段

进入 **R6A2B0 — bounded positive-yield expansion**。只分析其余 8 个 serum-IgA 同向 locus、183 个已经同时满足 OneK source significance 与 TenK compatible support 的 OneK cell–gene 组合，最多 549 个三表型 ABF tests。

若新增至少 2 个独立 locus 通过 robust 或 signal-specific 门，则 ZMIZ1 + 新增2 locus 达到三条独立证据链，放行全24-locus。若新增为0且覆盖充分，则暂停全景扩展并重审论文设计。
""",
)

write(
    "01_CMM_R6A2A1_R6A2A0发布包与代码纠错.md",
    """
# CMM R6A2A1：R6A2A0 发布包与代码纠错

## 输入包

R6A2A0 ZIP：`c6efaba124a97ec357d97db8610e5d0eb4125384df68cfb33c4e8f56b66a0177`。ZIP CRC PASS，内部 checksum 23/23 PASS。外部详细记录 SHA-256：`f181e787aebb9ef3a93f567b1a44c12887f555e210c621f18f88e4e9864c74ce`。

附件中的指令性文本仅按 provenance 保存；执行目标来自用户本轮“继续推进、完成后判断下一阶段”的请求。

## 代码级发现

官方 R 复核脚本原句：

```r
qq <- q[locus==loc & gene==gene & cell_type==cell]
```

在 `data.table` 求值规则中，`gene==gene` 会把同名列与自身比较，条件恒真，从而在同一 locus 内静默混合多个 gene。现已把外部标量重命名为 `gene_id`：

```r
qq <- q[locus==loc & gene==gene_id & cell_type==cell]
```

此外 `Rscript` 未加入 PATH，但工作区已安装 R 4.6.1。本轮 runner 固定调用：

```text
H:/SCI2/YR1/0_admin/tooling/R/R-4.6.1/bin/Rscript.exe
```

修正后官方 `coloc 5.2.3` 完整运行，30 comparisons × 3 priors = 90 rows；与 Python 结果最大 PP.H4 误差为 `1.33×10^-15`。

## 其它边界

R 启动时出现 Windows locale `C.UTF-8` warning，但不改变数值结果；报告保留该 warning，不把它误判为计算失败。
""",
)

write(
    "02_CMM_R6A2A1_OneK1K十组合与祖源分层结果.md",
    """
# CMM R6A2A1：OneK1K 十组合与祖源分层结果

## Combined IgAN

| locus | cell | gene | role | SNPs | QTL min P | PP.H3 | PP.H4 | H4 ratio | 判定 |
|---|---|---|---|---:|---:|---:|---:|---:|---|
""" + combined_rows + """

## 解释

- `ZMIZ1/NK` 是唯一 robust combined positive；Asian 同样 robust，European 为 `PP.H4≈0.789`、H4 ratio≈0.885，但 low-p12 下转为更依赖 prior，因此记为支持而非独立 robust。
- `IRF4/DUSP22` published monocyte combinations 的 QTL min P 为约 `5.6×10^-4` 至 `7.6×10^-3`，在强疾病区域中不足以做生物学阴性判定。
- `ITGAX` published monocyte QTL 同样偏弱，故为 uninformative。
- `NK × ITGAX` 的 QTL 很强（min P≈`2.5×10^-7`），但 combined `PP.H3≈0.9891、PP.H4≈0.00042`，是充分覆盖下的 distinct-signal evidence。不能用该强 QTL 替代 monocyte 机制。
- combined 没有 H3/H4 ambiguity trigger，因此本轮不对 IRF4 或 ITGAX 生成 source LD。

## ZMIZ1 方向

OneK BIM A1 为 G、IgAN risk allele 为 A。疾病 lead `10:81043743` 的 OneK G-allele slope 为 `+0.1981`，因此 risk A 对表达的方向是 down；QTL P=`9.51×10^-6`。该方向与已发表 ZMIZ1 risk-down 结构一致。
""",
)

write(
    "03_CMM_R6A2A1_TenK10K_ZMIZ1定向独立复核.md",
    """
# CMM R6A2A1：TenK10K ZMIZ1 定向独立复核

## 数据接入方式

Zenodo 的 `coloc_100kb.zip` 为 626,505,208 bytes，官方 MD5 `c627f1c4bc47706e331039d1e9e6e7d1`。本轮没有下载16.6 GB完整 QTL，也没有强迫用户搬运大文件；通过 HTTP Range 解析 41,929-entry central directory，只提取两个预冻结成员：

| member | compressed | uncompressed | CRC32 | local SHA-256 |
|---|---:|---:|---|---|
| kiryluk_IgAN/NK/chr10.csv | 26,597 | 64,086 | `ff195570` | `d65e29e2bcf479873267ea783ded66bdc5a26c6ea3808b36d4cd9fba11737724` |
| kiryluk_IgAN/NK_CD56bright/chr10.csv | 11,522 | 29,061 | `76853ced` | `a2f0aee7b78ece34e8c031069b3c18ac2a5c270123fcef36a14ef259087ea94c` |

成员 CRC、解压长度和本地 SHA-256 全部 PASS。因为没有读取整包所有字节，本轮不声称本地重算了整包官方 MD5。

## ZMIZ1 结果

| cell | SNPs | PP.H3 | PP.H4 | H4 ratio | top SNP | 解释 |
|---|---:|---:|---:|---:|---|---|
| NK | 826 | 0.001732 | 0.998255 | 0.998268 | chr10_79287258_G_A | supportive replication |
| NK_CD56bright | 826 | 0.926773 | 0.019352 | 0.02045 | chr10_79287258_G_A | distinct signal favored |

TenK gene-level NK ZMIZ1：ACAT P=`1.52×10^-24`，top variant P=`2.33×10^-27`。Source SuSiE 有两个 credible sets；CS2 位于约 GRCh38 79.278–79.288 Mb，与 disease/coloc top 区域相邻。

## 结论边界

TenK 作者预计算 CSV 未编码其 exact priors、完整 disease byte manifest 和每一项 harmonization 详情，因此不能替代我们的可复算 OneK analysis。它证明相同疾病标签、相同 gene、相同 NK context 在独立资源中有极强的单因果模型 shared-signal support。多信号最终裁决留给后续 source-CS/LD 分析。
""",
)

protocol = """
# R6A2B0 冻结协议：IgAN bounded positive-yield expansion

版本：v1.0，2026-09-14

## 触发原因

R6A2A1 的 strict published-cell benchmark 为 1/3 PASS，2/3 weak-QTL uninformative，未达到直接全24-locus门；但 ZMIZ1/NK 在 OneK robust、在 TenK author-precomputed coloc 强支持，Python/R 数值一致，证明方法链可运行。为保持 completion-first 目标，同时避免无边界全景扫描，增加有界中间阶段。

## 冻结 loci

`TNFSF4/18`、`REL`、`TNFSF8/15`、`REEP3`、`OVOL1/RELA`、`TNFSF12/13`、`TNFRSF13B`、`LIF/OSM`。

这些 locus 均满足：serum IgA nominal 且 risk-direction concordant；存在 OneK source-significant QTL；同 gene 有 TenK compatible broad-cell support；GSE127136 可检测至少一个候选 gene。

## 冻结组合与最大规模

只使用 `R6A2B0_frozen_8locus_183combination_universe.tsv` 的 183 个 OneK cell–gene 组合。疾病侧 combined 为 primary，European/Asian 为 support，最大 549 个 ABF tests。不得在运行后新增 gene/cell。

## 统计门

- priors：`p1=p2=1e-4`；`p12=1e-6, 1e-5, 1e-4`。
- robust：默认 `PP.H4>=0.80` 且 `H4/(H3+H4)>=0.80`，low-p12 不由 H3 主导。
- targeted-LD ambiguity：`H3+H4>=0.50`、H4 ratio≥0.20、尚未 robust、QTL与GWAS覆盖充分。
- sufficient distinct：疾病 min P≤5e-8、QTL min P≤1e-6、所有先验 H4<0.20。
- weak QTL：UNINFORMATIVE，不计阴性。

所有阳性按 locus 计数；同一 locus 多个 cell/gene 不重复充数。

## 出口

- 新增 ≥2 个 robust 或 signal-specific PASS loci：`GO_R6A2B_FULL_24_LOCUS`，因为连同 ZMIZ1 已有至少3个独立 locus。
- 新增 1 个：`CONDITIONAL_GO_ONE_MORE_BOUNDED_BLOCK`，不得直接写主稿。
- 新增 0 且覆盖充分：`HOLD_FULL_24_AND_REASSESS_MANUSCRIPT_DESIGN`。

TenK 只复核 OneK 触发前已冻结的同 gene/相容 cell；不从 TenK 全表反向挑选最佳结果。
"""
(ADMIN / "R6A2B0_bounded_positive_yield_protocol.md").write_text(protocol.strip() + "\n", encoding="utf-8")

write(
    "04_CMM_R6A2A1_最终判定与R6A2B0冻结目标.md",
    """
# CMM R6A2A1：最终判定与 R6A2B0 冻结目标

```text
IgAN_MAIN_PROJECT = CONDITIONAL_GO

R6A2A1 = COMPLETE
PUBLISHED_CELL_PRIMARY_PASS = 1 / 3
PUBLISHED_CELL_PRIMARY_UNINFORMATIVE = 2 / 3
PUBLISHED_CELL_PRIMARY_DISTINCT_FAIL = 0 / 3

ZMIZ1_NK_ONEK = ROBUST_SHARED_SIGNAL
ZMIZ1_NK_TENK = SUPPORTIVE_SINGLE_CAUSAL_REPLICATION
ITGAX_NK = DISTINCT_SIGNAL_FAVORED

STRICT_DIRECT_FULL24_GATE = NOT_MET
METHOD_FAILURE = NO
R6A2B0_BOUNDED_EXPANSION = GO
FULL_24_LOCUS = HOLD
TISSUE_SCALE_ANALYSIS = HOLD
```

## R6A2B0 规模

| locus | OneK cell–gene combinations | genes |
|---|---:|---:|
""" + next_rows + """

合计 183 个组合，最多 549 个三表型 coloc.abf tests。

## 决策逻辑

直接放行24-locus会违反 R6A2A0 的2/3正控门；把项目判 HOLD 又会把两个 weak-QTL uninformative 误当成方法失败。八 locus 有界扩展同时利用 serum-IgA trait support 和双 QTL 资源可复核性，可以用最小新增计算量判断是否具备至少3个独立阳性 locus 的完成潜力。

下一阶段唯一目标：**R6A2B0 — 8-locus/183-combination bounded positive-yield expansion**。
""",
)

write(
    "99_CMM_R6A2A1_详细行动记录_2026-09-14.md",
    """
# CMM R6A2A1 详细行动记录

日期：2026-09-14  
阶段：R6A2A1 — Positive-control signal gate + targeted TenK ZMIZ1 replication  
最终状态：**COMPLETE / CONDITIONAL_GO_R6A2B0**

## 1. 输入接入与历史边界

独立计算 R6A2A0 ZIP SHA-256=`c6efaba124a97ec357d97db8610e5d0eb4125384df68cfb33c4e8f56b66a0177`，ZIP CRC PASS，内部 23/23 checksum PASS。将输入包归档到 `9.Version/staging_downloads/R6A2A0_input`；代码部署到 `2_code/06_intake/igan_r6a2a`；原始详细记录保存在 `7.Report/rounds/R6A2A0`。

R6A2A0 附件只作为 provenance 和分析建议；本轮执行授权来自用户“继续推进、完成后判断下一阶段”。

## 2. 代码 hostile audit

发现官方 R 复核脚本的 `gene==gene` data.table self-comparison，会混合同 locus 多基因。修复为 `gene==gene_id`。发现 runner 依赖 PATH 中的 `Rscript`，但本机 R 已安装而未加入 PATH；固定到工作区 R 4.6.1。Python 6个原始脚本 syntax PASS，synthetic ABF test PASS。

## 3. OneK archive 与 benchmark 构建

完整流式读取 10,344,009,571-byte OneK archive，MD5=`e42239480f40abd21f221c0d77c82cc3`、SHA-256=`63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea`。只提取7个冻结 parquet，加 README/BIM 共9个成员。10/10组合可测，7/7 published-cell primary 可测。

细胞 active donors：Mono_C 851、Mono_NC 690、CD4_NC 980、NK 980。未使用统一980 donor替代 monocyte 的真实 donor 集。

## 4. GWAS harmonization

对 combined、European、Asian 三套 GRCh37 IgAN GWAS扫描三个 ±1 Mb locus。9/9 disease-region objects 均有至少500个 harmonized variants，三个 lead 坐标均存在。palindromic SNP 保守排除；BETA全部调整到 OneK BIM A1。

## 5. OneK coloc

运行30 comparisons；固定 `p12=1e-6/1e-5/1e-4`。combined 只有 ZMIZ1/NK robust。IRF4/DUSP22与ITGAX monocyte均 weak-QTL uninformative。NK/ITGAX 为强 H3、低 H4 distinct signal。combined ambiguity trigger=0，因此没有为这些组合批量生成LD。

官方 R coloc 5.2.3 产生90 prior-specific rows；与 Python 最大 PP.H4差 `1.33×10^-15`。

## 6. TenK 定向复核

检查 Zenodo 记录后确认 author-precomputed `coloc_100kb.zip` 含 `kiryluk_IgAN`。整包下载速度不稳定，停止低效的626 MB复制；安装 `remotezip 0.12.6` 做目录侦察，随后编写有重试、CRC与长度验证的 Range ZIP parser，只提取 NK/chr10 和 NK_CD56bright/chr10 两个预冻结成员。

ZMIZ1/NK author result：826 SNP，PP.H4=0.998255，H4 ratio=0.998268；NK_CD56bright 则 H3 favored。TenK gene-level与SuSiE本地包进一步确认 NK ZMIZ1 强QTL并存在两个source credible sets。

## 7. 科学裁决

严格2/3 published-cell门未通过，禁止直接宣告 full-24 GO；但一条 OneK robust + TenK supportive replication、90-row R复算和充分GWAS覆盖排除了“实现完全失效”。两个 primary non-pass 都是QTL太弱，不能计作反证。因此 IgAN从 GO调整为 `CONDITIONAL_GO`，进入8-locus bounded positive-yield expansion。

## 8. 下一阶段冻结

R6A2B0 只使用8个其余 serum-IgA同向 locus和183个预先存在的 OneK/TenK-compatible cell–gene combinations，最多549个tests。新增至少2个独立locus通过才放行full24；新增0且覆盖充分则暂停全景。

## 9. 依赖与大文件策略

新增 Python 包：`remotezip 0.12.6`。用户再次明确大文件和长计算可以交付脚本由其运行；后续如需新增完整 TenK 100 kb/1 Mb QTL，将提供断点续传、官方MD5、统一runner和回传清单。本轮通过Range只取得两个目标成员，无需用户下载16.6 GB大包。

本轮无Office文档，不涉及WPS或LibreOffice渲染。

## 10. 质控

- upstream ZIP CRC/checksum PASS；
- OneK archive byte/hash PASS；
- benchmark 10/10 testable；
- harmonized regions 9/9 PASS；
- Python/R 90/90数值一致；
- TenK target member CRC/length/SHA PASS；
- Python `py_compile`、JSON解析、结果不变量、发布包CRC与内部checksums均在发布前复核。
""",
)

write(
    "README.md",
    """
# R6A2A1 report set

本目录记录校正后的10-combination正控signal gate、Python/R复算、ZMIZ1/NK TenK定向复核以及R6A2B0有界扩展决策。

阅读顺序：`00` → `01` → `02` → `03` → `04` → `99`。
""",
)

write(
    "SOURCES_CHECKED_2026-09-14.md",
    """
# R6A2A1 sources checked — 2026-09-14

| Source | Use |
|---|---|
| https://pmc.ncbi.nlm.nih.gov/articles/PMC11824687/ | Published DICE cell-specific benchmark definitions |
| https://chr1swallace.github.io/coloc/ | Official coloc method/package behavior |
| https://zenodo.org/records/18910121 | OneK1K full cis-eQTL/genotype provenance |
| https://zenodo.org/records/18221260 | TenK10K full QTL, SuSiE and precomputed coloc archive metadata |

所有本轮数值结论来自实际工作区字节、官方 R 包复算和定向提取的 TenK 成员，不来自网页摘要。
""",
)

portfolio = {
    "schema_version": "1.0",
    "frozen_at": "2026-09-14",
    "decision_id": "R6A2A1",
    "ssc": {"status": "FROZEN_ARCHIVE"},
    "mg": {"regulatory_main_status": "NO_GO", "default_resume": False},
    "primary_project": {
        "project": "IGA_NEPHROPATHY",
        "status": "CONDITIONAL_GO",
        "completed_stage": "R6A2A1_POSITIVE_CONTROL_SIGNAL_GATE",
        "validated_anchor": "ZMIZ1_NK",
        "next_stage": "R6A2B0_BOUNDED_POSITIVE_YIELD_EXPANSION",
        "full_24_locus_status": "HOLD",
    },
    "data_policy": {"open_data_only": "HARD_CONSTRAINT", "permission_required_data": "EXCLUDED"},
}
(ADMIN / "project_portfolio_state_R6A2A1.json").write_text(json.dumps(portfolio, indent=2, ensure_ascii=False), encoding="utf-8")

# Preserve the corrected upstream record as provenance.
input_dir = ROUND / "inputs"
input_dir.mkdir(exist_ok=True)
for src in [
    Path(r"C:\Users\Administrator\Downloads\99_CMM_R6A2A0_详细行动记录_2026-09-14.md"),
    Path(r"C:\Users\Administrator\Downloads\CMM_R6A2A0_IgAN_PositiveControlBenchmarkCorrection_2026-09-14.zip"),
]:
    if src.exists():
        # The ZIP is already preserved under 9.Version; only link-level provenance
        # is needed here, so avoid duplicating it in the report tree.
        if src.suffix.lower() == ".md":
            shutil.copy2(src, input_dir / src.name)

print(CURRENT)
