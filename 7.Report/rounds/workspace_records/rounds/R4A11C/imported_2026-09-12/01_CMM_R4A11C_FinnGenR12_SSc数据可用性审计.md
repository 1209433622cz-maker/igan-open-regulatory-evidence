# CMM R4A11C — FinnGen R12 SSc 数据可用性审计

**审计日期：2026-09-12**

## 1. 直接回答：FinnGen R12 有没有我们缺的数据？

**有，而且是实质性的。** FinnGen R12官方在2024年5月6日发布了female-only与male-only GWAS summary statistics，并同时发布了female–male meta-analysis与heterogeneity statistics。项目此前最缺的正是“另一个真实sex-stratified SSc disease dataset”。

但必须把“R12有这类数据”与“我们已经拿到SSc sex-specific文件”分开：本轮尚未取得Green Library中 `M13_SYSTSLCE` 的真实female/male文件字节，因此不能把它写成“已接入”。

## 2. R12官方已确认的数据层

### 2.1 常规R12 GWAS

FinnGen R12主GWAS：

- 500,348 samples；
- 282,064 females；
- 218,284 males；
- 21,311,644 variants；
- 2,502 endpoints被分析（后续部分因技术/定义问题丢弃）；
- 使用REGENIE；
- R12公开summary statistics可通过public manifest获得。

SSc endpoint `M13_SYSTSLCE` 明确存在；E2G也能识别 `FINNGEN_R12_M13_SYSTSLCE` study。

### 2.2 R12 sex-specific release

官方release note明确：

- female/male individual results：2,207 endpoints；
- 262 endpoints因不适合sex-specific analysis而未发布；
- female/male各自使用REGENIE；
- 有合并两性结果和异质性统计的meta文件；
- 有跨endpoint的“任一性别P≤5×10⁻⁸”汇总文件；
- 有262个excluded endpoints及原因清单。

Green Library路径：

```text
gs://finngen-production-library-green/finngen_R12/
  finngen_R12_analysis_data/sex_difference/summary_stats/

gs://finngen-production-library-green/finngen_R12/
  finngen_R12_analysis_data/sex_difference/meta_analysis/meta_summary_stats/
```

excluded list：

```text
gs://finngen-production-library-green/finngen_R12/
  finngen_R12_analysis_data/sex_difference/
  regenie_single_sex_drop_list_plus_reason_262_endpoints.txt
```

## 3. 为什么R12 sex-specific格式非常适合本项目

官方sex-specific meta格式直接包含：

- `#CHR`, `POS`（GRCh38）；
- `REF`, `ALT`；
- `SNP`；
- `female_beta`, `female_se`, `female_pval`；
- `female_af_alt`, cases/controls AF；
- `male_beta`, `male_se`, `male_pval`；
- `male_af_alt`, cases/controls AF；
- `all_inv_var_het_p`（Cochran Q heterogeneity）；
- rsID。

这几乎正对当前H6/normalization/fine-map需求。与GCST009131相比，它避免了A2全缺、无原始SE、GRCh37以及多meta-study cohort-composition不一致等主要工程问题。

## 4. R12在本项目中的正确角色

### 4.1 不能替代2026 target GWAS

2026 Lancet Rheumatology研究是：

- 多欧洲队列meta-analysis；
- female cases = 9,097；
- male cases = 1,556；
- chr22 rs66578187与IRF4等是其sex-specific scientific discovery。

其Supplementary Table 1列出的欧洲队列未包含FinnGen。因此R12是一个真正不同的Finnish cohort，可承担独立疾病复制，但病例规模明显更小、人口遗传结构不同。

### 4.2 最强用途：独立sex-stratified replication

对于chr22和IRF4分别回答：

1. R12 female是否在相同区域出现可检测疾病信号？
2. rs66578187 / rs12203592是否存在、方向是否一致？
3. 区域fine-mapped signal是否与2026发现兼容？
4. female–male heterogeneity是否方向一致？
5. male“无信号”是否可能只是低功效？

### 4.3 第二用途：替代旧GCST009131做现代overall工程验证

R12 all-sex summary是GRCh38、单FinnGen分析、直接beta/SE/alleles，理论上更适合作为：

- H6 intake正控；
- harmonization正控；
- LD/RSS压力测试；
- overall SSc sensitivity；
- chr22/IRF4区域coverage检查。

它不再需要恢复A2或从OR/P构造近似SE。

### 4.4 第三用途：与FinnGen multiome的within-resource triangulation

FinnGen multiome公开说明其GWAS colocalization包括FinnGen R12。因此可优先检查SSc endpoint是否已经在CASCADE里产生R12 disease↔eQTL/caQTL线索。

但这里必须降调：R12 disease GWAS和FinnGen multiome都来自FinnGen生态系统，可能存在样本/祖源共享，所以**不能把这层叫独立分子复制**。独立分子复制仍由TenK10K承担。

## 5. SSc endpoint可用性的证据强度

### 已证实

- `M13_SYSTSLCE` 是FinnGen SSc endpoint；
- R12 study标识 `FINNGEN_R12_M13_SYSTSLCE` 可被外部研究门户识别；
- SSc病例数从R8的560、R10的680，增长到最新Risteys的904（745 female / 159 male）；
- R12 sex-specific infrastructure覆盖2,207 endpoints。

### 本轮未证实

- `M13_SYSTSLCE`是否不在262个excluded endpoint里；
- female/male具体R12文件名与字节；
- R12时点的准确female/male病例数；
- 其sex-specific summary是否可由本项目当前身份直接读取，还是需要FinnGen Sandbox权限。

因此下一步必须先读取excluded list和目录，而不是从病例数推断“必然有”。

## 6. Male分支功效风险

最新Risteys中SSc为745 female、159 male；R12时点不会高于最新版本。即使R12 male文件存在，male病例数也可能只有百余例。因此：

- male不显著不能证明female specificity；
- 应优先使用heterogeneity P和效应方向；
- 对chr22/IRF4都需要估算检测功效；
- 若male区域coverage良好但CI极宽，状态应为`SEX_DIFFERENCE_UNRESOLVED_LOW_POWER`；
- 只有正式heterogeneity支持且两性模型均充分可检测，才允许升级性别差异表述。

## 7. 数据接入顺序

1. 读取excluded endpoints列表，确认 `M13_SYSTSLCE` 状态；
2. 列出sex_difference/summary_stats下与该endpoint对应的female/male对象；
3. 列出meta_summary_stats对象；
4. 获取对象generation、size、checksum或provider metadata；
5. 以R4A11B P0 Provider Identity Binding gate绑定 `FinnGen R12 + M13_SYSTSLCE + female/male`；
6. H6 v2.1 / R12适配版检查schema、GRCh38、effect scale和sample-size semantics；
7. 只在上述通过后进入chr22/IRF4区域提取。

## 8. 对目前项目状态的影响

之前：

```text
2026 female/male bytes absent
→ PROJECT CONDITIONAL_GO
→ disease layer idle
```

现在：

```text
2026 target bytes absent
  ├─ Primary branch remains HOLD
  └─ FinnGen R12 replication branch becomes actionable
       → endpoint eligibility
       → sex-specific real bytes
       → chr22 / IRF4 replication
       → heterogeneity/power
```

因此项目仍是`CONDITIONAL_GO`，但已经不再是“等待型CONDITIONAL GO”，而是“有可执行独立复制分支的CONDITIONAL GO”。

## 9. 官方来源

- R12 sex-specific release note: https://docs.finngen.fi/release-notes/data-releases-2024
- Core R12 result locations: https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files
- Sex-specific file format: https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/sex-specific-gwas-results-format
- Public R12 manifest: https://storage.googleapis.com/finngen-public-data-r12/summary_stats/finngen_R12_manifest.tsv
- R12 PheWeb: https://r12.finngen.fi/
- SSc endpoint: https://risteys.finngen.fi/endpoints/M13_SYSTSLCE
- Multiome public release: https://www.finngen.fi/en/access_results
