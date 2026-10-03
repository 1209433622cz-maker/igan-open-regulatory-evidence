# CMM R7B1B v2：双向重分类结果与证据边界

## 完整 642 结果

| 判定 | n | 比例 |
|---|---:|---:|
| `STABLE_H3` | 409 | 63.7% |
| `STABLE_H4` | 78 | 12.1% |
| `AMBIGUITY_REMAINS_MODEL_SENSITIVE` | 46 | 7.2% |
| `H3_TO_UNINFORMATIVE` | 31 | 4.8% |
| `H4_TO_UNINFORMATIVE` | 24 | 3.7% |
| `AMBIGUITY_TO_H3` | 15 | 2.3% |
| `H3_TO_H4` | 8 | 1.2% |
| `H3_TO_MODEL_SENSITIVE` | 7 | 1.1% |
| `AMBIGUITY_TO_UNINFORMATIVE` | 6 | 0.9% |
| `H4_TO_MODEL_SENSITIVE` | 6 | 0.9% |
| `AMBIGUITY_TO_H4` | 5 | 0.8% |
| `H4_TO_H3` | 4 | 0.6% |
| `BORDERLINE_UNINFORMATIVE` | 2 | 0.3% |
| `BORDERLINE_TO_H4` | 1 | 0.2% |

## 多信号主状态

| 判定 | n | 比例 |
|---|---:|---:|
| `H3_SUPPORTED_STABLE` | 428 | 66.7% |
| `H4_SUPPORTED_STABLE` | 92 | 14.3% |
| `UNINFORMATIVE` | 63 | 9.8% |
| `MODEL_SENSITIVE` | 59 | 9.2% |

## PF10/PF50 敏感性

| 判定 | n | 比例 |
|---|---:|---:|
| `MATCH` | 491 | 76.5% |
| `NOT_COMPARABLE` | 122 | 19.0% |
| `PF50_UNINFORMATIVE` | 25 | 3.9% |
| `PF10_PF50_SENSITIVE` | 4 | 0.6% |

## 预设代表性比较

| comparison | locus | gene | cell | ABF | multi-signal | reclassification | max H4 |
|---|---:|---|---|---|---|---|---:|
| R7B1_000258 | 2 | IL12RB2 | NK | ABF_H4_DOMINANT | H4_SUPPORTED_STABLE | STABLE_H4 | 0.998 |
| R7B1_000410 | 4 | FCRL3 | B_IN | ABF_H4_DOMINANT | H4_SUPPORTED_STABLE | STABLE_H4 | 0.994 |
| R7B1_000411 | 4 | FCRL3 | B_MEM | ABF_H4_DOMINANT | H4_SUPPORTED_STABLE | STABLE_H4 | 0.991 |
| R7B1_000414 | 4 | FCRL3 | CD8_ET | ABF_H4_DOMINANT | H3_SUPPORTED_STABLE | H4_TO_H3 | 0.004 |

上述表只用于显示预先指定或按机器规则排序的结果，不用于新增候选。一个 comparison 可以同时含 shared 与 distinct signal pairs；机器终裁在跨 L 稳定 H4 时保留 shared-signal 状态，并在完整 signal-pair 表中保留其余 H3 pairs。

## 可发表表述

允许：

> PBC-wide ABF screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset.

不允许：

- complete multi-signal landscape of all 6,923 comparisons；
- independent disease replication；
- 所有 `UNINFORMATIVE` 均为生物学阴性；
- PF50 sensitivity 取代 PF10 primary model；
- 依据本轮后验新增 gene、cell 或 locus。
