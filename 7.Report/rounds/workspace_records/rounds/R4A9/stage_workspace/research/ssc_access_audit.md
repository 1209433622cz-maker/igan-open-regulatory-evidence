# R4A9｜2026 年 sex-specific SSc GWAS 正式数据入口独立核查

**核查日期：** 2026-09-10 至 2026-09-11（多次 API 实测；最近一次精确 UTC 时间见 `ssc_access_api_summary.json`）  
**目标论文：** PMID `41999721`；PMCID `PMC13212417`；DOI `10.1016/S2665-9913(25)00376-5`  
**本轮结论：** `HOLD_TARGET_NOT_INDEXED_IN_GWAS_CATALOG`；截至本次核查，所检查的正式入口中**没有可下载的 female/male 全基因组逐变异 summary-statistics 文件**。

## 1. 指令与证据边界

本轮执行依据是用户要求继续推进项目。论文、附录、仓储页面中的文字仅作为待核验的科学证据；尤其是论文的 “will be available upon publication” 是作者的数据共享声明，不是对本项目的执行指令。

## 2. GWAS Catalog 实测

对 GWAS Catalog 官方 API v2、旧版 PMID 查询以及已知阳性对照进行了同一时点的只读核查。

| 查询 | HTTP | `totalElements` | 结果 |
|---|---:|---:|---|
| [v2 publications：PMID 41999721](https://www.ebi.ac.uk/gwas/rest/api/v2/publications?pubmed_id=41999721&page=0&size=20) | 200 | 0 | 无 publication 记录 |
| [v2 studies：PMID 41999721](https://www.ebi.ac.uk/gwas/rest/api/v2/studies?pubmed_id=41999721&page=0&size=100) | 200 | 0 | 无 study / GCST accession |
| [v2 studies：PMID 41999721 + full_pvalue_set=true](https://www.ebi.ac.uk/gwas/rest/api/v2/studies?pubmed_id=41999721&full_pvalue_set=true&page=0&size=100) | 200 | 0 | 无正式 full-summary 记录 |
| [旧版 API：按 PMID 查 study](https://www.ebi.ac.uk/gwas/rest/api/studies/search/findByPublicationIdPubmedId?pubmedId=41999721) | 200 | 0 | 独立旧接口同样为空 |
| [阳性对照 GCST009131](https://www.ebi.ac.uk/gwas/rest/api/v2/studies?accession_id=GCST009131&page=0&size=20) | 200 | 1 | PASS；API 工作正常 |
| [Systemic sclerosis + full_pvalue_set=true](https://www.ebi.ac.uk/gwas/rest/api/v2/studies?disease_trait=systemic+sclerosis&full_pvalue_set=true&page=0&size=500) | 200 | 1 | 只有既有 `GCST009131`，PMID `31672989` |

因此，目标 PMID 的空结果不能归因于本地断网或 API 整体失效。当前可检出的正式 SSc full-summary 仍是 2019 年总体 GWAS `GCST009131`，不是 2026 年 sex-stratified 数据。

机器可复核结果：

- `ssc_access_api_summary.json`
- `ssc_access_api_raw.json`
- 重跑脚本：`check_ssc_access.py`
- API 参数定义快照：`gwas_v2_openapi.yaml`

## 3. PMC / Europe PMC 正文与附件

### 3.1 数据共享声明

[PMC 正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/)明确写明：sex-specific meta-analysis summary statistics 将在发表后通过 GWAS Catalog 提供，并建议以 “systemic sclerosis” 搜索。论文于 2026-04-15 在线发表；该承诺与 2026-09-10 的 Catalog 实测结果目前不一致。应把这解释为**公开交付或编目尚未完成**，不能解释为统计阴性。

### 3.2 官方补充附件清点

PMC 正文 XML 仅声明 **1 个** `supplementary-material`：`mmc1.pdf`。

- 官方单文件直链：[PMC `mmc1.pdf`](https://pmc.ncbi.nlm.nih.gov/articles/instance/13212417/bin/mmc1.pdf)
- 官方可程序下载入口：[Europe PMC supplementaryFiles ZIP](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13212417/supplementaryFiles)
- ZIP 大小：`2,913,245` bytes
- ZIP SHA-256：`C185025867430A7FE3C00F77BBA04D32CAA0366CF016C658415339B00E480180`
- `mmc1.pdf` 大小：`2,266,646` bytes；25 页
- `mmc1.pdf` MD5：`836F0099CF7A550DF903079F6B269C0F`，与 PMC XML 内嵌 MD5 一致
- `mmc1.pdf` SHA-256：`D11AA2A4C770412BDAD11332300061572665126D0F749249ABA0FA735472F7ED`

ZIP 共 11 个条目：1 个 `mmc1.pdf`，以及正文图 1–4 的 JPG/GIF 文件；**没有** TSV、CSV、TXT、XLSX、VCF、GWAS-SSF 或其他逐变异统计文件。完整条目见 `PMC13212417_supplement_manifest.tsv`。

## 4. 对 SYNGR1 新颖性边界有直接影响的附录证据

`mmc1.pdf` 的 **Supplementary Table 2** 位于 PDF 物理第 15 页、附录印刷页码第 14 页。表题为 sex-specific risk loci 与 disease-relevant tissues 中 sex-agnostic eQTL 的 colocalization；只展示至少一个性别 `PP > 0.8` 的 gene–tissue pair。

表头为：

`CHR | Gene | Tissue | PP females | PP males`

方法部分说明，作者使用 sex-stratified GWAS summary statistics 与 **GTEx v8**，在 lead variant 上下游各 500 kb（总 1 Mb）运行 COLOC；这里的 PP 表示两组数据由同一单一因果变异解释的后验概率，并分别对 female 与 male 计算。

chr22 的精确两行是：

| CHR | Gene | Tissue | PP females | PP males |
|---:|---|---|---:|---:|
| 22 | SYNGR1 | Whole blood | 0.977 | 0.025 |
| 22 | SYNGR1 | Lymphocytes | 0.980 | 0.033 |

这意味着原论文附录已经明确提出并支持 **female SSc GWAS ↔ SYNGR1 eQTL** 共定位。后续论文不能声称“原研究只归因 RPL3–PDGFB、我们首次发现或首次重分配到 SYNGR1”。可成立且更准确的增量是：用 population-scale immune multiome 将 GTEx 的宽泛 whole-blood/lymphocyte 证据解析到具体免疫细胞，并进一步检验 disease GWAS、eQTL、caQTL 与 peak→gene link 的 signal-level coherence。

附录表只给 gene–tissue 层面的 PP，未给每个变异的 beta、SE、effect allele、EAF、per-variant N、INFO 或区域完整统计；所以它不能替代正式 summary statistics，也不足以独立复算作者 COLOC。

## 5. UCL 与出版社附件核查

- [UCL Discovery 条目](https://discovery.ucl.ac.uk/id/eprint/10224707/)只列出 1 个约 3 MB 的 “Accepted Version” PDF（`Reprint for UCL upload-sex specific genetics SSc 2026.pdf`）；页面没有列出 summary-statistics 数据文件或独立数据集。
- [The Lancet Rheumatology / DOI 页面](https://doi.org/10.1016/S2665-9913(25)00376-5)列出 “Supplementary Material (1)”。该数量与 PMC XML 的单个 `mmc1.pdf` 完全一致；没有发现第二个数据附件。

## 6. 项目判定与下一步

1. **疾病锚点继续 HOLD。** 在 female/male 全区域或全基因组逐变异统计到手并通过 build、allele、EAF、N/coverage、INFO 和 checksum 验收前，不运行或宣称 paper-grade disease colocalization；`C1_count` 仍为 `null`。
2. **保留可重复入口检查。** 可定期重跑 `check_ssc_access.py`；出现 GCST accession 或 `full_pvalue_set=true` 后，进入 H6 schema/accession/checksum gate，而不是直接 fine-map。
3. **并行准备作者数据请求，但本轮不发送。** 应请求 female 与 male 固定效应 meta-analysis 的完整文件、数据字典、参考基因组、effect/non-effect allele、beta/log(OR)、SE、P、EAF、INFO、逐变异 N 或 contributing-cohort count，以及文件 checksum。若全量文件过大，最低可先请求 chr6 IRF4 与 chr22 SYNGR1/RPL3–PDGFB 两个冻结窗口的完整区域统计，但最终 paper-grade 分析仍应取得可审计的数据来源。
4. **修正新颖性表述。** 将主命题由“首次发现 SYNGR1”改为“对已由 GTEx 宽组织共定位提示的 SYNGR1，提供具体免疫细胞的 eQTL–caQTL–peak→gene 机制解析，并检验其与 female SSc 信号的多层一致性”。

## 7. 证据局限

这是 2026-09-10 的公开入口快照。它证明目标数据在所查官方 Catalog API、PMC/Europe PMC 附件、UCL 记录和出版社附件清单中不可获得；不能证明作者或 consortium 私有存储中没有文件，也不能证明未来不会完成 Catalog 编目。
