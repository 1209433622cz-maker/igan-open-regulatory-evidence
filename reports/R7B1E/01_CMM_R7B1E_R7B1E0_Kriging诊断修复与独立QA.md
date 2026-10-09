# R7B1E0 Kriging 诊断修复与独立 QA

## 缺陷定位

历史脚本 `11_run_r7b1b_v2_multisignal_locus.R` 中的 `safe_kriging()` 在调用 `kriging_rss()` 后，仅当返回值是 `data.frame` 时继续解析。对本机冻结环境的直接审计显示：

```text
R = 4.6.1
susieR = 0.14.2
kriging_rss return = list(plot, conditional_dist)
```

因此历史 `R7B1B_v2_all_fit_QC.tsv.gz` 的 disease/QTL Kriging 字段全部为空。这是诊断记录层缺陷，不等同于 SuSiE 或 coloc 后验错误。

## 重放边界

R7B1E0 使用既有 frozen z、LD、N、variant order 与 stored `s_rss` 重放 `kriging_rss()`。它没有重新拟合模型，没有替换 credible sets，没有改变 PF10/PF50 adjudication，也没有重新筛选 comparison。47 个 locus 的重放总耗时约 24.7 分钟。

| 项目 | 结果 |
|---|---:|
| loci | 47 |
| comparisons | 642 |
| diagnostic units | 2,568 |
| PASS | 2,568 |
| HOLD | 0 |
| historical `logLR>2` rows | 3,333 |
| official-rule raw rows | 2 |
| official-rule unique events | 1 |

## 唯一事件终裁

两条 raw flag 分别来自同一 disease diagnostic 的 PF10 与 PF50 记录，去重后为一个事件：comparison `R7B1_003438`、locus 38、C12orf57/B_IN、variant `12:6172202`（rs1800378）。其 `z≈2.20`、`conditional mean≈-0.66`、`logLR≈2.05`。该变异不属于任何 credible set；comparison 维持 stable H3，PP.H4 约 `5×10⁻6`，也不是 claim-bearing exemplar。

最终处置为 `REVIEWED_RETAIN_INPUT_NO_REFIT`。该结果允许写“诊断接口已修复且唯一官方规则事件经过人工/机器联合复核”，不允许写“数据中完全不存在 z–LD discrepancy”。

## 独立 QA

R7B1E0 独立 QA 为 21/21 PASS。检查覆盖：单元数、locus/comparison 数、有限值、历史宽松计数、官方判据去重、credible-set membership、无 posterior refit、历史标签未改写、signal semantics 数量与协议存在性。
