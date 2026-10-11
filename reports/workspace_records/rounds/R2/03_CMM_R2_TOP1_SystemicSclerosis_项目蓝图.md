# CMM R2 TOP1 项目蓝图

# Sex-biased immune regulatory cascades in systemic sclerosis

**项目状态：PRE-GO / awaiting data preflight**  
**推荐度：A+**  
**推荐作为本批54篇论文之后第一个真正启动的新论文项目。**

---

## 1. 暂定标题

### 主标题版本A（推荐）

**Single-cell multiome genetics resolves sex-biased immune regulatory cascades in systemic sclerosis**

### 版本B（更转化）

**Sex-stratified GWAS and population-scale single-cell multiomics prioritize regulatory programs and therapeutic targets in systemic sclerosis**

### 版本C（更保守）

**Integrative genetic and single-cell multiomic mapping of sex-specific regulatory mechanisms in systemic sclerosis**

---

## 2. 核心科学问题

SSc存在显著性别偏倚，而且2026 sex-stratified GWAS已经证明男性和女性存在不同的autosomal risk loci。

但目前尚未充分回答：

1. 这些sex-specific GWAS loci究竟作用于什么免疫细胞？
2. 风险variant是否先改变chromatin accessibility，再改变gene expression？
3. male-specific和female-specific loci是否通过不同immune regulatory programs发挥作用？
4. 这些遗传程序在真实SSc skin/lung病灶中是否处于异常激活状态？
5. 哪些程序是疾病风险信号，哪些可能连接vascular phenotype与fibrosis？

---

## 3. 核心假设

> SSc的性别差异不仅反映激素或细胞比例差异，还部分源于**autosomal variants在特定免疫细胞中的sex-biased regulatory programs**；其中部分variants通过chromatin accessibility变化影响基因表达，并在SSc皮肤/肺病灶的免疫-血管-纤维化网络中得到功能语境支持。

---

## 4. 主数据源

### A. SSc GWAS

2026 sex-specific GWAS：

- total SSc cases: 10,653；
- female cases: 9,097；
- male cases: 1,556；
- controls: 18,043；
- 已报告male-specific BCL11A；
- female-specific IRF4、RPL3-PDGFB；
- 其他female-specific IL12RB2、PXK、ARHGAP31、ULK3、IRF8。

文章声明summary statistics将在GWAS Catalog公开。

来源：  
https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/

### B. FinnGen single-nucleus multiome QTL

- N=1,108；
- 33 immune cell types；
- eQTL + caQTL；
- SuSiE fine-mapping；
- peak-gene links；
- CASCADE classes。

来源：  
https://www.finngen.fi/en/access_results

### C. Independent QTL replication

优先顺序：

1. TenK10K 28 immune cell eQTL；
2. OneK1K；
3. DICE lung-resident immune eQTL（特别针对lung/ILD机制）；
4. GTEx/eQTL Catalogue作为bulk/tissue辅助。

### D. SSc disease-tissue validation

候选公开队列：

- **GSE249279**：SSc skin single-cell + spatial；
- **GSE312591**：SSc skin scRNA；
- **GSE236111**：SSc skin scRNA，重点IFN/endothelial；
- 其他公开skin/lung cohorts后续补充。

---

## 5. 主分析路线

### Step 1 — GWAS harmonization

构建三套主要outcomes：

- combined SSc；
- female SSc；
- male SSc。

同时保留：

- primary Raynaud GWAS（secondary extension）；
- SSc-ILD HLA study只能作为背景/局部验证，不作为全基因组主outcome，除非获取完整GWAS。

### Step 2 — molecular QTL landscape

对33细胞类型获得：

- cis-eQTL；
- cis-caQTL；
- fine-mapped variants；
- peak-gene links；
- cell specificity。

### Step 3 — colocalization/fine-map

按locus进行：

- SSc GWAS fine-map；
- eQTL/caQTL fine-map；
- coloc.susie；
- simple loci补coloc.abf；
- HLA单独分析，不让HLA淹没全篇。

### Step 4 — regulatory cascade classification

最终候选分层：

#### Tier 1

`GWAS ↔ caQTL ↔ eQTL`均共享信号 + peak-gene link + cell specificity

#### Tier 2

GWAS ↔ eQTL强coloc，但caQTL不完整

#### Tier 3

GWAS ↔ caQTL，有合理peak–gene mapping但缺乏稳定eQTL

Tier 1作为正文主角。

### Step 5 — sex-specific comparison

核心输出不是简单male vs female显著性，而是：

- male-only cascade；
- female-only cascade；
- shared cascade with different effect magnitude；
- shared variant but different cell context；
- loci only visible in combined GWAS。

### Step 6 — independent QTL replication

优先用TenK10K：

- same direction；
- same/similar cell subtype；
- independent top variant或credible set；
- coloc replication。

### Step 7 — SSc tissue validation

scRNA处理必须donor-aware：

- pseudobulk per cell type/donor；
- disease vs control；
- diffuse vs limited（如metadata允许）；
- severity/skin score（如可用）；
- endothelial/fibroblast/immune states；
- candidate regulon/pathway activity。

### Step 8 — spatial layer

GSE249279若质量允许：

- final genes的spatial localization；
- immune–vascular–fibroblast proximity；
- 不把spatial co-localization写成causal interaction。

### Step 9 — translation

对Tier 1 genes：

- Open Targets tractability；
- DrugBank/ChEMBL；
- approved/investigational drugs；
- agonist/antagonist方向与遗传效应匹配；
- PheWAS潜在副作用。

---

## 6. Figure设计

### Fig.1 — Study design and evidence hierarchy

显示：

`GWAS → multiome → coloc → replication → SSc tissue → translation`

同时显示candidate count递减。

### Fig.2 — Sex-specific genetic-to-cell map

- rows: genes/loci；
- columns: immune cell types；
- panels: combined/female/male；
- encoding: eQTL/caQTL/coloc strength。

### Fig.3 — Regulatory cascades

选3–5个代表loci：

`risk variant → open chromatin peak → target gene → cell type`

展示credible sets和peak-gene link。

### Fig.4 — Independent replication

TenK10K / DICE：

- effect concordance；
- coloc；
- forest/meta。

### Fig.5 — SSc skin single-cell validation

- cell atlas；
- disease-state expression；
- final target score；
- sex stratification如metadata允许。

### Fig.6 — Spatial/interaction mechanism

围绕1–2条主程序，而非大而全CellChat网络。

### Fig.7 — Translation and final mechanistic model

- PheWAS；
- druggability；
- direction matching；
- final evidence matrix。

---

## 7. Results标题草案

1. **Sex-stratified SSc genetics reveals distinct regulatory loci across male and female disease risk**
2. **Population-scale immune multiomics maps SSc loci to cell-specific chromatin-to-expression programs**
3. **Fine-mapping and colocalization prioritize high-confidence sex-biased regulatory cascades**
4. **Independent immune-cell QTL resources replicate the strongest SSc regulatory programs**
5. **SSc skin single-cell atlases localize genetically prioritized programs to pathogenic immune, vascular, and fibrotic states**
6. **Spatial and regulatory-network analyses connect prioritized programs to immune–vascular–fibrotic niches**
7. **Phenome-wide and pharmacologic evidence refines translationally plausible SSc targets**

只看小标题就能读懂整篇文章。

---

## 8. Introduction四段逻辑

### P1

SSc临床负担 + fibrosis/vasculopathy + sex bias。

### P2

GWAS已发现遗传风险且2026证明sex-specific autosomal architecture。

### P3

真正gap：

> GWAS loci仍主要是非编码；传统bulk eQTL或单一expression层无法说明这些sex-biased variants在哪个immune cell、通过哪个regulatory element影响expression，更无法说明是否进入真实SSc tissue states。

### P4

本研究：

> sex-stratified GWAS + population-scale snRNA/snATAC QTL + fine-mapping/coloc + independent QTL + SSc skin/spatial + translation。

---

## 9. 预设失败条件（非常重要）

### NO-GO 1

male GWAS除MHC外几乎无可用信号，且multiome中无法复现任何male-specific non-MHC cascade。

→ 可降级为“female-dominant regulatory architecture”，但如果标题仍强调sex-biased则不成立。

### NO-GO 2

所有强信号仅来自HLA。

→ 不足以支撑当前设计，应切换疾病或改成HLA-specific paper。

### NO-GO 3

FinnGen multiome公开结果无法获得足够full summary statistics完成独立coloc。

→ 可使用CASCADE/公开fine-map结果做注释，但论文上限降低；不建议正式启动。

### NO-GO 4

TenK10K/OneK1K完全不复现主要candidate。

→ 不能用“robust target”措辞；若存在组织特异解释，需要DICE/SSc tissue提供足够强证据，否则淘汰。

### NO-GO 5

病灶scRNA中final genes完全缺乏表达或方向高度冲突。

→ 不修改阈值强行保留；把冲突作为context specificity解释或淘汰。

---

## 10. 期刊阶梯

如果所有公共数据Gate均通过且得到2–4条清晰regulatory cascade：

### 主目标

- Rheumatology
- Journal of Autoimmunity
- npj系列合适刊物
- disease-focused Q1 rheumatology/immunology journal

### 更高目标条件

如果额外加入：

- patient-level validation；或
- CRISPR/siRNA；或
- primary cell perturbation；

则可显著提高目标档次。

---

## 11. 当前完成度判断

### 已完成

- 54篇母版分析；
- scTWMR同质化识别；
- 2026新QTL资源升级路径识别；
- 候选疾病压力测试；
- TOP1科学问题与Figure/Methods/Results蓝图；
- GO/NO-GO gate预注册式设计。

### 尚未完成

- exact GWAS文件下载与字段QC；
- FinnGen multiome文件manifest核查；
- SSc scRNA metadata审计；
- literature duplicate scan到gene/locus层；
- compute dry-run。

因此项目状态应严格定义为：

> **PRE-GO, not analysis-started.**

---

## 12. 下一阶段目标

下一阶段不应立刻跑全量分析，而应执行：

# **R3 — Data & Novelty Preflight for SSc Regulatory-Cascade Project**

要输出：

1. data manifest；
2. download/access status；
3. genome build/ancestry/sample size；
4. exact file-level feasibility；
5. literature duplicate matrix；
6. final primary/replication datasets；
7. computational workflow；
8. hard GO/NO-GO decision。

如果R3 PASS，再进入R4正式重跑分析。
