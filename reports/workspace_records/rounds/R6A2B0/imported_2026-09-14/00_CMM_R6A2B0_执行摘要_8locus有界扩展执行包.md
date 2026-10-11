# CMM R6A2B0 执行摘要：8-locus bounded positive-yield expansion 执行包

**日期：2026-09-14**

## 状态

```text
R6A2A1_RELEASE_INTEGRITY = PASS
IgAN_MAIN_PROJECT = CONDITIONAL_GO

ZMIZ1_NK = ROBUST_ONEK + SUPPORTIVE_TENK
FULL_24_LOCUS = HOLD

R6A2B0_FROZEN_UNIVERSE = PASS
FROZEN_LOCI = 8
FROZEN_ONEK_CELL_GENE = 183
MAX_ABF_TESTS = 549
REQUIRED_ONEK_CHR_CELL_MEMBERS = 43

R6A2B0_INFERENCE_IN_THIS_CHAT = NOT_RUN
reason = uploaded YR1 snapshot excludes canonical 1_data large bytes

NEXT_ACTION = LOCAL_RUN_R6A2B0_8LOCUS_BOUNDED_EXPANSION
```

R6A2A1 发布包 SHA-256 独立重算为 `e1ec4c59321dff10d2056504c7090ec16c3d039875ce84aab2a9f8b0fdd1528a`；ZIP CRC PASS，内部 checksum `62/62` PASS。

## 冻结8个 locus

| locus      |   frozen_combinations |   frozen_genes |   frozen_cells |   best_OneK_q |
|:-----------|----------------------:|---------------:|---------------:|--------------:|
| LIF/OSM    |                    11 |              6 |              4 |  5.88989e-06  |
| OVOL1/RELA |                    67 |             24 |             12 |  7.06045e-139 |
| REEP3      |                     2 |              1 |              2 |  3.90775e-06  |
| REL        |                     8 |              6 |              3 |  1.56122e-18  |
| TNFRSF13B  |                    20 |              9 |              7 |  2.18636e-18  |
| TNFSF12/13 |                    63 |             21 |             14 |  6.50813e-266 |
| TNFSF4/18  |                    10 |              3 |              6 |  1.15723e-130 |
| TNFSF8/15  |                     2 |              1 |              2 |  2.32818e-10  |

这些组合全部来自 R6A2A1 预冻结 universe；未增加新 gene/cell。183 个组合无重复。

## 计算压缩

虽然 universe 有183个组合，但 OneK raw archive 实际只需抽取 **43 个 chromosome×cell Parquet 成员**。因此本轮代码采用：

一次完整 archive 流式身份校验
→ 选择性提取43成员
→ 一次构建183组合QTL
→ 三套GWAS一次区域扫描
→ 最多549个ABF
→ 官方R coloc复核
→ locus-level machine adjudication

不会为183组合预先批量构建 LD。

## R6A2B0 放行规则

- 新增≥2个独立 robust/signal-specific PASS loci：连同 ZMIZ1 至少3个独立阳性，进入 full-24 landscape。
- 新增1个：只允许 `CONDITIONAL_GO_ONE_MORE_BOUNDED_BLOCK`。
- 新增0且覆盖充分：`HOLD_FULL24_REASSESS_MANUSCRIPT_DESIGN`。
- H3/H4 ambiguity：只给触发组合做 source LD。
