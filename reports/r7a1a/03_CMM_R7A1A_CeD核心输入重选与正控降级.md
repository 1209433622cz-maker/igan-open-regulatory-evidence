# R7A1A：CeD 核心输入重选与正控降级

## 三个候选 CeD 输入

### GCST90014442：排除

来源为 UK Biobank pleiotropy study，违反硬约束。公开可下载与研究来源合格是两个独立条件。

### GCST010064：研究对题，但 schema 不完整

2020 Immunochip meta-analysis 对应冻结正控来源：12,948 cases / 14,826 controls，127,855 行；36 个非 MHC 1 Mb 临时区域。文件有 A1/A2、OR、P，但没有 SE。因此只保留为 secondary disease-evidence/sensitivity object。

### GCST000612：当前合格核心

2010 genome-wide array，4,533 cases / 10,750 controls；harmonised GRCh37：

- bytes：40,403,376
- SHA-256：`d6f6a3656b6f0d86045f5115f31b1020ddcf05dec34545d1034b9c4c4929441c`
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

- GWAS Catalog PBC `GCST90061440`: https://www.ebi.ac.uk/gwas/studies/GCST90061440
- GWAS Catalog CeD `GCST000612`: https://www.ebi.ac.uk/gwas/studies/GCST000612
- GWAS Catalog CeD `GCST010064`: https://www.ebi.ac.uk/gwas/studies/GCST010064
- 被排除的 UKB-derived CeD `GCST90014442`: https://www.ebi.ac.uk/gwas/studies/GCST90014442
- PBC 2021 GWMA (PMID 34033851): https://pubmed.ncbi.nlm.nih.gov/34033851/
- CeD 2010 GWAS (PMID 20190752): https://pubmed.ncbi.nlm.nih.gov/20190752/
- CeD 2020 Immunochip meta-analysis (PMID 31591516): https://pubmed.ncbi.nlm.nih.gov/31591516/
- GWAS Catalog summary-statistics access: https://www.ebi.ac.uk/gwas/labs/downloads/summary-statistics
