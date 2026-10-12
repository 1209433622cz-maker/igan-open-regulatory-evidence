# R5A2B 96 项 coloc 结果与官方 R 复核

## 分析矩阵

- 表型：EOMG、MG overall、LOMG；
- QTL：32 个独立重算的 source-significant cell–gene；
- 测试：96/96 完成；
- 默认先验：`p1=p2=1e-4, p12=1e-5`；
- 敏感性：`p12=1e-6` 与 `1e-4`。

结果：29 项 `FAIL_SUFFICIENT_COVERAGE_SINGLE_CAUSAL`，67 项 `UNINFORMATIVE_OR_LOW_QTL_SIGNAL`；0 robust H4，0 `HOLD_LD_REQUIRED`。

EOMG 32 项中 29 项在强疾病信号与充分 QTL 覆盖下明确偏向 distinct signals。最高的三项为：

| cell/gene | H3 | H4 | H4/(H3+H4) | H4 @1e-4 |
|---|---:|---:|---:|---:|
| NK/TNIP1 | 0.9094 | 0.0662 | 0.0679 | 0.4149 |
| CD4_NC/TNIP1 | 0.4633 | 0.0552 | 0.1065 | 0.3687 |
| CD4_NC/CCDC69 | 0.8646 | 0.0492 | 0.0539 | 0.3411 |

三者都没有在默认门下形成 ambiguity；较高 p12 只抬高 H4 的绝对 posterior，低/默认先验仍强烈由 H3 主导。最强 competitor QTL 的结果更明确，例如 CD4_NC/ANXA6 `H3=0.99974、H4=1.88×10^-5`。

LOMG 全部为疾病侧区域信号不足，最高默认 H4 的 NK/ATOX1 也只有 0.152，且 LOMG 区域最小 P 为 `1.48×10^-4`，不能被用作阳性共定位。

## 官方 R 复核

R 4.6.1 / coloc 5.2.3 对 96 个比较、3 个 p12 共 288 次运行全部完成：

- 最大 H4 差：`3.03×10^-15`；
- 最大 H4/(H3+H4) 差：`3.66×10^-15`；
- H0–H4 最大差：`1.14×10^-14`；
- top SNP：96/96 一致；
- robust H4：0。

因此 Python ABF 实现和最终门控已被官方实现复核。
