# CMM R3 — 统计兼容性与冻结分析协议 v1

**目的**：提前冻结“什么证据算强、什么分析允许进入主文、哪些结果必须降级”，防止看到结果后临时修改标准。

---

## 1. 总体原则

本项目不是把MR、coloc、scRNA、ATAC、spatial各跑一遍，而是检验一条有方向的调控链：

> `SSc genetic association → molecular QTL → regulatory element → target gene → cell type → disease tissue state`

每一层必须有不同的问题，不允许同一证据被重复包装成多层独立支持。

---

## 2. Harmonization hard rules

### 2.1 Genome build
首选统一到 **GRCh38**。

- FinnGen framework：GRCh38；
- TenK10K WGS：GRCh38；
- GSE312129：hg38；
- 2026 sex GWAS：**下载后核实，不预设**；
- GCST009131：按实际GWAS Catalog summary file metadata处理。

若需要liftOver：

1. 保留 original_chr/original_pos；
2. 记录chain版本；
3. 删除multi-map/unmapped；
4. liftover后重新对ref allele；
5. 不允许只根据rsID盲合并。

### 2.2 Alleles
必须明确：

- ref
- alt
- effect allele
- non-effect allele
- beta direction

A/T、C/G ambiguous SNP：

- 若MAF缺失且无法稳健判向，删除；
- 若有频率，只有在频率匹配足够明确时保留；
- indel必须左对齐、normalize。

### 2.3 Variant identity
主键优先：

`chr:pos:ref:alt@GRCh38`

rsID仅作为辅助字段。

---

## 3. GWAS signal definition

### Primary
2026 female/male sex-specific summary statistics。

### Secondary
2019 overall SSc GCST009131。

### Sensitivity
East Asian SSc GWAS仅用于 cross-ancestry locus support，不直接与Finnish LD混合fine-map。

### Locus window
默认 lead signal ±500 kb 起始；若credible set / LD block可用，则优先以 signal-defined region替代固定窗口。

MHC：默认独立处理，避免复杂LD污染全局阈值。

---

## 4. Fine-mapping策略

### 优先顺序
1. 使用 source-provided SuSiE molQTL credible sets；
2. GWAS若提供credible sets则直接使用；
3. 若需自己fine-map GWAS，必须使用与GWAS ancestry匹配的LD reference；
4. 不用一个通用1000G EUR LD替代所有源的source-specific LD，除非作为sensitivity。

### 输出
每个locus至少输出：

- number of independent signals
- CS size
- CS coverage
- lead variant
- max PIP
- shared variants across GWAS/caQTL/eQTL CS

---

## 5. Colocalization冻结规则

### 5.1 不再只用单因果变体 coloc.abf 作为唯一主方法
因为GWAS/eQTL/caQTL都可能多信号。

### Primary
**SuSiE-aware / signal-aware colocalization**，在数据允许时逐信号比较。

### 三组关键检验
1. GWAS ↔ caQTL
2. GWAS ↔ eQTL
3. caQTL ↔ eQTL

### Full cascade强证据
理想情况：三者在相容signal/credible-set层面均有共享证据，并且peak–gene link支持对应关系。

### 阈值
不预注册一个“PP4=0.80即绝对真”的机械规则。

建议：

- **Strong**: PP shared ≥0.80；
- **Moderate**: 0.50–0.80，需附加fine-mapping/replication支持；
- <0.50：不进入Tier-1。

如果source-provided coloc采用不同prior/metric，主报告中明确注明，不能直接把不同模型posterior横向等同。

---

## 6. Regulatory cascade分类

### Tier C1 — Full cascade
GWAS ↔ caQTL shared signal + caQTL/eQTL linked + peak→gene relation + GWAS/eQTL support。

### Tier C2 — Expression-mediated
GWAS ↔ eQTL强共享，但chromatin link不完整。

### Tier C3 — Accessibility-mediated candidate
GWAS ↔ caQTL强共享，但target gene仍不确定。

### Tier C4 — Positional/supportive only
只有lead SNP overlap/nearest gene/weak annotation。

**主文重点只放C1，少量C2。C3/C4进入补充材料。**

---

## 7. MR的角色重新限定

R3不建议让MR成为全论文中心。

原因：

- TenK10K等资源已经做了大量cell-specific MR atlas；
- 单基因cis instruments容易与coloc信息重复；
- 多信号和LD条件下，未经共享因果验证的MR容易产生误导。

### MR只用于
对完成C1/C2证据链的target做：

- constrained cis-MR / SMR-like sensitivity；
- directionality consistency；
- 与coloc共同解释。

### 不允许
“MR显著 = 证明该基因在该细胞中导致SSc”。

建议措辞：

> genetically supported association / genetically proxied effect / evidence consistent with a regulatory contribution

而不是：

> causal gene / causal cell mechanism

除非有更强干预证据。

---

## 8. TenK10K replication protocol

### 目标
复制的不是“P值”，而是：

1. same target gene；
2. compatible cell lineage；
3. same risk-allele → expression direction（可判定时）；
4. independent donor cohort。

### Cell mapping
FinnGen 33 cell types ↔ TenK10K 28 cell types建立一个预定义 mapping table：

- exact match
- parent-lineage match
- no match

不在看到结果后临时把所有T细胞都算“复制”。

---

## 9. GSE312129 disease tissue protocol

### 9.1 主用途
“genetic-to-disease-state concordance”，不是重新做一篇SSc atlas。

### 9.2 预定义分析
对 Tier-1/C1 targets：

1. gene detection rate by cell type；
2. pseudobulk SSc vs HC within corresponding cell type；
3. donor-level effect estimate；
4. snATAC peak accessibility if homologous regulatory region可定位；
5. motif/TF program（仅当cascade本身支持）；
6. cell-state enrichment；
7. spatial localization in SSc Visium/Xenium。

### 9.3 pseudoreplication防护
统计单位必须以**donor**为主，不把34,525 nuclei当成34,525独立患者。

优先：

- pseudobulk per donor × cell type；
- mixed model with donor random effect（若适用）；
- effect size + CI；

不以单细胞Wilcoxon超小P值作为主证据。

### 9.4 Sex分析限制
SSc n=10（7F/3M）；不能以此独立发现sex-specific tissue effects。

允许：

- descriptive stratification；
- check whether effect is directionally contradictory；
- sensitivity excluding one sex；

不允许：

- 强claim male-vs-female tissue mechanism。

---

## 10. Independent tissue replication

### GSE249279
主用于：

- target gene/cell state replication；
- fibroblast/EndoMT context；
- spatial localization。

### GSE236111
当target涉及IFN/endothelium时升级为重点；否则补充。

### GSE312932
仅Tier-1 target出现后做高分辨率空间定位。

---

## 11. Translation gate

DrugBank / ChEMBL / Open Targets / perturbation只对以下targets开放：

### Tier-1 target 必须满足至少
- strong genetic shared-signal evidence；
- identifiable gene and cell context；
- independent QTL support or strong orthogonal molecular evidence；
- disease tissue concordance。

否则，不允许为了“论文完整”硬加docking。

### Drug direction
必须结合：

- risk allele ↑/↓ expression；
- disease tissue ↑/↓ state；
- drug agonist/antagonist direction；

不能只因为“有药靶关系”就叫候选治疗。

---

## 12. Multiple testing

不同分析家族分别控制FDR，不把所有P混成一个总FDR：

- GWAS locus discovery：沿用原研究阈值；
- molQTL：source threshold + project sensitivity；
- tissue pseudobulk：BH FDR per cell-type family / planned family；
- pathway enrichment：BH FDR；
- ligand-receptor：只作为预定义target context，避免全局探索后选择性报告。

---

## 13. Negative results policy

本项目必须保留：

- sex-specific GWAS locus没有molQTL support；
- caQTL有而eQTL没有；
- eQTL有而tissue不表达；
- genetic direction和disease tissue direction不简单一致；
- TenK10K未复制；
- spatial不定位。

负结果决定哪些target降级，是论文可信度的一部分。

---

## 14. R4A smoke test

只做3个新 locus：

1. **BCL11A** (male-specific)
2. **IRF4** (female-specific)
3. **RPL3-PDGFB** (female-specific)

### smoke-test PASS
三者中至少一个能真实完成：

`GWAS signal → FinnGen ca/eQTL → peak–gene → cell → shared signal`

且文件字段、build、allele、LD流程全部跑通。

### smoke-test FAIL
如果三者全都因：

- variant coverage不足；
- no molQTL；
- no shared signal；
- allele/build无法可靠对齐；

则停止全量下载，重新评估整个sex-specific主故事。

---

## 15. 分析DAG

```text
A0_access
  ├─ A1_gwas_sex_female
  ├─ A2_gwas_sex_male
  ├─ A3_gwas_overall_fallback
  ├─ A4_finngen_eqtl
  ├─ A5_finngen_caqtl
  ├─ A6_finngen_finemap_peakgene
  ├─ A7_tenk10k_eqtl
  └─ A8_ssc_tissue

B0_schema_audit
  ↓
B1_build_normalize
  ↓
B2_allele_harmonize
  ↓
B3_locus_extract

C1_gwas_finemap
C2_molqtl_finemap
  ↓
C3_signal_coloc
  ↓
C4_regulatory_cascade
  ↓
C5_tenk10k_replication
  ↓
C6_tissue_concordance
  ↓
C7_tier_assignment
  ↓
C8_translation_only_for_Tier1
```

任何上游gate失败，后续不自动继续。
