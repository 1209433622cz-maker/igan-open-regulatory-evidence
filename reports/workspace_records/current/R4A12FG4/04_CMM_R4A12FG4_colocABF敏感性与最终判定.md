# CMM R4A12FG4：coloc.abf 敏感性与最终判定

## 分析身份

由于 exact coverage 门未通过，本分析标记为 `POST_EXACT_COVERAGE_GATE_SINGLE_CAUSAL_DIAGNOSTIC_ONLY`。使用 891 个 exact GRCh38 REF/ALT 变异，FinnGen R12/R13 为 case-control，TenK10K NK 为 quantitative；QTL sdY 按 coloc 内部同公式由 varbeta、MAF、N 估计为 0.492066。软件为 R 4.6.1、coloc 5.2.3。

## 结果

| Release | p12 | PP.H3 | PP.H4 | H4/(H3+H4) |
|---|---:|---:|---:|---:|
| R12 | 1e-6 | 0.2692 | 0.3558 | 0.5693 |
| R12 | 1e-5 | 0.0641 | 0.8467 | 0.9297 |
| R12 | 1e-4 | 0.0074 | 0.9822 | 0.9925 |
| R13 | 1e-6 | 0.3353 | 0.3311 | 0.4968 |
| R13 | 1e-5 | 0.0843 | 0.8319 | 0.9080 |
| R13 | 1e-4 | 0.0099 | 0.9802 | 0.9900 |

两版 top shared variant 均为 `1:67324915:T:C`，单变异 H4 posterior 约 0.393–0.394。主先验下达到预设 H4 门，但低共享先验下 H4 <0.50 且 H4/(H3+H4) <0.80，因此不能判稳健 shared。

NK source SuSiE 有两个 credible sets，违反把单因果模型当作最终模型的前提；coloc 官方文档也要求 ABF 使用稠密变异图谱。本轮 exact overlap 只有 65.23%，疾病 regional lead P≈2.6–2.8×10^-5，且 R12/R13 是高度重叠的 release 更新而非独立复制。

最终分类：R12 与 R13 均为 `AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY`。保留 IL12RB2 作为需要 LD-aware 判定的 secondary all-sex candidate；不升级 C1、不启动 chromatin layer、不启动 R4B，也不写成阴性。
