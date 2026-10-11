# CMM R5A2B0 执行摘要：chr5 bounded pilot 预验收与执行冻结

**日期：2026-09-14**

## 判定

```text
R5A2A4_RELEASE = PASS
CHR18_EXPRESSION_MEDIATION = FROZEN_FAIL
MG_MAIN_PROJECT = CONDITIONAL_GO

R5A2B_CHR5 = GO_BOUNDED_FINAL_ATTEMPT
R5A2B_INFERENCE_IN_THIS_SANDBOX = NOT_RUN_RAW_LARGE_INPUTS_NOT_INCLUDED_IN_YR1_ZIP

FROZEN_GENES = 8
FROZEN_ONEK1K_SOURCE_SIGNIFICANT_CELL_GENE = 32
PRIMARY_DISEASE = EOMG
SUPPORT_DISEASE = MG_overall
CONTRAST_DISEASE = LOMG

NEXT_LOCAL_ACTION = RUN_R5A2B_CHR5_BOUNDED_SMOKE
```

`YR1.zip` 是代码/结果/报告快照，不包含 `1_data` 大文件，因此当前会话无法诚实地假装已经读取本机 10.34 GB OneK1K archive、1.46 GB PLINK 或三套原始 GWAS。它们在既往本地 R5A2A2/R5A2A4 中已验收，本轮为这些**现有本地字节**生成了不重新下载的可执行 R5A2B 管线。

## 新增关键事实

1. 冻结 8 个基因中共有 **32 个 OneK1K source-significant cell–gene**，分布：`{'ANXA6': 12, 'RPS14': 7, 'GM2A': 5, 'CCDC69': 2, 'TNIP1': 2, 'TCOF1': 2, 'ATOX1': 1, 'SLC36A1': 1}`。
2. `TNIP1` 只有 `NK` 与 `CD4_NC` 两个 OneK1K source-significant cell；其余强竞争基因的 QTL 往往更强。
3. TenK10K 中 `TNIP1` 最大 SuSiE PIP≈0.5535，疾病 lead 进入 B-naive TNIP1 credible set，但 lead QTL PIP≈0.0236。
4. `ANXA6/GM2A/RPS14/CCDC69` 的 TenK10K 最大 PIP 接近 1，但疾病 lead 不在其 source CS；这类“强 eQTL、弱疾病对齐”正是必须通过 coloc 排除的竞争信号。
5. Braun 2024 overall MG 中 rs6861227 的 23andMe replication 为同方向 nominal 支持，combined overall MG P≈3.03e-8；但论文明确说 TNIP1 没通过 EOMG-specific replication 门。日本 overall MG 中该 SNP P≈0.284 且方向相反。因此 chr5 不能被预写成稳定 EOMG-specific locus。

## 冻结分析

只运行：
- 8 个基因；
- 32 个 source-significant OneK1K cell–gene；
- EOMG 主检验、overall MG 支持、LOMG 对照；
- 最多 96 个单信号 smoke tests。

只有 robust H4 或明确 H3/H4 ambiguity 才为**触发组合**建立 cell-specific source LD；不允许为全部 32 个组合批量建 LD。

## 停止规则

- 若没有 robust/shared 或可解决 ambiguity：`FAIL_CHR5_EXPRESSION_MEDIATION`。
- 若只有强 competitor eQTL 但 disease signal 为 H3/distinct：同样 FAIL。
- 若 TNIP1/竞争基因出现 signal-level PASS：才进入 TenK10K 独立复制。
- 若 chr5 失败：`NO_GO_MG_REGULATORY_MAIN → IgAN_OPEN_DATA_PREFLIGHT`，不转 chr2/chr8 救故事。
