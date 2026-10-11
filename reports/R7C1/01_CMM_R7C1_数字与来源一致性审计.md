# R7C1 数字与来源一致性审计

## 审计方法

每一个 R7C1 新增数字均与 R7C0 冻结 TSV/JSON 机器表进行双向核对。审计不从报告文字反推数字，也不将 Figure 4 的标签作为独立数据源。

## 通过项目

1. FinnGen R12/R13 疾病 CS 身份、大小、交集、Jaccard、lead variant 和 PIP 相关值与 `R7C0_FinnGen_R12_R13_IL12RB2_signal_identity.json` 一致。
2. 三档 p12 下的 PP.H4 与 H4/(H3+H4) 与 `R7C0_FinnGenR13_x_OneK_NK_IL12RB2_coloc.tsv` 一致。
3. OneK QTL CS 的 2/2 disease-CS coverage 与 source-CS 成员表一致。
4. 固定 27 基因、22 个相关细胞 eQTL coverage 和唯一 IL12RB2 disease-coloc 结果与 CASCADE 固定表一致。
5. disease–eQTL、disease–caQTL、credible-set sizes、peak–gene beta 与 TSS 距离均与 chromatin adjudication JSON 一致。
6. OMIX 的两个公开矩阵、样本身份和描述性限制与 byte-level QC 表一致。
7. 引用 1–25 连续，正文引用范围 1–25，25/25 均被引用。

## 机器结果

`R7C1_machine_hostile_QA.json`：38/38 PASS，0 FAIL。

R7B4B2 基线 MD、DOCX、WPS PDF 的 SHA-256 分别继续匹配冻结值；R7C1 没有覆盖这些文件。
