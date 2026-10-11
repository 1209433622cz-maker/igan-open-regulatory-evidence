# CMM R6A2A1：OneK1K 十组合与祖源分层结果

## Combined IgAN

| locus | cell | gene | role | SNPs | QTL min P | PP.H3 | PP.H4 | H4 ratio | 判定 |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| IRF4/DUSP22 | CD4_NC | DUSP22 | CROSS_CELL_SECONDARY | 2,083 | 2.53e-05 | 0.3153 | 0.0717 | 0.1853 | UNINFORMATIVE_OR_WEAK_QTL |
| IRF4/DUSP22 | CD4_NC | IRF4 | CROSS_CELL_SECONDARY | 2,083 | 2.13e-05 | 0.2949 | 0.0306 | 0.0941 | UNINFORMATIVE_OR_WEAK_QTL |
| ITGAM/ITGAX | NK | ITGAX | CROSS_CELL_SECONDARY | 1,354 | 2.5e-07 | 0.9891 | 0.0004 | 0.0004 | FAIL_SUFFICIENT_COVERAGE |
| IRF4/DUSP22 | Mono_C | DUSP22 | PUBLISHED_CELL_CLASS_PRIMARY | 2,082 | 0.00757 | 0.1138 | 0.0460 | 0.2878 | UNINFORMATIVE_OR_WEAK_QTL |
| IRF4/DUSP22 | Mono_NC | DUSP22 | PUBLISHED_CELL_CLASS_PRIMARY | 2,083 | 0.0041 | 0.1694 | 0.0386 | 0.1858 | UNINFORMATIVE_OR_WEAK_QTL |
| IRF4/DUSP22 | Mono_C | IRF4 | PUBLISHED_CELL_CLASS_PRIMARY | 2,082 | 0.00056 | 0.1276 | 0.0963 | 0.4301 | UNINFORMATIVE_OR_WEAK_QTL |
| IRF4/DUSP22 | Mono_NC | IRF4 | PUBLISHED_CELL_CLASS_PRIMARY | 2,083 | 0.000982 | 0.1422 | 0.0642 | 0.3110 | UNINFORMATIVE_OR_WEAK_QTL |
| ITGAM/ITGAX | Mono_C | ITGAX | PUBLISHED_CELL_CLASS_PRIMARY | 1,355 | 0.00138 | 0.2070 | 0.1037 | 0.3338 | UNINFORMATIVE_OR_WEAK_QTL |
| ITGAM/ITGAX | Mono_NC | ITGAX | PUBLISHED_CELL_CLASS_PRIMARY | 1,354 | 5.93e-05 | 0.2197 | 0.0786 | 0.2636 | UNINFORMATIVE_OR_WEAK_QTL |
| ZMIZ1 | NK | ZMIZ1 | PUBLISHED_CELL_CLASS_PRIMARY | 3,551 | 3.51e-07 | 0.0656 | 0.9306 | 0.9341 | PASS_ROBUST_SHARED_SIGNAL |

## 解释

- `ZMIZ1/NK` 是唯一 robust combined positive；Asian 同样 robust，European 为 `PP.H4≈0.789`、H4 ratio≈0.885，但 low-p12 下转为更依赖 prior，因此记为支持而非独立 robust。
- `IRF4/DUSP22` published monocyte combinations 的 QTL min P 为约 `5.6×10^-4` 至 `7.6×10^-3`，在强疾病区域中不足以做生物学阴性判定。
- `ITGAX` published monocyte QTL 同样偏弱，故为 uninformative。
- `NK × ITGAX` 的 QTL 很强（min P≈`2.5×10^-7`），但 combined `PP.H3≈0.9891、PP.H4≈0.00042`，是充分覆盖下的 distinct-signal evidence。不能用该强 QTL 替代 monocyte 机制。
- combined 没有 H3/H4 ambiguity trigger，因此本轮不对 IRF4 或 ITGAX 生成 source LD。

## ZMIZ1 方向

OneK BIM A1 为 G、IgAN risk allele 为 A。疾病 lead `10:81043743` 的 OneK G-allele slope 为 `+0.1981`，因此 risk A 对表达的方向是 down；QTL P=`9.51×10^-6`。该方向与已发表 ZMIZ1 risk-down 结构一致。
