# CMM R6A3A1 执行摘要：pQTL 与 ZMIZ1 肾组织终裁

日期：2026-09-15  
阶段：R6A3A1 — R6A3A Completion-Design Gate 真实字节执行

## 最终判定

```text
R6A3A1_ACTUAL_EXECUTION = COMPLETE
PUBLIC_BYTE_LEVEL_PROVENANCE = PASS

TRACK_A_PQTL = FAIL_NO_ADDITIONAL_SHARED_SIGNAL
TRACK_B_ZMIZ1_KIDNEY = INTERPRETABLE_CASE_LOWER_NOT_SIGNIFICANT

IGAN_REGULATORY_MAIN = FROZEN_ARCHIVE
IGAN_DEFAULT_RESUME = NO

NEXT_STAGE = R7A0_OPEN_DATA_COMPLETION_FIRST_PORTFOLIO_PREFLIGHT
```

R6A3A0 是执行设计包，不是结果包。本轮完成了其此前未运行的公开数据下载、哈希固定、目标筛选、区域协调、signal-level pQTL colocalization 和肾组织供体级分析。

## Track A：Sun 2018 plasma pQTL

11 个冻结蛋白中 8 个在 permutation 表中被测量。只有 TNFSF8 和 TNFSF12 同时满足 permutation-adjusted source significance 与源 SuSiE credible set，因此只有这两个蛋白进入 731.6 MB nominal pQTL 与 459.6 MB source LBF 的稠密分析。

提取后共有 16,778 个去重 pQTL variants；与 combined IgAN GWAS 完成 GRCh37→GRCh38 和精确 allele set 协调后，TNFSF8 有 6,144 个共同变异，TNFSF12 有 5,164 个共同变异。三个合法 source-CS 分量均未达到共享信号门：

| protein | source component | default PP.H4 | default H4/(H3+H4) | low-p12 ratio | 判定 |
|---|---:|---:|---:|---:|---|
| TNFSF8 | L1 | 0.01809 | 0.01836 | 0.00187 | FAIL |
| TNFSF12 | L1 | 0.0000051 | 0.0000051 | 0.00000051 | FAIL |
| TNFSF12 | L2 | 0.001049 | 0.001049 | 0.000105 | FAIL |

TNFSF12 的 disease lead `rs3803800` 同时有 IgAN P=`1.21×10^-10` 与 nominal pQTL P=`9.45×10^-9`，但 source signal-level 分解明确由不同的主要信号解释。这个结果说明“同一个 lead 附近两边都显著”不能替代 colocalization。

## Track B：GSE127136 ZMIZ1 肾组织

严格按供体聚合 2,785 个肾细胞，排除 835 个外周血单核细胞。13 名 IgAN 与 6 名肾癌邻癌组织对照的 ZMIZ1 aggregate-kidney pseudobulk 结果为：

```text
case - control log2CPM difference = -0.25637
bootstrap 95% CI = [-0.83532, 0.33266]
exact permutation P = 0.48279
Welch P = 0.43777
Mann–Whitney P = 0.46705
```

方向为病例较低，但不显著，只能标为 `INTERPRETABLE_DONOR_LEVEL`。邻癌组织不能称为健康肾；aggregate-kidney 结果也可能受细胞组成影响。

## 为什么冻结 IgAN 主线

预冻结 final gate 要求至少 1 个新增 pQTL shared-signal locus，同时要求 ZMIZ1 肾组织结果达到 PASS 或可解释。Track B 达到“可解释”，Track A 为 0 个新增 locus，因此总门失败。继续扩大蛋白、位点或组织数据将违背预注册边界，并重复此前 immune cis-eQTL 扩张的问题。

下一阶段进入 R7A0，对 CeD、PBC 和 AA 做同一套 open-data、positive-evidence、completion-first 预检；任何疾病都必须先通过真实 GWAS 字节和至少两个稳健共享信号位点，才可成为新主项目。

