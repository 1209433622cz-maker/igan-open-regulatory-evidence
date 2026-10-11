# CMM / YR1 / SSc 项目全量再评估：Q1可行性、选题重审与论文重构方案

**日期：2026-09-13**  
**阶段建议：R4A13 — Scientific Thesis Reset & Feasibility Gate**  
**角色：医学 / 生物信息学博士生导师级 hostile audit**

---

## 0. 最终结论（先给结论）

### 0.1 是否应该立刻放弃 SSc、完全重新选题？

**不建议现在立刻彻底放弃 SSc。**

但也**不建议继续沿用当前“sex-biased immune regulatory cascades in SSc”的原始宽泛叙事继续堆分析**。目前项目已经出现结构性变化：

1. 2026 年 SSc sex-specific GWAS 已经完成“性别特异位点发现、候选基因功能注释、sex-differential expression、药物重定位”等工作；
2. 原论文已经对部分候选（包括 SYNGR1）做过 broad-tissue / GTEx 层面的共定位或功能解释，因此“发现 SYNGR1”“第一次做 sex-specific SSc coloc”已不是可保护创新；
3. SSc 单细胞、空间转录组、多组学、GWAS fine-mapping、TWAS/eQTL 等方向在 2024–2026 年快速拥挤；
4. 当前项目最核心的 2026 female/male full summary-statistics 仍未取得；
5. 当前唯一被深入推进的 IL12RB2 all-sex 分支依然停留在 `SUMMARY_ONLY_SOURCE_MATCHED_LD_REQUIRED`，不能替代 sex-specific 主问题；
6. 因此，项目现在“工程成熟度很高”，但“主生物学命题的可检验度仍然不足”。

**所以我的建议不是简单“继续”或“重选”，而是：**

> **保留 SSc 作为旗舰候选，但立即进行一次论文科学命题重置（thesis reset），把项目从“发现性别偏倚基因/通路”改造成“对已报道 sex-associated SSc loci 进行 cell-type-resolved、signal-level、chromatin→expression regulatory dissection，并进行独立疾病和疾病组织验证”。与此同时启动一个并行的新选题 Data/Novelty Preflight，作为硬退出后的替代方案。**

换句话说：**SSc 进入“有条件保留”，而不是“无条件继续”。**

---

# 1. 当前项目真正完成到了哪里？

## 1.1 工程成熟度 ≠ 论文结论成熟度

当前项目最大的优点是已经建立非常严格的工程和统计门控：

- provider identity binding；
- build/allele/variant-key 规范；
- summary-statistics intake gate；
- LD source 边界；
- hostile validator；
- multi-signal 分析前 coverage gate；
- source-CS PIP mass gate；
- external LD reference-shopping 停止规则；
- `NOT_TESTED / HOLD / FAIL / NEGATIVE / FALSIFIED` 状态分离。

这些内容非常有价值，说明项目已经具备高质量可重复分析的“基础设施”。

但从论文核心命题来看，必须承认：

> **当前没有一个完成的 C1 级 disease→caQTL→eQTL regulatory cascade。**

当前冻结状态仍是：

```text
PROJECT = CONDITIONAL_GO
R4B = HOLD
C1_count = null
PRIMARY_2026_FEMALE_MALE = NOT_OBTAINED
CHR22_SYNGR1_DISEASE_TEST = NOT_TESTED
IL12RB2_ALLSEX = SUMMARY_ONLY_SOURCE_MATCHED_LD_REQUIRED
FORMAL_MULTI_SIGNAL_COLOC = NOT_RUN
```

因此，现阶段不应把“完成很多代码、QA、LD审计、公开QTL接入”误读为“论文已经有主要发现”。

### 导师级判断

- **工程/可重复性成熟度：高**
- **主问题数据完整度：低–中**
- **核心因果/共享信号证据成熟度：低**
- **当前直接写成 Q1 原始研究论文的成熟度：不足**

---

# 2. 当前原始选题为什么需要重构？

## 2.1 原始选题的问题不是“科学问题差”，而是“创新表述已经落后于数据生态”

原始概念大致是：

> sex-specific SSc GWAS → immune-cell caQTL/eQTL → regulatory cascade → disease tissue → translation

这个框架在 2025 年前后非常有吸引力，但到 2026 年已经出现三层竞争：

### 第一层：原 2026 sex-specific SSc GWAS 本身已经走得比最初预期更远

该研究不仅报告 sex-specific loci，还做了功能注释、sex-differential expression 和药物重定位，并明确突出 IL12RB2 / interferon signalling。

因此新的论文不能把：

- female-specific loci；
- IL12RB2；
- SYNGR1 broad-tissue evidence；
- drug repurposing；

重新包装成自己的主要发现。

### 第二层：SSc 单细胞/空间组学领域已经明显拥挤

2025–2026 已经出现：

- SSc skin spatial multiomics；
- fibroblast–macrophage spatial niches；
- high-resolution fibroblast spatial phenotyping；
- SSc-ILD lung RNA/ATAC multiomics；
- large single-cell immune heterogeneity studies；
- exome + scRNA + eQTL integration。

因此“我们还加了 SSc scRNA/spatial”本身不再构成 Q1 创新。

### 第三层：population-scale single-cell QTL 已经快速成为新标准

FinnGen immune multiome 已公开：eQTL、caQTL、SuSiE、peak–gene、CASCADE、GWAS coloc；TenK10K / OneK1K 体系和 2026 年 Nature 单细胞 eQTL 方法学进一步提高了审稿人的预期。

因此“GWAS + single-cell eQTL”也不能再单独作为核心卖点。

---

# 3. 哪个创新仍然值得保护？

经过当前证据和竞争格局重审，我认为最值得保护、也最有机会达到一区标准的创新不是“发现新基因”，而是：

> **对已报道的 sex-associated SSc loci 做 cell-type-resolved regulatory mechanism resolution：在特定免疫细胞中，以 signal-level 方法证明 disease association、chromatin accessibility 和 gene expression 是否由同一遗传信号驱动，并用独立 sex-stratified disease data、独立 molecular-QTL cohort 和 untreated SSc tissue 进行正交验证。**

这与原论文的差异必须清楚：

- 原论文：**发现 sex-specific loci + broad functional annotation**；
- 新论文：**解释这些 loci 在何种 immune cell、通过哪一个 regulatory peak、影响哪一个 effector gene，并严格确认 same-signal coherence**。

这是从：

> locus discovery

升级到：

> **regulatory mechanism resolution**。

这是当前最合理的论文方向。

---

# 4. 是否应该继续把 chr22 / SYNGR1 放在主位？

## 4.1 可以保留，但不能“预设它一定正确”

SYNGR1 仍然是当前最有价值的候选之一，原因是已有 molecular convergence：

- chr22 female-associated locus；
- FinnGen immune multiome 中该区域存在强 caQTL / SYNGR1 eQTL；
- source-defined peak→SYNGR1 link；
- TenK10K SYNGR1 fine-mapping 与 FinnGen caQTL CS 有 exact-variant convergence。

但项目必须保留一个重要纪律：

> **SYNGR1 = prioritized candidate，不是 predetermined winner。**

因为：

1. 原 2026 论文已对 SYNGR1 有 broad-tissue coloc 支持，降低“发现”新颖性；
2. 该 locus 的原区域标签为 RPL3–PDGFB；
3. source peak 还连接其他多个基因；
4. 当前 disease-level female summary 不在本地，因此最重要的 disease↔molecular same-signal test 尚未进行。

### 必须保留 bounded gene competition

新设计中，chr22 不应只画 SYNGR1，而应预注册一个有来源依据的候选 gene universe（例如 source peak-linked genes + locus genes），然后按统一标准比较：

- disease↔eQTL shared signal；
- disease↔caQTL shared signal；
- caQTL↔eQTL shared signal；
- peak→gene source link；
- effect-direction coherence；
- independent QTL replication；
- disease-tissue support。

只有 SYNGR1 在统一竞争中胜出，才能称为 prioritized effector gene。

---

# 5. IL12RB2 分支应该怎么处理？

## 5.1 不能升级为论文主线

当前 IL12RB2 all-sex 分支完成了大量很有价值的工程工作：

- FinnGen R12/R13 real regional GWAS；
- TenK10K NK/CD8_TEM/CD4_CTL/CD4_TCM full variant-level eQTL；
- classic coloc prior sensitivity；
- full EUR503 external LD；
- source-CS coverage failure adjudication；
- source-matched LD request/validator。

但是它仍不能成为整篇论文的主创新，原因有三：

1. 2026 sex-specific SSc 原论文本身已经突出 IL12RB2；
2. 当前 disease input 是 all-sex FinnGen，不能替代 sex-specific discovery；
3. formal source-matched multisignal coloc 仍未完成。

## 5.2 最佳新角色：benchmark / positive-control locus

如果未来取得 female summary，IL12RB2 反而会非常有价值：

> **作为预注册 benchmark locus，用于证明整套 sex-specific disease→cell eQTL / multi-signal pipeline 能够复现一个原论文已重点支持的位点。**

这比把 IL12RB2 强行包装成“新发现”更科学，也更容易说服审稿人。

建议未来论文角色：

- IL12RB2：benchmark / positive control；
- chr22/SYNGR1 或其他真正被 cell-specific cascade 解析的 locus：novel mechanistic resolution；
- BCL11A / IRF4：negative/discordant/diagnostic loci 或 secondary comparison。

这样论文会从单基因故事升级为：

> **一个能区分“可解析、不可解析、跨资源不一致”的严谨框架。**

---

# 6. 新论文的核心科学问题应该改成什么？

## 不再建议的问题

> 哪些基因解释 SSc 性别差异？

这个太宽、容易变成 gene-list paper。

也不建议：

> 我们整合 GWAS、scRNA、ATAC、spatial 找到了 SYNGR1。

这在 2026 年不够强。

## 推荐的新核心问题

> **Can reported sex-associated systemic sclerosis loci be resolved into cell-type-specific chromatin-to-expression regulatory mechanisms that are driven by the same disease-associated genetic signal?**

中文：

> **已报道的性别相关 SSc 遗传位点，能否被严格解析为特定免疫细胞中由同一遗传信号驱动的染色质可及性→基因表达调控机制？**

### 次问题

1. 哪些 sex-associated loci 真正有 disease↔caQTL / disease↔eQTL shared signal？
2. shared disease signal 是否同时连接 caQTL 和 eQTL？
3. peak→gene 是否由 source data 支持，而不是最近基因映射？
4. 哪些 gene 在同一 locus 的 bounded competition 中胜出？
5. molecular mechanism 是否能在 TenK10K/OneK1K 等独立资源复现？
6. 相关 cell state / gene / regulatory program 是否在 untreated SSc tissue 中表现出疾病状态支持？
7. female vs male 是否存在真正的 effect heterogeneity，而不是“一个显著、另一个不显著”？

---

# 7. 推荐的统计分析重构

## 7.1 Disease genetics 层

### 必须输入

2026 female 和 male full summary statistics。

### 必须做

- provider identity binding；
- build/allele normalization；
- female/male effect estimates 直接比较；
- beta/SE 驱动的 sex-difference Z / heterogeneity test；
- 禁止用“一边 P<5e-8、一边 P>0.05”定义 sex specificity；
- locus-specific conditional/fine-mapping；
- source/ancestry-appropriate LD。

### 推荐 fine-mapping

优先：SuSiE-RSS / FINEMAP，前提是 LD 与 summary compatibility 通过。

如果 provider 无 source LD：

- external LD 只能做 sensitivity；
- 主结论不得依赖 external panel 的“漂亮”结果。

---

## 7.2 caQTL / eQTL 层

FinnGen immune multiome 应作为主要 regulatory mapping 资源，但不应只提取 top SNP。

每个 locus / cell / gene 应保存：

- full regional summary；
- source fine-mapping CS；
- source PIP；
- source peak→gene links；
- effect allele / effect direction；
- cell hierarchy。

### 不推荐

- top SNP overlap；
- credible-set overlap 直接称 coloc；
- default coloc.abf 单独当主证据。

---

## 7.3 Shared-signal 层：建议从“pairwise漂亮图”升级为 signal triangle

完整 C1 至少要求：

### Edge A
`Disease ↔ caQTL`

### Edge B
`Disease ↔ eQTL`

### Edge C
`caQTL ↔ eQTL`

并且：

### Edge D
`source peak → gene`

只有四个边都通过，才允许写：

> disease-associated regulatory cascade

### 主方法

- coloc.susie / multi-signal coloc；
- source fine-mapping signal matching；
- allele/direction coherence。

### 可增加 sensitivity

- HyPrColoc / moloc 类多性状共定位（只作为三层一致性的附加证据，不替代 pairwise signal diagnostics）；
- SMR/HEIDI（若输入完整，作为 sensitivity，不作为主因果证据）。

---

# 8. 性别问题必须重新定义

这是当前论文最容易被 Q1 审稿人攻击的地方之一。

## 8.1 “female-specific”不能等于“female significant, male nonsignificant”

未来主文必须至少区分：

1. female-specific association；
2. male-specific association；
3. shared association with different power；
4. statistically heterogeneous effect。

只有真正 beta/SE heterogeneity 支持，才可以强调 sex-differential genetic effect。

## 8.2 tissue 数据不要强做 sex×disease interaction

当前主要 tissue cohort 中 female/male 样本极不平衡，样本量也不足。

因此 tissue 的职责应是：

> disease-state orthogonal validation

而不是：

> 再证明一次 sex interaction。

这是一个非常重要的叙事收缩。

---

# 9. Tissue validation 应该如何重跑？

## 原则

**只有遗传门先通过，才启动 tissue 大分析。**

不要先跑几十GB组织数据然后再挑支持候选。

## GSE312129 推荐职责

对遗传门通过的 cell/gene/peak 做 targeted validation：

- donor-level pseudobulk disease vs control；
- cell-type / state localization；
- target gene expression direction；
- target regulatory peak accessibility（如果 assay 可支持）；
- target cell abundance/state shift；
- target module/activity；
- Visium spatial localization。

### 统计单位

必须以 donor 为主要 biological replicate，避免 cell-level pseudo-replication。

## GSE249279 推荐职责

独立 skin transcriptomic/spatial replication：

- 只验证预冻结 gene/cell/state；
- 不重新做一个全新的 atlas discovery。

## GSE236111

只做小样本 targeted replication。

## GSE312932

只在需要高分辨率 spatial localization 时启用。

---

# 10. 论文图件必须重新设计

当前原计划 Figure 1–7 有一个问题：**方法流程图权重过高，真正 disease genetics signal 太晚出现。**

对于一区稿件，我建议压缩为 6 张主图，使每张图都回答一个审稿问题。

## Figure 1 — Sex-associated SSc genetic landscape + study logic

职责：

- 2026 female/male GWAS loci；
- effect-size/heterogeneity；
- frozen candidate loci；
- 一小块 study architecture。

**不要把整张 Figure 1 做成 workflow infographic。**

## Figure 2 — Disease fine-mapping and independent sex-stratified replication

职责：

- chr22 / benchmark loci regional association；
- credible sets；
- female vs male effect；
- FinnGen sex-stratified replication（若可得）。

## Figure 3 — 论文核心图：disease→chromatin→expression signal triangle

建议主角为 chr22 locus（如果通过）。

包含：

- disease fine-map；
- caQTL fine-map；
- eQTL fine-map；
- same-signal / coloc.susie；
- peak→gene；
- allele-direction model。

这是整篇论文最重要的图。

## Figure 4 — Bounded effector-gene competition + independent molecular replication

职责：

- 统一候选 gene universe；
- SYNGR1 vs RPL3 vs 其他 linked genes；
- TenK10K / other replication；
- positive benchmark IL12RB2 与 discordant locus（IRF4等）形成方法对照。

## Figure 5 — Untreated SSc tissue validation

只展示遗传筛选后预注册结果：

- target cell；
- target gene；
- target state；
- peak/accessibility（如可用）；
- donor-level statistics。

避免“大而全 UMAP atlas”。

## Figure 6 — Independent tissue/spatial replication + integrated mechanism

- independent dataset；
- spatial localization；
- integrated evidence ladder；
- restrained mechanistic model。

### Supplementary

- QC；
- full locus tables；
- negative loci；
- prior sensitivity；
- external-LD sensitivity；
- all-cell results；
- extra UMAPs。

---

# 11. 论文 Results 逻辑建议重写

## Results 1
**Sex-associated SSc loci show heterogeneous levels of regulatory resolvability**

不是上来讲 SYNGR1，而是先建立 locus-level problem。

## Results 2
**A subset of sex-associated loci share disease and immune-cell regulatory signals**

用严格 shared-signal gate 分类。

## Results 3
**The chr22 locus resolves to a cell-type-specific chromatin-to-expression mechanism**

如果 SYNGR1 真正胜出，再在这里出现。

## Results 4
**Bounded locus competition and independent QTL replication prioritize the effector gene**

防结果导向。

## Results 5
**Untreated SSc tissue supports the genetically prioritized cell state and regulatory direction**

从 genetics 到 disease tissue。

## Results 6
**Benchmark and discordant loci define the boundary of the framework**

IL12RB2 做 benchmark；IRF4/BCL11A 等可作为不完全解析案例。

这会比“每个数据集一节”的传统 bioinformatics 文章高级很多。

---

# 12. Discussion 应该怎么写

Discussion 不要写成“我们发现了很多东西”。

建议 5 段：

1. **核心发现**：不是新 locus，而是 regulatory resolution；
2. **chr22 生物学解释**：为什么 cell-specific chromatin→expression 改进了原 locus annotation；
3. **sex interpretation**：区分 sex-associated vs sex-heterogeneous，说明 tissue 层不承担 sex interaction；
4. **方法学意义**：为什么 exact overlap / single-causal coloc 不足，signal-level adjudication 更可靠；
5. **限制**：无实验扰动、summary/LD source限制、tissue sample sex imbalance、association不能证明生物学因果。

---

# 13. 是否需要湿实验？

用户已明确偏好不做湿实验。

我的判断：

**可以不做湿实验，但一区上限取决于遗传证据链是否足够硬。**

在无湿实验前提下，必须提高以下部分的强度：

- source-matched / source-compatible LD；
- multi-signal fine-mapping；
- independent disease replication；
- independent molecular replication；
- disease tissue orthogonal validation；
- effect-direction coherence；
- negative controls / falsification。

如果这些都完整，稿件可以成为高质量 genetics / systems immunology / rheumatology computational paper。

如果这些缺两到三层，再多加 WGCNA/PPI/docking 也不会补回来。

---

# 14. 当前 Q1 可行性重新评级

以下不是投稿接受概率，而是“作为一篇 Q1 原始研究论文的科学准备度”。

| 维度 | 当前 | 如果按新方案并取得主数据 |
|---|---|---|
| 科学问题重要性 | 高 | 高 |
| 2026 新颖性 | 中 | 中高–高 |
| 主疾病数据完整性 | 低 | 高 |
| signal-level genetics | 低 | 高 |
| cell-specific regulatory evidence | 中高 | 高 |
| independent molecular replication | 中 | 高 |
| independent disease replication | 低–中 | 中高 |
| tissue orthogonal validation | 尚未正式启动 | 中高–高 |
| 可重复性/QA | 很高 | 很高 |
| Q1 manuscript readiness | **低–中** | **中高–高** |

### 关键判断

**现在项目最大风险不是“结果不漂亮”，而是“主问题所需关键输入不在手里”。**

这属于 feasibility risk，不属于 statistical failure。

---

# 15. 什么时候应该真正重新选题？

建议不要用模糊的“再等等”。设置硬退出门。

## SSc 保留条件

满足以下任一强路径即可继续：

### Path A（最佳）
- 2026 female/male full summary 获得并通过 P0/H6；
- chr22 或至少一个 locus 可进行 paper-grade fine-mapping；
- 至少一个 locus 的 disease↔caQTL + disease↔eQTL + caQTL↔eQTL 可正式测试。

### Path B（可接受）
- 2026 sex summary 获得；
- source disease LD不完美，但存在稳健的 multi-method signal resolution；
- FinnGen sex-stratified disease replication可用；
- molecular/tissue验证强。

## SSc 退出条件

如果在完成以下三项明确获取动作后仍无法获得可分析主数据：

1. GWAS Catalog /正式数据入口复核；
2. 通讯作者/数据提供方正式请求；
3. 可合法获得的独立 sex-stratified replication resource 复核；

并且：

- female/male full summary 仍不可获得；
- disease-side LD无法支持主要 loci 的 signal-level test；
- 只能依赖 all-sex FinnGen + QTL；

则建议：

> **停止把 SSc sex-specific regulatory genetics 作为主论文选题，保留全部工程资产作为方法/未来项目，并重新选题。**

这是明确的科学 STOP，而不是失败。

---

# 16. 如果重选，新题应该按什么标准选？

不要再从“疾病热门程度”开始。

新题必须先满足数据结构，再谈生物学故事。

## 新题 preflight 的 8 个硬条件

1. **完整、公开、可checksum的主GWAS summary**；
2. beta/SE/allele/AF/N信息完整；
3. 有 subtype/sex/context 中至少一种能真正形成新问题；
4. 有 source-compatible LD 或可合理获取；
5. 至少一个 population-scale cell-specific QTL / multiome resource；
6. 有独立 QTL replication；
7. 有独立 disease tissue single-cell/spatial 数据；
8. 近2年未被同样的数据组合和同样问题直接做完。

### 新题评价矩阵

建议重新对：

- Sjögren syndrome；
- myasthenia gravis；
- alopecia areata；
- 其他免疫/纤维化疾病；

做一个**数据可执行性优先于生物学想象力**的预审。

注意：以前 R2 的候选排名不能直接沿用，必须按 2026-09 最新公开数据重新检查。

---

# 17. 我建议的新阶段：R4A13

## 阶段名

> **R4A13 — Scientific Thesis Reset, Primary-Data Feasibility Gate & Parallel Topic Preflight**

## Track A — SSc flagship salvage / validation

### A1
正式完成 2026 female/male summary 的三路获取审计。

### A2
如果拿到数据：

`P0 → H6 → normalization → sex effect/heterogeneity → locus fine-map → LD diagnostics`

### A3
预注册三个 locus 角色：

- benchmark：IL12RB2；
- primary mechanistic candidate：chr22/SYNGR1 region；
- discordant/negative diagnostic：IRF4 或 BCL11A。

### A4
只有 A2 通过才启动 disease↔caQTL/eQTL signal triangle。

---

## Track B — Parallel new-topic preflight

不要等 SSc 数据期间空转。

对 3–5 个候选疾病做：

- 2026 novelty search；
- primary GWAS availability；
- sex/subtype/context availability；
- LD feasibility；
- FinnGen/OneK1K/TenK10K/FinnGen multiome coverage；
- disease tissue datasets；
- nearest competitor papers；
- estimated Q1 ceiling。

最后输出一个**可执行性×新颖性×证据强度**矩阵。

---

# 18. 下一阶段最不应该做什么

1. 不要继续扩 IL12RB2 第5/第6个细胞；
2. 不要再换 external LD panel；
3. 不要提前跑所有 SSc tissue 数据；
4. 不要补 WGCNA/PPI/LASSO/docking；
5. 不要为了“有结果”把 all-sex FinnGen 改写成 sex-specific evidence；
6. 不要把 classic coloc 高 PP4 当主结论；
7. 不要把 SYNGR1 写成预设唯一答案；
8. 不要先写完整 manuscript 再等数据；
9. 不要把工程进展当作生物学发现；
10. 不要为了保住原选题而降低证据门槛。

---

# 19. 最终导师级裁决

## 对当前项目

> **CONDITIONAL RETAIN / THESIS RESET REQUIRED**

不是 `STOP`，也不是 `GO_R4B_FULL`。

## 对当前论文方向

原方向：

> sex-biased immune regulatory cascades in systemic sclerosis

建议替换为：

> **Cell-type-resolved regulatory dissection of sex-associated systemic sclerosis loci**

或：

> **Resolving sex-associated systemic sclerosis loci into immune-cell chromatin-to-expression regulatory mechanisms**

## 对当前最核心目标

不再是：

> 继续让 IL12RB2 coloc 变漂亮。

而是：

> **先证明主 disease data 可以获得并允许 paper-grade signal-level genetics；若可以，则重启 chr22/SYNGR1 等 locus 的严格 mechanistic resolution；若不可以，则科学地退出该选题并切换到已通过并行 preflight 的新疾病。**

---

# 20. 下一阶段冻结状态

```text
PROJECT = CONDITIONAL_RETAIN
MANUSCRIPT_DIRECTION = RESET_REQUIRED
R4B = HOLD
C1_count = null

PRIMARY_SSC_SEX_GWAS = CRITICAL_FEASIBILITY_GATE
CHR22_SYNGR1 = PRIORITIZED_CANDIDATE_NOT_PREDETERMINED
IL12RB2 = BENCHMARK_CANDIDATE / SECONDARY_BRANCH
TISSUE_ANALYSIS = DEFER_UNTIL_GENETIC_GATE

NEXT_STAGE = R4A13
R4A13_TRACK_A = PRIMARY_DATA_FEASIBILITY + THESIS-LEVEL LOCUS DESIGN
R4A13_TRACK_B = PARALLEL_NEW_TOPIC_PREFLIGHT

FULL_TOPIC_RESELECTION_NOW = NO
HARD_RESELECTION_IF_PRIMARY_DATA_GATE_FAILS = YES
```

---

# 21. 本轮行动记录

本轮完成：

1. 基于项目全量交接摘要与 FG7/QA 状态重新审视主问题；
2. 将工程成熟度与论文科学成熟度分开评价；
3. 重新评估 2026 年 SSc sex-GWAS、SSc 单细胞/空间、多组学、QTL 竞争格局；
4. 判定原“发现性别偏倚基因/多组学整合”叙事已不足以支撑高水平创新；
5. 保留 SSc，但要求 thesis reset；
6. 将 SYNGR1 从“预设主角”恢复为 bounded competition 下的 prioritized candidate；
7. 将 IL12RB2 重定位为 benchmark / positive-control 候选；
8. 重构 disease genetics、shared-signal、tissue validation、figure architecture 和 Results 逻辑；
9. 建立 SSc 硬退出条件；
10. 建议启动并行新选题 preflight，避免关键数据不可得导致项目长期停摆。

---

# 22. 外部竞争格局复核（2026-09-13）

本轮外部核查重点包括：

- Rodriguez-Martin et al. 2026, *Lancet Rheumatology*: sex-specific autosomal susceptibility loci in SSc；
- Ishikawa et al. 2024, *Nature Communications*: SSc GWAS + fine-mapping + TWAS + regulatory annotation；
- 2025 *Annals of the Rheumatic Diseases*: SSc skin spatial multiomics / fibroblast-macrophage niche；
- 2026 *Annals of the Rheumatic Diseases*: SSc-ILD lung RNA/ATAC multiomics；
- 2025 SSc exome + machine-learning + scRNA/eQTL integration；
- FinnGen single-nucleus immune multiome public release (2026-08-13)；
- 2026 *Nature*: cell-type-specific eQTL architecture and complex traits。

这些工作共同说明：

> **2026 年的高水平门槛已经从“整合多组学”升级到“问题驱动、signal-level、cell-context-specific、independently replicated、falsifiable mechanism resolution”。**

---

**本文件建议作为 R4A13 的起始 scientific charter。下一轮如果继续推进，不应直接做新的大规模分析，而应先完成 Track A primary-data feasibility gate 与 Track B parallel-topic preflight。**
