# CMM R7B0：PBC-wide 56×14 benchmark 冻结协议

## 冻结对象

PBC GWAS remote inventory 与 locus ranges 定义 56 个 study-derived regions；OneK1K 固定 14 个细胞类型，形成 `56 × 14 = 784` 个预登记 scaffold rows。该文件是分析宇宙的身份和规则冻结，不是已经完成的 784 个 QTL 结果。

## 基因与变异规则

基因先按 OneK source cis-eQTL q<0.05 至少在一个细胞中纳入，随后对所有具有可用 summary、足够 disease–QTL overlap 和明确 GRCh37 BIM A1/A2 identity 的 cell–gene 组合进行测试。变异要求至少 200 个共同变异；未由直接 allele identity 解决的高频 palindromic variants 排除。每个 cell 只使用其真实 active donors；不得把 980 covariate rows 当作每个细胞的有效 QTL N。

## 统计和触发规则

screen 使用 coloc.abf，`p1=p2=1e-4`，`p12=1e-6/1e-5/1e-4`。只有默认 `PP.H4≥0.80` 且 `H4/(H3+H4)≥0.80`，或预设的 H3/H4 ambiguity（`PP.H3+PP.H4≥0.80` 且比例位于 0.20–0.80）才允许进入来源匹配 LD 和多信号分解。PF10 是 primary；corrected PF50 只能在 source identity 通过后作为 matched sensitivity。

分类固定为 `STABLE_H4`、`WEAKENED_H4`、`REVERSED_TO_H3`、`UNINFORMATIVE` 和 `QC_FAIL`。这些阈值在看全量 posterior 前冻结，避免从结果反推 universe 或 trigger。

机器冻结文件：`3_results/03_qtl/R7B0/R7B0_PBCwide_56x14_universe_scaffold.tsv` 和 `3_results/00_audit/R7B0/R7B0_PBCwide_universe_freeze.json`。
