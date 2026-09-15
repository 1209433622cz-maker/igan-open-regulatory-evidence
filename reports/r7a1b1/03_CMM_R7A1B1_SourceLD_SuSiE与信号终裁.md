# CMM R7A1B1：Source-LD、SuSiE 与信号终裁

**日期：2026-09-15**

## 1. GJOKA 疾病侧

只通过远程 ZIP range 读取下载冻结触发所需的 locus 2/4 summary 与 LD，共 4 个成员。

| locus | sumstats rows | sumstats SHA-256 | LD bytes | LD SHA-256 |
|---:|---:|---|---:|---|
| 2 | 2,324 | `a381929557351c2b05624d0e7085a536cb2112abd0bd6f518361e529891d8e12` | 57,496,850 | `fd1781aea429af71b036c6c419c9b458a1406da786e997a3f79882f0e508e041` |
| 4 | 2,587 | `f935a3f52f8049051c29a36086ca66f48f7352e43da52ec94bb3cee3e9edf369` | 72,084,475 | `147ef015a93c2f602b2c67e5ef26c55f4d8215a9cc1ae552c6a56de9a1c6add4` |

疾病 z 直接使用源 `STAT`，并保持与 GJOKA LD 相同的 A1 方向；QTL z 使用 OneK BIM-A1 方向和 OneK donor-matched LD。两侧可有不同 LD，但每个研究内部的 z/LD 方向必须一致。

## 2. OneK source-LD

| 基因 / 细胞 | donor N | LD variants | raw LD gate | PF10/PF50 gate |
|---|---:|---:|---|---|
| IL12RB2 / NK | 980 | 2,386 | PASS | PASS |
| FCRL3 / B_IN | 975 | 2,684 | PASS | PASS |
| FCRL3 / B_MEM | 970 | 2,687 | PASS | PASS |
| FCRL3 / CD4_NC | 980 | 2,684 | PASS | PASS |
| FCRL3 / CD8_ET | 980 | 2,684 | PASS | PASS |
| FCRL3 / NK | 980 | 2,684 | PASS | PASS |
| FCRL3 / NK_R | 750 | 2,667 | PASS | PASS |

原始矩阵的最小特征值约 `-3.6×10^-5` 到 `-4.6×10^-5`，符合 float32 相关矩阵的数值误差范围。残差 LD 明确加入性别、年龄、6 个 genotype PCs 和 PF10/PF50 expression factors；设计矩阵满秩，无小于 `-1×10^-8` 的 dual negative eigenvalue。

## 3. 多信号拟合

四个冻结配置：

```text
PF10_L5
PF10_L10
PF10_L20
PF50_L10
```

共 28 个疾病/QTL 拟合、120 个 signal-pair × prior 结果；28/28 两侧均收敛，全部至少一个 purity-filtered 95% 可信集。共有 837 行逐变异可信集成员已导出。

稳定性汇总：

| 基因 / 细胞 | min default PP.H4 | min default H4 ratio | min low-prior H4 ratio | 判定 |
|---|---:|---:|---:|---|
| IL12RB2 / NK | 0.9980 | 0.9980 | 0.9806 | 稳定 PASS |
| FCRL3 / B_IN | 0.9938 | 0.9938 | 0.9411 | 稳定 PASS |
| FCRL3 / B_MEM | 0.9912 | 0.9912 | 0.9187 | 稳定 PASS |
| FCRL3 / CD4_NC | 0.9914 | 0.9919 | 0.9244 | 稳定 PASS |
| FCRL3 / NK | 0.9396 | 0.9396 | 0.6086 | 稳定 PASS |
| FCRL3 / NK_R | 0.9712 | 0.9712 | 0.7715 | 稳定 PASS |
| FCRL3 / CD8_ET | 0.0036 | 0.0037 | 0.0004 | FAIL，多信号拆解后为不同信号 |

IL12RB2 的通过信号疾病 hit 是 `1:67820194`，QTL hit 是 `1:67825399`；FCRL3 通过细胞的疾病 hit 均为 `1:157669278`，QTL hit 随细胞为 `1:157668993`、`1:157668701` 或 `1:157625122`。hit 不相同不等于信号不同；最终判定由完整 credible-signal Bayes factor 和 source LD 决定。

## 4. 基因级判定

同一细胞必须在四配置中均存在满足以下条件的同一 signal-pair：默认 `PP.H4≥0.8`、默认 `H4/(H3+H4)≥0.8`、`p12=1e-6` 时 H4 比率≥0.5、两侧收敛且各至少一个 purity-filtered 可信集。

```text
FCRL3   = PASS_SIGNAL_SPECIFIC_SHARED_GENE
IL12RB2 = PASS_SIGNAL_SPECIFIC_SHARED_GENE
INAVA   = UNINFORMATIVE_WEAK_ONEK_QTL
```

因此 `ROBUST_SHARED_SIGNAL_GENES=2/3`，R7A1C 触发。
