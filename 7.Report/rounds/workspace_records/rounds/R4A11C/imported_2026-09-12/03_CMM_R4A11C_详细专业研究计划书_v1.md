# CMM R4A11C — 系统性硬化症 sex-biased immune regulatory cascade 详细专业研究计划书 v1

**项目状态：CONDITIONAL GO**  
**计划冻结日期：2026-09-12**  
**当前科学阶段：R4A11C（FinnGen R12战略重构）**  
**下一阶段：R4A12-FG（FinnGen R12 SSc sex-stratified acquisition & independent replication gate）**

---

## 一、项目总目标

本项目拟在已经发表的2026年系统性硬化症（systemic sclerosis, SSc）性别分层GWAS基础上，进一步解析其女性相关chr22风险位点是否通过**特定免疫细胞中的染色质可及性—基因表达调控链**作用于SYNGR1，并使用FinnGen R12性别分层SSc GWAS作为独立疾病复制，再在SSc真实疾病组织中验证该遗传优先机制是否被疾病状态重现。

项目不再以“发现SSc相关基因”“首次发现SYNGR1”“SSc+单细胞+MR”为主卖点。真正要回答的是：

> **已发表的female SSc–SYNGR1宽组织遗传关联，能否被解析为一个具有同一遗传信号支撑的cell-resolved variant→chromatin→gene regulatory mechanism，并在独立sex-stratified disease cohort中得到支持？**

这是一个严格可证伪的问题，而不是结果导向的多组学堆叠。

---

## 二、研究背景与未解决问题

### 2.1 已知事实

2026年SSc sex-stratified GWAS已经建立了明显的性别差异遗传结构，并报告女性相关IRF4及chr22 RPL3–PDGFB区域信号。其补充材料还已报告female SSc与SYNGR1在GTEx whole blood和lymphocytes中的高后验共定位。因此，本项目不能将“female SSc与SYNGR1相关”本身作为创新发现。

与此同时，本项目已经获得一组值得进一步检验的分子前置证据：TenK10K NK细胞SYNGR1 eQTL credible set与FinnGen immune multiome l2.NK目标caQTL credible set在两个GRCh38变异上精确重叠：

- `22:39351666:T:A`
- `22:39351775:G:A`

但FinnGen NK caQTL CS还存在第三个高概率成员，因此目前只能表述为`EXACT_CS_OVERLAP_CONFIRMED`，不能写成“分子共定位已证实”。

### 2.2 当前真正的知识缺口

仍未解决的问题有四层：

1. **Disease layer**：2026 female SSc disease signal与NK caQTL、SYNGR1 eQTL是否共享同一遗传信号？
2. **Regulatory layer**：chr22风险信号是否首先作用于一个明确的accessible chromatin element，再影响SYNGR1？
3. **Gene assignment**：SYNGR1是否在与RPL3、PDGFB及其余peak-linked候选基因的公平竞争中仍是最佳效应基因解释？
4. **Disease context**：遗传优先的细胞—基因调控模块是否在未经治疗的SSc皮肤/空间组织中表现出一致的疾病状态改变？

FinnGen R12的加入还新增第五个问题：

5. **Independent disease replication**：该female-associated signal能否在独立Finnish sex-stratified SSc cohort中表现出方向一致的女性效应和/或正式的sex heterogeneity？

---

## 三、中心假说

### H1 — Disease-to-chromatin hypothesis
2026 female SSc chr22疾病信号与FinnGen NK目标caQTL共享同一或高度一致的遗传信号，而不是简单的物理距离邻近。

### H2 — Chromatin-to-expression hypothesis
同一NK细胞层级中，目标caQTL signal与SYNGR1 eQTL signal具有可复核的signal coherence，并由source-defined peak→gene关系支持。

### H3 — Effector-gene prioritization hypothesis
在预先冻结的20个候选基因中，SYNGR1在疾病信号、分子QTL、peak→gene和独立QTL复制的联合证据上优于RPL3/PDGFB及其他候选，但这一结论必须由统一统计标准产生，不能通过结果后筛选。

### H4 — Independent sex-stratified replication hypothesis
FinnGen R12 female SSc在chr22区域呈现与2026发现方向兼容的疾病信号；若male统计功效足够，则female–male heterogeneity进一步支持性别差异。若male功效不足，则结论降级为“female-supported / sex difference unresolved”，而非“female-specific”。

### H5 — Disease-context concordance hypothesis
只有通过遗传C1门的候选机制，才预计在未经治疗SSc皮肤的相应细胞状态中出现方向一致的表达/可及性/空间富集改变。

---

## 四、研究目标（Specific Aims）

### Aim 1 — 建立paper-grade disease-anchor及独立复制框架

**Primary disease anchor**：2026 multi-cohort sex-stratified SSc GWAS。  
**Independent replication**：FinnGen R12 female/male SSc。  
**Engineering/sensitivity**：FinnGen R12 all-sex SSc。  
**Historical engineering only**：GCST009131 2019 overall SSc。

核心任务：

- 2026 female/male文件到位后执行P0 provider identity → H6 → normalization → coverage；
- 立即获取/验证FinnGen R12 `M13_SYSTSLCE` all-sex及sex-specific对象；
- 使用R12正式heterogeneity统计，而不是female显著/male不显著的错误比较；
- 将R12定位为独立疾病复制，不将其替代2026 discovery GWAS。

### Aim 2 — 建立chr22 disease→chromatin→expression signal triangle

三个必须分别通过的edge：

- **D1**：female SSc disease ↔ NK caQTL
- **E1**：female SSc disease ↔ SYNGR1 eQTL
- **M1**：NK caQTL ↔ SYNGR1 eQTL

只有D1、E1、M1均在同一细胞/兼容signal下通过，并且peak→gene与技术QC通过，才定义为**C1 regulatory cascade**。

### Aim 3 — 有界候选基因竞争与独立分子复制

固定20基因候选集合：

- Primary：SYNGR1
- Mandatory comparators：RPL3、PDGFB
- Additional：冻结FinnGen target peak-link snapshot中的17个其他候选

所有候选必须使用相同：

- genomic window；
- variant eligibility；
- coverage gate；
- LD/reference规则；
- fine-mapping参数；
- coloc priors/sensitivity；
- edge classification。

TenK10K继续承担**independent molecular replication**，避免FinnGen disease GWAS与FinnGen multiome在同一研究生态中的共享背景被误称为完全独立验证。

### Aim 4 — 真实SSc疾病组织验证

仅在C1或预先定义的强partial mechanism通过后启动。

优先级：

1. **GSE312129** — 主疾病组织multiome：untreated early dcSSc skin，snRNA+snATAC+spatial；
2. **GSE249279** — 独立skin scRNA/spatial replication；
3. **GSE236111** — IFN/endothelial条件性验证；
4. **GSE312932** — Xenium空间定位；
5. **GSE312591** — 仅当最终机制涉及RUNX1时作为条件性perturbation证据。

### Aim 5 — 建立克制的生物学解释与转化层

只有通过遗传和疾病组织双重门控的候选，才进入：

- PheWAS/safety；
- Open Targets/ChEMBL/DrugBank；
- directional druggability；
- potential therapeutic prioritization。

分子对接不作为核心证据，也不用于“救”失败的遗传机制。

---

## 五、数据资源分层与职责

|层级|数据源|职责|是否允许替代Primary|
|---|---|---|---|
|Disease discovery|2026 sex-stratified SSc GWAS|主疾病锚定；chr22/IRF4|否|
|Disease replication|FinnGen R12 sex-specific SSc|独立女性/男性复制、heterogeneity|否|
|Overall engineering|FinnGen R12 all-sex SSc|现代GRCh38工程/敏感性|否|
|Historical engineering|GCST009131|方法学失败模式与historical sensitivity|否|
|Primary chromatin QTL|FinnGen immune multiome|cell-specific caQTL、SuSiE、peak→gene|—|
|Independent expression QTL|TenK10K|eQTL independent replication|—|
|Disease tissue primary|GSE312129|疾病状态multiome/spatial|—|
|Disease tissue replicate|GSE249279|独立skin replication|—|

### FinnGen R12特别说明

R12 sex-specific release官方提供female/male单独REGENIE结果，以及包含`all_inv_var_het_p`的female–male meta文件；其GRCh38 REF/ALT/beta/SE结构非常适合当前P0/H6/fine-mapping框架。但sex-specific对象位于Green Library/Sandbox，必须先确认`M13_SYSTSLCE`不在262个excluded endpoints中并取得实际对象字节。

---

## 六、分析阶段与严格门控

### Phase 0 — Raw-input provenance reconstruction

正式分析前新增一个不可省略的输入层：

`RAW_INPUT_PROVENANCE_MANIFEST.tsv`

每个原始数据必须记录：

- source/provider；
- accession/object path；
- release/version；
- URL/bucket；
- download timestamp；
- bytes；
- SHA256/MD5；
- build；
- schema；
- access/license；
- redistribution status；
- downstream files generated。

这是因为当前上传的`YR1.zip`虽然代码/结果/报告完整，但规范化`1_data`不包含真实大体量原始输入。

### Phase 1 — FinnGen R12 acquisition gate

#### 1A. Endpoint eligibility

先读取：

`regenie_single_sex_drop_list_plus_reason_262_endpoints.txt`

硬条件：`M13_SYSTSLCE`不在excluded list。

#### 1B. Real-byte acquisition

至少取得：

- all-sex R12 SSc summary；
- female-only SSc summary；
- male-only SSc summary；
- sex-meta/heterogeneity summary；
- endpoint case/control metadata；
- R12 variant annotation/INFO；
- 如可用：R12 fine-mapping/colocalization输出。

#### 1C. P0 provider identity binding

必须绑定：

`FinnGen R12` + `M13_SYSTSLCE` + `female/male/meta` + actual file/object + provider evidence。

不能仅凭本地metadata声明。

#### 1D. H6 intake

检查：

- GRCh38；
- REF/ALT；
- effect allele；
- beta/se单位；
- AF语义；
- sample-size语义；
- duplicate keys；
- frozen region coverage；
- lead anchors。

### Phase 2 — R12 disease replication triage

冻结两个区域：

#### chr22 primary

- anchor：rs66578187 / chr22:39,328,807 (GRCh38)
- initial window：±500 kb
- window expansion只能依据预冻结signal boundary/LD规则，不因结果漂亮而扩大。

#### chr6 secondary

- anchor：rs12203592 / IRF4

输出：

- female beta/se/p；
- male beta/se/p；
- formal heterogeneity P；
- effect-direction concordance；
- regional lead；
- power/CI；
- classification。

#### R12 replication classification

- `REPLICATED_SIGNAL`
- `DIRECTIONAL_SUPPORT_ONLY`
- `INCONCLUSIVE_LOW_POWER`
- `DISCORDANT_WITH_ADEQUATE_POWER`
- `UNTESTABLE`

明确禁止：

> female显著 + male不显著 ⇒ female-specific

只有heterogeneity、CI和功效共同支持时才允许使用sex-differential/sex-biased language。

### Phase 3 — Primary 2026 disease-anchor

2026 summary bytes到位后立即优先于其他扩展分析：

P0 → H6 → FASTA normalization → coverage → ancestry-matched LD → RSS diagnostics → fine-mapping → D1/E1。

首先复现原论文SYNGR1 broad-tissue positive control（D0），作为疾病输入/allele/region的sanity check，然后才进行immune-cell-specific扩展。

### Phase 4 — Molecular signal analysis

#### D1 — Disease↔caQTL

问题：female-SSc信号是否与l2.NK target peak caQTL共享signal？

#### E1 — Disease↔eQTL

问题：female-SSc信号是否与SYNGR1 NK eQTL共享signal？

#### M1 — caQTL↔eQTL

问题：chromatin与expression QTL是否共享signal？

#### C1判定

C1仅在以下全部成立时通过：

1. D1 shared；
2. E1 shared；
3. M1 shared；
4. same cell or pre-declared compatible cell hierarchy；
5. source-defined peak→gene；
6. technical QC PASS；
7. candidate competition不出现更强、等价但被忽略的解释。

### Phase 5 — 20-gene bounded competition

不重新挑候选。对20基因统一建模并生成证据矩阵：

|Gene|Disease coloc|caQTL|eQTL|peak-link|TenK10K replicate|R12 disease replicate|final tier|
|---|---|---|---|---|---|---|---|

SYNGR1若胜出，应是因为全链证据更强，而不是预设结果。

### Phase 6 — Disease-tissue validation

启动条件：

- C1 PASS；或
- 明确的`PARTIAL_MECHANISM_STRONG`，且预先声明其局限。

分析原则：

- donor-level/pseudobulk优先；
- 不把细胞数当生物重复；
- cell-state directional validation；
- expression和accessibility分层；
- spatial仅验证定位与邻域，不把共定位当因果；
- GSE312129中male SSc仅少量样本，不做强sex-interaction主张。

### Phase 7 — Translation

只有Tier-1候选进入。输出以可药物性、已知靶点、预期作用方向、系统性风险为主，不用docking制造“验证”。

---

## 七、统计方法冻结原则

### 7.1 Variant normalization

- Primary build：GRCh38；
- REF/ALT需FASTA identity验证；
- multiallelic拆分；
- indel left normalization；
- palindromic SNP在AF不足时排除；
- 保存完整drop ledger。

### 7.2 Coverage gate

进入signal-level统计前必须满足：

- common variants ≥ 较小eligible set的80%；
- common variants ≥100；
- genomic span ≥100 kb；
- source retained 95% CS mass ≥0.90；
- frozen anchors/top variants未丢失。

未满足时状态为`UNTESTABLE/INSUFFICIENT_COVERAGE`，不是negative。

### 7.3 LD

优先顺序：

1. study-provided signed LD；
2. matching ancestry genotype reference；
3. 1000G Phase3 EUR作为预声明fallback。

必须保存：

- variant order hash；
- allele order hash；
- R对称性/对角；
- PSD/eigen diagnostics；
- z–LD consistency；
- reference sample provenance。

### 7.4 RSS gate

根据当前工程经验继续保留严格门：

- `estimate_s <= 0.10`
- `max_abs_standardized_kriging_residual <= 5`

失败则不强行运行SuSiE-RSS。

### 7.5 Fine-mapping与coloc

冻结软件版本框架继续沿用：

- R 4.6.0；
- susieR 0.14.2；
- coloc 5.2.3；

多信号区域优先SuSiE-aware signal pairing，不把单因果PP4作为唯一判断。每个edge同时报告：

- H3；
- H4；
- H4/(H3+H4)；
- priors sensitivity；
- signal pair；
- coverage；
- LD diagnostics。

### 7.6 Multiple testing

层级化控制：

- chr22 = primary confirmatory locus；
- IRF4 = secondary locus；
- 20-gene competition = fixed bounded family；
- disease tissue differential analyses = FDR control；
- exploratory cell states与空间模块明确标记exploratory。

---

## 八、结果分级与论文语言

### Tier 1 — Full cell-resolved regulatory cascade

Disease↔caQTL + Disease↔eQTL + caQTL↔eQTL + peak→gene + R12 replication + tissue concordance。

可使用：

> genetically supported, cell-resolved regulatory mechanism / convergent evidence

仍避免无实验条件下使用“proves causality”。

### Tier 2 — Expression-linked disease locus

Disease↔eQTL通过，但caQTL edge失败或不可测。

只能写：

> expression-linked disease signal

不能写chromatin-mediated cascade。

### Tier 3 — Molecular-only convergence

QTL↔QTL成立但疾病共享信号失败。

停止将其作为SSc mechanism主线。

### FALSIFIED

充分coverage、正确LD、technical PASS后，疾病signal与关键QTL均不共享。

接受主假说失败，不通过扩大窗口、换细胞或重新挑基因救结果。

---

## 九、预期结果与替代路径

### Scenario A — 最优

2026 female C1 PASS + R12 female replication + male heterogeneity支持 + disease tissue concordance。

**论文价值：高。** 可形成完整的sex-associated cell-resolved regulatory mechanism。

### Scenario B — C1 PASS，R12 low power

R12 female方向一致但未达formal replication，male CI宽。

结论：保留2026主机制，R12作为directional support；不强化sex specificity。

### Scenario C — R12复制，2026数据仍无法获取

可完成高质量replication/triage，但**不足以将R12替代primary discovery**。可继续等待2026数据，同时完成工程层；不建议直接写成终稿。

### Scenario D — R12与2026方向冲突且R12功效充分

立即进入hostile reassessment：

- variant normalization；
- ancestry/founder effects；
- phenotype definition；
- allelic heterogeneity；
- LD differences；
- effect heterogeneity。

在解释冲突前不启动大规模组织分析。

### Scenario E — disease edges失败

接受chr22主机制被证伪。IRF4作为预冻结secondary locus可运行一次；禁止无限all-loci rescue。

---

## 十、创新性与竞争定位

2026年后以下内容本身已不新：

- SSc + single-cell；
- SSc + MR；
- SSc + eQTL colocalization；
- SSc skin multiome；
- SYNGR1作为female chr22候选。

本项目可保留的创新组合为：

> **published sex-associated locus → signal-level disease/caQTL/eQTL triangle → cell-resolved peak→gene → independent FinnGen R12 sex-stratified disease replication → untreated disease-tissue concordance**

这里每一层承担不同审稿问题，而不是简单增加分析数量。

---

## 十一、Figure 1–7拟定职责

- **Figure 1**：研究设计、数据层级、证据门控与预注册停止规则；
- **Figure 2**：2026 discovery + FinnGen R12 female/male replication与heterogeneity；
- **Figure 3**：chr22 disease→caQTL→SYNGR1 signal triangle；
- **Figure 4**：20-gene candidate competition + TenK10K independent molecular replication；
- **Figure 5**：GSE312129 untreated SSc skin disease-context multiome；
- **Figure 6**：GSE249279独立/空间验证与必要的条件性数据；
- **Figure 7**：综合证据等级、sex interpretation与translation model。

主图不得按“软件顺序”排版。

---

## 十二、论文写作结构

### Introduction

1. SSc具有显著性别偏倚，但遗传性别差异的细胞调控机制仍不清楚；
2. 2026 sex-stratified GWAS已定位female-associated loci并提示SYNGR1，但broad-tissue QTL无法回答具体细胞/染色质机制；
3. population-scale immune multiome与独立sex-stratified FinnGen R12提供了signal-level refinement机会；
4. 本研究检验一个严格可证伪的cell-resolved regulatory cascade。

### Results建议标题

1. Sex-stratified SSc loci are prioritized under a frozen evidence framework
2. FinnGen R12 provides independent sex-stratified disease replication
3. The chr22 female-associated locus converges on an immune-cell chromatin signal
4. Signal-level integration prioritizes SYNGR1 against regional competitors
5. Independent TenK10K QTL data test molecular reproducibility
6. Genetic-priority programs are recapitulated in untreated SSc skin
7. Integrated evidence defines mechanistically supported and unsupported targets

### Discussion

顺序应为：

1. 主发现是什么；
2. 为什么比原GWAS的broad-tissue SYNGR1证据多一层；
3. R12为何是独立疾病复制但不是primary discovery；
4. cell-type/ancestry/sample overlap限制；
5. disease-tissue证据只是疾病环境一致性而非遗传因果替代；
6. future functional validation。

---

## 十三、投稿定位

取决于最终证据强度，而不是预先指定高IF。

### 若达到Full C1 + R12 replication + tissue multiome

可尝试：

- Genome Medicine
- Cell Genomics
- Nature Communications（需mechanistic depth特别强）
- Arthritis & Rheumatology / Annals of the Rheumatic Diseases相关档次需根据最终临床解释强度评估

### 若为强遗传multiome但组织层较弱

更现实：

- Rheumatology
- Arthritis Research & Therapy
- Genome Medicine（若遗传创新足够）

### 若最终只有partial expression-linked evidence

应降低目标，不用额外堆低价值分析伪装完整机制。

---

## 十四、当前GO / NO-GO规则

### GO到R4A12-FG

满足：

- R12 SSc endpoint sex-specific对象可确认；
- provider identity可绑定；
- 真实文件字节可取得或通过授权环境访问。

### HOLD

- endpoint存在但sex-specific对象不可访问；
- excluded-list状态未知；
-文件无provider identity或stratum信息；
- coverage/LD不足。

### NO-GO /主假说否定

- 2026 disease signal在充分数据/技术PASS下与caQTL/eQTL均不共享；或
- R12出现具有充分功效的强反向/不兼容疾病信号，且无法由ancestry/phenotype/LD解释；或
- 候选竞争显示SYNGR1不是可支持的最佳机制且无预先冻结替代机制通过。

---

## 十五、近期可执行任务（按优先级）

1. **立即：FinnGen R12 endpoint eligibility + real-object acquisition**；
2. 获取R12 all-sex `M13_SYSTSLCE`公开summary，替代GCST009131做clean engineering branch；
3. 在Green Library/Sandbox读取excluded list并取得female/male/meta对象；
4. 将R4A11B P0 provider identity gate与H6 v2.1适配R12 schema；
5. 提取chr22/IRF4冻结窗口，做effect/heterogeneity/power triage；
6. 若通过coverage，运行R12 disease↔FinnGen multiome预筛，并独立复现signal-level结果；
7. 2026主GWAS bytes一旦出现，优先切回Primary branch；
8. C1通过前不启动大规模疾病组织下载与正式图件制作。

---

## 十六、项目成功标准

本项目的成功不是“产出一个显著P值”，而是能给出一个审稿人可核验的结论：

> **对于已发表的female-associated SSc chr22 locus，我们能够明确区分：其是否真正与某一免疫细胞的染色质调控和SYNGR1表达共享遗传信号、是否在独立sex-stratified FinnGen cohort得到支持、以及该机制是否在未经治疗SSc组织中得到疾病环境一致性验证。**

即使最终结果为FALSIFIED，只要严格门控完整，也比通过后验扩分析得到一个不可复现的“阳性机制”更有科学价值。

---

## 主要官方数据说明

- FinnGen R12 public data: https://finngen.gitbook.io/documentation/data-download
- R12 sex-specific release: https://docs.finngen.fi/release-notes/data-releases-2024
- R12 sex-specific format: https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/sex-specific-gwas-results-format
- R12 core outputs: https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files
- FinnGen immune multiome: https://www.finngen.fi/en/access_results
- SSc endpoint: https://risteys.finngen.fi/endpoints/M13_SYSTSLCE
