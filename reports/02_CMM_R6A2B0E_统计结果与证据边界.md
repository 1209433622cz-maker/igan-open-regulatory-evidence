# R6A2B0E 统计结果与证据边界

日期：2026-09-14

## 549-test smoke matrix

combined 的 183 个比较中：0 个 robust shared signal、3 个 targeted-LD trigger、128 个 sufficient-coverage distinct-signal、52 个 weak/uninformative。European-only 中 6 个 smoke ambiguity；Asian-only 中 1 个 robust、5 个 ambiguity、101 个 sufficient-coverage distinct-signal 和 76 个 weak/uninformative。

combined 的三个 trigger 为：

| 位点 | gene×cell | SNPs | QTL N | QTL min P | H3 | H4 | H4 ratio | H4 at p12=1e-6 | H4 at p12=1e-4 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OVOL1/RELA | SIPA1×CD8_ET | 1,909 | 980 | 7.49e-6 | 0.376 | 0.327 | 0.465 | 0.046 | 0.829 |
| TNFSF12/13 | EIF4A1×CD4_NC | 2,987 | 980 | 9.20e-6 | 0.392 | 0.391 | 0.499 | 0.060 | 0.865 |
| TNFSF12/13 | SAT2×B_IN | 2,908 | 975 | 1.55e-6 | 0.615 | 0.177 | 0.224 | 0.021 | 0.683 |

这些结果随 `p12` 大幅变化，不能称为阳性。source-LD 和 multi-signal 阶段正是用于判断这种混合是否由多个 QTL signal 引起。

## Targeted multi-signal 结果

每个 trigger 运行 PF10-L5、PF10-L10、PF10-L20 和 PF50-L10。12/12 全部收敛；所有配置的 95% credible set 数均为 0。

| 组合 | PF10-L10 max PIP | disease lead PIP | 95% CS | 结论 |
|---|---:|---:|---:|---|
| SIPA1×CD8_ET | 0.0338 | 0.00378 | 0 | 无稳定 QTL credible signal |
| EIF4A1×CD4_NC | 0.1162 | 0.000658 | 0 | 无稳定 QTL credible signal |
| SAT2×B_IN | 0.3249 | 0.000201 | 0 | 无稳定 QTL credible signal |

因此 signal-specific coloc 行数为 0。这里的“无 credible set”不是“基因绝对无调控效应”，而是当前公开 OneK1K 区域统计量与 source-matched LD 无法定义满足纯度门的可共定位 QTL component。它足以否定这三个组合被升级为疾病共享表达信号。

## REEP3 次级观察

`REEP3×CD4_NC` 的 QTL 很强（min P≈2.31e-10），Asian-only smoke H4≈0.906；combined 和 European-only 不支持。Asian 区域疾病 min P≈4.55e-6，尚未达到全基因组显著。

允许的表述：

> 在预冻结 supportive ancestry 分析中观察到一个需要 source-LD 和 signal-level 复核的 Asian-only REEP3 shared-signal candidate。

禁止的表述：

- “REEP3 是已确认 IgAN 效应基因”；
- “REEP3 在多祖源中稳定共定位”；
- “R6A2B0 新增一个主分析阳性位点”；
- “IgAN full-24 landscape 已经获得足够阳性证据”。

## 项目层解释

此前 ZMIZ1 benchmark 的 OneK1K/TenK10K 双资源阳性仍有效。本轮说明把相同框架扩展到另外 8 个高优先位点时，combined IgAN 没有产生预期的新增阳性收益。项目仍保留一个可靠的正控/机制位点，但不足以支撑“多位点免疫细胞 cis-expression landscape”主论文设计。

因此下一步应先裁决 Asian REEP3，并同步比较三种可完成路线：单一 ZMIZ1 机制深描、加入 ancestry-specific REEP3 的双位点论文、或切换公开 pQTL/kidney regulatory layer。full-24 在路线重评之前继续 HOLD。

