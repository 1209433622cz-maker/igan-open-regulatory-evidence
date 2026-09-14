# CMM R6A2A1：最终判定与 R6A2B0 冻结目标

```text
IgAN_MAIN_PROJECT = CONDITIONAL_GO

R6A2A1 = COMPLETE
PUBLISHED_CELL_PRIMARY_PASS = 1 / 3
PUBLISHED_CELL_PRIMARY_UNINFORMATIVE = 2 / 3
PUBLISHED_CELL_PRIMARY_DISTINCT_FAIL = 0 / 3

ZMIZ1_NK_ONEK = ROBUST_SHARED_SIGNAL
ZMIZ1_NK_TENK = SUPPORTIVE_SINGLE_CAUSAL_REPLICATION
ITGAX_NK = DISTINCT_SIGNAL_FAVORED

STRICT_DIRECT_FULL24_GATE = NOT_MET
METHOD_FAILURE = NO
R6A2B0_BOUNDED_EXPANSION = GO
FULL_24_LOCUS = HOLD
TISSUE_SCALE_ANALYSIS = HOLD
```

## R6A2B0 规模

| locus | OneK cell–gene combinations | genes |
|---|---:|---:|
| LIF/OSM | 11 | 6 |
| OVOL1/RELA | 67 | 24 |
| REEP3 | 2 | 1 |
| REL | 8 | 6 |
| TNFRSF13B | 20 | 9 |
| TNFSF12/13 | 63 | 21 |
| TNFSF4/18 | 10 | 3 |
| TNFSF8/15 | 2 | 1 |

合计 183 个组合，最多 549 个三表型 coloc.abf tests。

## 决策逻辑

直接放行24-locus会违反 R6A2A0 的2/3正控门；把项目判 HOLD 又会把两个 weak-QTL uninformative 误当成方法失败。八 locus 有界扩展同时利用 serum-IgA trait support 和双 QTL 资源可复核性，可以用最小新增计算量判断是否具备至少3个独立阳性 locus 的完成潜力。

下一阶段唯一目标：**R6A2B0 — 8-locus/183-combination bounded positive-yield expansion**。
