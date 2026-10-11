# CMM R3 — 数据集修正与 Figure 主线更新

## 1. 为什么需要单独记录这个文件
上一轮属于“项目蓝图”，部分数据集是候选层。本轮进入可执行preflight后，需要把候选名录升级成**角色明确、不能随意互换**的数据体系。

---

## 2. 数据集角色修正

### GSE312129：从候选升级为 PRIMARY TISSUE MULTIOME
理由：

- early untreated dcSSc；
- 10 SSc + 4 HC；
- paired snRNA/snATAC；
- case-control disease multiome；
- 有Visium；
- 2026正式论文；
- sex分布已报告（SSc 7F/3M）。

### GSE249279：独立疾病组织复制
优点：样本/数据量较大、processed H5较轻、scRNA+spatial，适合验证 Tier-1 targets。

### GSE236111：IFN/endothelial定向复制
小样本，但如果遗传target落在IL12RB2/IFN/vascular axis，价值很高。

### GSE312932：高分辨空间“后置”
10个SSc Xenium，无HC；只在target已经冻结后回答“在哪里”，不回答“是否疾病差异”。

### GSE312591：从主候选降级为条件性perturbation
只有当RUNX1轴由上游遗传证据独立命中才调用。

---

## 3. Figure结构更新

### Figure 1 — Study design and evidence gates
不只是workflow图，要画出：

- sex-specific GWAS
- FinnGen caQTL/eQTL
- fine-mapping / coloc
- TenK10K replication
- disease skin multiome
- tiering / translation

并明确：**genetic discovery 与 disease tissue validation 是两种独立证据来源。**

---

### Figure 2 — Sex-specific SSc loci and cell-resolved molecular QTL map
建议：

- male/female locus map / Miami-derived summary（基于summary stats而非复制原Figure）；
- 8 sex-specific loci × 33 FinnGen cell types evidence matrix；
- 标注 caQTL-only / eQTL-only / full cascade。

核心问题：
> Which sex-biased loci are genetically active in which immune cells?

---

### Figure 3 — Fine-mapped variant→peak→gene regulatory cascades
只放最强2–4 loci。

每个locus：

- GWAS signal
- caQTL signal
- eQTL signal
- credible sets / PIP
- coloc posterior
- linked ATAC peak
- target gene
- cell type

避免传统“一个locusZoom + 一个boxplot”的松散拼接。

---

### Figure 4 — Independent population replication
FinnGen → TenK10K：

- gene/cell matching；
- effect direction；
- replication rate；
- exact vs lineage-level replication。

若OneK1K作为third layer，放Supplementary优先。

---

### Figure 5 — Untreated SSc skin disease-context concordance
GSE312129：

- donor-aware pseudobulk；
- target gene cell specificity；
- target accessibility；
- disease state / cell-state shift；
- 不重新讲整张SSc atlas。

---

### Figure 6 — Orthogonal tissue / spatial validation
根据target决定：

- GSE249279 independent skin；
- GSE236111 IFN/endothelial；
- GSE312932 Xenium spatial localization。

只有target相关的panel进入主文，其余补充。

---

### Figure 7 — Integrated evidence tier and translational direction
推荐用“证据等级图”而不是大PPI网络。

每个target列：

- GWAS
- caQTL
- eQTL
- fine-map
- coloc
- replication
- SSc tissue
- spatial
- PheWAS/safety
- druggability

最后只输出 1–3 个真正优先靶点。

---

## 4. Supplementary Figure原则

Supplementary用于：

- QC
- full loci
- negative loci
- cell mapping
- sensitivity priors
- alternative LD
- tissue donor QC
- cell annotation
- all-target tables

不把关键shared-signal证据藏到Supplementary。

---

## 5. Nature-style质量控制方向

- 白底；
- 统一无衬线字体；
- panel labels A/B/C固定位置；
- sex颜色最多作为一个编码维度，不能与cell type颜色混淆；
- cell type使用稳定palette跨Figure复用；
- forest/credible-set图显示CI/PIP，不只显示P；
- 任何heatmap必须有可解释图例，避免“红蓝很漂亮但数值不清”；
- 每张主图必须回答一个句子级科学问题；
- 不用Venn作为关键发现图；
- 不用PPI hairball；
- docking若不是核心证据，不进入主图。

---

## 6. 更新后的Figure逻辑

```text
Fig1  What is the question and evidence architecture?
 ↓
Fig2  Which sex-biased loci map to which immune regulatory cells?
 ↓
Fig3  What are the actual variant→peak→gene mechanisms?
 ↓
Fig4  Do these target/cell effects replicate genetically?
 ↓
Fig5  Are they remodeled in real untreated SSc skin?
 ↓
Fig6  Are they independently/spatially supported?
 ↓
Fig7  Which targets survive the entire evidence chain?
```

这是比“分析方法顺序”更成熟的Figure叙事。
