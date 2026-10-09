# CMM R7B2A 执行摘要：同输入归因与稿件锁定

## 最终判定

```text
PBC_PRIMARY_PROJECT = GO
R7B2A = COMPLETE

V3-G0_INPUT_LOCK = PASS
V3-G1_CONTRAST_VALID = PASS
V3-G2_COVERAGE = PASS
V3-G3_SIMULATION_INTERPRETABLE = PASS_WITH_SCOPE_LIMIT
V3-G4_ATTRIBUTION = PASS
V3-G5_MANUSCRIPT_LOCK_ASSETS = PASS

NEW_LOCUS_GENE_CELL_SELECTION = 0
NEW_BIOLOGICAL_ANALYSIS_REQUIRED = NO

NEXT = R7B2_FULL_ENGLISH_MANUSCRIPT_V1
```

R7B2A 按 RP v3 固定的 642 个 comparison 完成 A0/A1/A2/M 桥接。A0 是历史 GCST + 原支持集 ABF；A1 只把支持集改为实际多信号集合；A2 再把疾病统计改为 GJOKA matched-z；M 为历史冻结的来源匹配多信号结果。没有按结果增加或删除位点、基因、细胞或比较。

## 中心结果

- 实际多信号支持集相对原 ABF 每项少 19–114 个变异，中位少 65 个，中位减少 7.67%。
- A0 可在最大绝对误差 `3.543e-13` 内重放，642/642 top shared variant 一致。
- 支持集变化 A0→A1 改变 15/642 个分类，但历史 112 个 H4 全部保留。
- 疾病统计变化 A1→A2 改变 19/642 个分类。
- 同输入 A2→M 中，79 个 H4 和 413 个 H3 保持；8 个 H4→H3，10 个 H3→H4。
- 历史 12 个方向反转中，10 个仍是严格方向反转；IL12RB1/NK 与 SYNGR1/NK 应改写为 A2 歧义态经 M 解析。
- 固定/原生 sdY 及 GJOKA matched-z/rounded BETA-SE 敏感性均为 0 个分类变化。

## 模拟解释

486,000 次主模拟没有技术错误。325,218 次没有 signal pair 的原因可定位为一侧或两侧未形成 credible set；两侧均有 credible set 却没有 pair 的次数为 0；160,782 次形成可评价 pair。模拟必须同时报告无条件性能与 pair-conditional 性能。次级 mismatch 分支没有保存逐侧 CS 计数，因此其 69,346 个 zero-pair fit 不作 no-CS 机制归因，也不为此重跑 81,000 次拟合。

## 稿件定位

最稳健的中心表述为：PBC-wide single-causal screening 之后，对预设 high-information subset 进行同输入、来源匹配的多信号重分类，并用真值已知模拟区分信号发现充分性与已形成 signal pair 后的判定行为。真实数据支持双向重分类，但不能证明哪种方法在真实对象中“正确”或普遍优越。
