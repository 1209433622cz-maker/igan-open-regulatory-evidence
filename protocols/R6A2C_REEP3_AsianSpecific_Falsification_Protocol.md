# R6A2C 冻结协议：REEP3 Asian-specific falsification + design reassessment

日期：2026-09-14

## 唯一允许的候选

```text
disease = Asian-only IgAN
locus = REEP3
gene = REEP3
cell = OneK1K CD4_NC
region = chr10:64,363,048-66,363,048 GRCh37
smoke shared top = 10:65376395
```

## 冻结分析

1. 用 CD4_NC 的真实 980-donor 清单构建 raw、PF10 和 PF50 source-matched LD；
2. SuSiE-RSS 主配置 PF10/L10；敏感性 PF10/L5、PF10/L20、PF50/L10；
3. 仅对满足 95% CS purity 的 component 运行 Asian disease signal-specific coloc；
4. `p1=p2=1e-4`，`p12=1e-6/1e-5/1e-4`；
5. 对 combined、European-only 做相同 component 的方向、覆盖、频率与后验对照；
6. Asian disease min P 未达 5e-8，结论必须保留 discovery-candidate 限定。

## GO 门

```text
PF10_L10_CONVERGED = TRUE
STABLE_95PCT_CS >= 1
ASIAN_SIGNAL_PP_H4 >= 0.80
ASIAN_SIGNAL_H4_RATIO >= 0.80
ASIAN_LOW_PRIOR_H4_RATIO >= 0.50
ALLELE_BUILD_LD_QC = PASS
```

通过后仅允许 TenK10K 匹配 T-cell 的独立 QTL replication。TenK 也通过后，进入双位点/ancestry-aware 稿件可行性重评；仍不能自动启动 full-24。

## FAIL 门

任一核心门失败，冻结 `REEP3_ASIAN_EXPRESSION_MEDIATION = NOT_SUPPORTED_OR_UNRESOLVED`，不再扩展 IgAN 免疫细胞 cis-eQTL 位点。项目进入 design reassessment：比较 ZMIZ1 单位点机制稿、公开 pQTL/肾脏层、或换题，按“可完成性和真实阳性证据”排序。
