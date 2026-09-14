# R7A1B 冻结协议：PBC 三正控有界信号门

## 目标

只判断预注册的三条 PBC disease↔immune-cell eQTL 链能否形成至少两个稳健 shared signals。不得用 post-hoc 基因替换补救。

## 固定对象

```text
Disease = GCST90061440, GRCh37
Genes = IL12RB2, FCRL3, INAVA(C1orf106)
GJOKA disease-LD loci = 2, 4, 6
```

OneK 首轮仅分析已有 top-level 记录：

- IL12RB2：NK
- FCRL3：B_IN, B_MEM, CD4_NC, CD8_ET, CD8_NC, NK, NK_R
- INAVA/C1orf106：CD4_NC（弱 QTL 证伪组合）

最大 9 个 disease–OneK smoke comparisons。

## 顺序

1. 从本地 10.34 GB OneK raw archive 仅提取 chr1 目标 members，核对完整 cis 行数、build、allele 与 cell-specific donor。
2. disease/QTL 变异严格按 chr:pos:alleles 统一；记录 palindromic、重复、缺失与覆盖率。
3. 运行固定先验 coloc.abf smoke：`p1=p2=1e-4`，`p12=1e-6/1e-5/1e-4`。
4. 只有 robust H4 或可解释 H3/H4 ambiguity 才下载对应 GJOKA LD，并构建 OneK donor-matched source LD。
5. 多信号裁决通过后才进入 TenK 同基因、兼容细胞复制；TenK GRCh38 必须独立 build/allele harmonization。
6. 至少两个基因通过后，才下载 PBC liver scRNA 做 target detectability 与 donor-level orthogonal validation。

## 升级门

```text
ROBUST_SHARED_SIGNAL_GENES >= 2/3
TENK_SAME_GENE_COMPATIBLE_CELL_REPLICATION >= 1
PBC_LIVER_TARGET_DETECTABILITY = PASS
CORE_PERMISSION_DATA = FALSE
```

robust shared signal 默认要求 `PP.H4>=0.80` 且 `H4/(H3+H4)>=0.80`，并且先验敏感性不翻转成 H3；若存在多信号，必须在 source-LD 条件/精细定位后仍成立。

若失败：

```text
PBC_REGULATORY_MAIN = FROZEN_FAIL
CeD_AUTO_RESUME = NO
NEXT = NEW_RESEARCH_ARCHITECTURE_REDESIGN
```
