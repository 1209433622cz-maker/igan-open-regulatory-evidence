# CMM R6A2C1D：Source-LD、SuSiE 与 signal-specific coloc

日期：2026-09-14

## Source-matched LD

PLINK BED 按 SNP-major 读取，剂量严格解释为 BIM A1 dosage：PLINK code 0→2、2→1、3→0、1→missing。CD4_NC donor list 与 FAM 精确连接为 980/980，REEP3 区域保留 3,084 个非恒定变异；最大 missing rate 为 0。

raw correlation 的对称性偏差和对角偏差均为 0。float32 dual-space 最小特征值 `-2.11×10^-5` 属存储精度级数值误差；用于 SuSiE 的 PF10/PF50 residualized matrix 在 double-space 的最小特征值分别为 `-4.37×10^-15` 与 `-4.75×10^-15`，小于 -1e-8 的负特征值均为 0。

PF10 design 为 19 列、rank 19、residual df 961；PF50 design 为 59 列、rank 59、residual df 921。两矩阵最大元素差 0.03589，中位绝对差 0.00411。

## SuSiE 稳定性

| config | converged | iterations | 95% CS | max PIP variant | max PIP | shared top PIP |
|---|---:|---:|---:|---|---:|---:|
| PF10/L5 | yes | 4 | 1 | 10:65379304 | 0.0772 | 0.0597 |
| PF10/L10 | yes | 5 | 1 | 10:65379304 | 0.0787 | 0.0612 |
| PF10/L20 | yes | 7 | 1 | 10:65379304 | 0.0817 | 0.0643 |
| PF50/L10 | yes | 5 | 1 | 10:65379304 | 0.0787 | 0.0613 |

四套 95% CS 都由相同 15 个变异构成；PF10/L10 对三个敏感配置的 Jaccard 全部为 1.0。可信集 purity：min |r|=0.83460，mean |r|=0.94236，median |r|=0.92956。

## Signal-specific coloc

疾病侧使用 case-control Wakefield approximate Bayes factor；QTL 侧使用 SuSiE PF10/L10 的 component-specific `lbf_variable`。`p1=p2=1e-4`，按预注册计算三个 p12。

| disease | p12 | PP.H3 | PP.H4 | H4/(H3+H4) |
|---|---:|---:|---:|---:|
| Asian | 1e-6 | 0.45140 | 0.47502 | 0.51275 |
| Asian | 1e-5 | 0.08557 | 0.90048 | 0.91322 |
| Asian | 1e-4 | 0.00940 | 0.98907 | 0.99059 |
| combined | 1e-5 | 0.70037 | 0.07171 | 0.09288 |
| European | 1e-5 | 0.14658 | 0.01486 | 0.09206 |

Asian 通过冻结门；combined/European 均不支持同一 shared signal。方向和后验差异适合称 ancestry-specific discovery candidate，不足以称确定的 ancestry-specific mechanism。

主要限制：Asian 疾病区域 Pmin 约 `4.55×10^-6`；疾病 lead 不在 OneK common-variant QTL/genotype 交集；OneK donors 与 Asian disease sample 不同祖源，QTL-side LD 反映 OneK source cohort，结论必须保留 discovery 限定。

