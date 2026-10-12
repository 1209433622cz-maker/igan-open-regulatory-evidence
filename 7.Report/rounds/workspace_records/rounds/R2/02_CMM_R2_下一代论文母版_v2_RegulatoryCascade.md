# CMM R2：下一代新论文母版 v2.0

## Cell-type Regulatory Cascade + Orthogonal Disease-Tissue Validation

**用途：** 作为后续新论文的统一研究设计与写作母版。  
**目标：** 在纯公共数据条件下尽可能接近Q1原创研究的证据结构，并显著超越传统OneK1K scTWMR模板。

---

## 1. 母版的核心科学问题

推荐问题句式：

> Which genetically regulated, cell-type-specific chromatin-to-expression programs mediate susceptibility to **X disease**, and which of these programs remain supported across independent genetic resources and disease-relevant tissue states?

中文逻辑：

> **疾病X的遗传风险究竟通过哪些细胞类型中的“染色质开放性→基因表达”调控级联实现？这些级联能否被独立遗传资源与真实病灶组织共同支持？**

---

## 2. 与P34/P37母版的关键区别

### v1旧母版

`sc-eQTL → cis-MR → coloc → scRNA → PheWAS → drug`

### v2新母版

`GWAS fine-map`  
`↓`  
`cell-type caQTL fine-map`  
`↓`  
`peak–gene link`  
`↓`  
`cell-type eQTL fine-map`  
`↓`  
`multi-signal colocalization / constrained cis-MR`  
`↓`  
`independent QTL replication`  
`↓`  
`disease-tissue scRNA/spatial validation`  
`↓`  
`PheWAS / druggability / direction match`  
`↓`  
`1–3 final regulatory programs`

v2的最终研究对象不再只是“gene”，而是：

> **variant – regulatory element – gene – cell state – disease**

这一点会直接改变论文标题、Figure和Discussion的层级。

---

## 3. 四层证据架构升级为五层

| 层 | 核心问题 | 推荐证据 | 不通过时 |
|---|---|---|---|
| 1 Discovery | 哪些细胞/基因/峰值得关注？ | GWAS + eQTL/caQTL | 淘汰 |
| 2 Regulatory mechanism | 风险变异是否可能通过调控元件影响表达？ | SuSiE fine-map + peak-gene link + CASCADE | 降级为expression-only |
| 3 Genetic credibility | 是否共享因果信号、方向是否稳定？ | coloc.susie + cis-MR/SMR + independent cohort | 淘汰或标记uncertain |
| 4 Disease localization | 是否存在于真实病灶细胞状态？ | scRNA/spatial/pseudobulk/meta | 若不一致则报告context specificity |
| 5 Translation | 是否安全、可干预、方向一致？ | PheWAS + Open Targets/DrugBank/ChEMBL | 不强行drug repurposing |

---

## 4. 强制Gate设计

### Gate A：GWAS质量

必须满足：

- phenotype定义明确；
- cases足够；
- ancestry清楚；
- summary statistics含beta/SE/EAF或足够字段；
- build可统一；
- MHC区单独处理。

### Gate B：multiome QTL

必须区分：

- eQTL-only；
- caQTL-only；
- Full Cascade：`variant→CA→expression`；
- cell-shared vs cell-specific。

**Full Cascade优先级最高，但不要求所有最终靶点必须Full Cascade。**

### Gate C：colocalization

优先：

- SuSiE fine-mapping；
- coloc.susie；
- 对简单单峰locus可补coloc.abf；
- 进行prior sensitivity；
- 多gene coloc不强行选唯一gene。

### Gate D：独立复现

至少一种：

- TenK10K；
- OneK1K；
- DICE；
- GTEx/eQTL Catalogue；
- second GWAS；
- other ancestry。

### Gate E：病灶验证

必须尽量使用真正病灶组织，而不是永远用PBMC。

推荐：

- scRNA pseudobulk；
- cell-state DE；
- donor-aware模型；
- multi-dataset meta；
- spatial localization；
- cell-cell communication仅作为解释层，不作为因果证据。

---

## 5. Methods模块顺序

建议正文Methods严格按问题顺序，而不是软件顺序：

1. Study design and evidence hierarchy
2. Disease GWAS datasets and harmonization
3. Population-scale immune multiome QTL resource
4. Fine-mapping of disease and molecular QTL signals
5. Regulatory-cascade classification and peak–gene linking
6. Cell-type-specific colocalization
7. Colocalization-constrained cis-MR / SMR
8. Independent genetic replication
9. Disease-tissue single-cell/spatial validation
10. Phenome-wide safety assessment
11. Druggability and pharmacologic direction matching
12. Statistical framework and multiple-testing control

---

## 6. Results模块顺序

理想结果标题直接形成摘要：

1. **Genetic and multiomic resources define a high-resolution map of disease-associated regulatory loci**
2. **Cell-type-specific regulatory cascades prioritize a restricted set of candidate genes**
3. **Fine-mapping and colocalization distinguish shared causal signals from linked associations**
4. **Independent QTL resources replicate the strongest cell-gene programs**
5. **Disease-tissue single-cell states localize prioritized programs to pathogenic cellular niches**
6. **Phenome-wide and pharmacologic analyses refine translationally plausible targets**
7. **Integrated evidence nominates 1–3 high-confidence regulatory programs**

---

## 7. Figure 1–7母版

### Figure 1 — Study design + evidence gates

必须显示候选数量如何递减，而不是只放数据库logo。

### Figure 2 — Disease GWAS × cell multiome landscape

- cell type × gene heatmap；
- eQTL vs caQTL；
- sex/phenotype subgroup（若适用）。

### Figure 3 — Regulatory cascade

核心图：

`variant → ATAC peak → gene → disease`

每个final locus给：

- fine-map credible set；
- peak location；
- eQTL/caQTL effect；
- disease effect；
- cell specificity。

### Figure 4 — Colocalization + independent replication

- locus plots；
- PP4 / credible-set overlap；
- second QTL/GWAS replication。

### Figure 5 — Disease tissue

- scRNA cell atlas；
- candidate expression；
- disease vs control；
- state/pseudobulk；
- spatial location（如果有）。

### Figure 6 — Mechanistic convergence

只保留最关键的：

- TF/regulon；
- cell-cell signaling；
- pathway；

不能重新变回“大量GO/KEGG”。

### Figure 7 — Translation + final model

- PheWAS；
- druggability；
- agonist/antagonist方向匹配；
- final evidence matrix；
- graphical mechanistic model。

---

## 8. Introduction写作母版

### P1：临床问题

只写疾病负担、治疗限制、关键临床异质性。

### P2：遗传学知道了什么

强调GWAS发现大量非编码位点，但gene/cell解释不足。

### P3：真正的gap

推荐逻辑：

> Existing bulk and single-cell eQTL studies link variants to gene expression, but they often do not resolve the intervening regulatory element or distinguish regulatory programs that are specific to disease-relevant cell states.

### P4：研究设计

> We integrated sex/phenotype-stratified GWAS with population-scale single-cell chromatin and expression QTLs, fine-mapping, independent genetic replication, and disease-tissue single-cell/spatial datasets to resolve cell-specific regulatory cascades and prioritize translationally relevant targets.

---

## 9. Discussion母版

### 段1：只总结3–4个主发现

不要报所有gene。

### 段2：最强regulatory cascade

从variant/peak/gene/cell解释一条完整链。

### 段3：第二个生物学模块

例如sex difference、vascular vs fibrotic、B vs T cell。

### 段4：病灶组织一致性/冲突

冲突不是必须修掉；可以说明外周与病灶context不同。

### 段5：治疗意义

只讨论方向一致且有真实drug/tractability证据的靶点。

### 段6：Strengths

- multiome；
- fine-mapping；
- independent replication；
- disease tissue；
- evidence-gated design。

### 段7：Limitations

必须主动承认：

- ancestry；
- QTL donor characteristics；
- genetic lifelong perturbation ≠ pharmacologic acute perturbation；
- PBMC vs tissue；
- sex-stratified power imbalance；
- colocalization cannot uniquely prove gene in multi-gene loci；
- observational scRNA cannot prove mechanism。

---

## 10. 统计与因果语言红线

### 可以写

- genetically supported
- prioritized
- colocalized
- consistent with
- implicates
- supports a regulatory route
- candidate therapeutic target

### 没有功能实验时不写

- proves mechanism
- demonstrates therapeutic efficacy
- confirms causal mechanism
- validates drug repurposing
- directly mediates disease

---

## 11. 期刊定位

仅公共数据且做完整v2证据链：

### 合理主目标区间

- Rheumatology / Journal of Autoimmunity级别；
- npj系列；
- Journal of Translational Medicine；
- disease-specific高质量Q1；
- 若问题特别新且multiome结果很强，可尝试更高档。

### 若增加真正功能验证

则可以显著提高上限。

---

## 12. 母版的核心判断

> **新论文的竞争力不来自“又多加一种组学”，而来自是否能把每一层证据组织成一个越来越难被替代解释的因果/调控链。**

如果最终仍只得到“某基因在某细胞显著”，说明v2没有真正实现；只有当我们能把candidate压缩到少量可解释的`variant–peak–gene–cell–disease`程序时，这个母版才算成功。
