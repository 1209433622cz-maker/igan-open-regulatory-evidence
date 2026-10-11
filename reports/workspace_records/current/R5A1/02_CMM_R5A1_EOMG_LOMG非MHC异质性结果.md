# CMM R5A1：EOMG–LOMG 非 MHC 异质性结果

日期：2026-09-13

## 结果表

所有 beta 均相对 harmonised 文件的 ALT allele。

| 区域 / lead | ALT | EOMG beta（P） | LOMG beta（P） | Phet | Bonferroni Phet | 判定 |
|---|---|---|---|---:|---:|---|
| chr1 rs2476601 | G | -0.3851 (`3.61e-9`) | -0.3898 (`9.26e-15`) | 0.9545 | 1.000 | 亚型共享正控 |
| chr2 rs7596255 | T | +0.8321 (`3.87e-8`) | -0.2302 (`0.0544`) | `3.67e-8` | `1.47e-7` | EOMG–LOMG 方向翻转 |
| chr5 rs6861227 | G | +0.3710 (`1.05e-9`) | +0.0383 (`0.421`) | `1.64e-5` | `6.57e-5` | EOMG 富集 |
| chr18 rs7239261 | C | +0.0307 (`0.518`) | -0.2591 (`1.56e-14`) | `6.50e-7` | `2.60e-6` | LOMG 富集 |

## 技术复核

- chr2 的 effect allele 在 EOMG 与 LOMG 中均为 T，EAF 分别约 0.0191 与 0.0270；方向翻转不是由 effect allele 交换造成。
- chr5 的 EAF 分别约 0.1393 与 0.1400，频率高度接近；异质性来自效应幅度差异。
- chr18 的 EAF 分别约 0.6258 与 0.6317；LOMG 效应明显、EOMG 近零。
- chr1 两亚型效应量几乎相同，证明当前对齐和异质性计算能够保留预期的共享信号。

NCBI RefSNP 双 build 复核坐标：

| rsID | GRCh37 | GRCh38 |
|---|---:|---:|
| rs2476601 | chr1:114377568 | chr1:113834946 |
| rs7596255 | chr2:39379926 | chr2:39152785 |
| rs6861227 | chr5:150447128 | chr5:151067567 |
| rs7239261 | chr18:60005046 | chr18:62337813 |

这一步纠正了 OneK1K GRCh37 与 TenK10K/GWAS GRCh38 的跨 build 扫描风险。

## 科学解释边界

当前证据支持“存在可重复计算的亚型效应差异”，尚不支持：

- 某个最近基因是效应基因；
- EOMG 与 LOMG 由不同因果变异驱动；
- QTL 与疾病共享同一因果信号；
- 细胞类型或组织表达介导疾病风险。

R5A2 必须在每个区域以完整 summary statistics、等位基因 harmonization 和 LD 进行信号级检验。

机器可读表：`3_results/01_gwas/R5A1/EOMG_LOMG_heterogeneity_at_GWS_region_leads.tsv`。

