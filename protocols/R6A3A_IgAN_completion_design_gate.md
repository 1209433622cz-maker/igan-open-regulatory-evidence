# R6A3A 冻结协议：IgAN completion design gate

日期：2026-09-14  
状态：`GO_BOUNDED_PREFLIGHT`

## 目的

R6A2C/D 已证明 `Asian IgAN × REEP3 × CD4_NC` 在 OneK1K 中形成稳定的 signal-specific discovery signal，但未在 TenK10K 的相容 T-cell 资源中复制。IgAN 的多位点免疫细胞 cis-eQTL landscape 设计因此停止扩展。R6A3A 只判断现有 IgAN 资产能否重构为一篇证据充分、可完成的跨层论文。

## 冻结证据起点

```text
ZMIZ1_NK = VALIDATED_CROSS_RESOURCE_ANCHOR
REEP3_ONEK_ASIAN = DISCOVERY_PASS_ONLY
REEP3_TENK_CD4 = REPLICATION_FAIL_DISTINCT_SIGNAL_FAVORED
ADDITIONAL_8_LOCUS_COMBINED_ROBUST = 0
IMMUNE_CISEQTL_FULL24 = FROZEN_NO_GO
```

REEP3 不计入独立复制阳性，不得与 ZMIZ1 合并包装为双位点机制结果。

## Track A：公开 pQTL 字节级预检

只审计已冻结的 serum-IgA-concordant locus 中的蛋白编码对象：

```text
TNFSF4 / TNFRSF18
TNFSF8 / TNFSF15
OVOL1 / RELA
TNFSF12 / TNFSF13
TNFRSF13B
LIF / OSM
```

规则：

1. 只接受无需研究者审批、无需 UK Biobank RAP、无需受控访问的公开 summary-statistics 字节；
2. 每个对象冻结 accession、下载 URL、许可、build、allele/effect 定义、N、assay、行数、bytes 与 checksum；
3. 先验限定 cis-pQTL；必须有 beta/SE/P 和足够区域覆盖，才能进入 disease–pQTL coloc；
4. pQTL 阳性必须通过 signal-level shared evidence；单个 lead/proxy 或 MR P 值不算共定位；
5. 找不到公开可归档字节记为 `UNAVAILABLE_OPEN_DATA`，不解释为蛋白无作用。

## Track B：ZMIZ1 肾组织定位预检

首选 `GSE127136`，其公开 processed count matrix 已验收为 24,153 genes × 3,620 cells；肾组织 donor 为 13 IgAN 与 6 肾癌旁组织对照。R6A3A 必须先恢复或重建肾细胞注释，再进行 donor-level pseudobulk。

规则：

1. 生物学重复单位固定为 donor；
2. kidney 与 peripheral CD14 monocytes 分开；
3. 肾癌旁组织仅称 paracancer control，不能写成健康肾；
4. 首要目标只含 ZMIZ1，以及 Track A 预先通过 pQTL 门的基因；
5. tissue expression/localization 只作正交支持，不替代遗传共定位；
6. 只有首个数据集得到 donor-level 可解释信号后，才触发第二个公开 kidney/scRNA/spatial 资源复核。

## GO / STOP 门

进入论文级分析必须同时满足：

```text
PUBLIC_BYTE_LEVEL_PROVENANCE = PASS
AT_LEAST_ONE_ADDITIONAL_LOCUS_PQTL_SHARED_SIGNAL = PASS
ZMIZ1_KIDNEY_DONOR_LEVEL_LOCALIZATION = PASS_OR_INTERPRETABLE
CORE_CLAIM_REQUIRES_PERMISSION_DATA = FALSE
TARGET_SELECTION_WAS_PRE_FROZEN = TRUE
```

若 Track A 没有新增 signal-level 阳性，或 Track B 无法形成 donor-level 可解释定位：

```text
IGAN_REGULATORY_MAIN = FROZEN_ARCHIVE
NEXT = NEW_TOPIC_OPEN_DATA_BYTE_LEVEL_PREFLIGHT
```

不允许返回 full-24 immune cis-eQTL 扩展，也不允许用 REEP3 discovery-only 结果补足阳性数。

