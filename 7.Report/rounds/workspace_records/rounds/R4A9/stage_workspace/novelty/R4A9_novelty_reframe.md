# R4A9 hostile novelty reframe：把“首次发现 SYNGR1”改写为可检验的免疫细胞机制增量

**日期：** 2026-09-10（Asia/Hong_Kong）  
**审计对象：** 2026 年 sex-stratified SSc GWAS 正文与 Supplementary Table 2、R4A3/R4A5 分子与数据接入报告、R4A9 reference/LD/RSS 独立复核  
**目的：** 假设审稿人已经逐字读过原论文附录，并用最不利但合理的标准判断当前项目还能主张什么。

## 1. 最终重定位

当前项目**不能**再以“首次发现 female-SSc chr22 位点的效应基因为 SYNGR1”或“把 RPL3–PDGFB 重分配为 SYNGR1”为核心创新。原 2026 论文的 Supplementary Table 2 已明确报告 female SSc GWAS 与 **SYNGR1** 在 whole blood（PP=0.977）和 lymphocytes（PP=0.980）的 GTEx v8 eQTL 共定位；同表也已经报告 IRF4 和 IL12RB2 的 female 共定位。

仍可守住、且值得继续证伪的增量是：

> **在原论文已经提出的 SYNGR1 gene-level coloc 之上，检验 chr22 female-SSc 信号能否被解析为特定免疫细胞中的 disease–caQTL–eQTL–peak→gene 同一信号链，并用跨资源 QTL fine-mapping 约束该链。**

这应称为 **cell-resolved mechanistic refinement / immune multiomic refinement**，而不是 gene discovery、effector-gene reassignment 或 causal proof。

按论文创新潜力重新排序：

1. **chr22 / SYNGR1：第一优先级，但必须由 female disease summary statistics 决胜。** 它是三个候选中唯一仍有明显差异化窗口的位点。
2. **IRF4：第二优先级，作为跨资源不一致诊断和备份链。** 原论文的 GTEx 共定位已经很强；本项目新增的 B-naive 细胞结果目前又在 FinnGen 与 TenK10K 间不一致，因此还不能形成更强结论。
3. **IL12RB2：保留为工程正控，不再承担主创新。** 原论文已把它作为核心 female-specific gene，外部 2026 tissue-resident immune-cell 工作又已强调 SSc–IL12RB2 / lung NK；本项目目前只完成了 overall GWAS 的 reference/LD 工程验证，并未得到新的 paper-grade 生物学结果。

项目总体状态仍为：**CONDITIONAL GO；R4B HOLD；本项目对 female disease colocalization 的独立复现 NOT_TESTED；C1_count=null。** 原论文的 GTEx 单因果 COLOC 结果属于已发表外部证据，不等于本项目已接入原始 disease summary 并完成 signal-level 复核。

## 2. 原 2026 论文已经报告的内容

以下内容属于原论文，不能包装成本项目的新发现。

|主题|原论文已报告的精确内容|对本项目的约束|
|---|---|---|
|sex-specific SSc architecture|原论文自述为首个 SSc sex-stratified autosomal GWAS；共报告 8 个 sex-specific loci|不能使用“首次揭示 SSc 性别特异遗传结构”|
|新位点|male BCL11A；female IRF4 与 chr22 `rs66578187`，主文按邻近位置标为 RPL3–PDGFB|不能把这些疾病位点或 female association 当作新发现|
|chr22 / SYNGR1|Supplementary Table 2：SYNGR1 whole blood PP females=0.977、males=0.025；lymphocytes PP females=0.980、males=0.033|不能声称原研究遗漏 SYNGR1，也不能声称我们首次把该位点指向 SYNGR1|
|IRF4|Supplementary Table 2：lymphocytes 0.990、skin 0.998、lung 1.000（female PP）；原论文还报告 IRF4 是 novel female locus、相关变异具有 eQTL/sQTL 注释|不能把 IRF4 gene-level disease/eQTL 共定位当作新发现|
|IL12RB2|原论文把既有 SSc 位点 `rs6662198` 重新表征为 female-associated；Supplementary Table 2 报告 whole blood 0.837、lung 0.844；正文另有 pQTL、whole-blood/monocyte sex-differential expression 和重点生物学讨论|不能再以“发现 IL12RB2 female/NK 机制”作为主创新|
|chr22 主文叙事|正文和最终发表版 Figure 3（accepted manuscript Figure 2）使用 RPL3–PDGFB 区域标签，讨论部分突出 PDGFB；Supplementary Table 2 同时给出 SYNGR1 共定位|可研究主文标签与附录 coloc 之间的功能归因张力，但不能说 SYNGR1 从未被作者提出|
|方法分辨率|原论文在 lead 上下游 500 kb 使用 sex-stratified disease GWAS 与 sex-agnostic GTEx v8 做单因果 COLOC，并结合 FUMA/Open Targets、表达和药物注释|新增空间应集中在 primary immune cell、chromatin accessibility、peak→gene 和 multi-signal/signal-level 检验，而不是再做一次普通 GTEx coloc|

原论文最终发表版 Figure 3（accepted manuscript Figure 2）的候选行在 chr22 主要展示 PDGFB 与 RPL3，而 Supplementary Table 2 又报告 SYNGR1 coloc。这个不一致使“**对已有 SYNGR1 线索进行细胞和调控层级解析**”有价值，但不恢复“首次发现 SYNGR1”的新颖性。

## 3. 本项目已经独立新增的内容

这些结果来自本项目对公开资源的独立提取、重算或交叉验证。它们可以如实报告，但证据层级必须写清。

### 3.1 chr22 / SYNGR1

1. 在 FinnGen 区域接口的已测试细胞中，SSc lead `rs66578187`（源编码 `chr22:39328807 A>AT`）对 SYNGR1 显示强 marginal eQTL：l2.NK `p=9.9831e-110`，l2.CD8_TEM `p=4.7553e-83`。同变异、同细胞下 RPL3 较弱，PDGFB 在 CD8_TEM 为 `p=0.84948`；NK 中 PDGFB 未返回。该比较只支持**优先测试** SYNGR1，不支持基因因果排序，因为不同基因的表达量、可检测性和覆盖不等价。
2. 同一 lead 对 `chr22:39351520–39352777` peak 显示强 caQTL；该 peak 位于 SYNGR1 基因范围内，且 FinnGen 源 API 返回 peak→SYNGR1 link。link 证明资源中存在统计关联，不证明 accessibility 导致 expression。
3. TenK10K NK / SYNGR1 eQTL CS4 与 FinnGen l2.NK / target-peak caQTL CS1 在两个 coordinate+allele 完全相同的变异上相交：`22:39351666:T:A` 与 `22:39351775:G:A`。这是**cross-resource exact CS overlap**。
4. R4A5 补全分母后发现，FinnGen l2.NK caQTL CS1 有第三个成员 `22:39343182:C:T`，其 source probability=0.7470959；两个重叠成员概率合计仅 0.2529041。TenK10K 两成员各 PIP=0.5。因此“两个 CS 相同”“完整复制”或“强共定位”均不成立。

允许的当前表述是：

> “Public immune-QTL reanalysis identified a SYNGR1-linked molecular module at the chr22 locus, including strong NK-cell eQTL and caQTL associations, a source-defined peak–gene link, and exact coordinate-and-allele overlap between cross-resource credible sets.”

紧随其后的必要限定是：

> “This molecular convergence prioritizes SYNGR1 for disease-level testing but does not establish colocalization with female SSc, a causal variant, or accessibility-to-expression directionality.”

### 3.2 IRF4

1. TenK10K B-naive / IRF4 的 95% CS 为单成员 `6:396321:C:T`，PIP≈0.99931；该变异与原 female SSc lead 的坐标/等位基因表示一致。
2. FinnGen B-naive 中相同 pair 的 marginal `p=0.6728`。当前结果是跨资源不一致，而不是复制成功。
3. 原论文已经给出 IRF4 在 lymphocytes、skin、lung 的极高 female disease/eQTL PP；所以本项目的潜在新增只可能是**具体 B-cell 状态、为何跨资源不一致、以及经过完整 disease summary 后的 signal-level 复核**。

允许的当前表述是：

> “TenK10K fine-mapping nominated the female-SSc lead as a high-PIP IRF4 eQTL in naive B cells, whereas the exact FinnGen pair was not associated, motivating a bounded cross-resource heterogeneity analysis.”

不能写成“IRF4 在 B-naive 中得到独立复制”或“确定了 B-naive 为致病细胞”。

### 3.3 IL12RB2

1. R4A8B 构建了 1000 Genomes Phase 3 v5a EUR503、GRCh37 的 IL12RB2 区域 reference，并完成 A1 定向的 signed LD。
2. R4A9 用 PLINK2 独立导出 503×1555 dosage，并将区域 VCF GT 与 BED dosage 逐单元核对；两条 dosage 比较的最大差异均为 0，独立 LD 与冻结矩阵最大差异为 `6.99e-15`。这关闭了 source provenance、regional manifest 与 1,555 retained-variant VCF→BED→A1 dosage→LD 路径的问题；没有声称从完整 chr1 VCF 重新派生了全部 27,067 个区域基因型。
3. full public GCST009131 summary 的 RSS gate 仍失败：`estimate_s=0.1917849`、最大标准化 kriging residual=5.3614；SuSiE-RSS 未运行。coverage 分层支持 variant-dependent cohort/sample composition 是主要来源之一，但不能唯一归因。

这些是高质量**工程与质控结果**。它们不能写成 IL12RB2 fine-mapping、credible set、coloc 或新 SSc 机制。

## 4. 仍未测试的关键命题

|命题|当前状态|缺失的决定性证据|
|---|---|---|
|本项目能否独立复现 female SSc 与 SYNGR1 eQTL 的 signal-level shared signal|NOT_TESTED；原论文单因果 GTEx coloc 已发表|2026 female 完整区域统计、harmonization、匹配 LD、多信号分析|
|female SSc 与目标 caQTL peak 共享信号|NOT_TESTED|同上，并需完整 caQTL 统计和可解释覆盖|
|SYNGR1 eQTL 与 caQTL 是同一信号|NOT_TESTED|exact CS overlap 不能替代 signal-level coloc；需共同变异、LD、完整模型|
|完整 disease→caQTL→eQTL→SYNGR1 C1 链|NOT_TESTED；`C1_count=null`|三组 pairwise signal coherence、source link、同细胞映射和所有技术门均通过|
|NK 是特异或主要致病细胞|NOT_TESTED|所有可比细胞的统一覆盖、模型和多重检验；当前只是选定细胞中的强证据|
|分子 QTL 本身具有性别差异|NOT_TESTED|FinnGen/TenK10K QTL 不是本项目的 sex-stratified QTL 结果|
|SYNGR1 比 RPL3/PDGFB 更可能是疾病效应基因|PRIORITIZED, NOT ESTABLISHED|同一疾病信号下、同资源/同细胞/同覆盖的候选竞争与 disease anchoring|
|RPL3 或 PDGFB 不参与该位点|NOT_TESTED|NOT_RETURNED、弱 P 值或另一局部信号都不能作为排除证据|
|IRF4 B-naive 机制|NOT_TESTED / DISCORDANT|解决 TenK10K–FinnGen 差异并接入 female disease signal|
|IL12RB2 paper-grade fine-mapping|NOT_RUN|可用 summary schema 或合适的 cohort-aware covariance；当前 overall public file不通过RSS门|
|male/female 机制差异|NOT_TESTED|male 与 female 完整统计、正式交互/异质性比较；不能以 female 显著而 male 不显著替代|

## 5. 禁止主张及可替换措辞

|禁止或高风险措辞|问题|建议替换|
|---|---|---|
|“We first discovered SYNGR1 at the chr22 SSc locus.”|原论文 Supplementary Table 2 已报告 SYNGR1 coloc|“We extended prior GTEx colocalization of SYNGR1 by testing its immune-cell chromatin and expression context.”|
|“We reassigned the RPL3–PDGFB locus to SYNGR1.”|原论文已提出 SYNGR1；当前又无 disease-level signal test|“We prioritized a SYNGR1-linked module for signal-level comparison with the main-text RPL3–PDGFB annotation.”|
|“Independent replication in FinnGen and TenK10K.”|尚未证明参与者完全不重叠；两个 CS 也不相同|“Cross-resource exact coordinate-and-allele credible-set overlap.”|
|“A causal chromatin-to-expression cascade.”|coloc/link 不给出方向，且 disease link 未测|“A candidate SYNGR1-linked chromatin–expression module.”|
|“An NK-specific mechanism.”|未完成所有细胞的等覆盖比较|“An NK-cell signal in the evaluated datasets” 或在正式比较后用 “NK-enriched evidence”|
|“A female-specific molecular mechanism.”|疾病关联按性别分层，但 QTL 为 sex-agnostic|“A molecular module at a female-associated SSc locus.”|
|“PDGFB is excluded.”|PDGFB 在部分 pair 未返回或较弱，不是充分阴性|“PDGFB was not supported in the tested resource–cell combinations; incomplete coverage precluded exclusion.”|
|“Exact CS overlap proves colocalization.”|集合相交未处理 LD、完整概率分母和多信号|“Exact CS overlap motivated formal signal-level colocalization.”|
|“IL12RB2 was fine-mapped with GCST009131.”|RSS gate 失败，SuSiE 未运行|“IL12RB2 served as an engineering positive-control region; reference and signed-LD construction were reproduced.”|
|“The 2019 overall GWAS validates the female mechanism.”|不同 estimand，且与2026样本独立性未知|“The overall dataset was used only for pipeline validation.”|

另外，任何 “first” 主张都还需要在正式写稿前对相关单细胞 eQTL/caQTL、SSc fine-mapping 和 immune multiome 文献做系统检索；当前本地审计只能证明原论文与已记录竞争文献已经排除了若干宽泛的 first claim。

## 6. 三个位点的 hostile 排名

### 第一：chr22 / SYNGR1

**保留理由：** 原论文虽然已经报告 SYNGR1 broad-tissue coloc，却未把该结果解析到明确的 primary immune-cell chromatin–expression module；本项目已有强 marginal eQTL/caQTL、source peak→gene link 和经分母校准的 cross-resource exact CS overlap。这里存在真正可被证伪的增量。

**最大风险：** female disease signal 可能不与该 molecular module 共享；原 GTEx PP 可能受单因果假设影响；选峰和选细胞具有数据后选择风险；SYNGR1 的新颖性若写成 gene discovery 会被附录一票否决。

**职责：** 唯一 primary discovery locus。

### 第二：IRF4

**保留理由：** TenK10K B-naive 单成员高 PIP 提供了比 GTEx 更细的细胞假说，且 exact disease lead 便于技术审查。

**最大风险：** 原论文已有近乎 1.0 的多组织 coloc，新增空间本来就小；FinnGen exact pair 阴性使“复制”叙事不成立；可能只是资源、细胞定义、统计功效或模型差异。

**职责：** cross-resource heterogeneity / robustness locus；仅在 chr22 主链失败或 IRF4 差异被解释后升级。

### 第三：IL12RB2

**保留理由：** 区域信号清楚、历史 allele/LD 信息丰富，适合验证 harmonization、LD 和 RSS 诊断。

**最大风险：** 原论文与外部 immune-cell 研究均已高度饱和该生物学故事；当前 overall summary 又不能通过 paper-grade RSS gate。

**职责：** engineering positive control，不能占主标题、主摘要结果或主 Figure 的发现位。

## 7. 下一阶段最小可证伪目标

建议下一阶段只做一个冻结任务：

> **R4A10 / H6 — chr22 female disease-anchor falsification gate**  
> 在 `rs66578187` 上下游 500 kb 的固定 hg38 窗口内，用 2026 female SSc 区域完整统计检验其与 FinnGen l2.NK SYNGR1 eQTL、目标 peak caQTL，以及 TenK10K NK SYNGR1 eQTL 是否构成同一 signal-level module；RPL3 与 PDGFB 作为预先声明的竞争候选保留。

### 冻结输入

- disease：2026 female SSc full regional statistics；male 文件若同时取得，用于正式性别差异，不是 female 主分析的前提；
- primary cell mapping：FinnGen `l2.NK` ↔ TenK10K `NK`，明确两者不是完全同义细胞定义；
- primary gene：SYNGR1；predefined competitors：RPL3、PDGFB；
- primary peak：`chr22:39351520–39352777`（hg38）；
- disease lead：`rs66578187`, hg38 `chr22:39328807`；
- window：`chr22:38828807–39828807`，所有 indel 先经 FASTA normalization 和 build/allele 核验；
- reference：与 disease ancestry 匹配并通过 allele、order、coverage、LD 数值 QC 的 reference；
- statistics：遵循 R4A3 v5 的 multi-signal C1 门，PP.H4≥0.80 只作一个阈值，同时完整报告 H3、H4/(H3+H4)、先验敏感性和每个 signal pair。

### 一次性成败规则

1. **C1 PASS：** female disease↔SYNGR1 eQTL、female disease↔target-peak caQTL、eQTL↔caQTL 均有同一可解释 signal-level coherence；source peak→SYNGR1 link、same-cell mapping 和技术门同时通过。可以进入组织验证与正文写作。
2. **Partial A：** disease↔eQTL 通过、disease↔caQTL 不通过。可称 SYNGR1 expression-linked disease signal，不能称 chromatin cascade。
3. **Partial B：** disease↔caQTL 通过、disease↔SYNGR1 eQTL 不通过。保留 regulatory peak，SYNGR1 不是已建立的 effector gene。
4. **Molecular-only：** eQTL↔caQTL 通过，但任一 disease pair 不通过。该模块不是已支持的 SSc mechanism，chr22 主标题停止。
5. **FALSIFIED：** 在覆盖充分、LD/allele/模型均 PASS 后，disease 与两类 QTL 均无 shared signal。将 chr22/SYNGR1 降级，不扩大细胞或改窗口来救结果；再按预先规则转 IRF4。
6. **UNINFORMATIVE：** disease stats、QTL coverage、allele 或 LD 任一技术门失败。保持 NOT_TESTED，不记作阴性，也不启动 all-8 rescue。

这是一项足以改变项目走向的最小实验。female summary 未到位时，继续追加 QTL 浏览器证据不会解决核心新颖性问题；2019 overall GCST009131 也不能替代它。

## 8. 标题的精确可用措辞

### 8.1 下一阶段协议/报告标题：现在即可使用

> **Signal-level test of a SYNGR1-linked immune regulatory module at the female-associated systemic sclerosis chromosome 22 locus**

中文：

> **女性相关系统性硬化症 chr22 位点的 SYNGR1 免疫调控模块：信号级检验**

“test” 明确这是待证伪任务，不预先宣布结果。

### 8.2 仅在完整 C1 PASS 后可用于论文

首选：

> **Cell-resolved immune multiomics refines the female-associated systemic sclerosis chromosome 22 locus and implicates a SYNGR1-linked regulatory module**

更短版本：

> **Immune multiomic refinement of a female-associated systemic sclerosis locus implicates a SYNGR1-linked module**

避免使用：`discovers SYNGR1`、`reassigns RPL3–PDGFB`、`proves a causal cascade`、`female-specific regulatory mechanism`。

### 8.3 若仅得到 molecular-only 结果

> **Cross-resource immune-QTL fine-mapping prioritizes a SYNGR1-linked molecular module for testing at the systemic sclerosis chromosome 22 locus**

该标题只能作为方法/资源型短稿或阶段报告；缺少 disease anchoring 时不宜包装为完整 SSc mechanism paper。

## 9. 摘要可直接采用的措辞

### 9.1 Background

> A 2026 sex-stratified genome-wide association study identified rs66578187 as a female-associated systemic sclerosis locus, labelled by proximity as RPL3–PDGFB, and reported GTEx colocalization with SYNGR1 in whole blood and lymphocytes. The primary immune-cell context and chromatin-to-expression architecture underlying this existing SYNGR1 signal remain unresolved.

这两句同时承认原论文优先权，并明确真正未解决的问题。

### 9.2 Methods

> We integrated harmonized female systemic sclerosis regional summary statistics with population-scale immune-cell eQTL and caQTL data, source-defined peak–gene links, and cross-resource eQTL fine-mapping. We tested disease–eQTL, disease–caQTL, and eQTL–caQTL coherence at the signal level under a prespecified chr22 window, with SYNGR1 as the primary gene and RPL3 and PDGFB as predefined competitors.

只有正式取得并运行 female summary 后才能使用第一句的过去时；当前协议中应改为 `We will integrate` / `We will test`。

### 9.3 当前阶段 Results：现在可以在内部报告使用

> Public immune-QTL reanalysis showed strong rs66578187 associations with SYNGR1 expression and with an intragenic chromatin peak in NK-cell annotations. The peak had a source-defined link to SYNGR1, and its caQTL credible set shared two exact coordinate-and-allele variants with a TenK10K NK-cell SYNGR1 eQTL credible set. After restoring the complete FinnGen credible-set denominator, the shared variants accounted for 0.253 of its source probability; therefore, the overlap was treated as molecular prioritization rather than colocalization or replication. Female disease-level signal testing was not performed because the full 2026 summary statistics were not publicly accessible.

### 9.4 Results：仅在 C1 PASS 后使用的占位模板

> In the prespecified chr22 window, the female systemic sclerosis signal shared [one/two] signal(s) with the NK-cell SYNGR1 eQTL ([metric and value]) and the target caQTL ([metric and value]); the eQTL and caQTL signals were also coherent ([metric and value]). Comparable analysis of RPL3 and PDGFB showed [exact result with coverage], while sensitivity analyses across priors and LD specifications [result].

方括号必须由最终数值替换；如果竞争基因覆盖不足，应写 `could not be evaluated with comparable coverage`，不能写成阴性。

### 9.5 Interpretation：仅在 C1 PASS 后使用

> These findings refine, rather than newly identify, the SYNGR1 signal reported by the original GWAS, localizing it to an immune-cell chromatin–expression module linked to a female-associated systemic sclerosis locus. The results support SYNGR1 as an effector-gene candidate but do not by themselves establish molecular directionality or a sex-specific QTL effect.

### 9.6 若 C1 未通过

> Although a cross-resource SYNGR1-linked molecular QTL module was observed, it did not share a supported signal with the female systemic sclerosis association under the prespecified model. The data therefore do not support a disease-linked chromatin–expression cascade at this locus.

## 10. 审稿人最可能的五个攻击点及预先回答

1. **“SYNGR1 已经在原论文附录。”** 同意。全文必须引用该 PP，并把贡献写成 cell-resolved extension。
2. **“两个 CS 有交集不等于共定位。”** 同意。R4A5 已校准完整分母；正式结论只由 signal-level disease/QTL 检验决定。
3. **“你们的 QTL 不是 sex-stratified，不能称 female-specific mechanism。”** 同意。使用 `female-associated disease locus`，除非另有 QTL×sex 数据。
4. **“为何只看 NK 与这个 peak？”** 回答应是它们在 R4A3–R4A5 已被明确冻结为 primary test，并同时保留 RPL3/PDGFB 竞争和完整覆盖日志；不得在结果后改细胞或窗口。
5. **“这只是公开数据库再分析。”** 仅数据库信号不足以构成强稿。论文价值取决于正式 female disease anchoring、multi-signal robustness，以及后续独立 disease-tissue/functional validation；当前不提前承诺期刊层级。

## 11. 证据索引

- `research/ssc_access_audit.md`：Supplementary Table 2 原始定位、正式数据入口和附件完整性核查。
- `research/PMC13212417_mmc1.txt`：Supplementary Methods、Table 2 与 Table 3 文本提取。
- 工作区上级目录的 R4A3 报告：FinnGen exact-lead、peak link、覆盖与 C1 门；未随本轮轻量包重复附带。
- 工作区上级目录的 R4A5 报告：TenK10K 重算、FinnGen 完整 CS 分母与措辞校准；未随本轮轻量包重复附带。
- `repro/R4A9_independent_reference_ld_audit.md`：IL12RB2 reference/LD 独立复现。
- `repro/R4A9_independent_rss_gate.md`：overall summary RSS gate 的独立复现与 HOLD。
- 原论文：[Sex-specific autosomal susceptibility loci in systemic sclerosis](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/)。
- 竞争研究：[Tissue-resident immune cells drive genetic risk in autoimmune and lung diseases](https://pubmed.ncbi.nlm.nih.gov/42547572/)（Nature Immunology 2026；29 类 lung immune-cell eQTL，并已报告 SSc 的多基因共定位及 lung-NK-restricted IL12RB2 effects）。

## 12. 冻结判定

**Novelty status：PASS WITH MAJOR REFRAME。**

可继续的原因不是 SYNGR1 这个基因本身尚未出现，而是原论文尚未完成的 **cell-resolved disease–chromatin–expression signal test** 仍有明确空缺，并且本项目已有足够的分子证据为一次有界、可失败的 chr22 检验提供先验。只要完整 female disease signal 不支持该链，就应接受证伪并降级；在结果出来前，不再扩大“首次”“重分配”“因果级联”措辞。
