# CMM R4A.1：数据接入报告与待办请求草稿

日期：2026-09-08。下方所有联系文本均为草稿，本轮未发送邮件或提交任何访问申请。

## 1. 入口实测与状态变化

| 资源 | 本轮实际操作 | 当前状态 | 对主分析的影响 |
|---|---|---|---|
| 2026 SSc sex GWAS | 官方案例+PMID精确查询；新版v2 HTTP200但0 studies；2019记录控制成功 | PUBLIC_DECLARED；目标GCST及文件未取得 | male/female区域GWAS仍是硬阻塞 |
| FinnGen公开CASCADE | 4 gene、3 lead、IRF4区域JSON；rsID错误与canonical成功均留档 | BYTES_ACQUIRED；浏览器schema已实测 | 能做真实分子筛查，尚无完整nominal/fine-map release与LD输入 |
| TenK10K gene-level | 10,137,272 bytes，28份cell文件，MD5/CRC通过 | BYTES_ACQUIRED；结构解析通过 | 只用于gene级筛查，不支持方向或coloc |
| TenK10K SuSiE | 59,669,579 bytes，28份cell文件，MD5/CRC通过 | BYTES_ACQUIRED；CS结构解析通过 | 支持IRF4单变异CS检查，不能代替完整统计 |
| GCST009131 overall SSc | 获取官方研究元数据和full-summary目录链接 | MANIFEST_REFERENCE_VERIFIED；summary bytes未下载 | 仅保留备选，未进行主问题切换 |

续推进新增：IRF4 B系pmax=1区域slice已取得11,604条记录，不能再写成完全没有nominal字节；source-complete release/caQTL/LD仍缺。旧GWAS summary API及文档返回HTTP410，停止重复调用。详情见06报告。

### 网络错误不当作科学结果

旧版GWAS接口和错误版本的dbSNP API曾返回404，随后找到正确官方API；IRF4 rsID端点会错误返回empty；region端点需要chr前缀。所有失败响应保留用于定位问题。

TenK10K API整包请求曾HTTP504，改records下载后gene包成功；SuSiE整包传输停滞，停止本轮明确启动的下载进程后，用公开HTTP Range分15段取得。每段检查HTTP206、Content-Range、长度；重组后对照官方整包MD5。这个过程只解决传输，不改变数据内容。

## 2. FinnGen完整分析需要的最小文件

根据公开浏览器Data页面，发布目录包括：

- `eQTL/cis/`、`eQTL/cis_nominal/`
- `caQTL/cis/`、`caQTL/cis_nominal/`
- `eQTL/finemapping/`、`caQTL/finemapping/`
- `peak_gene_links/`（必要时nominal）
- `cascade/`、`coloc/`、`atac_peaks/`

先索取release README、cell定义、文件清单/索引，再按IRF4区域获取。已有FinnGen R12/KANTA coloc不是2026 SSc male/female GWAS的coloc，不能挪用。

官方表单需要真实姓名、机构、邮箱、国家，并包含研究使用声明。当前会话未提供这些申请信息；本轮没有代填身份或替用户承诺。现成下载说明若已在用户手中，可直接使用，无须重复申请。

入口：[FinnGen官方访问说明](https://www.finngen.fi/en/access_results)；[官方表单](https://elomake.helsinki.fi/lomakkeet/124935/lomake.html)。

## 3. GWAS Catalog求助草稿

收件人：`gwas-info@ebi.ac.uk`（[官方FAQ](https://www.ebi.ac.uk/gwas/docs/faq)）。

Subject: Locating sex-stratified systemic sclerosis summary statistics — PMID 41999721

Dear GWAS Catalog team,

We are trying to locate the male- and female-stratified GWAS summary statistics accompanying Rodriguez-Martin et al., “Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study” (PMID 41999721; DOI 10.1016/S2665-9913(25)00376-5).

The data-sharing statement points to the GWAS Catalog. On 8 September 2026, a query to the REST v2 studies endpoint with pubmed_id=41999721 returned zero studies. Could you please let us know whether accessions or a public summary-statistics download are available, or whether this submission is still being processed?

We require full regional or genome-wide results for both sexes, including genome build, alleles, effect sizes, standard errors, p-values and sample-size information. We do not need individual-level data.

Best regards,

[Name, affiliation and contact email — to be completed by the requester]

## 4. 对应作者请求草稿

收件人：从论文correspondence核实后填入，本文件不猜测邮箱。

Subject: Request for public male/female SSc GWAS results and a table clarification

Dear authors,

We are planning a cell-resolved molecular-QTL analysis of the SSc susceptibility loci reported in your 2026 study (PMID 41999721). We have not yet located its male/female summary-statistics accessions in the GWAS Catalog.

Could you please provide the public download links or accessions, including build and effect-allele definitions, and any available ancestry-matched LD or signal-level fine-mapping resources? If the genome-wide release is pending, complete regional results for rs12203592, rs2540100 and rs66578187 in both sexes would enable an initial technical assessment. For rs2540100, we need to account for the extended region toward BCL11A, rather than a short lead-centered window.

We also noticed that the IRF4 between-sex heterogeneity p-value is reported as 0.0009 in the Results text and 0.0090 in Table 2. Could you clarify which is correct?

We will cite the source study and follow the applicable data-use terms. We are requesting summary statistics only.

Best regards,

[Name, affiliation and contact email — to be completed by the requester]

## 5. 下一轮最小输入清单

优先提供male/female GWAS下载链接或完整区域文件，以及FinnGen下载说明/README。三lead表格、LocusZoom截图和已发表候选基因表不满足区域统计输入要求。

本轮已经取得的两个TenK10K ZIP不需要再次下载。只有IRF4逐变异方向或BCL11A远端窗口确实需要时，再规划更大区域资源。
