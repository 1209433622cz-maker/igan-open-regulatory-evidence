# R5A2A4 chr18 表达介导冻结判定

## 五问裁决

| 冻结问题 | 结果 | 判定 |
|---|---:|---|
| ZCCHC2 是否存在 source-significant eQTL？ | q=0.383 | NO |
| 是否有 marginal variant 通过局部阈值？ | 0/3,827 | NO |
| SuSiE 是否形成 95% credible signal？ | 0，六组均为 0 | NO |
| rs7239261 是否进入可信 QTL signal？ | PIP=0.00665 | NO |
| 去除 top eQTL 后是否有 lead block 残余信号？ | lead P=0.0177；全窗口 0 个通过 | NO |

最终状态：

```text
CHR18_DISEASE_LOCUS = RETAINED
CHR18_ONEK1K_PBMC_EXPRESSION_MEDIATION = FAIL_SUFFICIENT_COVERAGE
NK_R_ZCCHC2_MULTISIGNAL_RESCUE = FAIL
TENK10K_CHR18 = NOT_TRIGGERED
FURTHER_CHR18_GENE_CELL_RESCUE = STOP
```

R5A2A3 的 ABF H4 是弱 QTL 条件下由 rs7239261 的 nominal QTL 值与先验共同形成的单信号混合结果。source permutation、低 lead–top LD、无 credible set 以及条件分析共同表明，没有证据支持“隐藏的 ZCCHC2 次级 cis-eQTL 与疾病信号对齐”。

该判定只针对 OneK1K PBMC cis-expression mediation。其它组织、细胞状态、染色质或非表达机制不在本轮数据支持范围内，也不作为继续扩大 chr18 分析的理由。
