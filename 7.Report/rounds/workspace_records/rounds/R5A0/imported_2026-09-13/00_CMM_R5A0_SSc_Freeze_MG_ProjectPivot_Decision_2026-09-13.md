# CMM R5A0 — SSc 冻结与 MG 主项目正式切换决策

**日期：2026-09-13**  
**性质：项目级冻结决策 / 新主线启动基线**

## 1. 正式决策

自本轮起：

```text
SSc_SEX_SPECIFIC_Q1_MAIN = FROZEN_ARCHIVE
SSc_FORCE_SALVAGE = NO
SSc_DEFAULT_RESUME = NO

PRIMARY_PROJECT = MYASTHENIA_GRAVIS
PRIMARY_QUESTION = EOMG_vs_LOMG_REGULATORY_GENETICS

OPEN_DATA_ONLY = HARD_GATE
PERMISSION_REQUIRED_DATA = EXCLUDED
AUTHOR_EMAIL_REQUIRED_DATA = EXCLUDED
DAC_EGA_DBGAP_UKB_APPLICATION = EXCLUDED
GREEN_LIBRARY_OR_FORM_EMAIL_DOWNLOAD = EXCLUDED
```

这不是判定 SSc 科学问题无价值，而是基于新的数据治理硬约束主动停止一条关键输入不可公开复现的主论文路线。

## 2. SSc 资产处置

### 保留并迁移
- P0 provider identity gate
- H6 schema/readiness gate
- variant identity: chr:pos:ref:alt@build
- allele/build harmonization
- exact-overlap auditing
- source-CS PIP coverage gate
- LD symmetry/diag/PSD/finite QC
- z–LD diagnostics
- hostile validator / regression fixtures
- GO / HOLD / FAIL / FALSIFIED / UNTESTABLE 状态机
- release checksum / provenance / audit trail
- Nature-style figure QC
- donor-level pseudobulk原则
- bounded gene competition原则
- classic coloc prior-sensitivity审计

### 不迁移为 MG 结论
- SYNGR1 生物学结论
- IL12RB2 生物学故事
- SSc sex-specific claim
- SSc manuscript prose
- SSc tissue interpretation

### SSc 恢复条件
只有未来关键 sex-specific SSc summary statistics 和所需分析输入真正变为无需申请的公开数据时，才重新建立独立恢复评估；不自动恢复为主项目。

## 3. 新主项目

### 疾病
Myasthenia gravis (MG)

### 主轴
Early-onset MG (EOMG) versus late-onset MG (LOMG)

### 核心科学问题
哪些非-MHC遗传信号真正区分 EOMG 与 LOMG，并能否被解析为在独立公开单细胞遗传资源中可复现的免疫细胞特异调控机制？

### 目标证据链

```text
Overall MG / EOMG / LOMG GWAS
        ↓
formal subtype effect heterogeneity
        ↓
non-MHC locus prioritization
        ↓
OneK1K cell-eQTL + public source genotype / QTL LD
        ↓
TenK10K independent cell-eQTL replication
        ↓
signal-level disease–QTL adjudication
        ↓
MG PBMC disease-state validation
        ↓
EOMG thymus localization
        ↓
integrated subtype regulatory model
```

## 4. 新项目 Gate 0

进入正式分析前必须确认：

1. disease GWAS 可直接公开下载，不需要权限；
2. genome-wide summary 而不是 top hits；
3. build 可确认；
4. effect allele / other allele 或 REF/ALT 可解释；
5. beta/OR 与 SE/P 足以支持 subtype effect comparison；
6. 至少有两个公开 single-cell QTL resource；
7. 至少一个 QTL resource 有公开 genotype 或可验证 source fine-mapping；
8. 至少一个公开 MG disease-tissue dataset 支持 donor-level analysis；
9. 不依赖申请数据才能形成主要结论；
10. 预注册后禁止结果导向换细胞、扩窗口、换LD参考。

任一关键门失败，必须 HOLD/RESELECT，不用低证据方法补故事。

## 5. 当前已确认的公开资源入口

### Disease GWAS
计划使用 GWAS Catalog:
- GCST90432156 — overall MG
- GCST90432157 — EOMG
- GCST90432158 — LOMG

下一阶段必须对三个对象做真实 byte-level intake，而不是只依据论文说明。

### Primary molecular QTL
OneK1K 2026:
- full cis-eQTL summary
- 14 immune cell types
- 980-donor processed PLINK genotype
- covariates
- public Zenodo distribution

其关键价值是：可以在不申请 individual-level controlled data 的情况下重建 QTL-side source-matched LD。

### Independent molecular replication
TenK10K Phase 1:
- 28 immune cell types
- common full cis-eQTL ±100 kb
- source fine-mapping summaries
- public Zenodo distribution

TenK10K 在 MG 项目中优先作为 independent molecular replication，而不是要求受控 WGS 才允许整个项目推进。

### Disease tissue
优先级：
1. GSE297547 — MG + healthy control PBMC, scRNA + AbSeq，适合主 disease-state validation；
2. GSE227835 — MG PBMC，适合独立/亚型敏感性验证；
3. GSE233180 — 12 immunotherapy-naïve AChR-Ab+ EOMG thymus，适合 EOMG disease-state localization；不作为健康对照 DE 队列。

## 6. 论文设计冻结原则

### 主文避免
- “显著 vs 不显著 = 亚型差异”
- MHC 复杂区域作为第一个 mechanism showcase
- DEG→PPI→hub
- WGCNA救故事
- MR筛一堆基因
- drug network / docking
- 看到结果后增加细胞
- 单一高PP4替代完整signal adjudication
- cell-level pseudo-replication

### 主文优先
- EOMG/LOMG effect-size heterogeneity
- 非-MHC clean loci
- cross-resource QTL replication
- source-aware LD
- bounded gene competition
- donor-level tissue statistics
- negative / discordant loci
- 可证伪的证据等级

## 7. 主图初稿

- Figure 1 — Overall/EOMG/LOMG genetic architecture + formal heterogeneity
- Figure 2 — non-MHC locus prioritization / regional signal structure
- Figure 3 — OneK1K cell-specific regulatory resolution
- Figure 4 — TenK10K cross-resource replication + gene competition
- Figure 5 — MG PBMC donor-level validation + EOMG thymus localization
- Figure 6 — integrated subtype regulatory model

## 8. 下一阶段

```text
NEXT_STAGE = R5A1_MG_BYTE_LEVEL_PREFLIGHT
```

R5A1 不写论文、不下载大组织数据、不提前扩大候选基因。

必须先完成：

1. GCST90432156/157/158 三份 GWAS 实际字节下载；
2. SHA-256 / bytes / row counts / provenance；
3. schema 审计；
4. build 与 allele orientation；
5. sample-size / phenotype definitions；
6. non-MHC genome-wide significant loci；
7. EOMG-vs-LOMG exact variant overlap；
8. formal beta heterogeneity可计算性；
9. top loci × OneK1K coverage；
10. top loci × TenK10K coverage；
11. tissue target detectability preflight；
12. MG GO / HOLD / RESELECT 判定。

### GO_MG最低标准

```text
ALL_3_GWAS_BYTES = PASS
SCHEMA_FOR_HETEROGENEITY = PASS
NON_MHC_TESTABLE_LOCI >= 2
ONEK1K_QTL_TESTABLE >= 1 high-priority locus
TENK10K_REPLICATION_TESTABLE >= 1 same high-priority locus
PUBLIC_TISSUE_VALIDATION = FEASIBLE
NO_PERMISSION_DATA_REQUIRED_FOR_CORE_CLAIM = TRUE
```

只有达到这些条件，才进入：

```text
R5A2_MG_LOCUS_PILOT
```

## 9. 最终项目状态

```text
OLD_PRIMARY = SSc sex-specific regulatory genetics
OLD_PRIMARY_STATUS = FROZEN_ARCHIVE

NEW_PRIMARY = MG EOMG-vs-LOMG regulatory genetics
NEW_PRIMARY_STATUS = PRE-FLIGHT

PUBLIC_ONLY_POLICY = HARD_CONSTRAINT

CURRENT_GOAL =
VERIFY_BYTES_FIRST
THEN_TEST_HETEROGENEITY
THEN_SELECT_LOCI
THEN_RUN_QTL
THEN_RUN_TISSUE

NO_STORY_FIRST_ANALYSIS = TRUE
```

## 10. 导师级结论

正式停止继续为 SSc sex-specific 主论文寻找替代数据或补救分析。

后续工作的评价标准从“能否继续已有故事”切换为：

> **能否仅依靠直接公开数据，在不改变预注册问题的情况下，复现一条从 MG 亚型遗传差异到细胞特异调控、跨 QTL 资源复现和疾病组织支持的可证伪证据链。**

SSc 阶段积累的高质量工程体系作为方法资产完整继承，但新的 MG 论文必须从真实公开字节重新开始，不继承任何预设生物学结论。
