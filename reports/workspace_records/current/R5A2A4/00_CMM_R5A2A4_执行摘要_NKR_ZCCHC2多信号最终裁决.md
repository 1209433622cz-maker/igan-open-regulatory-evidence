# CMM R5A2A4 执行摘要：NK_R / ZCCHC2 多信号最终裁决

日期：2026-09-14  
最终状态：`R5A2A4 = COMPLETE`  
核心判定：`FAIL_CHR18_ONEK1K_PBMC_EXPRESSION_MEDIATION`

## 最终结论

R5A2A4 已按冻结协议完成 OneK1K `NK_R / ZCCHC2` 的 exact-active-donor source LD、协变量残差化 LD、官方 permutation/q-value 复核、SuSiE-RSS 多信号分析和强制条件分析。工程输入全部通过，但五个科学问题全部未通过：

1. ZCCHC2 的官方 source top-eQTL 不显著：nominal `P=4.96×10^-5`，permutation `P=0.0573`，`q=0.383`；
2. 3,827 个固定窗口变异中没有任何变异通过局部 Bonferroni 阈值 `1.31×10^-5`；
3. PF10 主分析及 5 组敏感性 SuSiE-RSS 均为 0 个 95% credible set；
4. 主分析最大 PIP 仅 0.0296，rs7239261 的 PIP 仅 0.00665；
5. 在 18:60243208 上强制条件化后，rs7239261 的 PF10 条件 `P=0.0177`，全窗口没有残余变异通过局部阈值。

rs7239261 与 ZCCHC2 nominal top `18:60243208` 在 exact NK_R donor 的 PF10 LD 中 `r²=0.0124`，属于不同 LD 结构。R5A2A3 中先验敏感的 H4 因而不能解释为隐藏的次级 ZCCHC2 eQTL 与疾病 lead 共定位。

## 边界

本轮否定的是“chr18 疾病位点通过 OneK1K PBMC NK_R 中 ZCCHC2 cis-expression 介导”的具体假说。结果不否定 chr18 疾病关联，也不排除其它组织、细胞或非表达调控层。按照预注册停止规则，不再在 chr18 更换 gene/cell 组合救故事，也不触发 TenK10K chr18 复制。

## 下一阶段

下一阶段固定为 `R5A2B_CHR5_TNIP1_BOUNDED_PILOT`。它只测试 chr5 / rs6861227 / TNIP1 及冻结的七个竞争基因，并先完成 source permutation 与单信号 smoke gate。只有触发条件成立才构建 cell-specific source LD。

若 chr5 也在充分覆盖下失败，则冻结 `NO_GO_MG_REGULATORY_MAIN`，转入 `IgAN_OPEN_DATA_PREFLIGHT`。MG 主项目当前仍为 `CONDITIONAL_GO`；组织分析和手稿规模分析继续 HOLD。
