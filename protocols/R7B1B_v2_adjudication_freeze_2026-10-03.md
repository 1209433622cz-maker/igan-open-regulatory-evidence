# R7B1B v2：642 个高信息比较的预结果多信号判定协议

冻结日期：2026-10-03
状态：`FROZEN_BEFORE_642_MULTISIGNAL_RESULT_REVIEW`

## 1. 适用范围与证据上限

本协议只适用于已经冻结的 642 个高信息比较：原始 184 个 primary trigger verification、455 个 H3 rescue/falsification，以及 3 个 borderline high-information calibration。不得根据本轮 SuSiE 结果增删 locus、gene、cell、configuration 或 threshold。

允许的最高层级表述是：

> PBC-wide ABF screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset.

不得将本轮结果称为全部 6,923 个 locus–gene–cell 比较的多信号全景。

## 2. 固定模型

- 疾病侧：GJOKA study-matched LD；`N = 24,510`。
- QTL 侧：OneK1K cell-specific active donors，current-release pseudobulk、genotype 与 covariates。
- 主模型：PF10，`L = 5, 10, 20`。
- 协变量敏感性模型：PF50，`L = 10`。
- `susie_rss`：`estimate_residual_variance = FALSE`，`estimate_prior_variance = TRUE`，`max_iter = 2000`，`tol = 1e-4`。
- `coloc.susie`：`p1 = p2 = 1e-4`；`p12 = 1e-6, 1e-5, 1e-4`。

## 3. 技术有效性

一个 comparison 只有同时满足以下条件才进入科学重分类：

1. source identity、build、rsID、position、BIM A1/A2 bridge 均通过；
2. GJOKA 与 QTL 的共同变异不少于 200；
3. PF10 L5/L10/L20 与 PF50 L10 共 4 个 disease/QTL SuSiE fit 全部完成并收敛；
4. posterior、LD 与 z-score 不出现非有限值。

没有 credible set 或没有 `coloc.susie` signal pair 属于信息不足，不自动归为技术失败。`estimate_s_rss`、kriging、CS purity 与 PSD projection warning 全量记录；除非导致 fit 不收敛或非有限值，否则作为诊断和敏感性信息，不在看到结果后新增排除阈值。

## 4. 单一 configuration 的固定判定

对每个 configuration：

- `H4_CONFIG_PASS`：默认 `p12=1e-5` 下至少一个 signal pair 同时满足 `PP.H4 >= 0.80` 与 `H4/(H3+H4) >= 0.80`，且同一 `idx1 × idx2` signal pair 在 `p12=1e-6` 下仍满足 `H4/(H3+H4) >= 0.50`。
- `H3_CONFIG_PASS`：默认 `p12=1e-5` 下至少一个 signal pair 同时满足 `PP.H3 >= 0.80` 与 `H4/(H3+H4) <= 0.20`。
- `HIGH_INFORMATION_CONFIG`：默认 `p12=1e-5` 下至少一个 signal pair 满足 `PP.H3 + PP.H4 >= 0.80`。

一个 comparison 可以同时存在 shared pair 与 distinct pair。只要跨模型 H4 稳定门通过，即保留 shared-signal 结论，并单独报告额外 distinct pairs。

## 5. PF10 主终裁

- `H4_SUPPORTED_STABLE`：PF10 L10 为 `H4_CONFIG_PASS`，且 PF10 的 3 个 L 中至少 2 个为 `H4_CONFIG_PASS`。
- `H3_SUPPORTED_STABLE`：未达到稳定 H4；PF10 L10 为 `H3_CONFIG_PASS`，且 PF10 的 3 个 L 中至少 2 个为 `H3_CONFIG_PASS`。
- `MODEL_SENSITIVE`：未达到上述两个稳定门，但至少一个 PF10 configuration 为 H4、H3 或 high-information。
- `UNINFORMATIVE`：PF10 没有任何 high-information signal pair。
- `QC_FAILURE`：未通过第 3 节技术有效性。

PF50 L10 只作为协变量模型敏感性，不替代 PF10 主终裁。PF10 与 PF50 的方向不一致时标记 `PF10_PF50_SENSITIVE`。

## 6. 双向重分类标签

ABF 起始态固定为：

- `ABF_H4_DOMINANT`：112 个 `ROBUST_H4_TRIGGER`；
- `ABF_AMBIGUOUS`：72 个 `H3_H4_AMBIGUITY_TRIGGER`；
- `ABF_H3_DOMINANT`：455 个 `H3_DISTINCT_SIGNAL`；
- `ABF_H4_BORDERLINE`：3 个 borderline calibration。

与 PF10 主终裁交叉后，输出：

- `STABLE_H4`、`H4_TO_H3`、`H4_TO_MODEL_SENSITIVE`、`H4_TO_UNINFORMATIVE`；
- `H3_TO_H4`、`STABLE_H3`、`H3_TO_MODEL_SENSITIVE`、`H3_TO_UNINFORMATIVE`；
- `AMBIGUITY_TO_H4`、`AMBIGUITY_TO_H3`、`AMBIGUITY_REMAINS_MODEL_SENSITIVE`、`AMBIGUITY_TO_UNINFORMATIVE`；
- `BORDERLINE_TO_H4`、`BORDERLINE_TO_H3`、`BORDERLINE_MODEL_SENSITIVE`、`BORDERLINE_UNINFORMATIVE`；
- `QC_FAILURE`。

## 7. 两个分母必须分开报告

1. 原始 184：报告 positive/ambiguous ABF cohort 的稳定率、H4 falsification burden、ambiguity resolution 与技术失败。
2. 完整 642：报告 H4→H3、H3→H4、stable H4、stable H3、ambiguity resolution、PF10/PF50 sensitivity、uninformative 与 QC failure。

不得将 455 个 H3 rescue comparisons 混入原始 184 的 primary endpoint 分母。

## 8. 冻结声明

本文件在 locus 7 与 locus 2 的代码/数值 smoke test 后、其余 639 个 comparison 的结果生成前冻结。两个 smoke loci 仅用于确认二进制 LD 读取、GJOKA 映射、SuSiE/coloc.susie 输出与旧正控方向一致；未据此修改 cohort、threshold 或分类规则。
