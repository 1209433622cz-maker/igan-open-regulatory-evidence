# CMM R5A1：Open-Data-Only 选题重构与论文方向重新设计

**日期：2026-09-13**  
**任务定位：博士生导师级选题/数据可执行性重审**  
**新增硬约束：不使用任何需要权限审批、DAC、EGA/dbGaP/UKB申请、Green Library、作者邮件、PI签署，或必须经邮件/表单获取下载指令的数据。**

---

## 1. 最终决策

### 1.1 当前 SSc sex-specific 主线

正式建议调整为：

```text
SSc_SEX_SPECIFIC_MAIN_MANUSCRIPT = HOLD_ARCHIVE
FORCE_CONTINUE_AS_Q1_PRIMARY = NO
METHODS_ASSETS_REUSABLE = YES
CURRENT_SSc_RESULTS_DISCARDED = NO
```

原因不是 SSc 没有科学价值，而是新的“公开数据零申请”约束直接切断了当前主论文最关键的两类输入：

1. 2026 female/male SSc 完整 summary statistics 当前尚不能直接无申请取得；
2. TenK10K source-matched WGS/LD 需要作者派生文件或 EGA controlled access；
3. FinnGen public results 的官方获取流程仍要求在线 form + email download instructions；
4. 用 2019 overall SSc GCST009131 替代 2026 sex-specific GWAS 会导致科学问题退化，而且该旧 GWAS 还存在 A2 全缺、无 original SE/EAF、GRCh37 等既有问题。

因此不建议把旧 SSc 项目硬改成一个普通 “overall GWAS + scRNA + eQTL” 论文冲一区。

---

## 2. 新的 Gate 0：Open-Data-Only

任何新选题在进入分析前必须同时满足：

### A. Disease GWAS
- 可通过直接 HTTP/FTP/API/公开 repository 下载；
- 不需要注册审批、PI、DAC、邮件回复或机构签署；
- genome-wide summary，而非只有 top hits；
- 至少有 CHR/POS + REF/ALT 或明确 effect/non-effect allele + beta/OR + SE/P；
- build 可确认；
- 最好有 phenotype stratification 或第二公开 GWAS。

### B. Molecular QTL
至少两个可直接下载资源：
- TenK10K Phase 1 public eQTL + SuSiE；
- OneK1K 2026 public full eQTL；
- eQTL Catalogue；
- 其它明确 unrestricted QTL。

优先级最高的是 OneK1K 2026，因为公开 Zenodo 已提供：
- full 1-Mb cell-type eQTL；
- top eQTL；
- **980 donor PLINK genotype**；
- covariates；
- cell×gene objects。

这允许在无需 controlled access 的情况下真正构建 **QTL-side source-matched LD**。

### C. Disease tissue
- GEO/SRA/ArrayExpress/CELLxGENE 直接下载；
- case/control 或至少明确 disease-state tissue；
- 有 donor metadata；
- 若没有健康对照，只允许 localization/state support，不伪装 case-control validation。

### D. LD
- 首选 study-provided public LD/fine-mapping；
- 次选公开 source genotype；
- disease-side只能用 external LD 时，必须显式降低结论等级；
- 不允许因为 external LD 不理想而 reference shopping。

### E. Novelty
不能仅仅是：
- DEG + MR；
- bulk eQTL coloc；
- WGCNA/PPI；
- docking；
- “single-cell验证hub gene”。

必须存在明确的 **signal-level / subtype / cell-state / regulatory-mechanism** 问题。

---

## 3. 候选疾病重新排序（按“公开数据零申请”而非纯生物学吸引力）

| Rank | 方向 | Data executability | Novelty ceiling | Disease tissue | 主要风险 | 综合建议 |
|---|---|---:|---:|---:|---|---|
| 1 | **Myasthenia gravis：EOMG vs LOMG regulatory genetics** | A | A- | A | 已有MR/coloc和早晚发遗传研究，需避开旧套路 | **首选** |
| 2 | **IgA nephropathy：immune→kidney regulatory convergence** | A | B+/A- | A | 2023 Nature Genetics 已做大量功能注释，2026竞争快速增加 | **备选1** |
| 3 | SSc overall public-only | B- | B- | A | 退回旧GWAS且失去sex主轴，不值得作为当前Q1主线 | **归档备选** |
| 4 | Sjögren disease | C | A- | A | 关键GWAS资源含dbGaP/非完全开放路径 | **不符合新硬约束** |
| 5 | Alopecia areata | B-/C | B+ | A | 现代强GWAS多依赖FinnGen或旧GWAS，主疾病锚偏弱 | **暂不优先** |

---

# 4. TOP1 新方向：Myasthenia gravis

## 4.1 为什么最适合新的约束

2024 Nature Communications MG meta-analysis 已将 discovery summary statistics 存入 GWAS Catalog：

- Overall MG: **GCST90432156**
- Early-onset MG (EOMG): **GCST90432157**
- Late-onset MG (LOMG): **GCST90432158**

研究规模：
- overall discovery：5,708 cases / 432,028 controls；
- EOMG：1,391 cases；
- LOMG：2,404 cases；
- overall 共识别 12 independent genome-wide significant hits across 11 loci（合并 replication 后）。

这些 summary 可以通过 GWAS Catalog 公开下载，不要求联系作者。

### 公开 disease tissue

当前已核实：

- **GSE233180**：12 位 immunotherapy-naïve AChR-Ab+ EOMG thymus，scRNA/VDJ；
  - 10 female + 2 male；
  - 适合 EOMG thymic B-lineage / immune-state localization；
  - 无健康 thymus 对照，不能单独声称 disease-vs-control DE。
- **GSE227835**：MG vs healthy control PBMC scRNA，重点包含 seronegative MG；
- **GSE297547**：MG + healthy control PBMC，T/B enriched scRNA + AbSeq + 部分 immune repertoire。

### 公开 QTL

- TenK10K：28 immune cell types，full 100-kb cis-eQTL + SuSiE 公开；
- OneK1K 2026 Zenodo：
  - 14 immune cell types；
  - full 1-Mb eQTL；
  - public PLINK genotype for 980 donors；
  - 可重建真正的 OneK1K source-matched LD；
- eQTL Catalogue FTP：可直接区域抓取。

---

## 4.2 不能再做的 MG 论文套路

MG 已经存在：
- early vs late onset genetic studies；
- CTLA4 等位点细化；
- bulk-eQTL MR；
- drug-target MR；
- classic coloc；
- pQTL / PheWAS / druggability；
- JTM 级 multi-omics target-prioritization。

因此新论文**不能**以：

> “MR筛选MG候选基因并用单细胞验证”

作为核心。

---

## 4.3 建议的新科学问题

> **Which non-MHC genetic loci distinguish early- from late-onset myasthenia gravis, and can these subtype-associated signals be resolved into reproducible immune-cell-specific regulatory mechanisms using fully open single-cell genetic resources?**

中文：

> **哪些非MHC遗传位点真正区分早发与晚发重症肌无力，这些亚型相关疾病信号能否在完全公开的单细胞遗传资源中被解析为可复现的免疫细胞特异调控机制？**

关键不是“MG相关基因”，而是：

```text
EOMG vs LOMG heterogeneity
        ↓
non-MHC locus selection
        ↓
cell-type eQTL fine-mapping
        ↓
signal-level disease↔eQTL adjudication
        ↓
OneK1K ↔ TenK10K replication
        ↓
MG PBMC / EOMG thymus disease-state localization
```

---

# 5. 新 MG 分析设计

## Figure 1 — Genetic architecture and subtype heterogeneity

不再用 workflow 做整张主图。

内容：
1. Overall MG / EOMG / LOMG Manhattan；
2. non-MHC genome-wide loci；
3. EOMG vs LOMG beta / SE forest；
4. formal effect heterogeneity；
5. loci 分类：
   - EOMG-predominant；
   - LOMG-predominant；
   - shared；
   - unresolved。

必须避免：
> “EOMG显著、LOMG不显著 = subtype-specific”

必须正式比较效应。

---

## Figure 2 — Open-data fine-mapping and locus prioritization

针对预冻结非-MHC loci：

1. GWAS regional association；
2. 1000G EUR sensitivity LD；
3. conditional/signal structure；
4. source study supplementary/index evidence；
5. gene competition，不允许 nearest-gene shortcut。

MHC 单独放 Supplementary 或做独立专门分析，不与普通 chr loci 混跑。

---

## Figure 3 — Cell-type regulatory resolution

Primary QTL resource：
> **OneK1K 2026**

原因：
- summary open；
- genotype open；
- 可构建 source-matched QTL LD。

Secondary independent molecular resource：
> **TenK10K**

分析：

```text
MG/EOMG/LOMG GWAS
        ↕
OneK1K cell-eQTL
        ↕
TenK10K cell-eQTL
```

每 locus 比较：
- B cell；
- CD4 T；
- CD8 T；
- NK；
- monocyte；
- 必要时 subtype。

禁止看到结果后临时增加细胞。

---

## Figure 4 — Cross-resource replication

定义：

### R1 strong
- disease signal consistent；
- OneK1K shared-signal evidence；
- TenK10K same gene/cell-class replication；
- allele/direction coherent。

### R2 moderate
- disease↔QTL 一资源强；
- 第二资源支持 gene/cell but signal resolution有限。

### R3 molecular-only
- QTL漂亮但 disease signal 不共享。

### R4 falsified
- technical gates 充分而两资源均不支持。

只把 R1 放主文机制图。

---

## Figure 5 — Disease-tissue validation

### PBMC
使用：
- GSE227835；
- GSE297547。

核心：
- donor-level pseudobulk；
- predefined target cells；
- target gene/state；
- disease vs HC；
- effect direction；
- 不以单细胞数量充当 n。

### EOMG thymus
GSE233180：
- 仅做 disease-state localization；
- B-lineage / T-B interaction context；
- 不伪装成 EOMG vs healthy thymus DE。

---

## Figure 6 — Integrated subtype model

最终只保留：

```text
subtype genetic effect
→ immune-cell regulatory effect
→ cross-QTL replication
→ disease tissue localization
```

不放：
- PPI网络大图；
- docking；
-泛化 drug network；
- 大量 enrichment 气泡图。

---

# 6. LD 与 colocalization 在“零申请”条件下如何重新定义

由于不再追求 controlled disease source genotype：

### QTL side
可做到很强：
- OneK1K public PLINK genotype → native/source-matched LD；
- TenK10K source SuSiE summary → independent replication。

### disease side
多数 meta-GWAS 没有 source genotype。

所以论文必须明确：

- disease fine-mapping 使用公开 ancestry-matched LD；
- 进行 LD sensitivity；
- 不把 external-LD结果写成 “source-matched disease fine-map”；
- 对多信号/高LD loci保守降级；
- MHC 默认不作为主 mechanistic locus。

### Primary evidence
不再要求所有 locus 都强行 coloc.susie。

采用证据等级：

1. effect heterogeneity；
2. regional disease signal；
3. cell-eQTL source fine-map；
4. cross-resource molecular replication；
5. coloc / signal matching（可判定时）；
6. tissue support。

这样避免因“无疾病source LD”再次把项目锁死。

---

# 7. IgAN 作为 Plan B

## 优点
- 2023 Nature Genetics GWAS：10,146 biopsy-confirmed cases + 28,751 controls；
- summary stats 明确公开；
- 多个非-HLA强 locus；
- GEO GSE127136；
- 2026 新公开 glomerular disease single-nucleus/Xenium 数据 GSE286184；
- kidney tissue biology 非常丰富。

## 缺点
- 原 2023 Nature Genetics 已做 extensive functional annotation / causal-cell/pathway / drug-target prioritization；
- 2026 已有 disease-context QTL atlas preprint；
- 2026 又出现 GWAS + scRNA / kidney genetic-cell atlas 类工作。

因此若选择 IgAN，不能做普通：

> GWAS + scRNA + MR

必须改成更窄的问题，例如：

> **blood immune regulatory signal → kidney resident cell disease-state convergence**

综合上限略低于当前建议的 MG subtype 方向。

---

# 8. 为什么不建议继续硬改 SSc

如果完全不使用申请数据，SSc 可用的是：

- 2019 GCST009131 overall；
- public TenK10K；
- public OneK1K；
- public GEO SSc tissue；
- external 1000G LD。

但会出现：

1. 失去原论文最重要的 sex-specific thesis；
2. 2019 GWAS 格式质量已知不理想；
3. 2026 更强 GWAS 已发表，却不用它的完整 sex-specific data；
4. SSc single-cell/multiome/spatial 已高度拥挤；
5. 很容易退化成 “旧GWAS + 新single-cell”的拼接型论文。

因此：

> **不建议把 SSc all-sex public-only 版本作为新的 Q1 主论文。**

SSc 项目应保存为：
- methods engineering asset；
- data-QA framework；
- 如果未来真正公开 sex-specific summary，再恢复。

---

# 9. 哪些原 SSc 工作可以直接迁移

全部保留：

- P0 provider identity；
- H6 schema/readiness；
- build/allele harmonization；
- exact variant keys；
- hostile validator；
- source-CS coverage；
- classic coloc prior sensitivity；
- GO/HOLD/FAIL/UNTESTABLE 状态机；
- release checksum；
- Nature-style figure framework；
- donor-level tissue QC；
- bounded gene competition。

不迁移：
- SYNGR1 biological conclusion；
- IL12RB2 story；
- SSc-specific manuscript prose；
- sex-specific claims。

即：

> **换题，但不重新发明分析工程。**

---

# 10. 下一阶段正式目标

建议停止继续编号 R4A12FG8。

开启：

> **R5A1 — Open-Data-Only Topic Re-selection & Byte-Level Preflight**

## Track A：MG byte-level feasibility

真实下载/检查：

1. GCST90432156；
2. GCST90432157；
3. GCST90432158；
4. build；
5. beta/SE/ref/alt/AF；
6. genome-wide row count；
7. overlap with OneK1K/TenK10K；
8. non-MHC GWS loci；
9. EOMG vs LOMG effect heterogeneity；
10. top 5–10 loci的QTL可测性。

### GO_MG 条件

至少满足：

- 三份 GWAS 全部直接公开可下载；
- field 完整；
- ≥2 non-MHC loci 有 subtype-differential evidence；
- ≥1 locus 在 OneK1K 和 TenK10K 都有强 cell-eQTL；
- public QTL variant coverage 足够；
- public tissue 中 target gene/cell 可检测。

否则不进入 full analysis。

---

## Track B：IgAN shadow preflight

只做同等的字节级最小预审，不跑 full analysis。

若：

```text
MG = FAIL
IgAN = PASS
```

则切换 IgAN。

若：

```text
MG = PASS
```

则停止广泛选题，进入 R5A2 MG locus-level pilot。

---

# 11. 最终状态

```text
PUBLIC_ONLY_POLICY = HARD_CONSTRAINT

SSc_PRIMARY_Q1 = HOLD_ARCHIVE
SSc_FORCE_SALVAGE = NO

TOP1_NEW_TOPIC = MYASTHENIA_GRAVIS
PRIMARY_AXIS = EOMG_vs_LOMG
PRIMARY_NOVELTY =
  SUBTYPE_HETEROGENEITY
  + CELL_TYPE_REGULATORY_RESOLUTION
  + CROSS_SC_EQTL_REPLICATION
  + DISEASE_TISSUE_VALIDATION

TOP2_BACKUP = IgA_NEPHROPATHY

FINNGEN_FORM_EMAIL = EXCLUDED
EGA = EXCLUDED
DBGAP = EXCLUDED
UKB_APPLICATION = EXCLUDED
AUTHOR_REQUEST = EXCLUDED

DIRECT_GWAS_CATALOG = ALLOWED
ZENODO = ALLOWED
GEO_SRA = ALLOWED
EQTL_CATALOGUE = ALLOWED
1000G_PUBLIC_REFERENCE = ALLOWED

NEXT_STAGE = R5A1_BYTE_LEVEL_PREFLIGHT
```

---

# 12. 本轮核心来源

1. Braun A et al. Genome-wide meta-analysis of myasthenia gravis uncovers new loci and provides insights into polygenic prediction. Nature Communications, 2024. GWAS Catalog: GCST90432156–GCST90432158.
2. TenK10K Phase 1 public eQTL summary statistics, Zenodo 18221260.
3. OneK1K 2026 public full eQTL + genotype, Zenodo 18870747.
4. GSE233180 — immunotherapy-naïve EOMG thymic single-cell atlas.
5. GSE227835 — MG PBMC scRNA.
6. GSE297547 — MG/HC PBMC scRNA + AbSeq/repertoire.
7. IgAN 2023 Nature Genetics GWAS and public summary statistics.
8. GSE127136 and GSE286184 — public IgAN/glomerular disease single-cell/spatial resources.
9. eQTL Catalogue public FTP summary statistics.

---

## 13. 导师级一句话结论

**在“不申请任何数据”的硬约束下，与其把当前 SSc sex-specific 论文降级为旧 overall GWAS 的拼接稿，不如冻结 SSc 主线并迁移已经建立的高标准遗传门控体系；以 MG 的 EOMG–LOMG 亚型异质性为第一新题，通过公开 GWAS Catalog + OneK1K source genotype/eQTL + TenK10K independent sc-eQTL + GEO MG tissue 构建一条从亚型遗传效应到免疫细胞调控机制的完全公开、可复现证据链。**
