# R7B1A 执行摘要：PBC-wide ABF 与触发集冻结

**日期：** 2026-10-03

**研究计划：** R7B0 v2 之 WP1/WP2 前半段

**写作治理：** QiTeng v0.3.24.2

## 最终判定

```text
R7B0A_CURRENT_RELEASE_MODEL_IDENTITY = PASS
HISTORICAL_PF10_SOURCE_IDENTITY = HOLD_UNRESOLVED

R7B1A_ELIGIBILITY_AND_ABF = COMPLETE
R7B1A_INDEPENDENT_QA = PASS_12_OF_12

FROZEN_COMPARISONS = 6,923
ABF_ELIGIBLE = 5,460
INSUFFICIENT_VARIANT_OVERLAP = 1,463

ROBUST_H4_TRIGGER = 112
H3_H4_AMBIGUITY_TRIGGER = 72
H3_DISTINCT_SIGNAL = 455
NO_TRIGGER_OR_UNINFORMATIVE = 4,821

R7B1B_EXACT_TRIGGER_SET = 184
R7B1B_LOCUS_COUNT = 25
R7B1B_CELL_LOCUS_LD_BLOCKS = 120

NEXT = R7B1B_SOURCE_MATCHED_MULTISIGNAL_RECLASSIFICATION
MANUSCRIPT_REWRITE = HOLD
```

## 本轮完成的实质工作

1. 独立验收 R7B0A 输入包并追溯历史 PF10；扫描未找到可证明历史 PF10 身份的原始 `*_PF10.txt`，因此历史来源身份继续 `HOLD_UNRESOLVED`。
2. 使用当前公开 OneK1K pseudobulk、980-donor PLINK genotype、cell-active donor 与明确的 PF10/PF50 covariate columns，完成 7 个历史 comparison 的当前版本双模型复核。14/14 model-identity rows、28/28 fits 均通过硬 QC；G1B 当前版本身份门通过。
3. 在读取任何 PBC-wide posterior 前，冻结 56 个 GJOKA non-HLA regions、14 个 OneK cells、source-q 基因规则、TSS±1 Mb、≥200 variant overlap 和 ABF trigger。
4. 建立 589 个 locus–gene、6,923 个 locus–gene–cell 比较；locus 19 没有满足冻结 source-eGene 规则的基因，因此保留在疾病 universe，但没有可测试 QTL comparison。
5. 将 GCST90061440 PBC GWAS 定向到 OneK BIM A1；56/56 loci 的疾病侧区域均有至少 200 个可用变异。
6. 从公开 pseudobulk 与 PLINK BED 重新计算当前版本 PF10 nominal eQTL，并完成全部 6,923 个 ABF 结果。运行时间约 75.5 秒。
7. 独立 QA 复算键集合、trigger logic、posterior 和、QTL 文件集合、历史正控与哈希，12/12 PASS。

## 科学解释

184 个触发是下一阶段的**技术工作集**，不是 184 个共定位阳性。72 个为预定义 H3/H4 ambiguity；112 个为默认先验下 robust H4，但其中 11 个在 `p12=10^-6` 时 `H4/(H3+H4)<0.5`。全部 ambiguity 在审慎先验下均未保持 H4 优势。这一结构直接说明单因果 posterior 对先验和局部信号架构敏感，必须进入 source-matched multi-signal adjudication。

历史锚点通过一致性检查：IL12RB2–NK、FCRL3–B_IN/B_MEM/CD8_ET 的 H4 与旧冻结值一致。历史弱 QTL 对照 INAVA 不满足新 universe 的 gene-level source q 门，因而被规则性排除；它继续保留为历史 control，不得被写成 R7B1 的新阴性。

## 下一阶段

R7B1B 必须完整处理 exact 184 triggers，不得二次挑选。所需输入为 25 个 GJOKA loci 的 50 个远端成员，压缩传输约 357.7 MB、解压约 1.08 GB；QTL 侧需要 120 个唯一 cell–locus blocks 的 PF10 与 corrected PF50 model-matched LD。终点是 184/184 的 `STABLE_H4 / WEAKENED_H4 / REVERSED_TO_H3 / UNINFORMATIVE / QC_FAIL` 完整重分类。
