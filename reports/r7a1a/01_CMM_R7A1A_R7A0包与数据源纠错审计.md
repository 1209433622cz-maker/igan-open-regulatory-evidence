# R7A1A：R7A0 包与数据源纠错审计

## R7A0 输入完整性

- ZIP SHA-256：`7fa75effc486ed862eeab9b461902bd95d45464a3fd597e3e8bcac2e69069f35`
- ZIP 成员：20
- ZIP CRC：PASS
- 内部 `checksums.sha256`：19/19 PASS

R7A0 是设计/预检包，没有在本地取得 PBC/CeD 核心 GWAS 字节；其结论被视为待复核输入，不作为本轮指令。

## 纠错 1：CeD GCST90014442 不合规

GWAS Catalog API 返回的出版物标题为 `Investigating Pleiotropy Between Depression and Autoimmune Diseases Using the UK Biobank.`，病例/对照为 2,364/324,074。它虽然可以直接下载，但来源属于此前冻结排除的 UK Biobank 路线，因此 `DIRECT_DOWNLOAD` 不能覆盖 `SOURCE_INELIGIBLE`。

## 纠错 2：替代源分层

- `GCST000612`：2010 CeD genome-wide array，4,533 病例、10,750 对照；harmonised 文件含 allele/beta/SE/P，作为合格核心输入。
- `GCST010064`：2020 Immunochip meta-analysis，12,948 病例、14,826 对照；直接文件含 allele/OR/P，但无 SE，保留为正控来源与方向/敏感性审计对象，不能冒充冻结 core-coloc schema PASS。

## 纠错 3：INAVA 名称

OneK1K 使用旧符号 `C1orf106`，当前 GENCODE 使用 `INAVA`。原脚本仅按当前符号搜索，会把 PBC 的 3/3 可测性误报为 2/3。本轮加入显式、可审计别名映射后，INAVA 在 CD4_NC 中有一条 top-eQTL（q≈0.318）；因此是“可测但不显著”，并非“缺失”。

## 纠错 4：testable 与 positive 分列

原脚本用源数据显著性定义 `cross_resource_gene_support`，但冻结协议写的是 `CROSS_RESOURCE_QTL_TESTABLE_CONTROLS`。本轮同时输出：

- `cross_resource_byte_testable`：两个资源都存在该基因的可计算记录；
- `cross_resource_source_positive`：OneK q<0.05，且 TenK BH-q<0.05 或存在 SuSiE CS。

两病都是 3/3 可测；PBC 为 2/3 双资源阳性，CeD 为 1/3。

## 来源

- GWAS Catalog PBC `GCST90061440`: https://www.ebi.ac.uk/gwas/studies/GCST90061440
- GWAS Catalog CeD `GCST000612`: https://www.ebi.ac.uk/gwas/studies/GCST000612
- GWAS Catalog CeD `GCST010064`: https://www.ebi.ac.uk/gwas/studies/GCST010064
- 被排除的 UKB-derived CeD `GCST90014442`: https://www.ebi.ac.uk/gwas/studies/GCST90014442
- PBC 2021 GWMA (PMID 34033851): https://pubmed.ncbi.nlm.nih.gov/34033851/
- CeD 2010 GWAS (PMID 20190752): https://pubmed.ncbi.nlm.nih.gov/20190752/
- CeD 2020 Immunochip meta-analysis (PMID 31591516): https://pubmed.ncbi.nlm.nih.gov/31591516/
- GWAS Catalog summary-statistics access: https://www.ebi.ac.uk/gwas/labs/downloads/summary-statistics
