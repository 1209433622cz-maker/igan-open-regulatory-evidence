# CMM R4A12FG6 执行摘要：输入补全与多信号门判定

日期：2026-09-13

## 最终判定

- 总项目：`CONDITIONAL_GO`
- 正式 R4B：`HOLD`
- `C1_count = null`
- 2026 female/male SSc 主数据：`NOT_OBTAINED`
- IL12RB2 all-sex 分支：`SUMMARY_ONLY_SOURCE_MATCHED_LD_REQUIRED`
- Full EUR503 external-LD：`FAIL_INPUT_COVERAGE_FOR_MULTISIGNAL`
- 三细胞完整成员接入：`PASS_THREE_MEMBER_INTAKE`
- 三细胞单因果诊断：6/6 release×cell 组合均为 `AMBIGUOUS_PRIOR_SENSITIVE`
- 正式多信号共定位：`NOT_RUN_PRE_FROZEN_EXTERNAL_LD_GATE_FAILED`
- `SECONDARY_SIGNAL_SUPPORTED = false`
- `STOP_IL12RB2_ALLSEX_BRANCH = false`

## 关键进展

FG5 所缺的两类输入都已实际补齐。工作区原有 27,067 变异、503 人的完整 EUR503 区域 PLINK 面板已被重新识别并直接解码；三个预注册 TenK10K 成员 CD8_TEM、CD4_CTL、CD4_TCM 共选择性取得 1,664,453,342 个压缩字节，并逐一通过整成员 CRC、解压字节数、行结构和精确基因过滤，各得到 1,366 条 IL12RB2 记录。

完整 EUR503 面板将 current 891 exact set 的 LD 覆盖提高到 764/891（85.75%），超过预冻结的 80% 总覆盖线。ALT 剂量方向、LD 对称性、对角线、PSD 和 AF 一致性均通过；直接 BED 解码还对历史 503×1,555 剂量矩阵逐值复现，最大绝对差为 0。

但决定多信号门的是信号覆盖，而不是总体覆盖：

| 条件 | 结果 | 判定 |
|---|---:|---|
| current exact set LD 覆盖 | 764/891 = 85.75% | PASS |
| NK CS1 PIP mass | 61.74% | FAIL，要求≥95% |
| NK CS2 PIP mass | 72.73% | FAIL，要求≥95% |
| rs17129789 / rs6662198 / rs1954118 | 缺 / 有 / 有 | FAIL，要求全部存在 |
| LD 数值结构 | 对称、diag≈1、min eigen=-5.69e-14 | PASS |

所以没有运行 SuSiE-RSS/coloc.susie。删除高 residual 变异、换一个 external panel 或以 proxy 补齐均会违反 FG5 预冻结规则。

## 三细胞结论

三细胞各有 891/1,366（65.23%）与 FinnGen R12/R13 精确 REF/ALT 重叠，QTL top 和疾病区域 lead 均覆盖，五个反向等位基因对均被排除。三个 QTL top 的疾病效应方向均与 eQTL 方向一致：

| Cell | QTL top | QTL P | R13 disease P | 方向 |
|---|---|---:|---:|---|
| CD8_TEM | 1:67326053:A:C | 1.46e-19 | 9.25e-4 | beta 均为负 |
| CD4_CTL | 1:67327248:G:A | 3.06e-17 | 1.39e-3 | beta 均为负 |
| CD4_TCM | 1:67332644:T:G | 1.80e-16 | 1.38e-3 | beta 均为负 |

然而 coloc.abf 的 H4 对 p12 极敏感。R13 中 p12 从 1e-6、1e-5 到 1e-4 时：CD8_TEM 为 0.160/0.656/0.950，CD4_CTL 为 0.225/0.744/0.967，CD4_TCM 为 0.193/0.705/0.960。因此这些结果只能支持“跨细胞、方向一致且值得做 source-LD 判定”，不能升级为 shared causal signal。

四个细胞的 eQTL z 结构高度相关，NK 与三细胞的相关系数为 0.806–0.901。当前更准确的表述是“跨淋巴细胞的共享调控结构”，不应写成 NK 特异；三细胞来自同一 TenK10K 资源，也不构成独立人群复制。

## 下一阶段

下一阶段冻结为：

> **R4A12FG7 — Source-matched LD Access Package + Primary-data Trigger**

不再轮换 external reference。准备 TenK10K EGA `EGAS50000001654 / EGAD50000002377` 的受控访问材料，并优先请求仅覆盖 IL12RB2 100-kb、1,366 个变异的 source correlation/LD 矩阵。2026 female/male SSc summary statistics 字节一旦到位，立即中断该支线并返回 chr22/SYNGR1 主线。
