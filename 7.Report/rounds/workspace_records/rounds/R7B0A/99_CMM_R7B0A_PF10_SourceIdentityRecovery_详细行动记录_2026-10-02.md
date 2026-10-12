# R7B0A：PF10 Source Identity Recovery 与主分析解锁审计

**日期：2026-10-02**  
**上游阶段：R7B0 v7 = CONDITIONAL_COMPLETE**  
**本轮目标：解决 `G1 PF10 source identity = HOLD_PARTIAL`，但不通过选择有利模型来解锁 R7B1。**

## 1. 输入验收

- `CMM_R7B0_PBC_SourceModelBenchmark_2026-10-02_v7.zip`
  - SHA-256: `1a343e197dbb172eb7cb01901ff779249cf1b9f6313de8991f6305aced2c4ced`
  - ZIP CRC: PASS
  - internal checksums: 50/50 PASS
- `YR1(3).zip`
  - SHA-256: `97cf0e8df7e38277b40a85c4c4a36fab24edb700cfeb5c07f9a1ccbddd8b0bb5`
- 历史 `08_build_onek_residual_ld.py`
  - SHA-256: `ce0d8268e59d2cad13667253c03ddd347b1cc375e6de7a8e64644378d1939ef8`

公共项目仓库远端 HEAD 已独立核验为：
`ac9127f575b7790fca9ca11e82a5a8485797ed7a`

## 2. 本轮最关键的新发现

R7B0 v7 原本把问题表述为“当前 2026 PF50 archive 的前十 PF 不能完全复现历史 PF10 summary，因此需要找回历史 PF10 bytes”。

继续追到 R7A1B 的真实 LD 构建代码后，问题可以更精确地表述：

### 2.1 历史 QTL summary 的 PF10 来源

OneK/Xue 的 TensorQTL source script 显式读取：

```text
{cell}_covar_peer_factors_PF10.txt
```

即 source eQTL summary 的模型确实有一个独立落盘的历史 PF10 covariate file。

### 2.2 本项目 R7A1B 的 PF10 LD 来源

YR1 中真实 `08_build_onek_residual_ld.py` 并没有读取那个历史 PF10 文件，而是读取：

```text
updated_covariates_OneK1K_980_donors/{cell}_mx_pf50.txt
```

然后定义：

```text
PF10 = sex + PC1-6 + age + PF1-10
PF50 = sex + PC1-6 + age + PF1-50
```

因此，R7A1B 所谓 PF10 residualized LD 实际来自**2026 updated PF50 covariate archive 的前十因子**。

### 2.3 这解释了 3/7 与 4/7

R7B0 对当前公开 PF1-10 进行 nominal-QTL 公式复算后：

- 3/7 与 frozen source summary 达到严格复现；
- 4/7 未达到严格容差。

这意味着旧的：

```text
historical PF10 source summary
+
R7A1B “PF10” residualized LD
```

在至少 4 个冻结组合中**不能证明是同一个 covariate model 的 summary+LD 配对**。

因此，过去“PF10 primary 已证明完全 source/model-matched”的表述应正式撤回。

这并不证明历史结果错误；它证明的是**历史 summary–LD model identity 未被充分建立**。

## 3. 上游 PEER pipeline 对来源身份的进一步解释

`powellgenomicslab/PEER_factors` 的公开代码显示，OneK 的 PEER 工作流先生成一个 50-factor matrix，再通过 `make_new_PF_covar_option11.R` 逐个写出 PF0–PF50 covariate files。

PF10 的逻辑本质是：

```text
sex + 6 genotype PCs + age + PF1..PF10
```

其中 PF1..PF10 来自同一个历史 50-factor PEER fit。

Genome Biology 2023 报告 option #11 为最优 QC 方案：稀疏基因过滤 + log1p + standardization，并对 0–50 PF 做 eQTL sensitivity。

这给出两个不同问题：

1. **Historical reproduction**：能否找回产生 source raw eQTL summary 的确切历史 PF10 / PF50 factor values？
2. **Future primary inference**：能否用一个公开、冻结、内部一致的 current release 重新产生 QTL summary 与 LD？

这两个问题不应再绑成同一个无限期阻塞门。

## 4. Source-recovery 层级

### Tier A — BYTE_IDENTICAL

找到原始：

```text
{cell}_covar_peer_factors_PF10.txt
```

并记录 byte size、SHA-256、sample IDs、covariate rows。

这是最强历史复现。

### Tier B — FUNCTIONALLY_RECONSTRUCTED

找到产生 source summary 的**同一历史 50-factor matrix**（例如历史 option-11 `{cell}_mx_pf50.txt`）。

因为原作者公开脚本将 PF10 定义为同一 factor fit 的 PF1–PF10，所以可以确定性重构 PF10。若 7/7 nominal summary 严格复现，则历史 G1 可升级为 `FUNCTIONAL_IDENTITY_PASS`。

### Tier C — REGENERATED_FROM_HISTORICAL_INPUTS

仅找回历史 pseudobulk、known covariates、PEER option/seed，但没有 factor matrix；重新运行 PEER。

由于 R/PEER 版本与数值随机性可能影响 latent factors，这只能在最终 7/7 summary reproduction 通过时升级。

### Tier D — CURRENT_2026_RELEASE

使用 2026 Zenodo current covariates、pseudobulk、genotype：

```text
current PF1-10 -> de novo PF10 QTL summary + current PF10 LD
current PF1-50 -> de novo PF50 QTL summary + current PF50 LD
```

它**不能恢复 historical byte identity**，但可以建立一个比旧分析更干净、完全公开、内部 model-matched 的新 primary inference family。

## 5. 本轮推荐的协议修订

### 5.1 历史来源身份继续 HOLD，但降为 archive/provenance gate

```text
HISTORICAL_PF10_BYTE_IDENTITY = UNRESOLVED
HISTORICAL_SOURCE_REPRODUCTION = 3_OF_7_STRICT_PASS
```

不得把其改写成 PASS。

### 5.2 R7B 主分析改用 current-release de novo dual-model

新的 R7B primary 不再把 frozen source beta/SE 与 2026-derived LD 强行配对。

对每个 frozen comparison / 后续 eligible PBC-wide comparison：

```text
CURRENT_RELEASE_PF10:
current pseudobulk
+ current genotype
+ current sex/age/PC1-6/PF1-10
→ de novo QTL beta/SE/z
+ LD residualized with SAME donors/covariates

CURRENT_RELEASE_PF50:
current pseudobulk
+ current genotype
+ current sex/age/PC1-6/PF1-50
→ de novo QTL beta/SE/z
+ LD residualized with SAME donors/covariates
```

这两条才是以后 `model-matched PF10/PF50` 的严格定义。

### 5.3 为什么这不是针对结果改模型

这个修订由**source provenance conflict**触发，而不是由某个 H4 posterior 好不好看触发；并且修订发生在 56×14 full posterior 启动之前。

因此它符合 R7B0 “先冻结模型身份，再扩展结果”的原则。

## 6. R7B0A targeted 解锁门

在进入 56×14 前，只对历史冻结的 7 个组合运行 current-release PF10/PF50 双模型。

必须同时输出：

- current PF10 beta/SE/z；
- current PF50 beta/SE/z；
- current PF10 LD / PF50 LD identity hashes；
- active donor identity；
- z–LD `estimate_s_rss` / kriging diagnostics；
- SuSiE convergence；
- CS number/purity；
- all coloc.susie signal pairs；
- p12 = 1e-6/1e-5/1e-4。

### G1B PASS 的定义

G1B 是**模型身份/QC gate，不是 H4-positive gate**。

只要 7 个比较均满足：

- summary 与 LD 来自同一 current release；
- donors/covariates/variant order 可追溯；
- no unresolved allele mismatch；
- QTL and disease fits 可审计；
- z–LD diagnostic 无未解释严重异常；

则：

```text
G1B_CURRENT_RELEASE_MODEL_IDENTITY = PASS
```

即使某一 comparison 在 PF10 为 H3、PF50 为 H4，仍然可以 PASS G1B；那是**生物学/模型敏感性结果**，不是 QC failure。

## 7. 对 FCRL3–CD8_ET 的新解释原则

当前已知：

```text
historical PF10 -> H3 dominant
current matched PF50 -> H4 dominant
```

在 current matched PF10 尚未正式重跑 signal-level coloc 前，不能判定：

- “CD8_ET reversal 被推翻”，也不能判定
- “PF50 恢复了真实 H4”。

R7B0A targeted dual-model 将决定它属于：

- stable H3；
- PF-number-sensitive；
- current PF10/PF50 discordant；
- 或历史-source-drift。

无论结果如何都必须保留。

## 8. 对 56×14 benchmark 的影响

R7B1 的 disease universe、14 cells、gene-inclusion 和 trigger 规则继续保持冻结。

建议只调整 QTL effect-statistics 的身份：

```text
selection/testability:
source q<0.05 may remain an external pre-result ascertainment filter

primary effect statistics:
current-release de novo matched PF10

sensitivity:
current-release de novo matched PF50
```

这样可以避免因为历史 source identity 不完全可恢复而永久阻塞系统 benchmark，同时不根据 PBC posterior 重新选择 genes/cells。

## 9. 历史 PF10 是否还值得继续找？

值得，但不应再成为唯一关键路径。

原因：

- 找到 Tier A/B 可以解释为什么 3/7 exact、4/7 drift；
- 可以完成 source reproducibility paper trail；
- 可以判断 2026 updated release 与 historical latent factors 的具体漂移。

但即使最终无法取得历史文件，只要 current-release dual-model pipeline 完整闭环，R7B1 仍可在明确 versioned reanalysis 的前提下继续。

## 10. 当前状态修订

```text
R7B0 = CONDITIONAL_COMPLETE

HISTORICAL_PF10_SOURCE_IDENTITY = HOLD_UNRESOLVED
HISTORICAL_PF10_REPRODUCTION = PASS_3_OF_7

R7A1B_PF10_SUMMARY_LD_FULL_MODEL_MATCH =
NOT_ESTABLISHED_FOR_4_OF_7

CURRENT_2026_PF50_MODEL = AVAILABLE
CURRENT_2026_PF10_MODEL = DERIVABLE_AND_RERUNNABLE

R7B0A_CURRENT_RELEASE_DUALMODEL_TARGETED =
NEXT_CRITICAL_PATH

R7B1_FULL_56x14 = HOLD
```

## 11. 下一阶段冻结目标

```text
R7B0A_CURRENT_RELEASE_PF10_PF50_MATCHED_TARGETED_GATE
```

执行顺序：

1. 保留原 `01_r7b0_targeted_pf50_tensorqtl_compatible.py` 输出的 current PF10/PF50 files；
2. 用 current PF10 summary + current PF10 LD 重新运行 7 组合的 L5/L10/L20；
3. 用 current PF50 summary + current PF50 LD 运行 L10；
4. 完成 7 组合 z–LD / convergence / CS audit；
5. 冻结 current PF10 vs PF50 reclassification；
6. 若 G1B model-identity/QC PASS，进入 `R7B1_PBC_WIDE_ELIGIBILITY_AND_ABF_SCREEN`；
7. historical PF10 source recovery 转为并行 provenance lane，不再阻塞新 benchmark。

## 12. 结论

本轮没有恢复到 exact historical PF10 bytes，所以不能把 historical G1 改写为 PASS。

但是进一步审计证明，旧项目的“PF10 LD”本来就来自 2026 updated PF50 archive 的 PF1-10，而 source summary 来自另一个历史 PF10 file。继续把两者强行绑定为 primary source-matched pair，反而不够严谨。

因此最强的修正不是继续无限等待一个可能不再公开的历史文件，而是：

> **历史模型保持 unresolved 并完整披露；新 R7B benchmark 全部转为 current-release、de novo、summary–LD 同源的 PF10/PF50 双模型。**

这比恢复旧结果更符合 PBC-wide SCI 二区重设计的科学目标。
