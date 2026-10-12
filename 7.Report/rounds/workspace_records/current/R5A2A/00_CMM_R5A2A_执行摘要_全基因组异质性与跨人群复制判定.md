# CMM R5A2A 执行摘要：全基因组异质性与跨人群复制判定

日期：2026-09-14  
项目：Myasthenia Gravis（EOMG vs LOMG）  
最终状态：`MG_MAIN = CONDITIONAL_GO`；`R5A2A1_CHR18_INPUT_ACQUISITION = GO`；`SIGNAL_LEVEL_INFERENCE = HOLD`

## 本轮最终判定

R5A1-QA2 对候选排序的纠偏成立，但本轮独立计算进一步收紧了论文表述。chr18 / rs7239261 被正式冻结为首个机制验证区域；它的优先级来自欧洲总体 MG 的 23andMe 复制、日本 MG 的同一变异复制和既往 LOMG 区域证据，不来自全基因组显著的 EOMG–LOMG 异质性。

对 EOMG 与 LOMG 两套 harmonised GWAS 的 5,231,937 个非 MHC、REF/ALT 完全一致的共享变异进行全基因组效应差异检验后，Bonferroni 阈值为 `9.55668999836963e-09`，通过变异数为 0。rs7596255 的 Phet=`3.6732e-08`，虽低于传统 `5e-8`，但对本次实际检验数校正后 P=`0.1922`，不得称为全基因组显著异质性位点。

日本 NBDC `hum0197.v29.MG-gwas.v1` 已完成真实字节级接入：

- 229,751,515-byte ZIP，SHA-256 `2b93e8832b1fd6f13dbe66f60373da544bcff72bd9b8a716e4f60a2cb6b6b67f`；
- ZIP CRC、唯一数据成员、官方字典、header、9,034,566 行和字段范围全部通过；
- rs7239261：GRCh37 `18:60005046:A:C`，C 为效应等位基因，β=-0.129494，SE=0.0428419，P=0.001253072，方向与欧洲 LOMG 一致；
- rs6861227：G 为效应等位基因，β=-0.0662169，P=0.2840654，与欧洲 EOMG 方向不一致且不显著；
- rs7596255 与 rs2476601 在官方过滤后的日本文件中不存在，记为 `NOT_PRESENT_AFTER_PUBLIC_SOURCE_FILTERS`，不能记为阴性复制。

OneK1K genotype 的续传也已完成：233,198,074 bytes、官方 MD5 完全一致、ZIP CRC 通过；真实 PLINK 数据为 980 donors、5,326,925 variants、GRCh37。rs2476601、rs6861227 和 rs7239261 精确存在，低频 rs7596255 不在 MAF>5% 的公共面板中。原审计脚本把 `__MACOSX/._*` 资源分支误判为第二套 PLINK 文件，本轮已修正并复跑通过。

## 冻结排序

| 排名 | 区域 | 角色 | 当前证据边界 |
|---:|---|---|---|
| 1 | chr18 / rs7239261 | 主机制验证 | 独立疾病复制最完整；候选基因保持 TNFRSF11A/PIGN/ZCCHC2 有界竞争 |
| 2 | chr5 / rs6861227 | 次级分子验证 | EOMG discovery 与分子 QTL 较强，但 EOMG 特异复制和日本复制不支持 |
| 3 | chr2 / rs7596255 | 低频探索位点 | nominal Phet 最低，但全检验校正不通过、疾病复制失败、OneK1K lead 缺失 |
| 4 | chr1 / rs2476601 | 共享效应正控 | EOMG 与 LOMG 效应一致，保留用于验证流程正确性 |

chr8:138.298 Mb 是本轮全基因组扫描中第二个较强的距离簇，但目前没有独立疾病复制，继续留在探索观察表，不进入主机制链。

## 下一阶段

下一阶段冻结为 `R5A2A1_MG_CHR18_INPUT_CLOSURE`：先下载并验收 OneK1K 全量 raw cis-eQTL，再只提取 chr18 主区域、用 980-donor source genotype 构建实际共享变异 LD，并运行信号级共定位。TenK10K 16.56 GB 全量文件采用顺序门控：只有 OneK1K 首轮为 `PASS` 或可解决的 `HOLD_TESTABLE` 时才下载。

当前允许的论文措辞是：`replication-supported, LOMG-enriched chr18 locus prioritized for regulatory resolution`。不得称其为全基因组显著的亚型异质性位点，也不得提前把效应基因指定为 TNFRSF11A。
