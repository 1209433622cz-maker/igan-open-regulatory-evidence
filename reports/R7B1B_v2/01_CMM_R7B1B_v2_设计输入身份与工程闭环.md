# CMM R7B1B v2：设计、输入身份与工程闭环

## 独立审计与设计修订

输入审计包的外部 SHA-256、ZIP CRC 与 7/7 internal checksums 均已通过。我们没有把附件内容当作执行指令直接采用，而是从冻结的 6,923-row master table 独立重建并验证 642 comparisons、286 cell–locus blocks 与 94 GJOKA members。原始 184 未被删除或重新定义。

## 字节级输入

- GJOKA：94/94 members，47 loci；50 个本地复用，44 个 range-fetch；解压字节 2,714,228,510。
- OneK1K：公开 pseudobulk、980-donor PLINK genotype、cell-specific donor lists 与 updated PF50 covariates。
- QTL：642 × PF10/PF50 = 1,284 summaries。
- LD：286 cell–locus blocks × PF10/PF50 = 572 binary correlation matrices，总字节约 2.061 GB；矩阵在 block 层复用，避免按 gene 重复存储。
- 原始 184 个 PF10 summary 逐变异数值回归：184/184 PASS。

## source-identity 修正

端到端正控发现，旧候选级 LD 目录沿用较早的 R7A1B QTL 变异集合。以 IL12RB2–NK 为例，旧实现进入 GJOKA/SuSiE 的共同变异为 1,016 个；current-release v2 重建为 1,033 个。新增 17 个变异来自当前冻结比较集，IL12RB2–NK 的 shared-signal 方向保持不变。v2 因而统一以 current-release comparison identity 重新构建 PF10/PF50 LD，不再混用旧候选目录。

## 可恢复执行

47 个 locus 分开运行，每个 comparison 写独立 state、fit QC、signal-pair posterior 与 credible-set members。调度器允许中断后只续跑未完成项。运行环境固定为 R 4.6.1、susieR 0.14.2、coloc 5.2.3。
