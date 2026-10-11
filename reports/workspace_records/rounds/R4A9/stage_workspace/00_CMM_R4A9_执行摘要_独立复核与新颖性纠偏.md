# CMM R4A9 执行摘要：独立复核、正式附件审计与新颖性纠偏

日期：2026-09-10 至 2026-09-11（Asia/Hong_Kong）

## 最终判定

> **PROJECT = CONDITIONAL GO**  
> **R4B = HOLD**  
> **R4A8B reference / dosage / signed-LD engineering = PASS（已独立复现）**  
> **2019 overall SSc RSS branch = HOLD（结果已独立复现）**  
> **2026 female/male summary-statistics access = HOLD**  
> **Published female-SSc↔SYNGR1 eQTL evidence = SUPPORTIVE, NOT INDEPENDENTLY REPRODUCED**  
> **Our disease↔caQTL and molecular signal-level coloc = NOT_TESTED**  
> **C1_count = null**

本轮完成了此前中断的 reference/LD 工程闭环，但同时发现一个必须立即修正论文定位的事实：2026 SSc 原论文官方补充表已经报告 female SSc 与 **SYNGR1** eQTL 的高后验共定位，whole blood 为 `0.977`、EBV-transformed lymphocytes 为 `0.980`，男性分别只有 `0.025` 和 `0.033`。因此不能再把“首次发现 SYNGR1”或“首次把 RPL3–PDGFB 位点重分配到 SYNGR1”作为新论文主创新。[PMC 正文与官方补充入口](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/)

## 本轮完成的工程闭环

1. `R4A8B_IGSR` 的完整 chr1 1000 Genomes Phase 3 v5a VCF 为 `1,216,886,729` bytes，MD5 `609b38c12de89175b3d85c1588e4905c`，与 [Zenodo 3359882](https://zenodo.org/records/3359882) 公布值完全一致。原始 TBI 的 MD5 也完全一致。
2. 2,504 人 panel 中的 503 名 EUR 样本与 `EUR.samples`、FAM、区域 VCF 的样本及顺序完全一致；区域 VCF 的 27,067 个双等位 SNP 与五列表型 manifest 逐行完全一致。
3. 用 PLINK2 重新导出全部 1,555 个保留变异的 GWAS-A1 剂量，并直接从区域 VCF 的 GT 字段独立解码同一 `503 × 1555` 矩阵。区域 VCF→PLINK BED 与 PLINK2→原自写 BED 解码器均逐单元完全相同，最大绝对差均为 `0`。
4. 以 PLINK2 剂量独立计算相关矩阵，与冻结 signed-LD 的最大绝对差为 `6.99×10^-15`；rs3790566/rs3790567 的 `r=0.994613984367`、`r²=0.989256977898`。该 PASS 覆盖源文件 provenance、区域 manifest 与 1,555 个保留变异的 VCF→BED→A1 dosage→LD 路径；本轮没有从完整 chr1 VCF 重新派生全部 27,067 个区域基因型。
5. R/susieR 独立复算得到 `estimate_s=0.1917849224`、最大绝对标准化 kriging residual `5.361425644`，再次违反预冻结门槛 `s≤0.1` 且 residual `≤5`。因此 SuSiE-RSS 继续 `NOT_RUN`。这说明原 HOLD 是数据协方差兼容性问题，不是 BED 解码、样本选择或 LD 方向错误。

## 数据入口核查

截至本轮最近一次自动复核（精确 UTC 时间记录于 `research/ssc_access_api_summary.json`）：

- GWAS Catalog v2 按 PMID `41999721` 查询 publication、study 和 `full_pvalue_set=true` 均为 HTTP 200、`totalElements=0`；旧 API 同样为空。
- 阳性对照 `GCST009131` 返回正常；按 disease trait 查询的 full summary 只有 2019 overall SSc 数据。
- Europe PMC 官方 supplementary ZIP 只有 `mmc1.pdf` 与正文图片，没有 TSV、CSV、XLSX、VCF、GWAS-SSF 或其他全基因组逐变异统计文件。
- 原论文的数据共享声明仍明确称 sex-specific meta-GWAS summary statistics 将通过 GWAS Catalog 提供；当前状态应解释为发布或编目尚未完成，不能解释为阴性。

## 新颖性纠偏后的可发表命题

原论文已做到的是：

`female SSc GWAS → GTEx whole blood / EBV lymphocyte SYNGR1 eQTL colocalization`

本项目已经新增但仍属描述性或分子层证据的是：

`exact disease lead rs66578187 → immune-cell SYNGR1 eQTL + intragenic-peak caQTL → source peak→SYNGR1 link → TenK10K/FinnGen exact-CS overlap`

真正尚未被证明、也最能形成新论文增量的是：

`female SSc signal → specific immune-cell caQTL → peak → SYNGR1 expression signal`

因此主命题改为：**在具体免疫细胞中，用染色质开放性和表达 QTL 的多信号、跨资源证据，机制化解析并独立验证原论文已经提出的 female-SSc–SYNGR1 共定位。** 论文不得使用 “first discovery of SYNGR1” 或 “reassignment from RPL3–PDGFB to SYNGR1”。

## 下一阶段：R4A10 / H6

下一阶段冻结为 **Sex-specific SSc Intake and Extension-only Gate**：

1. 取得 female 和 male 完整 summary statistics；先运行本轮已生成的流式 H6 intake 脚本，验证 checksum、build、效应等位基因、SE、EAF、INFO、样本设计和目标区域覆盖。
2. 先复现原论文的 GTEx whole-blood/EBV-lymphocyte SYNGR1 共定位，作为可重复性正控；原补充材料没有公开 priors 和逐变异输入，因此结果需分为精确复现、方向一致或不可复现。
3. 只在 LD/RSS 兼容性通过时运行多信号分析。首要新增检验是 female disease↔NK caQTL；随后检验 disease↔SYNGR1 eQTL 和 caQTL↔eQTL coherence。male 作为预先定义的性别对照。
4. SYNGR1 是主候选；RPL3、PDGFB 与源链接基因保留为匹配覆盖下的有界竞争集合。IRF4 是第二位点，不在 chr22 结果明确前扩展 all-8 或组织验证。
5. 若数据仍未公开，保持 `HOLD_EXTERNAL_ACCESS`；不再用 2019 overall 文件制造 sex-specific 结果，也不把高覆盖子集筛选包装成主要 fine-mapping。

本轮详细证据、行动记录、H6 脚本及运行说明均在 R4A9 目录中。
