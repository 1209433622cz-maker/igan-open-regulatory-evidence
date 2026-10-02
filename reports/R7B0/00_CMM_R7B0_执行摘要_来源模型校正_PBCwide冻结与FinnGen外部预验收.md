# CMM R7B0 执行摘要：来源模型校正、PBC-wide 基准冻结与 FinnGen 外部预验收

日期：2026-10-02  
写作规范：QiTeng Academic Writing Skill v0.3.24.2，QITENG_Q1 证据分级模式

## 最终状态

```text
FINAL_DECISION = RETAIN_PBC__MAJOR_REDESIGN
R7B0 = CONDITIONAL_COMPLETE__G1_SOURCE_MODEL_HOLD
PF10_SOURCE_REPRODUCTION = 3/7 STRICT PASS; 4/7 FAIL_OR_TOLERANCE_EXCEED
CORRECTED_PF50 = EXECUTED_FOR_ALL_7_TARGETS
FINNGEN_IL12RB2_PBC_COLOC = PUBLIC_ENDPOINT_SUPPORT
FINNGEN_FCRL3_PBC_COLOC = NOT_FOUND_IN_TESTED_MARGINAL_ENDPOINT
PBCWIDE_56x14 = SCAFFOLD_FROZEN__FULL_QTL_ELIGIBILITY_PENDING
SIMULATION = PROTOCOL_FROZEN_BEFORE_RESULTS
R7B1 = HOLD
NEXT = R7B0_PF10_SOURCE_IDENTITY_RECOVERY
```

## 本轮回答的问题

研究计划书 v2 要求先回答一个方法学问题：历史 OneK1K PF10 summary、细胞 active-donor genotype、PF10 residualized LD 是否属于同一来源模型。为此，本轮固定 7 个既有触发组合，不扩展位点或细胞，并用公开 pseudobulk、980-donor PLINK、cell-specific donor list 和 PF50 covariate archive 重建 TensorQTL 1.0.10 nominal 公式。

PF10 公式复现不是全通过：IL12RB2–NK、FCRL3–CD8_ET、FCRL3–NK 三个组合逐变量通过；FCRL3–B_IN、B_MEM、NK_R 以及一个接近阈值的 CD4_NC 组合未达到预设严格容差。PLINK A1 剂量和 AF 与既有 source-LD 逐项对齐，最大标准化剂量差约 `9.6×10^-7`，因此当前最合理的解释是“公开 PF50 archive 的前十因子不能直接证明等同于历史 PF10 文件”，而不是等位基因或 genotype 解码错误。

纠正后的 PF50 nominal summary 已对 7 个目标全部计算，并与 PF50 residualized LD 配对完成 SuSiE-RSS/coloc.susie。主要模型类别变化是 FCRL3–CD8_ET 从历史 PF10 的 H3-dominant 转为 corrected PF50 的 H4-dominant；CD4_NC 的 corrected PF50 未给出可用 coloc summary。由于 PF10 source identity 仍未完全恢复，这些变化只能作为 model-sensitivity signal，不能升级为最终稳健性结论。

## 外部资源边界

FinnGen CASCADE 公开 API 对 `chr1_67307966_T_C` 和 `chr1_67308980_A_G` 返回 CHIRBIL_PRIM–IL12RB2 eQTL 共定位记录，l1.NK、l2.NK 和 PBMC 的 `PP.H4` 为约 `0.970`，credible-set overlap 为 5–9 个变异。FCRL3 边界变异的 90 条公开配对中没有 CHIRBIL_PRIM 记录。该结果支持 IL12RB2 作为外部 PBC–molecular-QTL 复制轴，但仍不等于 OneK1K 的同一细胞模型已被独立复制。

PBC-wide 分析宇宙已冻结为 `56 loci × 14 cell types = 784` 个 scaffold rows。基因纳入、变异身份、重叠数、LD、palindromic allele 和 reclassification 规则已在结果前写入 JSON；目前尚未把全量 56 loci 的 QTL eligibility 或扩展 posterior 冒充为完成。

## 门控判断

G0 输入和来源字节：通过。G1 PF10 source-model proof：暂缓，3/7 严格通过。G2 corrected PF50：计算完成，但只能作为条件敏感性。G3 PBC-wide universe：协议与 scaffold 冻结，full eligibility 待执行。G4/G5 benchmark 与 simulation：尚未产生结果。故 R7B1 不启动，下一阶段先恢复历史 PF10 covariate identity 或取得作者提供的原始 PF10 文件，再重跑受影响组合并决定是否进入全量 benchmark。

## 交付

- `01_CMM_R7B0_OneK来源模型与PF50修正审计.md`
- `02_CMM_R7B0_FinnGen公开外部证据预验收.md`
- `03_CMM_R7B0_PBCwide_56x14冻结协议.md`
- `04_CMM_R7B0_模拟基准协议冻结.md`
- `05_CMM_R7B0_下一阶段冻结目标.md`
- `99_CMM_R7B0_详细行动记录_2026-10-02.md`

主要机器结果位于 `3_results/00_audit/R7B0`、`3_results/03_qtl/R7B0` 和 `3_results/04_integration/R7B0`。大文件没有复制到公共仓库；本轮只保留哈希、receipt、scaffold 和可执行代码。
