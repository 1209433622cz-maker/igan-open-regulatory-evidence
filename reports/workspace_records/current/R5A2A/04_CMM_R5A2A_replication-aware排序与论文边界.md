# CMM R5A2A：replication-aware 排序与论文边界

## 排序原则

排序不再由单一 Phet、最近基因或 top-eQTL 决定，而按以下证据层级评估：

1. 独立疾病 GWAS 是否复制同一变异或同一区域；
2. 亚型 discovery 是否清晰，且异质性强度是否经全检验校正；
3. OneK1K/TenK10K 是否提供可检验的 cell–gene 信号；
4. source genotype、build、lead/credible-set coverage 是否支持信号级分析；
5. 是否能在公开 MG 组织数据中做后续疾病状态定位。

## Rank 1：chr18 / rs7239261

- 欧洲 overall MG：ALT C β=-0.1944，P=3.981e-20；
- EOMG：C β=0.0307，P=0.5184；LOMG：C β=-0.2591，P=1.561e-14；
- Phet=6.4971e-7，未通过全共享 Bonferroni；
- 23andMe overall MG：换算到 ALT C 后 β=-0.07623，P=4.43e-4；
- 日本 MG：ALT C β=-0.129494，P=0.001253，方向一致；
- OneK1K genotype 精确包含该 lead；历史研究也支持 TNFRSF11A 区域偏向 late-onset MG。

因此它是“复制支持的 LOMG 富集疾病位点”，适合作为首个 regulatory resolution pilot。效应基因仍需在 TNFRSF11A、PIGN、ZCCHC2 和实际区域 eQTL 基因间竞争。

## Rank 2：chr5 / rs6861227

该位点的 EOMG discovery 很强，OneK1K/TenK10K 筛查显示多个可检验的分子 QTL。Braun overall MG replication 为 nominal positive；但论文明确指出 EOMG/TNIP1 信号未在 EOMG replication 中复制，日本总体 MG 同一变异也不支持。因此它适合作为 chr18 失败后的次级分子验证，不再是默认主位点。

## Rank 3：chr2 / rs7596255

这是 nominal Phet 最低位点，但它没有通过对 5,231,937 个实际共享变异的 Bonferroni 校正，EOMG/SOS1 信号未在 23andMe 复制，且约 2% 的 lead 不在 OneK1K MAF>5% genotype 中。它只能作为低频、外部 LD 受限的探索位点。

## 正控与观察表

- chr1 / rs2476601：亚型效应一致，作为共享 MG 风险和流程正控；
- chr8:138.298 Mb：本轮出现方向相反的 nominal 候选簇，但没有独立疾病复制，只保留在 watchlist。

## 论文可以与不可以声称的内容

当前可以声称：三套公开 MG GWAS 支持强烈亚型效应差异结构；chr18 位点获得欧洲与日本疾病复制，并优先进入公开免疫 QTL 信号解析。

当前不能声称：

- 存在全基因组显著的 EOMG–LOMG heterogeneity variant；
- rs7239261 已与某个 eQTL 共定位；
- TNFRSF11A 已被确定为效应基因；
- 23andMe 或日本总体 MG 构成 LOMG-specific replication；
- lead-eQTL 共现或表达可检测等价于因果调控链。
