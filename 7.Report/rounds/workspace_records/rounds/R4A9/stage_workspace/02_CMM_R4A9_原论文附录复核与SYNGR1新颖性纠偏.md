# CMM R4A9：原论文官方附录复核与 SYNGR1 新颖性纠偏

日期：2026-09-10

## 1. 为什么必须纠偏

此前项目根据正文对新女性位点的 “RPL3–PDGFB” 区域标签，提出用 immune multiome 重新解析 SYNGR1 的设想。该方向的分子证据仍然有价值，但本轮完整核查官方 supplementary appendix 后发现：**原作者已经用 female/male SSc GWAS 与 GTEx v8 做过 COLOC，并在 chr22 只报告了 SYNGR1 的高后验结果。**

因此，SYNGR1 不是本项目首次提出的疾病效应基因候选。

## 2. 官方附件完整性

[PMC 正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/) 的 XML 只声明一个 supplementary material：`mmc1.pdf`。可程序化下载的 [Europe PMC supplementaryFiles endpoint](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13212417/supplementaryFiles) 返回一个 ZIP：

- ZIP：2,913,245 bytes；SHA-256 `c185025867430a7fe3c00f77bba04d32caa0366cf016c658415339b00e480180`。
- `mmc1.pdf`：2,266,646 bytes；25 页。
- PDF MD5：`836f0099cf7a550df903079f6b269c0f`，与 PMC XML 内嵌 MD5 完全一致。
- PDF SHA-256：`d11aa2a4c770412bdad11332300061572665126d0f749249aba0fa735472f7ed`。
- ZIP 其余条目均为正文图 JPG/GIF；没有逐变异 summary-statistics 文件。

## 3. Supplementary Table 2 的直接证据

表位于 PDF 物理第 15 页、附录印刷页码第 14 页。表题说明：只列至少一个性别 `PP>0.8` 的 gene–tissue pair。

| CHR | Gene | Tissue | PP females | PP males |
|---:|---|---|---:|---:|
| 22 | SYNGR1 | Whole blood | 0.977 | 0.025 |
| 22 | SYNGR1 | Lymphocytes | 0.980 | 0.033 |

附录方法说明：作者将 sex-stratified meta-GWAS 与 GTEx v8 在 lead variant 上下游各 500 kb 的窗口中输入 COLOC，分别计算 female 和 male；表中的 “Lymphocytes” 对应 GTEx `Cells_EBV-transformed_lymphocytes`。

附录未提供：

- COLOC priors；
- 每个区域实际进入分析的变异列表；
- GWAS 与 GTEx allele harmonization 记录；
- beta、SE、EAF、INFO、per-variant N；
- PP 的可重算中间输出。

所以这些数值是**已发表支持证据**，但当前无法独立复现。

## 4. 原论文还已做到什么

原论文候选基因图表已经把 SYNGR1 列入 chr22 位点，V2G score 为 `0.20`，并标注 blood、immune-cell 与 skin eQTL 证据。正文更强调 RPL3 的邻近位置与 PDGFB 的纤维化/药理背景，但这不能被转述为“原文完全没有考虑 SYNGR1”。

原论文可被准确概括为：

> chr22 位点在正文中按 RPL3–PDGFB 命名，但其候选基因与 COLOC 补充分析已经支持 SYNGR1，且支持主要来自女性 GWAS。

## 5. 本项目真正新增的层级

当前项目的增量不在 gene name，而在证据分辨率与机制层：

1. **具体免疫细胞。** rs66578187 在 FinnGen l2.NK 对 SYNGR1 的 eQTL p=`9.9831×10^-110`，在 l2.CD8_TEM 为 `4.7553×10^-83`；原论文只报告宽泛 whole blood 与 EBV lymphocytes。
2. **染色质层。** 同一 rs66578187 对 `chr22:39351520–39352777` peak 是极强 caQTL，l2.NK p=`4.1304×10^-178`，l2.CD8_TEM p=`5.3238×10^-179`。
3. **peak→gene。** 来源模型给出该 peak 到 SYNGR1 的关联；该 peak 位于 SYNGR1 基因内部，但 link 与物理位置都不能单独证明因果方向。
4. **跨资源 exact-CS overlap。** TenK10K NK/SYNGR1 eQTL CS 与 FinnGen NK caQTL CS 在 `22:39351666:T:A`、`22:39351775:G:A` 精确重叠。完整 FinnGen l2.NK caQTL CS 有 3 个成员，两个重叠成员的概率质量合计 `0.2529041`，所以只能称 exact overlap，不能称两个 CS 相同或正式共定位。

## 6. 允许与禁止的主张

仅在完整 disease signal-level C1 通过后可以写：

> We resolve the published female-SSc–SYNGR1 colocalization at immune-cell resolution by integrating chromatin accessibility, expression QTLs, peak-to-gene links, and cross-resource fine-mapping evidence.

在 disease summary 未取得前，必须把 “resolve” 写成计划性或条件性措辞，例如 “we test whether … can be resolved”。

不能写：

- first discovery of SYNGR1 at the locus；
- first assignment/reassignment of the locus to SYNGR1；
- the original study considered only RPL3/PDGFB；
- NK mediation has been demonstrated；
- a complete regulatory cascade has been established。

## 7. 新颖性最终评价

“SYNGR1 作为效应基因”本身的新颖性已经被原论文占据。**具体免疫细胞中的 disease→chromatin→expression 多层信号一致性**仍是清楚、可证伪且有发表价值的增量，但它必须依赖：

- female/male disease summary 的独立复现；
- disease↔caQTL 新共定位；
- eQTL↔caQTL 的完整信号级 coherence；
- 跨细胞与候选基因竞争；
- priors、LD、覆盖与多信号敏感性分析。

完整 claim 边界见 `results/R4A9_claim_boundary_matrix.tsv`。
