# CMM R7A1A 执行摘要：PBC/CeD 真实字节与 QTL 正控终裁

**日期：2026-09-15**

## 最终判定

```text
R7A1A = COMPLETE
NEW_PRIMARY_PROJECT = NOT_YET_APPROVED

PBC = GO_R7A1B_BOUNDED_SIGNAL_GATE
CeD = HOLD_NOT_SELECTED

NEXT_STAGE = R7A1B_PBC_3CONTROL_SIGNAL_GATE
```

PBC 与 CeD 都通过了 R7A0 字面技术门：合格开放 GWAS 字节、可计算 schema、至少 5 个非 MHC 临时区域、3/3 正控在 OneK1K 与 TenK10K 均可找到数据。真正拉开差距的是阳性密度。PBC 有 2/3 正控在两个 QTL 资源中均为源数据阳性；CeD 只有 1/3。PBC 还确认存在 56 组研究样本匹配的 locus sumstats/LD 矩阵。

因此不宣布 PBC 已成为主项目，也不同时为两个疾病投入信号级计算。下一轮只允许用 PBC 的 IL12RB2、FCRL3、INAVA/C1orf106 做一次有边界终裁；至少 2/3 得到稳健 disease↔OneK shared signal，并有至少 1 个同基因兼容细胞的 TenK 独立复制，才允许 `NEW_PRIMARY_PROJECT=PBC`。

## 真实字节

| 对象 | 字节 | SHA-256 | 结果 |
|---|---:|---|---|
| PBC GCST90061440 | 373,673,109 | `439aa72c59b876236de2b8172c443a447cefa6868ace535183cec8b758a05921` | 5,054,572/5,054,572 数值行有效；45 个非 MHC 临时区域 |
| CeD GCST000612 harmonised | 40,403,376 | `d6f6a3656b6f0d86045f5115f31b1020ddcf05dec34545d1034b9c4c4929441c` | 507,833/523,390 数值行满足严格条件；12 个非 MHC 临时区域 |
| CeD GCST010064 | 10,451,587 | `5c7a91b5ee4e4e63d8c11a8fca2ff4a0b2ffe64042e6494154ea34d31b259b7c` | 来源合格但缺 SE，仅作 2020 研究来源审计 |

`GCST90014442` 虽有约千万变异和大样本，但研究标题及元数据明确为 UK Biobank 分析，违反冻结排除规则，未下载为核心输入。

## 六正控终裁

| 疾病 | 正控 | OneK1K | TenK10K | 判定 |
|---|---|---|---|---|
| PBC | IL12RB2 | NK q≈7.53e-9 | 15 个 BH-q<0.05 细胞；11 个 SuSiE 细胞 | 双资源阳性 |
| PBC | FCRL3 | 7 个 q<0.05 细胞 | 17 个 BH-q<0.05 细胞；14 个 SuSiE 细胞 | 双资源强阳性 |
| PBC | INAVA/C1orf106 | CD4_NC 可测，q≈0.318 | CD4_Proliferating 阳性且有 CS | 可测但 OneK 弱 |
| CeD | CSK | 14 细胞可测，均 q≥0.05 | 5 个 BH-q<0.05 细胞；3 个 SuSiE 细胞 | OneK 弱 |
| CeD | TRAFD1 | 14 细胞可测，均 q≥0.05 | B_naive BH-q<0.05，无 SuSiE CS | OneK 弱 |
| CeD | UBASH3A | 4 个 q<0.05 T 细胞 | 13 个 BH-q<0.05 细胞；11 个 SuSiE 细胞 | 双资源阳性 |

## 来源

- GWAS Catalog PBC `GCST90061440`: https://www.ebi.ac.uk/gwas/studies/GCST90061440
- GWAS Catalog CeD `GCST000612`: https://www.ebi.ac.uk/gwas/studies/GCST000612
- GWAS Catalog CeD `GCST010064`: https://www.ebi.ac.uk/gwas/studies/GCST010064
- 被排除的 UKB-derived CeD `GCST90014442`: https://www.ebi.ac.uk/gwas/studies/GCST90014442
- PBC 2021 GWMA (PMID 34033851): https://pubmed.ncbi.nlm.nih.gov/34033851/
- CeD 2010 GWAS (PMID 20190752): https://pubmed.ncbi.nlm.nih.gov/20190752/
- CeD 2020 Immunochip meta-analysis (PMID 31591516): https://pubmed.ncbi.nlm.nih.gov/31591516/
- GWAS Catalog summary-statistics access: https://www.ebi.ac.uk/gwas/labs/downloads/summary-statistics
