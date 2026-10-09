# R7B1C simulation implementation freeze v1

冻结日期：2026-10-09
上游协议：`R7B0_simulation_grid.tsv`、`R7B0_simulation_freeze.json`、研究计划书 v2
状态：`IMPLEMENTATION_FROZEN_BEFORE_PILOT_RESULTS`

## 1. 不变的上游设计

- 六个场景 S1–S6、486 行参数网格、每行 1,000 replicates、总计 486,000 replicates 均不改变。
- `seed`、`maf`、`causal_r2`、`susie_L`、`p12`、disease N=24,510、QTL N=750 均直接继承 R7B0。
- primary methods 为冻结的 single-causal Wakefield ABF 与 source-matched `susie_rss`/`coloc.susie`；S6 额外运行 deliberately mismatched LD。
- pilot replicate 不进入正式估计，也不允许据 pilot 修改参数网格或判定阈值。

## 2. 经验 LD 模板

固定两个来源可追溯模板：

1. GJOKA locus 2 disease LD + OneK NK PF10 active-donor/model-matched LD；
2. GJOKA locus 4 disease LD + OneK B_IN PF10 active-donor/model-matched LD。

每个模板先按 rsID、GRCh37 position 与冻结 block variant order 对齐，再从完整共同集合中选择一个连续 128-variant 子块。窗口选择规则为：遍历全部连续 128-variant 窗口，在每个窗口内寻找与 `r²=0.2/0.5/0.8` 最接近的变异对；最小化三个目标的最大绝对偏差，完全平局时取起始索引较小者。该规则只读取 LD，不读取模拟 posterior。

经验矩阵若存在数值性非正定，统一做 symmetric eigenvalue clipping（下限 `1e-6`）并重新标准化为相关矩阵；保存原始最小特征值、修正量和最终 hash。每一 grid row 的奇数 replicate 使用 locus 2 模板，偶数 replicate 使用 locus 4 模板，因此每格两个模板各 500 次。

## 3. 摘要统计生成模型

对每个 trait 使用标准 summary-statistic 模型：

```text
z ~ Normal(sqrt(N) * R_true * b_std, R_true)
b_std = beta_per_allele * sqrt(2 * MAF * (1-MAF))
```

固定效应：

- disease 第一信号 `beta = log(1.12)`，第二信号为第一信号的 `-0.8` 倍；
- QTL 第一信号 `beta = 0.30 SD/allele`，第二信号为第一信号的 `-0.8` 倍；
- `MAF` 使用 grid 值 0.05/0.20/0.40；不冒充模板变异的真实等位基因频率。

因果索引仅由模板 LD 和 `causal_r2` 决定；选择时要求索引间至少相隔 5 个有序变异。场景真值：

| 场景 | disease | QTL | true shared |
|---|---|---|---|
| S1 | a | a | a |
| S2 | a | b | none |
| S3 | a,b | a | a |
| S4 | a,b | a,c | a |
| S5 | a,b | c,d | none |
| S6 | a,b | a,c | a |

## 4. 方法配置

- ABF：disease prior SD=0.20；QTL prior SD=0.15；`p1=p2=1e-4`；`p12` 取 grid 值。
- SuSiE-RSS：`L` 取 grid 值 5/10/20；`estimate_residual_variance=FALSE`；`estimate_prior_variance=TRUE`；`max_iter=2000`；`tol=1e-4`。
- multi-signal shared decision：任一 eligible signal pair 同时满足 `PP.H4>=0.80` 与 `H4/(H3+H4)>=0.80`。
- multi-signal distinct decision：无 shared decision，且任一 pair 满足 `PP.H3>=0.80` 与 `H4/(H3+H4)<=0.20`。
- 无 credible set、无 eligible pair或后验不足者为 `UNINFORMATIVE`；不得记为生物学阴性。

S6 的 true z 仍由来源匹配模板生成。matched analysis 使用同一模板；mismatched analysis 将 locus 2 的 z 按冻结索引交给 locus 4 LD，反之亦然。ABF 不使用 LD，因此只计算一次。

## 5. 输出与评价指标

- false shared-signal classification：S2/S5 中 H4 decision rate；
- true shared-signal recovery：S1/S3/S4/S6 中 H4 decision rate；
- ABF→multi-signal H4/H3/uninformative reclassification；
- disease/QTL 95% credible-set any/all-causal coverage、credible-set size；
- SuSiE convergence、eligible pair rate、QC failure；
- S6 matched 与 mismatched 的 H4 decision、best-H4、coverage 和 convergence 差；
- posterior Brier score 与 fixed-bin calibration；
- 按 scenario、MAF、r²、L、p12、template 完整报告，不选择性删除不利格点。

## 6. pilot 与正式启动门

pilot 固定取每个场景中 `MAF=0.20, r²=0.50, L=10, p12=1e-5` 的一行，每行 50 replicates，并完整重放两次。

正式 grid 只能在以下条件全部满足后启动：

1. 两次 pilot 的 replicate-level TSV 去除运行时字段后字节级一致；
2. 300/300 replicate 均有合法 ABF 输出；
3. SuSiE 双性状执行成功率至少 95%；
4. S1 matched multi-signal H4 rate 高于 S2；
5. 输入模板、causal map、implementation grid 和软件版本均写入 hash manifest。

若 pilot 失败，只允许修复确定性、I/O、数值稳定性或实现错误；任何统计规则修改都必须形成新版本并明确说明发生在正式 grid 之前。

## 7. 证据边界

本模拟校准的是两个经验 LD 模板、固定效应量与冻结参数网格下的推断行为。它不代表所有 ancestry、样本量、效应分布或基因组区域，也不能把较低 false-H4 直接解释成真实生物机制验证。
