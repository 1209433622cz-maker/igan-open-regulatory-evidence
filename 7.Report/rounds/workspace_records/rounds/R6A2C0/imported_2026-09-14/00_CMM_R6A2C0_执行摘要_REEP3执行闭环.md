# CMM R6A2C0 执行摘要：REEP3 Asian-specific falsification 执行闭环

**日期：2026-09-14**

## 当前状态

```text
R6A2B0E_UPSTREAM_INTEGRITY = PASS
UPSTREAM_SHA256 = bfd7bf7e17fa03f2b715ad25d707720fbfd96064865af19a70c34055a9375f80
UPSTREAM_INTERNAL_CHECKSUM = 47/47 PASS

REEP3_ASIAN_SMOKE = BOUNDED_TRIGGER_ONLY
R6A2C_EXECUTION_PACKAGE = READY
R6A2C_SIGNAL_SPECIFIC_RESULT = PENDING_LOCAL_SOURCE_BYTES

FULL24 = HOLD
TENK_REEP3 = HOLD_UNTIL_R6A2C_PASS
TISSUE_SCALE_ANALYSIS = HOLD
```

冻结的 smoke 基线：Asian `REEP3×CD4_NC` PP.H4≈0.9057、H4/(H3+H4)≈0.9179、低 p12 ratio≈0.5278；combined PP.H4≈0.0763，European≈0.0149。Asian disease 区域最小 P≈4.55×10^-6，因此即使 R6A2C 全部通过，也只能定义为 **ancestry-specific discovery candidate**。

## R6A2C 主门

必须顺序通过：
1. exact 980-donor CD4_NC source LD；
2. PF10 主 LD 与 PF50 sensitivity LD；
3. PF10/L10 SuSiE 收敛；
4. 至少1个在 PF10-L5、PF10-L20、PF50-L10 中均 Jaccard≥0.50 的稳定95% CS；
5. 对该稳定 component 的 Asian signal-specific coloc：default H4≥0.80、H4 ratio≥0.80、低 p12 ratio≥0.50。

任何核心门失败即冻结 `REEP3_ASIAN_EXPRESSION_MEDIATION = NOT_SUPPORTED_OR_UNRESOLVED`，并停止继续扩展 IgAN immune cis-eQTL loci。
