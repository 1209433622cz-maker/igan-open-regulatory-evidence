# CMM R4A12FG6：跨细胞信号结构与 coloc 敏感性裁决

## 1. QTL top 与疾病方向

| Cell | QTL top | QTL beta | R13 disease beta | R13 disease P |
|---|---|---:|---:|---:|
| CD8_TEM | 1:67326053:A:C | -0.2478 | -0.2363 | 9.25e-4 |
| CD4_CTL | 1:67327248:G:A | -0.4026 | -0.2291 | 1.39e-3 |
| CD4_TCM | 1:67332644:T:G | -0.1795 | -0.2283 | 1.38e-3 |

三个细胞在 R12/R13 都保持同向。R12/R13 疾病 regional lead `1:67448804:T:A / rs1954118` 也都被 QTL 覆盖，但其 QTL P 从 2.54e-4 到 1.11e-2，显示区域可能含多个结构，不能压缩成单一 lead 叙述。

## 2. 预注册 p12 网格

| Cell | Release | H4 @1e-6 | H4 @1e-5 | H4 @1e-4 |
|---|---|---:|---:|---:|
| CD8_TEM | R12 | 0.119 | 0.575 | 0.931 |
| CD8_TEM | R13 | 0.160 | 0.656 | 0.950 |
| CD4_CTL | R12 | 0.226 | 0.745 | 0.967 |
| CD4_CTL | R13 | 0.225 | 0.744 | 0.967 |
| CD4_TCM | R12 | 0.180 | 0.687 | 0.956 |
| CD4_TCM | R13 | 0.193 | 0.705 | 0.960 |

六个组合均随 p12 大幅漂移。在保守 1e-6 下 H4 只有 0.119–0.226，在宽松 1e-4 下达到 0.931–0.967。该模式与 NK 既有结果一致，统一分类为 `AMBIGUOUS_SINGLE_CAUSAL_PRIOR_SENSITIVE`。

## 3. 跨细胞结构

在共同 891 个变异上：

- NK–CD8_TEM：beta r=0.771，z r=0.806
- NK–CD4_CTL：beta r=0.846，z r=0.901
- NK–CD4_TCM：beta r=0.821，z r=0.867
- 三个 secondary cells 之间 z r=0.838–0.917

这给出跨淋巴细胞调控广度，并提示“NK-only”并不准确。由于四个细胞来自同一 TenK10K 资源，细胞间结果不能表述为独立队列复制。

## 4. 裁决

- 方向与跨 release 一致：支持继续 source-LD 判定；
- source CS 与 external LD 不充分：不能正式区分 shared/distinct；
- ABF 先验敏感：不能把高 p12 下的 H4 单独作为结论；
- 多信号门失败：不运行 SuSiE-RSS，不把未运行写成阴性。

最终：`SUMMARY_ONLY_SOURCE_MATCHED_LD_REQUIRED`。
