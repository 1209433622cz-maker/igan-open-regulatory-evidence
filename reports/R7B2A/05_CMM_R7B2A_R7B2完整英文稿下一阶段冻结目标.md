# R7B2A：R7B2 完整英文稿下一阶段冻结目标

## 下一阶段

```text
NEXT = R7B2_FULL_ENGLISH_MANUSCRIPT_V1
WRITING_ENGINE = QITENG_v0.3.24.2_ONLY
ARTICLE_TYPE = ORIGINAL_RESEARCH
POSITION = DISEASE_FOCUSED_EMPIRICAL_METHODS_EVALUATION
BIOLOGICAL_SCOPE = FROZEN
NEW_LOCUS_GENE_CELL_FISHING = NO
NEW_SIMULATION_SCENARIO = NO_BY_DEFAULT
```

## 必须完成

1. 以 unresolved attribution problem → A0/A1/A2/M matched-input design → PBC real-data reclassification → truth-known calibration → bounded external/tissue evidence → inference limits 构建英文 argument map。
2. 更新 Methods，使 `S_A`、`S_M`、GCST、GJOKA matched-z、fixed/native sdY、rounded sensitivity 和 M 的接口可复算。
3. Results 使用同输入主数值 15、19、8、10、79、413，并保留历史 12 的审计说明。
4. 模拟同时报告无条件与 pair-conditional 结果，明确 0 technical error、325,218 no-CS 和 160,782 pair-evaluable。
5. Figure 2/3 使用 R7B2A source data；Figure 4–6 继承冻结外部/组织边界。
6. 完成 numeric-token QA、claim-source QA、Methods–Results mirror、图注一致性和 hostile review。

## 不触发新计算的事项

次级 mismatch zero-pair 的逐侧 CS 计数缺失不构成重跑理由；作者信息和投稿接口字段等待真实信息；目标期刊格式在科学正文 v1 通过后确定。

## 出口

- 完整英文稿在 27 条 claim ledger 内闭环：进入 hostile manuscript audit 与期刊格式化。
- 出现可复现数字矛盾：仅回到对应 R7B2A source/ledger 修复。
- 不因行文困难重新打开疾病、位点、基因或细胞筛选。
