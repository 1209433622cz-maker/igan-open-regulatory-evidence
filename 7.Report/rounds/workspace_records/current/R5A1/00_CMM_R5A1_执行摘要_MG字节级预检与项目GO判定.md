# CMM R5A1 执行摘要：MG 字节级预检与项目 GO 判定

日期：2026-09-13  
项目：Myasthenia gravis（MG）EOMG vs LOMG 亚型异质性调控遗传学  
本轮结论：`CONDITIONAL GO — TRANSFER PENDING`

## 正式判定

SSc sex-specific 主论文已按 R5A0 决议冻结为归档项目与方法工程资产库。本轮没有继续补救 SSc，也没有把旧项目的 SYNGR1 或 IL12RB2 预设带入 MG。

MG 通过了疾病 GWAS、亚型异质性、非 MHC 位点数、双 QTL 资源筛查和公开组织可检测性门。当前仅 OneK1K 980 donors genotype 的本地完整字节验收因 Zenodo 持续 504 未完成。因此：

```text
R5A2_INPUT_ACQUISITION = GO
R5A2_INFERENTIAL_ANALYSIS = HOLD
MANUSCRIPT_SCALE_ANALYSIS = HOLD
IgAN_FALLBACK = NOT_TRIGGERED
```

## 冻结门控结果

| 门 | 结果 | 证据 |
|---|---|---|
| 三套 MG GWAS 实际字节 | PASS | 3 个 gzip 共 20,810,370 行，字段、数值、坐标、等位基因和流完整性通过 |
| EOMG–LOMG 异质性模式 | PASS | 论文定义和对照独立性支持独立样本 z 检验；ALT-aligned log(OR) 可计算 |
| 非 MHC 可测区域 ≥2 | PASS | 4 个描述性 GWS 区域；3 个异质性检验经 4 区域 Bonferroni 后通过 |
| OneK1K eQTL 可测性 | PASS（筛查级） | 14 细胞 top cis-eQTL 实际字节通过；GRCh37 build 已纠正 |
| TenK10K 独立复制可测性 | PASS（筛查级） | 28 细胞 gene-level 与 SuSiE 实际字节通过；GRCh38 |
| OneK1K source-aware LD | SOURCE PASS / LOCAL PENDING | 公共 PLINK 980 donors、MAF>0.05、233,198,074 bytes、MD5 已确认；本地仅余 17,702,861 bytes，源端 504 |
| 公开 MG 组织中候选基因可检测 | PASS | GSE227835 一例 AChR+ MG 与一例健康对照实矩阵均检测到 TNIP1 及全部 15 个候选基因 |
| 核心结论依赖受限数据 | PASS | 不依赖 EGA、dbGaP、UKB、作者请求或 Green Library |

## 三个待验证主区域

1. **chr5 / rs6861227 / TNIP1**：EOMG 明显强于 LOMG；TNIP1 在 OneK1K 与 TenK10K 均有显著 cell-eQTL，TenK10K 中疾病 lead 位于 B-naive TNIP1 credible set。它是 R5A2 的第一证伪对象。
2. **chr2 / rs7596255**：EOMG 与 LOMG 在同一 ALT allele 上方向翻转，且 EAF 接近；必须在 SOS1、DHX57、GALM、SRSF7 间做区域信号和基因竞争。
3. **chr18 / rs7239261**：LOMG 强、EOMG 近零；比较 TNFRSF11A、PIGN、ZCCHC2。

chr1 / rs2476601 的 EOMG 与 LOMG 效应一致，用作共享效应正控。

上述均为**筛查级候选**。top-eQTL、SuSiE credible-set 共现和单细胞表达可检测不能替代 disease–eQTL 共定位，也不能支持因果或中介表述。

## 下一阶段

下一阶段冻结为 `R5A2_MG_BOUNDED_THREE_LOCUS_PILOT`。先完成 OneK1K genotype、OneK1K 全量 cis-eQTL、TenK10K 全量 ±100 kb cis-eQTL 的断点续传与 checksum；随后只分析 chr5、chr2、chr18 三个区域，chr1 作正控。OneK1K genotype 仅含 MAF>0.05 变异，低频 rs7596255 是否缺失必须如实报告并以区域共同变异覆盖裁定。只有 source-aware LD、区域 harmonization、共定位、独立复制和敏感性分析通过，才进入组织机制验证。

运行入口：`2_code/06_intake/mg_r5a2/RUN_R5A1_TRANSFER_AND_R5A2_LARGE_INPUTS.ps1`。
