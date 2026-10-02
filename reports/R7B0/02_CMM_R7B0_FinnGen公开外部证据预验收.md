# CMM R7B0：FinnGen 2026 公开外部证据预验收

## 资源与可访问性

FinnGen 2026 immune multiome 已提供公开 CASCADE gene、region、variant-coloc 和 phenotype API；个体级 genotype/LD 不在本轮使用，避免把受限资源写成公开复现。

`CHIRBIL_PRIM` 的公开 phenotype metadata 为 760 cases、372,273 controls、3 genome-wide significant signals。此前仅根据旗舰图的 439-trait filter 推断 PBC 不在 overview；本轮通过 `coloc/by_variant` 直接核查后，撤销“PBC absent”表述。

## 直接机器证据

对 IL12RB2 的两个 CASCADE top variants 查询公开 endpoint，均返回 3 条 CHIRBIL_PRIM 配对：FinnGen R12 GWAS 与 IL12RB2 eQTL 的 l1.NK、l2.NK 和 PBMC 记录。三条记录的 `PP.H4.abf` 为约 `0.9698–0.9706`，credible-set overlap 为 5–9，GWAS/QTL beta 均为负向。该证据支持一个可复查的 PBC–IL12RB2 external public coloc axis。

对 FCRL3 marginal lead 的公开 variant endpoint 返回 90 条配对，但没有 CHIRBIL_PRIM 记录。因此 FCRL3 在 FinnGen CASCADE 中目前只有强分子层可行性，缺少本轮直接读取的 PBC coloc 证据。

## 解释边界

FinnGen R12 的直接 endpoint 是外部公开资源层支持，不等于 OneK1K 的同一 cell-specific LD 和 phenotype model 已被完全复现，也不替代 disease-side study-derived LD。IL12RB2 可进入后续 external replication adjudication；FCRL3 不能因为 OneK1K/TenK 证据而自动获得同等 FinnGen PBC claim。

公开事实来源：[FinnGen access/results](https://www.finngen.fi/en/access_results)、[FinnGen multiome code release](https://zenodo.org/records/21982484)、[CASCADE public API](https://cascade.finngen.fi/)。本地 receipt 位于 `3_results/01_intake/R7B0/finngen_cascade`。
