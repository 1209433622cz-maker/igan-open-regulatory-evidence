# CMM R4A12FG4：R4A12FG5 下一阶段冻结目标

## 阶段名称

> **R4A12FG5 — External-LD Gate + Three-cell Replication Adjudication**

## 固定范围

Track A 只对当前 891 个 exact overlap 建立 1000G EUR503 signed LD：按 rsID/build/allele逐项映射，检查 AF 相关、缺失率、矩阵顺序、对称性、PSD、条件数、z–LD 不一致和敏感性。任一关键门失败即停止 external-LD multi-signal 分析，转为等待 TenK10K/EGA source-matched LD。

Track B 只增加预排序前三个 secondary cells：`CD8_TEM`、`CD4_CTL`、`CD4_TCM`。仍使用 100-kb 包、同一 IL12RB2、同一 exact harmonization 和同一 p12 网格；不得根据结果临时换细胞或扩大至 1 Mb。

## 决策规则

- `SECONDARY_SIGNAL_SUPPORTED`：external LD 全部门通过，multi-signal shared 结果稳定，且三个 secondary cells 中至少两个方向/信号结构一致。它仍只是 all-sex secondary finding，不能满足主 C1。
- `SUMMARY_ONLY`：外部 LD 不充分或 multi-signal 不能稳定收敛；保存当前锚点和 ABF 诊断，等待 source-matched LD。
- `STOP_IL12RB2_ALLSEX_BRANCH`：只有输入、LD、覆盖都充分，并且 NK 加三个预注册细胞在合理模型下稳定支持 distinct/unshared，才停止该 secondary branch。
- chr22/SYNGR1 female/male 主路线完全独立；真实 2026 sex-stratified bytes 到达时优先级高于 FG5。

## 不进入的工作

当前不启动 caQTL/peak→gene 扩张，不下载 1-Mb TenK10K 七包，不把 R12/R13 当独立复制，不用更多细胞挽救不理想结果。
