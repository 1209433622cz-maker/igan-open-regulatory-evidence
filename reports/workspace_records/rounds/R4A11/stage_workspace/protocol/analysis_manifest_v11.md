# CMM R4A11：Master Analysis Manifest v11

冻结日期：2026-09-12  
机器母版：`analysis_manifest_v11.json`  
候选表：`candidate_registry_v11.tsv`

> **本文件是人读版。机器执行与冲突裁决以同目录 JSON 为准。v11 覆盖 R3–R4A10 中互相冲突的分析条款；旧文件继续作为证据和审计历史，不作为并行执行协议。**

## 1. 当前科学状态

| 状态 | 冻结值 |
|---|---|
| Project | `CONDITIONAL_GO` |
| R4B | `HOLD` |
| 2026 female/male disease bytes | `NOT_OBTAINED` |
| disease-level analysis | `NOT_TESTED` |
| molecular exact-CS overlap | `CONFIRMED_DESCRIPTIVE_ONLY` |
| molecular signal-level coloc | `NOT_TESTED` |
| C1_count | `null` |

`null` 表示没有合格疾病层输入，因此尚未检验。它不能改写成 0、阴性或“共定位失败”。

## 2. 新颖性边界

原论文已经报告 female SSc 与 SYNGR1 的 broad-tissue eQTL 共定位：whole blood PP4=0.977，lymphocytes PP4=0.980。因此，本项目不得声称首次发现 SYNGR1，也不得声称首次把 RPL3–PDGFB 位点重分配给 SYNGR1。

若全部预注册门通过，允许的核心表述是：

> 在已发表 female-SSc–SYNGR1 eQTL 共定位基础上，解析其免疫细胞分辨率的 chromatin-to-expression 信号结构。

## 3. 目标身份与输入门

目标研究固定为 PMID `41999721`、PMCID `PMC13212417`、DOI `10.1016/S2665-9913(25)00376-5` 的 sex-stratified SSc GWAS。female 与 male 必须分别具备：

- 可归档的真实文件字节；
- 提供方 URL 或作者直传记录；
- 下载前已有的 provider/repository/author checksum 证据；
- GRCh38、效应量纲、病例/对照数、样本量语义和 ancestry 元数据；
- H6 v2.1 退出码 0 且 JSON exact status 为 `PASS_FROZEN_REGIONS_INTAKE_READY_FOR_HARMONIZATION`。

2019 overall SSc `GCST009131` 只保留为工程正控，绝不替代 2026 female/male estimand。

## 4. 冻结位点和窗口

### chr22 primary

- anchor：rs66578187，GRCh38 `chr22:39,328,807`，allele set `A/AT`；
- D0 单因果已发表 coloc 方向复现：`chr22:38,828,807–39,828,807`（±500 kb）；
- D1/E1/M1 primary：`chr22:38,328,807–40,328,807`（±1 Mb）；
- sensitivity：±500 kb 与 ±2 Mb；敏感性窗口不能取代 primary。

### chr6 IRF4 secondary

- anchor：rs12203592，GRCh38 `chr6:396,321`，allele set `C/T`；
- primary：`chr6:1–1,396,321`，因端粒截断；
- sensitivity：`chr6:1–896,321` 与 `chr6:1–2,396,321`；
- 只在 chr22 primary 完成后作为次级诊断位点。

## 5. 唯一 primary signal triangle

| 节点 | 资源 | 冻结对象 | 当前状态 |
|---|---|---|---|
| Disease | 2026 SSc GWAS | female | `PENDING_BYTES` |
| caQTL | FinnGen immune multiome | `l2.NK`, peak `chr22-39351520-39352777` | source fine-map/peak-link evidence 已保存；正式 summary/LD 待定 |
| eQTL | TenK10K | NK, SYNGR1 `ENSG00000100321` | source fine-map 已保存；正式 signal-level 输入复核待定 |
| peak→gene | FinnGen snapshot | target peak→SYNGR1 | 描述性 link 已确认，不单独证明因果 |

已确认的两个 exact cross-resource CS members 是 `22:39351666:T:A` 和 `22:39351775:G:A`。它们在 TenK10K NK/SYNGR1 CS4 的 PIP 均为 0.5，在 FinnGen l2.NK caQTL CS1 的 probability 分别为 0.2006173 和 0.0522868。这是精确成员重叠，**不是 signal-level colocalization**。

FinnGen l2.NK SYNGR1 eQTL 是 within-resource 支持；`l2.CD8_TEM` 是预声明次级细胞。它们不能替换 primary TenK10K NK eQTL 来获得主分析阳性。

## 6. 候选基因竞争

`candidate_registry_v11.tsv` 固定 20 个基因：19 个来自冻结的 R4A3 peak-link snapshot，另加强制保留原位点标签中的 PDGFB。SYNGR1 是 primary；RPL3、PDGFB 和其余 17 个基因是有边界的 competitors。

所有候选使用相同窗口、变异资格、coverage、LD、fine-mapping、priors 和 edge classifier。每个同一信号三角的排序分数固定为三条边 primary PP.H4 的最小值；每个基因保留其最大 coherent-triplet 分数并完整报告。与 SYNGR1 差值不超过 0.05 时报告 multi-gene；competitor 高出超过 0.05 时报告 alternative-gene。`NOT_RETURNED` 或 `NOT_TESTED` 不等于统计阴性。

## 7. Normalization 与 variant eligibility

Normalization 必须在冻结的 GRCh38 FASTA 上执行；当前 FASTA path 和 SHA-256 均为 `null`，状态为 `PENDING_REFERENCE`。正式运行前先记录参考文件哈希，再用：

```text
bcftools norm -m -any -f <GRCh38.fa> <input>
```

合并键固定为 `chromosome:normalized_position:normalized_ref:normalized_alt`，不允许只按 rsID 合并。indel 左对齐并最简化，多等位记录先拆分。归一化后相同 key 若 association 字段矛盾则 HOLD；完全一致副本只能在记录计数后去重。

核心字段必须满足 finite effect、finite SE>0、0≤P≤1、合法坐标和 allele。项目资格阈值为 INFO≥0.8、MAF≥0.01。A/T 或 C/G 且 EAF 缺失、无法协调或 EAF∈[0.42,0.58] 的记录在 LD/coloc 前删除，并逐条记录唯一 primary drop reason。

## 8. Coverage、LD 与 RSS 门

任一 pairwise 分析必须同时满足：

- 共同变异占较小 eligible set 至少 0.80；
- 至少 100 个共同变异；
- 共同位置跨度至少 100 kb；
- 每个来源 95% credible set 保留累计 PIP 至少 0.90；
- anchors 和 top variants 被保留。

这些是本项目的 anti-truncation/signal-retention 门，不是普适标准。失败状态为 `UNTESTABLE` 或 `UNINFORMATIVE`，不能标为 DISTINCT。

LD 顺序固定为：经核验的 study-provided signed LD；否则使用 1000 Genomes Phase 3 v5a EUR503，并要求 ancestry、effect allele、variant order 全部一致。QTL 必须使用 resource-matched LD 或 source fine-map object，不能静默套用 disease LD。

矩阵 QC：最大非对称误差≤1e-8，对角线偏离 1≤1e-6，最小特征值容差≥−1e-6。RSS 还需 `estimate_s≤0.1` 且最大绝对 kriging residual≤5。不得删除异常变异来强迫 PASS。

## 9. Fine-mapping 与 coloc

环境冻结为 R 4.6.0、susieR 0.14.2、coloc 5.2.3。`susie_rss` 参数为：

```text
L=10
max_iter=1000
coverage=0.95
min_abs_corr=0.5
estimate_residual_variance=FALSE
z_ld_weight=0
prior_variance=50
check_prior=TRUE
```

D0 用 `coloc.abf`，p1=1e-4、p2=1e-4、p12=1e-5，只作为方向性正控，不能满足 C1。D1/E1/M1 用 `coloc.susie`，`back_calculate_lbf=FALSE`。primary priors 同上，p12 sensitivity 固定为 1e-6、1e-5、1e-4。

每一条边的状态为：

- `SHARED`：primary H4≥0.80 且 H4/(H3+H4)≥0.90；每个 p12 sensitivity 同时 H4≥0.50 且比值≥0.80；
- `DISTINCT`：primary H3≥0.80 且 H3/(H3+H4)≥0.90；每个 p12 sensitivity 保持该比值≥0.90，且两性状均有可检测、收敛信号；
- `INCONCLUSIVE`：技术门通过但不满足以上两式，包括 H0/H1/H2 主导；
- `UNTESTABLE`：任一输入、identity、coverage、LD、RSS 或 convergence 门失败。

## 10. C1 和负结果状态机

C1 需要一个固定 `(disease_signal_id, caqtl_signal_id, eqtl_signal_id)` 三元组，使 D1、E1、M1 三条边全部为 SHARED，并同时具备 peak→gene link、技术 PASS 和冻结候选竞争。不能从三个不同信号对中各取最大 H4 拼接“闭环”。

| 边组合 | 状态 | 允许解释 |
|---|---|---|
| D1/E1/M1 同一三元组均 SHARED | `C1_CANDIDATE` | 可进入候选竞争和 male claim gate |
| E1 SHARED、D1 DISTINCT | `Partial_A` | 禁止 chromatin cascade |
| D1 SHARED、E1 DISTINCT | `Partial_B` | 不确认 SYNGR1 effector |
| M1 SHARED、疾病边非 SHARED | `Molecular_only` | 禁止 SSc mechanism |
| D1 与 E1 均 DISTINCT，且全部技术/功效门充分 | `FALSIFIED` | chr22 主假设被证伪 |
| 任一必需边 INCONCLUSIVE/UNTESTABLE | `UNINFORMATIVE` | 不形成阴性结论 |

## 11. Male 与性别表述

male 必须使用同一研究、窗口、normalization、variant eligibility、LD、RSS、SuSiE、priors 和 edge classifier。female SHARED 而 male 不 SHARED 时，如果 male coverage/power 不足或正式 heterogeneity/interaction 不成立，状态只能是 `SEX_DIFFERENCE_UNRESOLVED`。

在没有足够性别差异证据时，允许写 “immune regulatory module at a female-associated SSc locus”；不得写 “female-specific molecular mechanism”。若队列重叠协方差未知，也不得用假设独立的 beta-difference 检验作为性别特异证据。

## 12. All-8 与停止规则

All-8 对主分析的 rescue 已取消。若以后保留 8 位点，只能作为预列位点、固定方法并控制多重性的独立探索性补充；它不能升级 chr22 主张、把 R4B 改成 GO、抹去 primary falsification 或形成无复制的 C1。

任一上游 HOLD 后，下游一律保持 `NOT_RUN/NOT_TESTED`。禁止用 overall GCST009131 代替目标、改 primary cell/peak/window、挑次级阳性信号或删除不一致变异继续。

## 13. 固定 DAG 与下一阶段

```text
raw-byte receipt + provider checksum freeze
  → H6 v2.1
  → GRCh38 normalization/allele orientation
  → pairwise dense coverage
  → signed LD + RSS
  → D0 published-coloc directional reproduction
  → female disease fine-mapping
  → D1 + E1 + M1
  → same-signal triangle
  → frozen 20-gene competition
  → matched male analysis and claim gate
  → C1 / Partial / FALSIFIED / UNINFORMATIVE
```

下一阶段为 **R4A12 — Byte-arrival-triggered Harmonization and Coverage Gate**。只有真实 female/male 文件或完整预注册区域文件携带 provider metadata/checksum 并通过 H6 v2.1 后才触发。定期公开入口刷新属于维护，不再单独算作科学阶段。

## 14. 验证

`validate_analysis_manifest_v11.py` 会核对 target、窗口、20 基因表、状态边界、软件参数和 10 个本地证据文件的实际 SHA-256。当前结果为 70/70 PASS。这个 PASS 证明协议和现有证据被冻结且自洽，不代表缺失的疾病文件或 reference FASTA 已取得。
