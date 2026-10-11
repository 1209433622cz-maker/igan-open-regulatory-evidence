# CMM R4A12FG5 执行摘要：External-LD Gate + Three-cell Replication Adjudication

日期：2026-09-13

## 最终判定

- 总项目：`CONDITIONAL_GO`
- 正式 R4B：`HOLD`
- `C1_count = null`
- 2026 female/male SSc 主数据：`NOT_OBTAINED`
- IL12RB2 all-sex 分支：**`SUMMARY_ONLY`**
- External-LD：**`FAIL_INPUT_COVERAGE_FOR_MULTISIGNAL`**
- 三细胞复核：**`PARTIAL_SOURCE_SUMMARY_ONLY`**
- 不触发 `STOP_IL12RB2_ALLSEX_BRANCH`
- 不升级 `SECONDARY_SIGNAL_SUPPORTED`

本轮严格按 FG4 预注册范围，仅检查 archived EUR503 LD 与 `CD8_TEM / CD4_CTL / CD4_TCM`。未换细胞、未扩大到 1 Mb、未启动 caQTL。

## 1. FG4 输入完整性

用户上传的 R4A12FG4 release：
- ZIP SHA-256：`f2f500cae52b83a77bba55f9d1455d9eabad1c63f1320833716494c8f818ab53`
- ZIP CRC：PASS
- `checksums.sha256`：45/45 PASS
- FG4 冻结状态复现：`SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED`

## 2. Track A：External-LD 严格门

当前可复核 archive 中可直接取得的是 R4A8B/R4A9 保存的 **503×1,555** EUR503 工程剂量矩阵；它是旧 GCST009131 harmonization 后的保留子集，**不是**原 27,067-variant full regional reference。

FG4 R13 disease↔NK exact harmonized variants共 891 个，其中只有 **329/891（36.92%）** 能映射到 archived 1,555-variant LD 子集。

更关键：
- NK source CS1：archived subset **0 members / 0 PIP mass**
- NK source CS2：archived subset **0 members / 0 PIP mass**
- NK QTL top `rs17129789`：缺失
- FinnGen regional lead `rs1954118`：缺失
- `rs6662198`：保留

因此 external-LD multi-signal gate **硬失败**。这不是“1000G EUR503 被科学否定”，而是**当前归档的旧工程子集覆盖不足**。

数值上329×329子矩阵本身对称且数值PSD，但疾病z–LD诊断仍有最大标准化残差>5；数值健康不能弥补signal coverage为0的source-CS缺口。

## 3. Track B：预注册三细胞

source-level证据仍支持继续验证，而不是停止分支：

| Cell | gene ACAT P | QTL top | R13 top-marker disease P | source CS |
|---|---:|---|---:|---:|
| CD8_TEM | 5.17e-17 | 1:67326053:A:C | 9.25e-4 | 2 |
| CD4_CTL | 9.77e-15 | 1:67327248:G:A | 1.39e-3 | 1 |
| CD4_TCM | 3.05e-14 | 1:67332644:T:G | 1.38e-3 | 2 |

各细胞source CS中已有大量variant能在FinnGen R13疾病区域精确匹配；例如CD4_TCM CS1为13/13完整疾病覆盖。但当前上传包不包含这三种细胞的完整per-variant beta/SE文件，因此本轮没有伪造新的 `coloc.abf`。

更重要的是，现有 archived EUR503 LD 子集对这些secondary CS同样极不完整：CD8_TEM CS1、CD4_CTL CS1、CD4_TCM CS1均无成员进入该LD子集。即使先取得三细胞beta/SE，也不能基于当前329-variant LD子集做paper-grade multi-signal判定。

## 4. Source-matched LD 状态

本轮公开源复核显示：
- TenK10K Zenodo公开的是eQTL summary、SuSiE CS、coloc等aggregate结果；在已检查的公开文件列表中未见per-gene source correlation/LD matrix。
- TenK10K 1,925人的WGS genotype位于 EGA `EGAS50000001654`，其中SNP/indel multi-sample VCF dataset为 `EGAD50000002377`，属于受控访问。
- 因此source-matched TenK10K LD仍不是当前公开本地字节。

## 5. 当前科学解释

FG4的prior-sensitive `coloc.abf`仍只能作为single-causal sensitivity：
- `p12=1e-5` 时 H4≈0.83–0.85；
- `p12=1e-6` 时降至≈0.33–0.36。

FG5没有产生足以升级或推翻该结论的新signal-level证据。external-LD输入覆盖失败，因此本轮正式分类为：

> **`SUMMARY_ONLY_EXTERNAL_LD_INPUT_INCOMPLETE`**

不是 shared，不是 distinct，也不是 biological negative。

## 6. 下一阶段

冻结为：

> **R4A12FG6 — Full EUR503 Reference Completion + Three-cell Full-summary Intake Gate**

先在用户本地已有的27,067-variant EUR503 regional PLINK reference上重建当前891个variant的signed LD，再选择性取得三种secondary cell的完整TenK10K 100-kb eQTL成员。只有full-reference LD通过预冻结覆盖/CS/anchor门，才允许LD-aware multi-signal分析。

2026 female/male chr22/SYNGR1主线仍具有更高优先级；本轮实时GWAS Catalog接口对 PMID 41999721 仍返回 `totalElements=0`。
