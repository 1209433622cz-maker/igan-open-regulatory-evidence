# CMM R6A2C1D 执行摘要：REEP3 真实实跑与跨资源终裁

日期：2026-09-14

## 最终结论

本轮把 R6A2C0 从“执行准备包”推进为真实计算，并继续完成触发后的 TenK10K 独立分子复核。

```text
R6A2C_ONEK_SIGNAL_GATE = PASS_ASIAN_SPECIFIC_DISCOVERY_CANDIDATE
R6A2D_TENK_REPLICATION = FAIL_INDEPENDENT_TENK_REPLICATION

REEP3_CLAIM_CEILING = ONEK_DISCOVERY_ONLY
IGAN_TWO_LOCUS_ANCESTRY_AWARE_MANUSCRIPT = NO_GO
IMMUNE_CISEQTL_FULL24 = FROZEN_NO_GO

NEXT = R6A3A_IGAN_COMPLETION_DESIGN_GATE
```

## OneK1K 真实信号级结果

- 精确使用 CD4_NC 的 980 donors 与 3,084 个 REEP3 QTL/基因型共同变异；
- raw、PF10、PF50 source-matched LD 均通过结构门；
- PF10/L5、PF10/L10、PF10/L20、PF50/L10 四套 SuSiE-RSS 全部收敛；
- 四套配置各得到 1 个 95% credible set，成员完全相同，Jaccard 均为 1.0；
- PF10/L10 的可信集有 15 个变异，purity min |r|=0.8346；
- Asian signal-specific coloc：默认 `PP.H4=0.90048`，`H4/(H3+H4)=0.91322`；低 `p12=1e-6` 时比值为 `0.51275`；
- combined 与 European 默认 `PP.H4` 分别只有 `0.07171` 与 `0.01486`，均为 H3 主导。

因此 OneK 结果通过预冻结的 ancestry-specific discovery 门，但疾病区域最小 P 约为 `4.55×10^-6`，未达全基因组显著。该结果不能称为已确立的亚洲特异性致病机制。

## TenK10K 独立复核

TenK10K 公开 gene-level 数据确认 REEP3 是 T-cell cis-eQTL gene：

| cell | ACAT P | source CS | source max PIP |
|---|---:|---:|---:|
| CD4_Naive | 3.21×10^-12 | 1（44 members） | 0.0451 |
| CD4_TCM | 7.82×10^-7 | 1（61 members） | 0.1345 |
| Treg（辅助） | 0.00481 | 0 | — |

但“同一基因有强 eQTL”不等于“同一疾病信号得到复制”。OneK PF10/L10 的 15 个可信集成员全部唯一映射到 GRCh38 后，与 TenK source CS 的精确位置+等位基因交集为 0。TenK 作者预计算的 `kiryluk_IgAN × REEP3` coloc 也显示：

| cell | PP.H3 | PP.H4 | H4/(H3+H4) |
|---|---:|---:|---:|
| CD4_Naive | 0.9650 | 0.0314 | 0.0315 |
| CD4_TCM | 0.9687 | 0.0258 | 0.0259 |
| Treg（辅助） | 0.2109 | 0.0470 | 0.1823 |

两个冻结的 replication cells 都明确支持 distinct disease/QTL signals。因此 REEP3 不计入跨资源阳性。

## 项目判断

IgAN 项目当前只有 ZMIZ1/NK 这一条跨资源遗传调控锚点。8-locus 扩展没有新增 combined robust signal，REEP3 虽有 OneK Asian discovery signal，但 TenK replication 失败。现有证据不支持多位点 immune cis-eQTL landscape，也不支持 ZMIZ1+REEP3 双位点论文。

下一阶段改为 R6A3A：仅对公开 cis-pQTL 资源做字节级可用性预检，并对 ZMIZ1 做肾组织 donor-level 定位预检。只有新增至少一个独立 pQTL shared-signal locus，且 ZMIZ1 在肾组织层可形成可解释的 donor-level 支持，才恢复论文级分析。

