# R7B1C simulation implementation freeze v1.1

冻结日期：2026-10-09
状态：`PRE_FULL_GRID_ENGINEERING_CORRECTION`
取代：v1 中 S6 的 cross-locus mismatch 定义；其余规则全部不变。

## 修订原因

v1 pilot 未读取或汇总 posterior，仅依据进程状态和运行时触发工程停止。S1–S5 的两次 pilot 各完成 250/250 replicates、fit failure=0；S6 将 locus 2 z 交给 locus 4 LD（反向亦然）后，两个工作进程持续接近 `max_iter=2000`，约 11 分钟仍未完成 50 replicates。该设计同时改变基因组区域、LD 结构和索引语义，压力过强，无法把结果解释为现实的 source/model mismatch。

## 唯一修订

S6 的真值和 matched analysis 仍使用同一位点的 GJOKA disease LD 与 OneK PF10 QTL LD。mismatched analysis 现在：

- disease z 继续配对同一 GJOKA disease LD；
- QTL z 由 PF10 true LD 生成，但分析时替换为同一 cell、同一位点、同一变异顺序的 PF50 residualized LD；
- 不改变变异、因果索引、效应量、seed、L、p12 或判断门。

因此 S6 只检验 QTL covariate-model LD mismatch。它是现实且有界的 sensitivity；若 PF10/PF50 差异很小，允许结果显示 posterior distortion 很小，不得为了制造效应扩大错配。

## 保持不变

- 六场景、486 行、486,000 replicates；
- 两个 128-variant empirical templates；
- 效应生成模型和固定效应量；
- causal index map；
- ABF/SuSiE/coloc 配置与分类阈值；
- pilot 两次重放及五项正式启动门；
- 完整报告所有场景和不利结果。

## v1 失败资产

v1 incomplete pilot 输出必须移动到 `pilot_v1_cross_locus_aborted_*`，并保留日志；不得混入 v1.1 pilot 或正式 486,000 replicate 汇总。
