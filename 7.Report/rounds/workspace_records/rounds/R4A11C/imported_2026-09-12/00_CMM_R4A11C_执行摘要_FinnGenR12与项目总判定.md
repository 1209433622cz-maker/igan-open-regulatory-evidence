# CMM R4A11C 执行摘要：FinnGen R12 与项目总判定

**日期：2026-09-12**  
**范围：FinnGen R12 数据可用性核查 + `YR1.zip` / `YR1 (2).zip` 全量项目审计 + 研究计划重构。**

## 1. 最终结论

本轮最重要的新判断是：**FinnGen R12 确实存在能够部分填补当前项目最大缺口的数据层。** R12 在 2024-05-06 发布了 2,207 个 endpoint 的 female-only / male-only REGENIE GWAS，以及将两性结果合并并提供 Cochran's Q 性别异质性检验的 meta-analysis 文件。SSc endpoint `M13_SYSTSLCE` 明确存在于 R12 体系，常规 R12 GWAS 也可通过公开 manifest 获取。

这意味着项目不必继续处于“只能等待 2026 Lancet Rheumatology sex-specific meta-GWAS 原始 summary statistics”的纯等待状态。新的最佳结构应为：

> **2026 multi-cohort female/male SSc GWAS = primary disease discovery / definitive anchor**  
> **FinnGen R12 female/male SSc = independent sex-stratified replication branch**  
> **FinnGen R12 all-sex SSc = clean engineering / overall sensitivity branch**  
> **FinnGen immune multiome = primary caQTL / peak→gene molecular layer**  
> **TenK10K = independent eQTL replication layer**  
> **SSc disease tissue multiome = post-genetic-gate disease-context validation**

但要严格区分：**FinnGen R12 不能替代 2026 的 9,097 female / 1,556 male case multi-cohort GWAS作为论文主疾病锚定。** R12 是芬兰孤立人群、病例规模更小，更适合“独立复制、性别异质性支持、工程验证”。

## 2. R12 对项目真正补了什么

### 2.1 高价值新增

1. **female/male 单独 GWAS summary statistics**：此前项目最缺的就是性别分层疾病数据；R12至少提供一个独立sex-stratified disease branch。
2. **female–male heterogeneity statistics**：可直接使用正式性别异质性检验，避免“female显著、male不显著，所以female-specific”的错误推断。
3. **标准REGENIE字段**：R12 sex-specific/meta格式包含REF/ALT、beta、SE、P和allele frequency，更适合H6、harmonization、fine-mapping与coloc，而不像2019 GCST009131存在A2/SE缺失和meta covariance mismatch问题。
4. **R12 all-sex public GWAS**：可替换GCST009131成为更现代、更干净的overall SSc工程与敏感性数据源。
5. **R12 disease↔FinnGen multiome precomputed colocalization**：2026公开的FinnGen multiome明确包含“GWAS colocalization against FinnGen R12”，可作为优先级筛查和正交核查入口。

### 2.2 尚未被本轮“字节级确认”的事项

R12 sex-specific文件位于FinnGen Green Library / Sandbox路径。本轮从官方文档确认了发布、格式和目录，但**没有在本地取得 `M13_SYSTSLCE` female/male对象或262个excluded endpoints列表的真实字节**。因此目前状态必须写成：

> `R12_SEX_SPECIFIC_INFRASTRUCTURE = CONFIRMED`  
> `M13_SYSTSLCE_ENDPOINT = CONFIRMED`  
> `M13_SYSTSLCE_SEX_SPECIFIC_FILE_BYTES = NOT_YET_OBTAINED`  
> `M13_SYSTSLCE_NOT_IN_EXCLUDED_LIST = NOT_YET_BYTE_VERIFIED`

鉴于SSc在R10已有680病例（560 female / 120 male），当前Risteys最新版本已有904病例（745 female / 159 male），从病例规模看其进入R12 sex-specific分析的概率很高；但正式研究计划仍以“读取excluded list和实际对象”为硬门，不用推测替代证据。

## 3. 当前本地项目文件的总状态

### YR1.zip

- 223,457,545 bytes；
- 560个ZIP entries（其中436个实际文件、124个目录项）；
- ZIP CRC PASS；
- 主要是规范层、代码、结果、报告、release与历史快照；
- 代码catalog 81项、结果catalog 129项、release catalog 14项、报告catalog 114项；
- 当前协议已冻结到R4A11 v11，H6 v2.1已具备较成熟的真实数据接入门；本对话后续的R4A11B又增加了Provider Identity Binding（P0）补丁。

### YR1 (2).zip

- 305,330,092 bytes；
- 113个ZIP entries（其中89个实际文件、24个目录项）；
- ZIP CRC PASS；
- 主要是54篇参考论文、2026 sex-specific SSc目标论文及其supplement/web snapshots，以及手稿/图件目录骨架。

### 最关键的归档缺口

规范化的 `1_data` 在这次上传的 `YR1.zip` 中**没有任何真实原始数据成员**。虽然`3_results`保留了TenK10K CS、FinnGen快照、IL12RB2 LD矩阵、RSS诊断等重要派生结果，但完整GCST009131原始GWAS、1000G EUR完整参考、正式FinnGen/TenK10K原始release等大体量输入并未随该归档自包含。

因此项目目前是：

> **科学逻辑/协议/审计链成熟，原始输入层的归档可复现性仍需补强。**

后续正式paper release必须单独建立 `RAW_INPUT_PROVENANCE_MANIFEST`：记录每个原始数据的URL/accession、版本、字节数、SHA256/MD5、下载日期、许可证/访问条件和本地不可随包分发原因。

## 4. 当前最可靠的科学事实

1. 2026 target GWAS：female SSc 9,097病例，male SSc 1,556病例；female-specific新位点包括IRF4和RPL3–PDGFB区域。
2. 原论文已经在GTEx层报告female SSc–SYNGR1共定位：whole blood PP4=0.977、lymphocytes PP4=0.980。因此“首次发现SYNGR1”已经不成立。
3. 本项目冻结的分子证据：TenK10K NK/SYNGR1 eQTL CS4与FinnGen l2.NK target-peak caQTL CS1在两个GRCh38变异精确重叠：`22:39351666:T:A`、`22:39351775:G:A`。这只是**exact-CS overlap**，不是signal-level coloc。
4. 2019 overall SSc工程分支的外部LD RSS门失败（estimate_s约0.192；最大标准化残差约5.36），因此不能为了跑出SuSiE而忽略meta-analysis cohort-composition mismatch。
5. 当前 manuscript 和 figures 仍是pre-results骨架，没有任何通过disease gate的正式主图/结果段。

## 5. 更新后的核心论文命题

不建议继续使用宽泛题目“sex-biased regulatory cascades in SSc”，因为原论文已做sex-GWAS、GTEx eQTL colocalization、V2G及药物层；2026年也已有SSc皮肤multiome/spatial、lung-resident immune eQTL以及SSc scRNA+MR研究。

最有竞争力的命题应收窄为：

> **Can a published female-associated SSc locus be resolved from broad-tissue eQTL colocalization to a cell-resolved variant→chromatin→SYNGR1 regulatory signal, and does that signal replicate in an independent sex-stratified SSc cohort?**

中文可表述为：

> **在已发表female SSc–SYNGR1宽组织共定位基础上，解析chr22位点是否通过特定免疫细胞中的染色质可及性—SYNGR1表达调控链发挥作用，并在独立FinnGen R12性别分层SSc GWAS中验证其疾病与性别一致性。**

## 6. 项目总判定

**项目继续：`CONDITIONAL GO`，但研究策略发生积极升级。**

此前唯一硬入口是2026 female/male bytes；本轮以后可并行推进一条真正有科学价值的FinnGen R12 branch。因此不建议继续“等待而不分析”，也不建议提前进入SSc组织scRNA。

### 推荐的下一阶段

正式进入：

# **R4A12-FG — FinnGen R12 SSc sex-stratified acquisition & independent replication gate**

目标不是写论文，而是取得并验收真实R12 SSc对象：

- R12 all-sex `M13_SYSTSLCE`；
- R12 female-only / male-only SSc summary；
- female–male heterogeneity meta file；
- excluded-endpoint list；
- endpoint-specific N / case-control metadata；
- 如可用，R12 fine-map / colocalization输出。

只有真实字节过P0/H6/normalization/coverage后，才测试chr22与IRF4。2026目标GWAS一旦发布，仍立即升级为primary branch。

## 7. 关键官方来源

- FinnGen R12 data download: https://finngen.gitbook.io/documentation/data-download
- FinnGen R12 sex-specific release note (2024-05-06): https://docs.finngen.fi/release-notes/data-releases-2024
- FinnGen sex-specific GWAS format: https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/sex-specific-gwas-results-format
- FinnGen R12 methods: https://finngen.gitbook.io/documentation/methods/phewas
- FinnGen multiome public release: https://www.finngen.fi/en/access_results
- Risteys SSc endpoint: https://risteys.finngen.fi/endpoints/M13_SYSTSLCE
- Target 2026 SSc study: https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/
