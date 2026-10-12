# CMM R6A1：GO/NO-GO 与 R6A2 冻结目标

## R6A1 门控

八项门全部通过，机器可读状态见 `R6A1_final_gate_adjudication.json`。

```text
IgAN_MAIN_PROJECT = GO
R6A1 = COMPLETE
R6A2 = GO

PUBLISHED_NON_HLA_LOCI = 24
ONEK1K_TESTABLE_LOCI = 22
TENK10K_TESTABLE_LOCI = 24
CROSS_RESOURCE_CANDIDATE_LOCI = 22
SERUM_IGA_NOMINAL_CONCORDANT_SIGNALS = 9
PUBLISHED_CONTROL_RECOVERY = 4 genes / 3 loci
KIDNEY_DETECTABILITY = PASS

NEW_COLOC_POSITIVE_CLAIMS = 0
MANUSCRIPT_SCALE_ANALYSIS = HOLD_UNTIL_R6A2_GATE
```

## R6A2 的首批顺序

1. benchmark positive-control：`IRF4/DUSP22`、`ZMIZ1`、`ITGAM/ITGAX`。
2. trait-concordant cross-resource：除已重叠的 IRF4 locus 外，`TNFSF4/18`、`REL`、`TNFSF8/15`、`REEP3`、`OVOL1/RELA`、`TNFSF12/13`、`TNFRSF13B`、`LIF/OSM`。
3. 其余 cross-resource testable locus。
4. CFH、IGH 作为 resource-asymmetric 特殊层，不强行制造 OneK1K 复制。

排序只决定计算顺序，不决定论文结论。最终必须完成 24-locus universe，不能在首个阳性出现后停止，也不能把多个同 locus gene 计成多个独立阳性。

## 下一阶段唯一合法目标

**R6A2A — 三个已发表正控 locus 的真实 signal-level recovery gate。**

完成 build/allele harmonization、区域变异重叠、coloc.abf 预筛和必要时的 targeted source-LD。若至少 2/3 正控 locus 在技术覆盖充分条件下得到可解释 signal-level 支持，则继续 R6A2B 全 24-locus；否则先修复方法，不直接扫描全景。
