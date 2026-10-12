# CMM R3 — SSc 数据入口与可获取性 Manifest

**核查日期**：2026-09-05  
**目的**：把“文献里提过”“网页上存在”“我们真的能下载并用于统计分析”严格分开。

---

## 1. 主GWAS层

### 1.1 2026 sex-specific SSc GWAS — PRIMARY

**文献**  
Rodriguez-Martin I, et al. *Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study.* The Lancet Rheumatology. 2026;8(6):e438-e450.  
PMID: 41999721  
DOI: 10.1016/S2665-9913(25)00376-5

**样本**

- SSc cases total: 10,653
- controls total: 18,043
- male SSc: 1,556
- male controls: 6,990
- female SSc: 9,097
- female controls: 11,053

**已报告 sex-specific loci**

- male novel: BCL11A
- female novel: IRF4
- female novel: RPL3-PDGFB
- five known SSc loci newly characterized as female-specific

**论文已经做过的功能层**

- positional evidence
- eQTL / sQTL
- pQTL
- chromatin interactions
- Open Targets V2G
- regulatory colocalization (>80% posterior threshold for reported positive evidence)
- whole-blood sex differential expression
- drug repurposing

**这对新稿的影响**  
严禁把“sex GWAS + bulk eQTL + V2G + drug prediction”包装成新贡献。新稿必须依靠 **cell-type caQTL/eQTL regulatory cascade + independent replication + disease tissue** 来产生新增信息。

**数据可得性声明**  
原文：sex-specific meta-analysis summary statistics will be available via GWAS Catalog upon publication.

**本轮实际检查结果**

- 论文和PMC：已公开；
- GWAS Catalog trait page：存在 systemic sclerosis；
- 按 PMID/DOI/title/GCST检索：本轮仍未确认该2026研究的精确GCST accession；
- 因此尚未获得可验证的 female/male full summary files。

**状态**：🔴 `HARD_GATE_PENDING`

入口：
- <https://pubmed.ncbi.nlm.nih.gov/41999721/>
- <https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/>
- <https://www.ebi.ac.uk/gwas/efotraits/MONDO_0005100>

---

### 1.2 2019 overall SSc GWAS — FALLBACK / PIPELINE CONTROL

**文献**  
López-Isac E, et al. *GWAS for systemic sclerosis identifies multiple risk loci and highlights fibrotic and vasculopathy pathways.* Nature Communications. 2019.

- 26,679 individuals
- 9,095 cases
- 17,584 controls
- European ancestry meta-analysis
- 27 independent genome-wide significant signals

**GWAS Catalog**：GCST009131  
**状态**：🟢 OPEN / RELIABLE FALLBACK

入口：<https://www.ebi.ac.uk/gwas/labs/studies/GCST009131>

**用途限制**：
- 可用于 harmonization pipeline、coloc/fine-mapping smoke test；
- 可作为 overall SSc主分析的保底方案；
- **不能替代2026 male/female stats并继续声称是sex-specific causal architecture。**

---

### 1.3 East Asian / Japanese SSc GWAS — TRANS-ANCESTRY AUXILIARY

2024 Japanese SSc GWAS提供独立 ancestry signal，可用于：

- candidate locus external support；
- cross-ancestry consistency；
- fine-mapping sensitivity；

但不适合和 FinnGen/TenK10K 直接混为一个同质European discovery分析。

**状态**：🟢 secondary only

---

## 2. Population-scale molecular QTL层

### 2.1 FinnGen single-nucleus multiome — PRIMARY MOLQTL DISCOVERY

官方公开日：**2026-08-13**

| 指标 | 官方值 |
|---|---:|
| individuals | 1,108 |
| snRNA nuclei | 10,612,211 |
| snATAC nuclei | 7,100,899 |
| cell types | 33 (9 level-1 + 24 level-2) |
| genes | 27,294 |
| ATAC peaks | 297,024 |
| variants | 17,167,198 |

**可用结果**：

- cis-eQTL summary statistics
- cis-caQTL summary statistics
- SuSiE fine-mapping
- peak–gene links
- CASCADE categorization
- GWAS colocalization (FinnGen R12/KANTA)
- consensus peaks
- cell-type accessibility tracks

**访问方式**：官方说明需要填写online form，随后通过email获得下载指引；下载本身免费。

**状态**：🟡 `PUBLIC_BUT_MANUAL_ACCESS_STEP`

官方入口：<https://www.finngen.fi/en/access_results>

### Build
FinnGen genotype data官方采用 GRCh38/hg38。multiome release本身的具体 variant file header/build 仍需要下载后逐文件核实，不以常识代替实际schema检查。

FinnGen build说明：<https://docs.finngen.fi/finngen-data-specifics/red-library-data-individual-level-data/genotype-data/human-genome-build-we-use-and-how-do-we-report-genotypes>

### 本项目正确用途

FinnGen是**遗传调控 discovery**，不是SSc疾病组织样本。其价值是：

`variant → cell-specific chromatin accessibility → cell-specific gene expression`

而不是证明该基因在SSc皮肤中差异表达。

---

### 2.2 TenK10K Phase 1 — INDEPENDENT eQTL REPLICATION

- 1,925 donors
- European ancestry
- ~5.44 million PBMCs after QC
- 28 immune cell types
- matched WGS
- 154,932 common-variant sc-eQTLs / 17,674 eGenes（项目论文报告）

Zenodo开放：

- gene-level common cis-eQTL results
- full common cis p-values ±100 kb
- one file per 28 immune cell types

**状态**：🟢 OPEN

入口：<https://zenodo.org/records/18221260>

**R3建议**：
TenK10K只承担“独立复制/方向支持”，不要把它再做成一篇泛疾病MR atlas，因为其团队已经对大量疾病/biomarkers做过这一层。

---

### 2.3 OneK1K — SECONDARY / LEGACY REPLICATION

- 982 donors
- 1.27M PBMCs
- 14 immune cell types
- 26,597 independent cis-eQTLs

**状态**：🟢 open downloads

入口：<https://onek1k.org/>

**定位**：若FinnGen与TenK10K在某细胞类型定义不完全对应，可用于较粗粒度的第三证据层；不再作为主创新资源。

---

## 3. SSc disease-tissue validation层

### 3.1 GSE312129 — PRIMARY DISEASE-TISSUE MULTIOME

**研究**：early, untreated diffuse cutaneous SSc skin

- 10 SSc + 4 healthy controls
- SSc: 7 female / 3 male
- HC: 2 female / 2 male
- average SSc disease duration ~14.4 months
- baseline mRSS ~22.9
- snRNA + snATAC
- 34,525 QC nuclei (paper)
- 12 major cell types
- Visium on all 10 SSc tissue sections
- raw GEO tar: ~54.3 GB
- assembly: hg38

**状态**：🟢 OPEN

GEO：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE312129>

### 正确分析角色

1. genetically prioritized gene 是否在对应/相近 cell type 中表达；
2. target gene 是否呈 SSc-vs-HC state shift；
3. target regulatory peak/linked motif/program 是否在 disease state 改变；
4. genetic cascade 所指向的 immune cell 是否与 fibroblast/vascular niche发生疾病特异重塑；
5. 空间层只用于定位/邻域支持。

### 不允许的过度推断

- 10+4样本不能自己做population QTL；
- Visium只有SSc不能作为独立SSc-vs-HC spatial DE；
- 数据本身的 70% female / 30% male 与疾病流行病学相近，但 **n=3 male太小，不能承担强sex×disease interaction验证**。

因此疾病组织层是“disease-context validation”，不是第二个sex-GWAS。

---

### 3.2 GSE312932 — XENIUM OPTIONAL SPATIAL

- 10 SSc samples
- Xenium
- no healthy control series in this accession
- raw ~30.6 GB

**状态**：🟢 OPEN / OPTIONAL

入口：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE312932>

**用途**：Tier-1 gene/cell pair的空间定位、邻域、cell-cell proximity。  
**不用途**：SSc-vs-HC spatial differential expression。

---

### 3.3 GSE249279 — INDEPENDENT SKIN RNA/SPATIAL REPLICATION

- 42 samples
- human SSc skin scRNA + spatial
- merged raw counts H5 ~392.9 MB
- GEO raw tar ~34.5 MB + SRA
- focus: myofibroblast + EndoMT + Hippo pathway

**状态**：🟢 OPEN / HIGH-VALUE REPLICATION

入口：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE249279>

优点：相对轻量，可作为R4最先进入的独立表达验证。

---

### 3.4 GSE236111 — SMALL TARGETED REPLICATION

- 2 healthy + 4 SSc
- scRNA skin
- IFN-1 / endothelial focus
- processed data available
- ~47.7 MB raw tar

**状态**：🟢 OPEN / SMALL-N

入口：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE236111>

如果优先 target落在 IFN / endothelial axis，这个数据集价值显著上升；否则只能作为补充。

---

### 3.5 GSE312591 — CORRECTED ROLE

**R2错误倾向**：将其视作一般疾病图谱候选。  
**R3修正**：主要是 SSc fibroblast RUNX1 knockdown vs control perturbation。

**状态**：🟡 CONDITIONAL

**只在RUNX1或其直接程序成为Tier-1时使用。**

---

## 4. 数据层兼容性速览

| Source | ancestry | build | scale | role | current risk |
|---|---|---|---|---|---|
| 2026 SSc sex GWAS | predominantly European | **verify file** | 10,653 cases | primary GWAS | **file unresolved** |
| GCST009131 | European | verify catalog file | 9,095 cases | fallback | low |
| FinnGen multiome | Finnish | GRCh38 framework; verify release file | 1,108 | primary molQTL | manual access |
| TenK10K | European | GRCh38 WGS | 1,925 | replication eQTL | low |
| GSE312129 | mixed US clinical cohort | hg38 | 10+4 | disease multiome | small patient n |
| GSE249279 | disease skin | hg38 spatial reported | 42 samples | independent tissue | low |
| GSE236111 | disease skin | verify per-file | 4+2 | IFN/EC validation | small n |

---

## 5. 下载优先级

### Phase A — <5 GB级别 / smoke test
1. 2026 sex GWAS full stats（若取得）
2. FinnGen manifest + BCL11A/IRF4/RPL3-PDGFB相关molQTL slices / fine-map files
3. TenK10K gene-level +必要的full cis files
4. GSE249279 processed H5
5. GSE236111 processed files

### Phase B — tens of GB
6. GSE312129 selected processed matrices / ATAC fragments
7. GSE312129 full 54.3 GB raw only if necessary
8. GSE312932 Xenium only after Tier-1 targets frozen

**原则**：不要先下载84+GB空间/多组学大包，再发现主GWAS文件拿不到。

---

## 6. R4A必须生成的本地manifest字段

每个实际文件：

```text
source_id
url_or_accession
local_path
filename
bytes
sha256
download_date
assembly
variant_id_schema
chr_schema
position_schema
ref_allele
alt_allele
effect_allele
beta_or_or
se
p
maf
sample_size
cell_type
gene_or_peak_id
notes
```

任何 build/allele 不明确的文件不得进入合并分析。
