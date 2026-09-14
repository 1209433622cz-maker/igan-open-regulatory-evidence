# R7A0 冻结协议：Open-data completion-first portfolio preflight

日期：2026-09-15

## 1. 触发原因

SSc sex-specific、MG regulatory-main 与 IgAN regulatory-main 均已在各自预冻结门控下停止。R7A0 不继续补救这些旧主线，也不先认定一个新疾病，而是比较三个可完成性候选：

1. celiac disease（CeD）；
2. primary biliary cholangitis（PBC）；
3. alopecia areata（AA）。

选择标准按用户的真实目标排序：真实阳性证据密度、公开数据闭环、能够完整写完，其后才是冲击一区的新颖性。

## 2. 硬约束

```text
OPEN_DATA_ONLY = TRUE
PERMISSION_REQUIRED_DATA = EXCLUDED
AUTHOR_REQUEST_DATA = EXCLUDED
EGA_DBGap_UKB_GREEN_LIBRARY = EXCLUDED
CORE_CLAIM_REQUIRES_PUBLIC_BYTES = TRUE
```

公开网页或论文声称“available”不算通过。必须得到可下载对象、真实字节、SHA-256、build、alleles、beta/SE/P 与样本定义。

## 3. 两级筛选

### Gate 0：元数据与小字节

每个候选先回答：

- 是否存在至少一套直接公开、含完整 effect allele、other allele、beta/OR、SE 和 P 的 GWAS；
- 是否有至少 5 个非 MHC 独立信号，避免再次陷入单一位点主线；
- OneK1K 与 TenK10K 是否能在同一组预定义位点上形成跨资源可测试集合；
- 是否有带供体标签的疾病组织单细胞或空间数据，且病例与合适对照可分离；
- 2024–2026 年是否已有同构的“GWAS + single-cell QTL + tissue validation”论文。

Gate 0 只下载 metadata、index、manifest、credible-set 或小型结果文件。单个大于 1 GB 的文件在候选通过前不得下载。

### Gate 1：真实字节与阳性证据预检

Gate 0 排名前两位的候选才进入真实字节检查。每个候选只运行 2–3 个预注册正控 locus：

- 疾病 GWAS 区域信号充分；
- 分子 QTL source-significant；
- 至少一个独立资源可复制；
- 组织数据中目标 gene/cell 可检测；
- 不允许先看全结果再选择正控。

## 4. GO 门

新主项目必须同时满足：

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

如三项都不通过，不把门槛改低。下一轮改为重选研究范式，而不是继续同一套 immune cis-eQTL 共定位框架。

## 5. R7A0 交付

- 三候选公开入口与真实可下载对象矩阵；
- 小文件 byte receipt 与 SHA-256；
- 每项非 MHC 信号数与 QTL 可测试性；
- 同构论文 hostile audit；
- 排名前两项的最小真实字节执行脚本；
- 单一主项目 GO/HOLD/FAIL 判定，或全体 FAIL。

