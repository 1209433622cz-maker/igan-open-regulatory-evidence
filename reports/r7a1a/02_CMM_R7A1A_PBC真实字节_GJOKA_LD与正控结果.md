# R7A1A：PBC 真实字节、GJOKA LD 与正控结果

## 核心 GWAS

- accession：`GCST90061440`
- GRCh37；欧洲五 panel meta-analysis；8,021 cases / 16,489 controls，N=24,510
- 本地字节：373,673,109
- MD5：`c48ede08359f6fc919810591cc0daad7`，与官方 metadata 一致
- SHA-256：`439aa72c59b876236de2b8172c443a447cefa6868ace535183cec8b758a05921`
- 5,054,572 行全部通过 chr/position/allele/beta/SE/P 严格数值检查
- 非 MHC P≤5e-8 行：5,522
- 1 Mb 距离临时 lead：45；仅用于 intake，不能称 LD-independent signals

## GJOKA 研究样本匹配输入

远端文件 `GJOKA_SUMSTATS.zip`：

- HTTP Content-Length：1,184,054,519
- Accept-Ranges：bytes
- central directory：112 成员，全部带 CRC
- 56 个 `sumstats_i.assoc.logistic`
- 56 个对应 `covmat_i.ld`
- 56/56 locus pair 完整

本轮读取全部小型 sumstats 成员并恢复 GRCh37 区间，没有下载 1.18 GB 整包及大矩阵，因为 R7A1B 尚未触发。三个正控分别落入：

- IL12RB2 → locus 2 → `covmat_2.ld`
- FCRL3 → locus 4 → `covmat_4.ld`
- INAVA → locus 6 → `covmat_6.ld`

## 正控

IL12RB2 与 FCRL3 是真正的双资源阳性。INAVA 在 TenK 有 CD4_Proliferating CS，但 OneK 仅旧符号 C1orf106/CD4_NC top-eQTL，q≈0.318。它必须保留在 R7A1B 作为预注册的弱/证伪对象，不能被替换成更好看的基因。

## PBC 判定

```text
PBC_R7A1A_LITERAL_GATE = PASS
PBC_CROSS_RESOURCE_TESTABLE = 3/3
PBC_CROSS_RESOURCE_SOURCE_POSITIVE = 2/3
PBC_STUDY_MATCHED_LD = PASS_56_PAIRS
PBC = GO_R7A1B_BOUNDED
```

- GWAS Catalog PBC `GCST90061440`: https://www.ebi.ac.uk/gwas/studies/GCST90061440
- GWAS Catalog CeD `GCST000612`: https://www.ebi.ac.uk/gwas/studies/GCST000612
- GWAS Catalog CeD `GCST010064`: https://www.ebi.ac.uk/gwas/studies/GCST010064
- 被排除的 UKB-derived CeD `GCST90014442`: https://www.ebi.ac.uk/gwas/studies/GCST90014442
- PBC 2021 GWMA (PMID 34033851): https://pubmed.ncbi.nlm.nih.gov/34033851/
- CeD 2010 GWAS (PMID 20190752): https://pubmed.ncbi.nlm.nih.gov/20190752/
- CeD 2020 Immunochip meta-analysis (PMID 31591516): https://pubmed.ncbi.nlm.nih.gov/31591516/
- GWAS Catalog summary-statistics access: https://www.ebi.ac.uk/gwas/labs/downloads/summary-statistics
