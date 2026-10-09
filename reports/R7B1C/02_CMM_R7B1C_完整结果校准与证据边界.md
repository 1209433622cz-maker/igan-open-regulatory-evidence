# CMM R7B1C：完整结果、校准与限制

## 场景结果

| 场景 | 真值共享 | ABF H4 | matched H4 | matched H3 | uninformative | disease CS all coverage | QTL CS all coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1_one_shared | True | 65.94% | 54.12% | 0.05% | 45.83% | 95.45% | 55.97% |
| S2_distinct_correlated | False | 20.50% | 16.00% | 23.15% | 60.85% | 95.35% | 58.17% |
| S3_disease2_qtl1_partial | True | 36.87% | 33.44% | 2.12% | 64.43% | 40.25% | 55.72% |
| S4_two_by_two_one_shared | True | 14.59% | 9.57% | 2.65% | 87.78% | 40.53% | 5.38% |
| S5_two_by_two_none_highLD | False | 4.32% | 1.12% | 8.18% | 90.70% | 40.48% | 5.11% |
| S6_matched_vs_mismatched_LD | True | 14.58% | 9.49% | 2.70% | 87.81% | 40.16% | 5.35% |

## 判定解释

distinct 场景中的 H4 率用于 false-shared classification；shared 场景中的 H4 率用于 recovery。`UNINFORMATIVE` 保持为无足够 signal-pair evidence，未被改写成 H3 或生物学阴性。credible-set coverage 以每个 trait 的全部真因果变异是否进入任一 95% CS 计算。

ABF Brier score 为 **0.4055**；将无 signal-pair 的 multi-signal prediction 记为 0 时，其 Brier score 为 **0.5088**。后者更差，主要受复杂 shared 场景中大量无 signal-pair/低 CS coverage 影响；它是明确标注的 decision-calibration summary，不应被解释为经过证明的全局 posterior probability，也不能拿来宣称 multi-signal posterior 全局失准。

`L=5/10/20` 的场景级判定率变化很小，说明本轮主要结论不是由 L 选择驱动。相反，MAF、因果变异相关度与先验 p12 明显影响 H4 和 credible-set formation：低 MAF 主要导致无信息；S2 在 causal-r²=0.8 时 matched false H4 仍约 37.47%；高 p12 会提高 ABF 与 multi-signal 的 H4 判定率。

S4/S5/S6 的 QTL all-causal 95% CS coverage 仅约 5%，对应 opposite-effect/high-correlation 结构下的弱 signal recovery。此时较低 H4 很大程度上体现模型 abstention 与 CS 形成失败，而不能全部解释为正确识别 H3。

## 限制

- 只有两个经验 LD 模板；
- disease 与 QTL 效应量固定，没有构成完整 effect-size distribution；
- grid MAF 是生成参数，不是模板变异的实测 MAF；
- S6 只检验同位点 PF10/PF50 QTL covariance-model mismatch；
- 两个 PF10/PF50 模板非常接近，因此 S6 的近零效应不能外推到 ancestry mismatch、不同 reference panel 或严重样本错配；
- max signal-pair H4 不等价于对完整 trait pair 的单一校准概率；
- simulation 校准不能替代外部 molecular/chromatin replication。
