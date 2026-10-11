# CMM R5A2B 执行摘要：chr5 有界机制最终判定

日期：2026-09-14  
状态：`R5A2B = COMPLETE`  
最终判定：`FAIL_CHR5_EXPRESSION_MEDIATION`

## 核心结果

本轮实际接入本机已经验收的 OneK1K 全量 eQTL、980-donor genotype、14 个 cell-specific donor lists 和三套原始 MG GWAS，完成 8 个冻结基因、32 个 source-significant cell–gene、3 个疾病表型的全部 96 个 coloc.abf smoke tests。

```text
ROBUST_SHARED_SIGNAL = 0
RESOLVABLE_H3H4_AMBIGUITY = 0
SOURCE_LD_TRIGGER = 0
TENK10K_TRIGGER = 0
```

EOMG 的最高默认 H4 是 `NK/TNIP1`：

```text
PP.H3 = 0.9094
PP.H4 = 0.0662
H4/(H3+H4) = 0.0679
p12 1e-6 / 1e-5 / 1e-4 H4 = 0.00704 / 0.0662 / 0.4149
H4/(H3+H4) @ p12=1e-4 = 0.4213
```

这更支持强疾病信号和 source-significant TNIP1 eQTL属于不同信号。exact rs6861227 在 NK/TNIP1 中仅 `P=0.00631`，在 CD4_NC/TNIP1 中 `P=0.0937`。更强的 ANXA6、GM2A、RPS14 等 QTL 对 EOMG 几乎全部由 H3 主导。

全部 96 项已经由官方 R `coloc 5.2.3` 独立复核；288 个先验运行与 Python 最大 H4 差 `3.03×10^-15`，top SNP 全部一致。

## 项目判定

```text
CHR18_EXPRESSION_MEDIATION = FROZEN_FAIL
CHR5_EXPRESSION_MEDIATION = FAIL_SUFFICIENT_COVERAGE
MG_REGULATORY_MAIN = NO_GO
FURTHER_MG_LOCUS_RESCUE = STOP
MG_DISEASE_GENETICS = RETAINED
```

本轮不否定 rs6861227 的 MG/EOMG 疾病遗传关联；否定的是当前公开 PBMC eQTL 支持的 expression-mediated 主论文路线。按预注册停止规则，不再转 chr2、chr8 或更多 MG 位点。

下一阶段固定为 `R6A0_IGAN_OPEN_DATA_BYTE_LEVEL_PREFLIGHT`。IgAN 目前只是 active preflight candidate，尚未升级为主论文。
