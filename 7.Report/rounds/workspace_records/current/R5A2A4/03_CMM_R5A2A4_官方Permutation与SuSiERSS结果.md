# R5A2A4 官方 permutation 与 SuSiE-RSS 结果

## 官方 OneK1K top-eQTL

本轮新增接入官方 `OneK1K_TensorQTL_top_eQTL_summary.zip`：16,950,155 bytes，官方/实测 MD5 均为 `46e986dc53c9f4f1b6daa2b7a73d277c`，SHA-256 为 `a3100acf36aedfbb78ab7ddc1113b9dcb119170c9c4b863d37b99a0edee05d5d`，ZIP CRC PASS。

NK_R chr18 文件共有 127 个 phenotype，没有一个 `q<0.05`；最小 q-value 为 0.366。ZCCHC2 的 source top 为 `18:60243208`：

```text
nominal P = 4.9591491e-05
permutation P = 0.0572943
beta-approx P = 0.0583396
q-value = 0.3831456
slope = 0.3290516
SE = 0.0806116
```

因此 ZCCHC2 不满足 source-significant eQTL 条件。固定窗口局部 Bonferroni 阈值为 `0.05/3827=1.3065×10^-5`，也没有任何 marginal variant 通过。

## SuSiE-RSS

使用 R 4.6.1、susieR 0.14.2，以 PF10 residualized source LD 为主分析，N=750，L=10。另固定 PF10 L=5、L=20、估计 residual variance、raw LD L=10 和 PF50 LD L=10 五组敏感性。

| 配置 | 收敛 | 95% CS | 最大 PIP | rs7239261 PIP |
|---|---|---:|---:|---:|
| PF10 L10 主分析 | PASS | 0 | 0.02960 | 0.00665 |
| PF10 L5 | PASS | 0 | 0.03508 | 0.00497 |
| PF10 L20 | PASS | 0 | 0.02551 | 0.00932 |
| PF10 L10 estimate residual | PASS | 0 | 0.03193 | 0.00685 |
| raw L10 | PASS | 0 | 0.02981 | 0.00670 |
| PF50 L10 | PASS | 0 | 0.03079 | 0.00685 |

模型中的多个非零 prior-variance component 不是多个可信信号；所有 posterior 均分散，六组配置都没有形成 95% credible set。

## 强制条件化

基于 summary z-score 和三种 source LD，强制在 `18:60243208` 上条件化：

| LD | rs7239261 marginal P | conditional P | 最佳残余 P | 通过局部阈值 |
|---|---:|---:|---:|---:|
| raw | 0.00492 | 0.01722 | 0.00117 | 0 |
| PF10 | 0.00492 | 0.01769 | 0.00128 | 0 |
| PF50 | 0.00492 | 0.01512 | 0.00128 | 0 |

这里的 z/P 由发布表中的 rounded beta/SE 正态近似得到，故与 TensorQTL 原 nominal P 有轻微差异；判定使用 source permutation/q-value、SuSiE 和局部阈值的合并证据，不把近似 P 当成新的 source association test。
