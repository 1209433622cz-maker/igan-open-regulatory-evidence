# CMM R5A1-QA2 详细行动记录：MG replication-aware 再资格审查

**日期：2026-09-13**  
**轮次：R5A1-QA2**  
**目标：在不越过 OneK1K transfer gate 的前提下，独立复核 R5A1，检查候选优先级、异质性多重检验和独立 disease replication 是否足以支持 R5A2。**

## 1. R5A1 发布包独立 QA

对上传 `CMM_R5A1_MG_ByteLevelPreflight_2026-09-13.zip` 重新验收：

- SHA-256：`ada244a4ac800be619c6c322a4e93ad04f46b1c96dca4ac7be28bfad3b2cda01`
- ZIP entries：48
- CRC：PASS
- 包内 `checksums.sha256`：47/47 PASS
- 报告、JSON、TSV与代码均可读。

因此 R5A1 的工程完整性成立。

## 2. R5A1 科学结论保留部分

继续保留：

- 三套 MG GWAS真实字节与schema PASS；
- EOMG `<50` / LOMG `≥50`；
- 两套亚型 GWAS 对照独立，独立样本 effect-difference z test 在设计层面可用；
- chr1/2/5/18 的 lead effect 数值与 ALT 对齐可复现；
- OneK1K 与 TenK10K build 已正确分轨；
- QTL index 仅用于 screening，不等于 coloc；
- GSE227835 spot-check 只证明 detectability；
- OneK1K genotype 本地未完整，推断 HOLD。

## 3. 发现的第一项科学级问题：candidate ranking 忽略 disease replication

R5A1 把 chr5/TNIP1 排第一，主要来自：
- EOMG enrichment；
- OneK1K + TenK10K 双资源 eQTL；
- TenK10K SuSiE；
- disease lead进入 TNIP1 CS。

重新核查 Braun 2024 后发现：
- SOS1 和 TNIP1 的 EOMG discovery loci **没有在23andMe EOMG replication中复制**；
- chr18 rs7239261 在 LOMG discovery 后于独立 23andMe 数据同方向复制；
- rs7239261 combined evidence继续显著。

历史 MG 研究也重复支持 TNFRSF11A late-onset enrichment。

2026 日本 MG GWAS进一步给出 rs7239261 同方向 overall-MG association。

因此原排序受“molecular prettiness”影响过强，需要改为 disease-replication-aware 排序。

## 4. 候选重新冻结

### Primary — chr18 rs7239261 region

理由：
- strongest replication-aware disease credibility；
- late-onset历史一致性；
- Japanese cross-ancestry support；
- 同一区域存在多个合理 eGene，因此非常适合做无预设的 gene competition。

候选 effector genes至少包括：
- TNFRSF11A
- ZCCHC2
- PIGN
- PHLPP1
以及其它 TenK10K fine-mapped genes。

任何一个都不得在正式 coloc 前写成 causal effector。

### Secondary — chr5 rs6861227 region

TNIP1保留，但降级：
- QTL evidence strong；
- independent EOMG replication negative；
- ANXA6/CCDC69/GM2A/RPS14等竞争者分子证据甚至更强。

### Exploratory — chr2 rs7596255 region

- discovery Phet最小；
- 但 SOS1 replication negative；
- lead EAF≈2%，超出 OneK1K MAF>5% genotype范围；
- 必须以区域共同 common variants 判断可测性。

### Positive control — chr1 rs2476601

继续作为 shared-effect control。

## 5. 发现的第二项科学级问题：4-region Bonferroni 不能支持 genome-wide heterogeneity

R5A1先从相同的 EOMG/LOMG GWAS 选择4个非-MHC GWS区域，再对4个lead的 Phet 做 Bonferroni。

这不是错误的候选排序方法，但属于 selection-conditioned inference。它不能证明：
- 3个 genome-wide significant subtype-heterogeneous loci。

修正后的状态：

```text
chr2/chr5/chr18 =
DISCOVERY_SELECTED_SUBTYPE_HETEROGENEITY_CANDIDATES

GENOMEWIDE_HETEROGENEITY =
NOT_TESTED
```

## 6. 新增正式修复代码

`compute_mg_genomewide_subtype_heterogeneity.py`

功能：
- streaming exact merge；
- ALT effect alignment；
- independent-sample beta-difference；
- MHC默认排除；
- 全部 shared testable variants 作为多重检验分母；
- 输出 top / candidates / JSON。

QA：
- py_compile PASS；
- synthetic regression PASS；
- effect-allele flip PASS；
- known rs7239261 input复现 `Phet≈6.50e-7`。

由于本对话没有三套原始 600MB GWAS 字节，只包含 R5A1 派生结果，不能在沙箱中伪造 genome-wide scan 已运行。脚本应在用户已保存三套原始数据的 `H:\SCI2\YR1` 执行。

## 7. 新增公开 disease replication 资源

核实 NBDC：

`hum0197.v29.MG-gwas.v1`

- Unrestricted-access；
- 1,434 Japanese MG cases；
- 42,913 controls；
- 9,034,566 variants；
- ~948 MB；
- 不需 DAC/PI/邮件申请。

本轮定位到 direct ZIP URL，但沙箱下载接口失败，所以状态严格写：

```text
SOURCE_PUBLIC = PASS
LOCAL_BYTES = NOT_OBTAINED_THIS_ROUND
```

不把网页存在误写成字节已接入。

## 8. OneK1K 状态

R5A1 已记录：
- expected 233,198,074 bytes；
- MD5 `be1053e34fa023bc808388d4e0bf2aa1`；
- 当前本地缺 17,702,861 bytes；
- Zenodo 504。

本轮没有用户本机 partial chunks，因此不能在本沙箱继续拼接。继续使用已有断点续传脚本；其科学门仍然是：

`LOCAL_GENOTYPE_IDENTITY = PENDING`

## 9. 为什么现在不下载 10.3GB + 16.6GB 全量 QTL

在 candidate ordering 和 genome-wide heterogeneity 尚未重新校准时，立即拉取全部 QTL 会把大量计算/带宽投入到可能被降级的 chr5/chr2。

更高价值顺序是：

1. genome-wide heterogeneity；
2. disease replication hierarchy；
3. OneK1K genotype闭合；
4. chr18 targeted QTL；
5. 只有 chr18不成立或需要比较时再扩 chr5/chr2。

这符合“数据和方法追求完美，但不做无信息量的大计算”的原则。

## 10. 最终状态

```text
PROJECT = MG_RETAIN
OPEN_DATA_ONLY = HARD_CONSTRAINT

R5A1 = PASS_WITH_SCIENTIFIC_REQUALIFICATION
R5A1_PACKAGE = PASS

GENOMEWIDE_HETEROGENEITY = NOT_TESTED
ONEK1K_GENOTYPE_LOCAL = PENDING
JAPANESE_MG_PUBLIC_SOURCE = PASS
JAPANESE_MG_LOCAL_BYTES = PENDING

PRIMARY_LOCUS = chr18_rs7239261_region
SECONDARY = chr5_rs6861227_region
EXPLORATORY = chr2_rs7596255_region
CONTROL = chr1_rs2476601_region

R5A2_INPUT_ACQUISITION = GO_SELECTIVE
R5A2_INFERENTIAL_ANALYSIS = HOLD

NEXT_STAGE =
R5A2A_MG_REPLICATION_AWARE_GENETIC_GATE
```

## 11. 下一阶段成功标准

只有同时完成：

- all-shared genome-wide Phet calibration；
- chr18 disease replication级别冻结；
- OneK1K genotype identity PASS；
- chr18 OneK1K full regional eQTL；
- source-aware QTL LD；
- TenK10K regional independent replication；
- signal model assumptions/QC；

才进入：

`R5A2B_MG_CHR18_MECHANISTIC_PILOT`

组织单细胞仍 HOLD。

## 12. 本轮交付

- 执行摘要；
- 全基因组异质性审计；
- replication-aware重新排序；
- 日本MG公开GWAS预验收；
- R5A2A冻结目标；
- 详细行动记录；
- candidate matrix TSV；
- genome-wide heterogeneity Python；
- PowerShell orchestrator；
- 来源记录；
- checksum release ZIP。
