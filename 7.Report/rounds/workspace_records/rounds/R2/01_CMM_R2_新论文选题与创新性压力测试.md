# CMM R2：新论文选题与创新性压力测试

**日期：2026-09-05**  
**任务定位：** 将上一轮54篇论文的写作/证据链分析真正转化为可启动的新论文项目，而不是继续做文献总结。  
**核心原则：** 不以“能不能跑出来”为主要标准，而以“2026年9月是否仍有足够创新窗口、数据能否闭环、审稿人最难攻击的证据层是否具备”为主标准。

---

## 1. 本轮最重要的战略修正

上一轮得到的最佳公共数据母版是：

> `sc-eQTL → MR → colocalization → replication → disease scRNA → PheWAS/drug`

这一母版在2024–2025年仍有明显竞争力，但到2026年已快速同质化。最新检索显示，该框架已被用于SLE、胆石症、肥胖、骨关节炎、慢性肺病、MS/EBV、表观遗传年龄等多个方向。因此，**下一篇如果仍以OneK1K 14类PBMC为主资源，仅替换疾病名称，创新风险已经偏高。**

真正值得升级的是：

> **从“cell-specific expression causality”升级到“cell-specific regulatory cascade”。**

即不只问：

> 哪个细胞中的哪个基因与疾病存在遗传支持？

而进一步问：

> 哪个遗传变异在什么细胞中先改变染色质开放性，再改变基因表达，并最终与疾病风险共享因果信号？这个链条是否能在独立QTL、真实病灶组织和药理层得到正交支持？

---

## 2. 为什么现在出现了一个新的窗口

### 2.1 FinnGen population-scale single-nucleus multiome 已公开

FinnGen于2026-08-13公开新的单核multiome资源：

- 1,108名个体；
- 10,612,211个snRNA-seq nuclei；
- 7,100,899个snATAC-seq nuclei；
- 33种细胞类型（9个一级、24个二级）；
- 27,294个基因；
- 297,024个chromatin-accessibility peaks；
- 17,167,198个遗传变异；
- 提供cis-eQTL与cis-caQTL；
- 提供SuSiE fine-mapping；
- 提供peak–gene links；
- 提供GWAS colocalization与CASCADE regulatory-mechanism分类。

这意味着可以从过去的：

`variant → expression → disease`

升级为：

`variant → chromatin accessibility → expression → disease`

这不是单纯多加一种组学，而是**把非编码GWAS信号的调控路径显式化**。

主要来源：  
https://www.finngen.fi/en/access_results  
https://www.medrxiv.org/content/10.1101/2025.11.25.25340489v1.full

### 2.2 TenK10K提供更高细胞分辨率的独立QTL复现

TenK10K Phase 1 已公开：

- 28种免疫细胞；
- common-variant cis-eQTL全量summary statistics；
- 可作为FinnGen multiome或OneK1K发现结果的独立复现层。

来源：  
https://zenodo.org/records/18221260

### 2.3 tissue-resident eQTL正在改变“外周血代表病灶”的审稿逻辑

2026年Nature Immunology发表肺组织驻留免疫细胞eQTL研究，覆盖29种免疫亚群，明确说明：仅使用外周血eQTL可能遗漏组织驻留免疫细胞中的疾病遗传作用。

来源：  
https://www.nature.com/articles/s41590-026-02596-2

因此新稿应尽可能加入：

- disease-relevant tissue scRNA/spatial；或
- tissue-resident eQTL；或
- 至少明确证明外周信号在病灶组织中有相同细胞/状态语境。

---

## 3. 2026年不再建议完整复制的路线

### 3.1 OneK1K-only scTWMR

**风险：高。**

原因不是OneK1K质量下降，而是该数据集已经被反复应用。若研究结构仍然是：

`14 immune cells → MR → coloc → PPI → DrugBank`

则很容易被编辑认为是“phenotype replacement”。

### 3.2 MR显著后再堆PPI/GO/KEGG

这类分析对解释有帮助，但不能提升因果可信度。新稿应把篇幅优先投入：

- fine-mapping；
- multi-signal colocalization；
- independent QTL replication；
- disease-tissue validation；
- perturbation/functional evidence；
- direction-aware pharmacology。

### 3.3 单一coloc.abf作为全部“因果证明”

2026年PLOS Genetics的大规模评估进一步强调：一个colocalized locus可能对应多个gene，colocalization并不等同于唯一因果基因。

因此建议升级为：

- SuSiE fine-mapping + coloc.susie；
- sensitivity priors；
- multi-gene locus明确保留不确定性；
- 独立eQTL/caQTL或功能数据帮助拆分候选。

来源：  
https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1012141

---

## 4. 候选选题创新性压力测试

评分维度：

- **Clinical gap**：疾病问题是否重要；
- **GWAS power**：是否有足够规模的公开GWAS；
- **Cell/tissue fit**：是否有合适的scRNA/spatial/组织资源；
- **Novelty window**：截至2026-09是否尚未被同构研究占满；
- **Multiome upgrade value**：eQTL+caQTL是否能产生真正新增信息；
- **Execution risk**：数据下载、样本量、复现等风险；
- **Q1 ceiling**：纯公共数据条件下合理期刊上限。

### 4.1 候选总表

| 排名 | 方向 | 综合建议 | 主要优点 | 主要风险 |
|---:|---|---:|---|---|
| **1** | **Systemic sclerosis (SSc)：性别特异免疫调控级联** | **A+ / GO** | 2026最新sex-stratified GWAS；强烈女性偏倚；免疫-血管-纤维化三轴；皮肤scRNA/spatial和肺组织证据丰富；multiome能真正回答非编码调控机制 | SSc已有大量遗传学研究，需要把“sex × cell × chromatin→expression”写成唯一主命题 |
| **2** | **Sjögren disease：腺体-免疫细胞特异调控级联** | **A / GO after data check** | 2025 GWAS meta分析病例接近1万；唾液腺病灶scRNA强；临床未满足需求明确；适合IFN/B-cell轴 | 2026已有IFN-eQTL/mQTL MR文章，必须避开“再做一遍IFN靶点” |
| **3** | **Myasthenia gravis：年龄/细胞状态特异遗传机制** | **A- / CONDITIONAL GO** | 2024大型GWAS 5708 cases+43万controls并有early/late-onset亚型；thymus/PBMC生物学合理 | 2024已有druggable MR+immune-cell colocalization，需以EOMG/LOMG异质性或multiome regulatory cascade为创新核心 |
| **4** | **Alopecia areata：scalp免疫特权崩溃的遗传调控级联** | **B+ / CONDITIONAL GO** | 2026 JACI有高质量scalp scRNA；病灶组织非常适合定位；机制故事鲜明 | FinnGen AA病例约千级，GWAS power可能限制全转录组筛选；需寻找更强summary statistics |
| 5 | Celiac disease：肠黏膜细胞调控级联 | B+ | 免疫/上皮组织相关性极强；公共数据丰富 | IBD/CeD遗传解析领域竞争极强，且IBD 2026 Nature已经把cell-type eQTL推到很高水平 |
| 6 | IgA nephropathy | B | 肾-黏膜免疫故事强 | 2026已有CureGN disease-specific QTL atlas和多项跨疾病遗传研究，窗口快速收窄 |
| 7 | Primary biliary cholangitis | B- | 肝组织/免疫/药物转化明确 | 2026已有多篇MR、实验验证及npj SBA多组学文章，明显拥挤 |
| 8 | Ankylosing spondylitis/PsA | B- | GWAS强、免疫机制明确 | 2026已有cTWAS+coloc+fine-mapping+Geneformer/AlphaGenome甚至siRNA，单纯multiome追加不够 |
| 9 | Sarcoidosis | C+ | 肺组织高度匹配 | 2026 Nature Immunology已经直接用lung resident eQTL解析sarcoidosis，重复风险高 |

---

## 5. TOP1为何选择Systemic Sclerosis，而不是最“热门”的疾病

### 5.1 有一个非常明确、可写成Introduction第三段的gap

SSc是一个典型的：

> **immune dysregulation + vasculopathy + fibrosis**

疾病，而且具有非常明显的性别偏倚。

2026年The Lancet Rheumatology完成了迄今最重要的sex-stratified SSc GWAS之一：

- 10,653 SSc cases；
- 18,043 controls；
- 1,556 male cases；
- 9,097 female cases；
- 发现BCL11A男性特异信号以及IRF4、RPL3-PDGFB等女性特异信号。

更重要的是，该研究本身明确指出sex-specific genetic architecture存在，但其功能解析仍主要停留在传统functional annotation、sex-differential expression和drug repurposing。

来源：  
https://pubmed.ncbi.nlm.nih.gov/41999721/  
https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/

因此新的科学问题不是：

> “SSc有哪些风险基因？”

而应是：

> **“SSc的sex-biased GWAS风险究竟通过哪些免疫细胞中的染色质—转录调控级联实现，并且这些遗传程序是否在皮肤/肺等真实病灶细胞状态中得到支持？”**

这个问题与现有GWAS并不重复，而是自然承接它的未解决机制。

### 5.2 SSc的病灶组织数据特别适合完成Localization层

可用的公开资源包括：

- SSc skin scRNA-seq：GSE312591；
- SSc skin single-cell + spatial：GSE249279；
- SSc skin IFN/endothelial scRNA：GSE236111；
- 2026 SSc skin transcriptomics进一步提示skin-lung共享机制。

这允许最终候选不是停留在“CD4 T cell gene”，而是进一步验证：

- 是否在SSc lesion中差异表达；
- 位于哪个immune/non-immune subpopulation；
- 是否进入endothelial/fibroblast interaction network；
- 是否与diffuse/limited、fibrosis severity或IFN state一致。

### 5.3 有天然的第二层临床问题：Raynaud → SSc

2026 Rheumatology研究显示primary Raynaud phenomenon与SSc存在共享遗传结构，并识别MEOX2、ADRA2A、IL12A、NFKB1、TNIP1等pleiotropic loci。

来源：  
https://pubmed.ncbi.nlm.nih.gov/41965070/

因此若主项目跑出稳定结果，可以自然扩展为：

> 哪些cell-specific regulatory cascades属于“early vascular predisposition”，哪些更偏向“established fibrotic autoimmune disease”？

这比传统“列出SSc靶点”更接近一个真正的生物学故事。

---

## 6. TOP2：Sjögren disease为何值得保留

### 优势

2025 ACR汇报的GWAS meta-analysis已经达到约10,003 SjD cases，并识别13个新的风险位点；FinnGen R11也已有约4,083病例，说明GWAS power正在快速上升。

来源：  
https://acrabstracts.org/abstract/meta-analysis-of-gwas-data-from-10003-sjogrens-disease-cases-identifies-thirteen-sjogrens-risk-loci/  
https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2025.1554991/full

### 主要竞争

2026 iScience已经发表：

`IFN-related DEG → eQTL/mQTL SMR → colocalization → serum validation`

因此下一篇不能再以“IFN-associated causal genes in Sjögren”为中心。

真正可做的升级方向应是：

> **B-cell/plasma-cell and gland-resident immune regulatory cascades**

而非再做一个全血IFN靶点筛选。

---

## 7. TOP3：Myasthenia gravis为何属于Conditional GO

2024 Nature Communications的MG GWAS meta-analysis提供：

- 5,708 MG cases；
- 432,028 controls；
- 并有early-onset / late-onset亚型GWAS。

来源：  
https://www.nature.com/articles/s41467-024-53595-6

这为“疾病异质性”提供了比普通病例-对照GWAS更强的故事空间。

但2024 Journal of Translational Medicine已经发表：

`druggable eQTL/pQTL MR → colocalization → immune cell specificity`

因此MG若启动，应采用：

> **EOMG vs LOMG immune regulatory-cascade heterogeneity**

而不是再次筛MG drug targets。

---

## 8. 本轮最终决策

### GO：建立一个新的母版v2，而不是立即批量跑疾病

**母版名称：**

> **Cell-type regulatory-cascade prioritization with disease-tissue orthogonal validation**

### 推荐先导项目：

> **Systemic sclerosis sex-biased immune regulatory cascade project**

### 暂不建议：

- 直接启动OneK1K-only新疾病；
- PBC/AS/IBD等已经高度拥挤的疾病；
- 在没有GWAS power检查的情况下启动AA；
- 先跑全套分析、最后再想科学问题。

---

## 9. 下一阶段必须先过的硬Gate

在真正下载大规模数据并跑分析前，下一轮应做一个 **R3 Data & Novelty Preflight**，只有同时满足以下条件才正式GO：

1. SSc combined/female/male GWAS summary statistics可稳定获得并完成build/allele QC；
2. FinnGen multiome eQTL+caQTL的可下载格式与cell annotation确认；
3. TenK10K可以作为至少一个独立QTL复现来源；
4. SSc skin scRNA/spatial至少两个独立队列可复现；
5. 不与2026 Lancet Rheumatology和Nature Immunology论文形成“仅重新注释”的重复；
6. 预先定义colocalization/fine-mapping硬门；
7. 预先定义如果只有HLA信号、只有单一SNP、或male power不足时的NO-GO规则。

只有通过这些Gate，才进入正式计算阶段。

---

## 10. 一句话总结

上一轮我们学会了如何模仿54篇论文；这一轮得到的更重要结论是：

> **下一篇不能再模仿它们的表面流程，而要利用2026刚出现的multiome QTL资源，把“基因—疾病关联”升级成“遗传变异—染色质—表达—细胞状态—病灶组织—疾病”的调控级联。**

这才是目前最值得投入的新论文方向。
