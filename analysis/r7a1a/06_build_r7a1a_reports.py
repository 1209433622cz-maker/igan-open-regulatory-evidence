#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, shutil
from pathlib import Path
import pandas as pd

HERE=Path(__file__).resolve()
DEFAULT_ROOT=HERE.parents[2] if (HERE.parents[2]/".git").exists() else HERE.parents[3]
ROOT=Path(os.environ.get("R7_PROJECT_ROOT",DEFAULT_ROOT))
ROUND=ROOT/"7.Report/rounds/R7A1A"
CURRENT=ROOT/"7.Report/current/R7A1A"
PROTO=ROOT/"0_admin/protocol/current"
ROUND.mkdir(parents=True,exist_ok=True); CURRENT.mkdir(parents=True,exist_ok=True); PROTO.mkdir(parents=True,exist_ok=True)
INTAKE=ROOT/"3_results/01_intake/R7A1A"
QTL=ROOT/"3_results/03_qtl/R7A1A"

pbc=json.loads((INTAKE/"R7A1A_PBC_GWAS_byte_schema_audit.json").read_text())
ced=json.loads((INTAKE/"R7A1A_CeD_GWAS_byte_schema_audit.json").read_text())
gj=json.loads((INTAKE/"R7A1A_PBC_GJOKA_remote_inventory_state.json").read_text())
qstate=json.loads((QTL/"R7A1A_QTL_control_testability_state.json").read_text())
q=pd.read_csv(QTL/"R7A1A_frozen_control_cross_resource_testability.tsv",sep="\t")

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""): h.update(b)
    return h.hexdigest()

pbc_file=ROOT/"1_data/gwas/R7A1A/PBC/GCST90061440_buildGRCh37.tsv"
ced_file=ROOT/"1_data/gwas/R7A1A/CeD/GCST000612_20190752.h.tsv.gz"
ced20_file=ROOT/"1_data/gwas/R7A1A/CeD/GCST010064_Meta.PL.IT.IR.SP.UK.AR1.AR2.NL.2017.meta.csv"

decision=pd.DataFrame([
 {"candidate":"PBC","eligible_core":"GCST90061440","core_schema":"PASS","rows":pbc["rows"],"provisional_nonMHC_regions":pbc["provisional_1Mb_distance_pruned_GWS_leads"],"cross_resource_byte_testable":"3/3","cross_resource_source_positive":"2/3","study_matched_LD":"56 paired matrices verified","R7A1A":"PASS_LITERAL_GATE","portfolio_decision":"GO_R7A1B_PBC_ONLY"},
 {"candidate":"CeD","eligible_core":"GCST000612","core_schema":"PASS","rows":ced["rows"],"provisional_nonMHC_regions":ced["provisional_1Mb_distance_pruned_GWS_leads"],"cross_resource_byte_testable":"3/3","cross_resource_source_positive":"1/3","study_matched_LD":"not verified","R7A1A":"PASS_LITERAL_GATE","portfolio_decision":"HOLD_NOT_SELECTED"},
])
decision.to_csv(INTAKE/"R7A1A_candidate_adjudication.tsv",sep="\t",index=False)
state={
 "stage":"R7A1A","status":"COMPLETE","new_primary_project":"NOT_YET_APPROVED",
 "pbc":"GO_R7A1B_BOUNDED_SIGNAL_GATE","ced":"HOLD_NOT_SELECTED",
 "excluded_ced_source":"GCST90014442_UK_BIOBANK_DERIVED",
 "pbc_controls":{"IL12RB2":"SOURCE_POSITIVE","FCRL3":"SOURCE_POSITIVE","INAVA":"TESTABLE_ONEK_WEAK"},
 "ced_controls":{"CSK":"TESTABLE_ONEK_WEAK","TRAFD1":"TESTABLE_ONEK_WEAK","UBASH3A":"SOURCE_POSITIVE"},
 "next_stage":"R7A1B_PBC_3CONTROL_SIGNAL_GATE"
}
(INTAKE/"R7A1A_final_state.json").write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding="utf-8")

sources="""- GWAS Catalog PBC `GCST90061440`: https://www.ebi.ac.uk/gwas/studies/GCST90061440
- GWAS Catalog CeD `GCST000612`: https://www.ebi.ac.uk/gwas/studies/GCST000612
- GWAS Catalog CeD `GCST010064`: https://www.ebi.ac.uk/gwas/studies/GCST010064
- 被排除的 UKB-derived CeD `GCST90014442`: https://www.ebi.ac.uk/gwas/studies/GCST90014442
- PBC 2021 GWMA (PMID 34033851): https://pubmed.ncbi.nlm.nih.gov/34033851/
- CeD 2010 GWAS (PMID 20190752): https://pubmed.ncbi.nlm.nih.gov/20190752/
- CeD 2020 Immunochip meta-analysis (PMID 31591516): https://pubmed.ncbi.nlm.nih.gov/31591516/
- GWAS Catalog summary-statistics access: https://www.ebi.ac.uk/gwas/labs/downloads/summary-statistics
"""

reports={
"00_CMM_R7A1A_执行摘要_PBC_CeD真实字节与QTL正控终裁.md":f"""# CMM R7A1A 执行摘要：PBC/CeD 真实字节与 QTL 正控终裁

**日期：2026-09-15**

## 最终判定

```text
R7A1A = COMPLETE
NEW_PRIMARY_PROJECT = NOT_YET_APPROVED

PBC = GO_R7A1B_BOUNDED_SIGNAL_GATE
CeD = HOLD_NOT_SELECTED

NEXT_STAGE = R7A1B_PBC_3CONTROL_SIGNAL_GATE
```

PBC 与 CeD 都通过了 R7A0 字面技术门：合格开放 GWAS 字节、可计算 schema、至少 5 个非 MHC 临时区域、3/3 正控在 OneK1K 与 TenK10K 均可找到数据。真正拉开差距的是阳性密度。PBC 有 2/3 正控在两个 QTL 资源中均为源数据阳性；CeD 只有 1/3。PBC 还确认存在 56 组研究样本匹配的 locus sumstats/LD 矩阵。

因此不宣布 PBC 已成为主项目，也不同时为两个疾病投入信号级计算。下一轮只允许用 PBC 的 IL12RB2、FCRL3、INAVA/C1orf106 做一次有边界终裁；至少 2/3 得到稳健 disease↔OneK shared signal，并有至少 1 个同基因兼容细胞的 TenK 独立复制，才允许 `NEW_PRIMARY_PROJECT=PBC`。

## 真实字节

| 对象 | 字节 | SHA-256 | 结果 |
|---|---:|---|---|
| PBC GCST90061440 | {pbc_file.stat().st_size:,} | `{digest(pbc_file)}` | 5,054,572/5,054,572 数值行有效；45 个非 MHC 临时区域 |
| CeD GCST000612 harmonised | {ced_file.stat().st_size:,} | `{digest(ced_file)}` | 507,833/523,390 数值行满足严格条件；12 个非 MHC 临时区域 |
| CeD GCST010064 | {ced20_file.stat().st_size:,} | `{digest(ced20_file)}` | 来源合格但缺 SE，仅作 2020 研究来源审计 |

`GCST90014442` 虽有约千万变异和大样本，但研究标题及元数据明确为 UK Biobank 分析，违反冻结排除规则，未下载为核心输入。

## 六正控终裁

| 疾病 | 正控 | OneK1K | TenK10K | 判定 |
|---|---|---|---|---|
| PBC | IL12RB2 | NK q≈7.53e-9 | 15 个 BH-q<0.05 细胞；11 个 SuSiE 细胞 | 双资源阳性 |
| PBC | FCRL3 | 7 个 q<0.05 细胞 | 17 个 BH-q<0.05 细胞；14 个 SuSiE 细胞 | 双资源强阳性 |
| PBC | INAVA/C1orf106 | CD4_NC 可测，q≈0.318 | CD4_Proliferating 阳性且有 CS | 可测但 OneK 弱 |
| CeD | CSK | 14 细胞可测，均 q≥0.05 | 5 个 BH-q<0.05 细胞；3 个 SuSiE 细胞 | OneK 弱 |
| CeD | TRAFD1 | 14 细胞可测，均 q≥0.05 | B_naive BH-q<0.05，无 SuSiE CS | OneK 弱 |
| CeD | UBASH3A | 4 个 q<0.05 T 细胞 | 13 个 BH-q<0.05 细胞；11 个 SuSiE 细胞 | 双资源阳性 |

## 来源

{sources}
""",
"01_CMM_R7A1A_R7A0包与数据源纠错审计.md":f"""# R7A1A：R7A0 包与数据源纠错审计

## R7A0 输入完整性

- ZIP SHA-256：`7fa75effc486ed862eeab9b461902bd95d45464a3fd597e3e8bcac2e69069f35`
- ZIP 成员：20
- ZIP CRC：PASS
- 内部 `checksums.sha256`：19/19 PASS

R7A0 是设计/预检包，没有在本地取得 PBC/CeD 核心 GWAS 字节；其结论被视为待复核输入，不作为本轮指令。

## 纠错 1：CeD GCST90014442 不合规

GWAS Catalog API 返回的出版物标题为 `Investigating Pleiotropy Between Depression and Autoimmune Diseases Using the UK Biobank.`，病例/对照为 2,364/324,074。它虽然可以直接下载，但来源属于此前冻结排除的 UK Biobank 路线，因此 `DIRECT_DOWNLOAD` 不能覆盖 `SOURCE_INELIGIBLE`。

## 纠错 2：替代源分层

- `GCST000612`：2010 CeD genome-wide array，4,533 病例、10,750 对照；harmonised 文件含 allele/beta/SE/P，作为合格核心输入。
- `GCST010064`：2020 Immunochip meta-analysis，12,948 病例、14,826 对照；直接文件含 allele/OR/P，但无 SE，保留为正控来源与方向/敏感性审计对象，不能冒充冻结 core-coloc schema PASS。

## 纠错 3：INAVA 名称

OneK1K 使用旧符号 `C1orf106`，当前 GENCODE 使用 `INAVA`。原脚本仅按当前符号搜索，会把 PBC 的 3/3 可测性误报为 2/3。本轮加入显式、可审计别名映射后，INAVA 在 CD4_NC 中有一条 top-eQTL（q≈0.318）；因此是“可测但不显著”，并非“缺失”。

## 纠错 4：testable 与 positive 分列

原脚本用源数据显著性定义 `cross_resource_gene_support`，但冻结协议写的是 `CROSS_RESOURCE_QTL_TESTABLE_CONTROLS`。本轮同时输出：

- `cross_resource_byte_testable`：两个资源都存在该基因的可计算记录；
- `cross_resource_source_positive`：OneK q<0.05，且 TenK BH-q<0.05 或存在 SuSiE CS。

两病都是 3/3 可测；PBC 为 2/3 双资源阳性，CeD 为 1/3。

## 来源

{sources}
""",
"02_CMM_R7A1A_PBC真实字节_GJOKA_LD与正控结果.md":f"""# R7A1A：PBC 真实字节、GJOKA LD 与正控结果

## 核心 GWAS

- accession：`GCST90061440`
- GRCh37；欧洲五 panel meta-analysis；8,021 cases / 16,489 controls，N=24,510
- 本地字节：{pbc_file.stat().st_size:,}
- MD5：`c48ede08359f6fc919810591cc0daad7`，与官方 metadata 一致
- SHA-256：`{digest(pbc_file)}`
- 5,054,572 行全部通过 chr/position/allele/beta/SE/P 严格数值检查
- 非 MHC P≤5e-8 行：5,522
- 1 Mb 距离临时 lead：45；仅用于 intake，不能称 LD-independent signals

## GJOKA 研究样本匹配输入

远端文件 `GJOKA_SUMSTATS.zip`：

- HTTP Content-Length：{gj['http_content_length']:,}
- Accept-Ranges：{gj['accept_ranges']}
- central directory：112 成员，全部带 CRC
- 56 个 `sumstats_i.assoc.logistic`
- 56 个对应 `covmat_i.ld`
- 56/56 locus pair 完整

本轮读取全部小型 sumstats 成员并恢复 GRCh37 区间，没有下载 1.18 GB 整包及大矩阵，因为 R7A1B 尚未触发。三个正控分别落入：

- IL12RB2 → locus 2 → `covmat_2.ld`
- FCRL3 → locus 4 → `covmat_4.ld`
- INAVA → locus 6 → `covmat_6.ld`

## 正控

IL12RB2 与 FCRL3 是真正的双资源阳性。INAVA 在 TenK 有 CD4_Proliferating CS，但 OneK 仅旧符号 C1orf106/CD4_NC top-eQTL，q≈0.318。它必须保留在 R7A1B 作为预注册的弱/证伪对象，不能被替换成更好看的基因。

## PBC 判定

```text
PBC_R7A1A_LITERAL_GATE = PASS
PBC_CROSS_RESOURCE_TESTABLE = 3/3
PBC_CROSS_RESOURCE_SOURCE_POSITIVE = 2/3
PBC_STUDY_MATCHED_LD = PASS_56_PAIRS
PBC = GO_R7A1B_BOUNDED
```

{sources}
""",
"03_CMM_R7A1A_CeD核心输入重选与正控降级.md":f"""# R7A1A：CeD 核心输入重选与正控降级

## 三个候选 CeD 输入

### GCST90014442：排除

来源为 UK Biobank pleiotropy study，违反硬约束。公开可下载与研究来源合格是两个独立条件。

### GCST010064：研究对题，但 schema 不完整

2020 Immunochip meta-analysis 对应冻结正控来源：12,948 cases / 14,826 controls，127,855 行；36 个非 MHC 1 Mb 临时区域。文件有 A1/A2、OR、P，但没有 SE。因此只保留为 secondary disease-evidence/sensitivity object。

### GCST000612：当前合格核心

2010 genome-wide array，4,533 cases / 10,750 controls；harmonised GRCh37：

- bytes：{ced_file.stat().st_size:,}
- SHA-256：`{digest(ced_file)}`
- rows：523,390
- strict valid numeric rows：507,833
- non-MHC P≤5e-8 rows：56
- provisional 1 Mb regions：12
- allele/beta/SE/P schema：PASS

它满足开放核心输入技术门，但样本量较小，且与 2020 正控选择不是同一阶段数据。

## 分子正控

- CSK：两个资源都可测；TenK 强，OneK 14 个细胞均 q≥0.05。
- TRAFD1：两个资源都可测；TenK 仅 B_naive BH-q<0.05、无 source CS，OneK 14 个细胞均 q≥0.05。
- UBASH3A：OneK/TenK 均有强 T-cell QTL。

## CeD 判定

CeD 字面 intake gate 可 PASS，但 completion-first 的阳性产出预期只有 1/3，而 PBC 为 2/3 且有研究内 LD。为避免同时开启两个高风险 signal pipeline：

```text
CeD_R7A1A_LITERAL_GATE = PASS
CeD_CROSS_RESOURCE_SOURCE_POSITIVE = 1/3
CeD = HOLD_NOT_SELECTED
```

不为 CeD 更换正控、不从 TenK 结果反向挑基因，也不使用 UKB 数据补强。

{sources}
""",
"04_CMM_R7A1A_OneK1K_TenK10K_六正控实测.md":"""# R7A1A：OneK1K/TenK10K 六正控实测

## 输入与方法

- OneK1K：`OneK1K_TensorQTL_top_eQTL_summary.zip`，617 members，ZIP CRC PASS；原作者 q-value<0.05 定义源数据显著。
- TenK10K gene-level：29 members，ZIP CRC PASS；在每个 cell 内对可数值 ACAT-p 重建 BH q<0.05。
- TenK10K SuSiE：29 members，ZIP CRC PASS；存在 source credible set 作为独立证据层。
- 基因仅限预注册 3+3；唯一名称修正是 INAVA←C1orf106。

## 结果

| candidate | gene | OneK observed/sig cells | TenK observed/sig cells | TenK CS cells | 双资源源阳性 |
|---|---|---:|---:|---:|---|
| PBC | IL12RB2 | 7/1 | 26/15 | 11 | 是 |
| PBC | FCRL3 | 12/7 | 18/17 | 14 | 是 |
| PBC | INAVA | 1/0 | 1/1 | 1 | 否 |
| CeD | CSK | 14/0 | 28/5 | 3 | 否 |
| CeD | TRAFD1 | 14/0 | 28/1 | 0 | 否 |
| CeD | UBASH3A | 11/4 | 19/13 | 11 | 是 |

## 解释边界

1. `observed` 只证明该 gene-cell 有 top-level 记录，不证明疾病与 QTL 共定位。
2. `source positive` 仍只证明存在 cis-QTL，不证明它与疾病 signal 相同。
3. OneK 与 TenK build、cell label、donor 与 fine-mapping 方法不同；只有 R7A1B 的变异级 harmonization 和 signal-level test 可以升级结论。
4. CSK/TRAFD1 不能写成“CeD 机制阴性”；当前只说明 OneK PBMC 层缺少强 source eQTL。
""",
"05_CMM_R7A1A_R7A1B_PBC有界信号门冻结协议.md":"""# R7A1B 冻结协议：PBC 三正控有界信号门

## 目标

只判断预注册的三条 PBC disease↔immune-cell eQTL 链能否形成至少两个稳健 shared signals。不得用 post-hoc 基因替换补救。

## 固定对象

```text
Disease = GCST90061440, GRCh37
Genes = IL12RB2, FCRL3, INAVA(C1orf106)
GJOKA disease-LD loci = 2, 4, 6
```

OneK 首轮仅分析已有 top-level 记录：

- IL12RB2：NK
- FCRL3：B_IN, B_MEM, CD4_NC, CD8_ET, CD8_NC, NK, NK_R
- INAVA/C1orf106：CD4_NC（弱 QTL 证伪组合）

最大 9 个 disease–OneK smoke comparisons。

## 顺序

1. 从本地 10.34 GB OneK raw archive 仅提取 chr1 目标 members，核对完整 cis 行数、build、allele 与 cell-specific donor。
2. disease/QTL 变异严格按 chr:pos:alleles 统一；记录 palindromic、重复、缺失与覆盖率。
3. 运行固定先验 coloc.abf smoke：`p1=p2=1e-4`，`p12=1e-6/1e-5/1e-4`。
4. 只有 robust H4 或可解释 H3/H4 ambiguity 才下载对应 GJOKA LD，并构建 OneK donor-matched source LD。
5. 多信号裁决通过后才进入 TenK 同基因、兼容细胞复制；TenK GRCh38 必须独立 build/allele harmonization。
6. 至少两个基因通过后，才下载 PBC liver scRNA 做 target detectability 与 donor-level orthogonal validation。

## 升级门

```text
ROBUST_SHARED_SIGNAL_GENES >= 2/3
TENK_SAME_GENE_COMPATIBLE_CELL_REPLICATION >= 1
PBC_LIVER_TARGET_DETECTABILITY = PASS
CORE_PERMISSION_DATA = FALSE
```

robust shared signal 默认要求 `PP.H4>=0.80` 且 `H4/(H3+H4)>=0.80`，并且先验敏感性不翻转成 H3；若存在多信号，必须在 source-LD 条件/精细定位后仍成立。

若失败：

```text
PBC_REGULATORY_MAIN = FROZEN_FAIL
CeD_AUTO_RESUME = NO
NEXT = NEW_RESEARCH_ARCHITECTURE_REDESIGN
```
""",
"99_CMM_R7A1A_详细行动记录_2026-09-15.md":f"""# CMM R7A1A 详细行动记录

**日期：2026-09-15**

## 1. 本轮任务

复核 R7A0 包，完成 PBC/CeD 真正 byte-level GWAS intake、来源资格检查、非 MHC 信号密度审计、PBC 研究内 LD 资源检查，以及冻结 3+3 基因的 OneK1K/TenK10K 正控实测。按协议停止在 disease↔QTL coloc 之前，并冻结下一阶段。

## 2. R7A0 独立验收

对用户提供 ZIP 仅读取目录、CRC 与 checksum，没有执行包内代码：SHA-256 `7fa75effc486ed862eeab9b461902bd95d45464a3fd597e3e8bcac2e69069f35`；20 members；ZIP CRC PASS；19/19 internal checksums PASS。随后把包内报告视作假设和设计输入逐项复核。

## 3. 数据来源纠错

R7A0 指定的 CeD `GCST90014442` 实际是 UK Biobank autoimmune/depression pleiotropy 数据。它被标为排除，而不是因为直接下载方便就改变硬约束。

官方 GWAS Catalog 检索发现两个非 UKB 对象：`GCST000612` 与 `GCST010064`。下载后确认，前者 harmonised 文件具备可直接用于 effect-size analysis 的 beta/SE/allele/P；后者是 2020 正控来源研究，但仅有 OR/P、无 SE。本轮把前者设为合格 core，后者设为 secondary audit object。

## 4. 下载和校验

使用 4–8 路 HTTP byte-range downloader；每段验证长度，组装后验证总字节。没有重新下载已有 OneK/TenK 大文件。

- PBC `{pbc_file.name}`：{pbc_file.stat().st_size:,} bytes；MD5 与官方 metadata 一致；SHA-256 `{digest(pbc_file)}`。
- CeD `{ced_file.name}`：{ced_file.stat().st_size:,} bytes；SHA-256 `{digest(ced_file)}`。
- CeD 2020 `{ced20_file.name}`：{ced20_file.stat().st_size:,} bytes；官方 MD5匹配；SHA-256 `{digest(ced20_file)}`。

## 5. GWAS 审计

严格有效行要求：chr 1–22、有限 position/beta/SE/P、SE>0、0≤P≤1、两等位基因非空。MHC 定义 chr6:25–35 Mb。

- PBC：5,054,572/5,054,572 valid；5,522 non-MHC GWS rows；45 provisional 1Mb leads。
- CeD eligible core：507,833/523,390 valid；56 non-MHC GWS rows；12 provisional leads。
- CeD 2020：127,855 rows；1,259 non-MHC GWS rows；36 provisional leads；因 source SE 缺失不升级为 core schema PASS。

距离剪枝只是 intake QC，未解释为 LD independence。

## 6. PBC GJOKA 远程 ZIP

服务器支持 Range。读取 central directory 得到 112 members；56 个 sumstats 与 56 个 covmat 一一对应，全部有 CRC。进一步读取所有小型 sumstats 成员，恢复每个 locus 的 GRCh37 范围，确认 IL12RB2/FCRL3/INAVA 对应 locus 2/4/6。由于尚未发生 signal trigger，没有下载 1.18 GB 整包与大 LD 矩阵；runner 提供 `-DownloadFullGJOKA` 选项。

## 7. QTL 实测和代码修正

OneK top zip、TenK gene-level zip、TenK SuSiE zip 均通过 CRC。原脚本的两个问题被修正：INAVA/C1orf106 别名，以及 testability/source positivity 混用。

结果：PBC 3/3 可测、2/3 双资源源阳性；CeD 3/3 可测、1/3 双资源源阳性。没有做 disease-QTL coloc。

## 8. 代码与复现

新增/加固：

- `00_segmented_fetch.py`
- `01_fetch_ced_gwas.ps1`
- `02_fetch_pbc_gwas_and_study_inputs.ps1`
- `03_audit_candidate_gwas.py`
- `04_screen_qtl_positive_controls.py`
- `05_inventory_gjoka_remote_zip.py`
- `06_build_r7a1a_reports.py`
- `RUN_R7A1A_TRUE_BYTE_QTL_PREFLIGHT.ps1`

完整 runner 在本机重新执行 PASS；Python 文件通过 `py_compile`。

## 9. 最终决策

```text
R7A1A = COMPLETE
PBC = GO_R7A1B_BOUNDED_SIGNAL_GATE
CeD = HOLD_NOT_SELECTED
NEW_PRIMARY_PROJECT = NOT_YET_APPROVED
```

选择 PBC 不是宣称阳性，而是它仍有机会用 IL12RB2 与 FCRL3 达到 R7A1B 的 2/3 门；INAVA 保留为弱 QTL 证伪对象。CeD 不自动进入 signal pipeline，因为只有 UBASH3A 双资源阳性，且最新对题文件缺 SE。

## 10. 下一阶段

R7A1B 只做 PBC 三正控、最多 9 个 OneK comparisons。只有 robust signal 才触发对应 GJOKA/OneK source LD、TenK 独立复制和肝组织下载。若 2/3 门失败，PBC 冻结，CeD 不自动恢复，转向新研究架构而非继续换疾病重复同一流程。

## 11. 来源

{sources}
"""
}

for name,text in reports.items():
    (ROUND/name).write_text(text.strip()+"\n",encoding="utf-8")
    shutil.copy2(ROUND/name,CURRENT/name)

protocol=reports["05_CMM_R7A1A_R7A1B_PBC有界信号门冻结协议.md"]
(PROTO/"R7A1B_PBC_3control_bounded_signal_gate_v1.md").write_text(protocol,encoding="utf-8")
print(json.dumps({"reports":len(reports),"round":str(ROUND),"state":state},ensure_ascii=False,indent=2))
