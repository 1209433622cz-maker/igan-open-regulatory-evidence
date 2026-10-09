# CMM R7B1E 执行摘要：诊断闭环与证据总冻结

## 最终判定

```text
R7B1E0_KRIGING_DIAGNOSTIC_REPLAY = PASS
R7B1E0_SIGNAL_SEMANTICS = PASS
R7B1E0_INDEPENDENT_QA = 21/21 PASS

R7B1E_CLAIM_EVIDENCE_FREEZE = PASS
R7B1E_FIGURE1_6_SOURCE_FREEZE = PASS
R7B1E_INDEPENDENT_QA = 21/21 PASS

HISTORICAL_CLASSIFICATIONS_CHANGED = NO
POSTERIOR_REFIT_REQUIRED = NO
NEW_GENE_CELL_LOCUS_SELECTION = NO
GENERAL_METHOD_SUPERIORITY = NOT_ESTABLISHED

NEXT = R7B2_MANUSCRIPT_V1
```

本轮先完成 R7B1E0，而没有直接进入证据整合。原因是历史 R7B1B runner 对 `susieR::kriging_rss()` 的返回对象采用了错误接口假设：代码只接受 `data.frame`，但当前 `susieR 0.14.2` 返回包含 `plot` 与 `conditional_dist` 的 list。由此造成历史 fit-QC 表中 Kriging 字段系统性缺失。修复仅重放诊断，不重拟合 SuSiE 或 coloc，也不改变既有后验。

精确重放覆盖 47 个 locus、642 个 comparison 和 2,568 个 disease/QTL × PF10/PF50 诊断单元，2,568/2,568 PASS。历史宽松计数 `logLR>2` 为 3,333 行；按 `susieR` 绘图代码实际使用的 `logLR>2 AND |z|>2` 判据，仅有 2 行，对应同一 comparison 的 1 个唯一事件。该事件为 `rs1800378`，不进入任何 credible set，所在 comparison 为 stable H3 且不承担核心主张，因此保留输入、不重拟合。

信号语义审计进一步确认，92/92 个 stable-H4 comparison 在 L10 与至少一个其它 PF10 L 设置中保留同一 shared signal-pair identity；428/428 个 stable-H3 comparison 保留同一 distinct pair identity。32 个 stable-H4 comparison 同时存在 H3-qualifying pair，说明同一 comparison 内可以并存 shared 与 distinct signal pairs。后续稿件必须区分 comparison-level state 与 signal-pair identity，不能把 H3 pair 支持写成“全区域不存在共享信号”。

在诊断与语义闭环后，R7B1E 将 R7B0A、R7B1A、R7B1B、R7B1C、R7B1D 和肝组织边界整合为 22 条 claim–evidence ledger，并冻结 Figure 1–6 的 8 个 panel-level source rows。允许的最高主张为：

> PBC-wide screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset, with scenario-dependent calibration and bounded external/tissue support.

这个表述保留了 PBC-wide screening，但不暗示 6,923 个 comparison 全部接受多信号分析；保留了模拟中假 H4 的下降，也同时报告 shared-signal recovery 的代价；保留 IL12RB2/FCRL3 的跨资源支持，但不升级为完整调控级联、组织介导或一般方法优越性。
