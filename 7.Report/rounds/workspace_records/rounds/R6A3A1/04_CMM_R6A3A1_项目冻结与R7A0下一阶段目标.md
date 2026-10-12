# IgAN 项目冻结与 R7A0 下一阶段目标

日期：2026-09-15

## 当前项目组合

```text
SSc_SEX_SPECIFIC_MAIN = FROZEN_ARCHIVE
MG_REGULATORY_MAIN = FROZEN_ARCHIVE
IGAN_REGULATORY_MAIN = FROZEN_ARCHIVE

SSc_DEFAULT_RESUME = NO
MG_DEFAULT_RESUME = NO
IGAN_DEFAULT_RESUME = NO
```

IgAN 仍保留可复用的 ZMIZ1 跨资源正控、REEP3 祖源特异发现信号、完整 GWAS/QTL/tissue 字节和方法工程，但这些不能合并包装成一个达到冻结门槛的多位点 regulatory-main 论文。

## 下一阶段

```text
R7A0 = OPEN_DATA_COMPLETION_FIRST_PORTFOLIO_PREFLIGHT
CANDIDATES = CELIAC_DISEASE / PRIMARY_BILIARY_CHOLANGITIS / ALOPECIA_AREATA
NO_PRIMARY_PROJECT_ASSIGNED_YET = TRUE
```

CeD 目前具有一个新的公开组织入口：GEO `GSE315138` 已于 2026-01-31 公开，内容为 active CeD 与正常对照的 duodenal biopsy scRNA-seq。这个事实只使 CeD 获得 Gate-0 优先级，不代表其 GWAS、样本量、QTL 正控或新颖性已经通过。

PBC 与 AA 同样进入比较，是因为它们有明确疾病组织与免疫遗传机制，且历史压力测试中未因当前三个项目的失败理由被排除。R7A0 不在本轮预先指定胜者。

## 新主项目的硬门

```text
FULL_GWAS_BYTES_AND_SCHEMA = PASS
NON_MHC_INDEPENDENT_SIGNALS >= 5
PRE_REGISTERED_TESTABLE_LOCI >= 3
ROBUST_SHARED_SIGNAL_LOCI >= 2
CROSS_RESOURCE_REPLICATION_LOCI >= 1
PUBLIC_DISEASE_TISSUE = PASS
CORE_CLAIM_REQUIRES_PERMISSION_DATA = FALSE
HOSTILE_NOVELTY = PASS_OR_MANAGEABLE
```

Gate 0 先查 metadata、小型 manifest、credible set 与组织样本表；任何大于 1 GB 的文件在候选通过前不下载。只有排名前两项进入真实字节和 2–3 个预注册正控 locus 的计算。

如果三者都失败，下一步改研究范式，不再把同一套 immune cis-eQTL 框架换一个疾病继续运行。

冻结协议：`0_admin/protocol/current/R7A0_open_data_completion_first_portfolio_preflight_v1.md`。

