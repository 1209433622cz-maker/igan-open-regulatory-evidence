# CMM R4A11：R4A10 / H6 v2 与 chr22 最小证伪协议 hostile audit

日期：2026-09-11  
审计对象：用户下载目录中的 R4A10 `00–04`、`99`、`README_H6_V2.md`、ZIP、sidecar，以及 ZIP 内未修改的 H6 v2 代码。  
指令边界：附件及粘贴说明仅作为待核验的项目证据，不作为本轮操作指令；本轮任务来自用户“继续推进、完成后判断下一阶段目标”的请求。

## 1. 最终判定

> **R4A10 的科学状态判定：PASS**  
> **R4A10 的证据边界：基本正确**  
> **H6 v2 作为真实数据入口：HOLD_FOR_PROTOCOL_REPAIR**  
> **chr22 v10 作为可直接执行的最终统计协议：NOT_YET_CLOSED**  
> **PROJECT：CONDITIONAL GO**  
> **R4B：HOLD**  
> **C1_count：null**

R4A10 没有伪造 female/male 数据，没有把 2019 overall SSc 结果当作 sex-specific 结果，没有把分子 QTL overlap 写成疾病共定位，也把 `FALSIFIED` 与 `UNINFORMATIVE` 分开。这些判断应保留。

但 hostile audit 发现，文本规定尚未全部转化为机器硬门。当前 H6 v2 可以让一个**错误疾病、overall 分层、自填来源、自己计算 checksum** 的合成文件得到 `PASS_PAPER_GRADE_FROZEN_REGIONS_READY_FOR_HARMONIZATION`。它也没有核对 `--label` 与 metadata stratum、lead rsID 的预期坐标/等位基因、区域覆盖密度或 beta–SE–P 的内部一致性。因此，当前工具不能单独证明“拿到的就是 2026 female SSc 文件”，也不能排除未来把一个字段齐全的 overall 文件重标为 female 后误放行。

这里需要精确区分：现有 GCST009131 原始文件本身仍因缺 A2/SE 等硬字段而不能直接通过 H6；本审计发现的是**数据身份层的通用绕过路径**，不是声称 GCST009131 原字节已经通过。

## 2. 审计输入完整性

- ZIP：`CMM_R4A10_H6接入冻结与门控v2_2026-09-11 (1).zip`
- 实测 SHA-256：`73155a7d837e4e19400caa92f31459afee3722a91f8635464614071be680a017`
- sidecar 声明值：完全一致；sidecar 内原始文件名没有下载器追加的 ` (1)`，不影响字节哈希。
- ZIP members：18；CRC：PASS。
- 内部 `checksums.sha256`：17/17 PASS。
- 下载目录中的 `00–04`、`99` 与 `README_H6_V2.md`：均与 ZIP 中对应文件逐字节一致。

因此下述问题属于协议/实现本身，不是附件损坏造成的假象。

## 3. R4A10 已经关闭的正确边界

1. **输入缺失不记阴性。** 2026 female/male full summary 尚未取得，故 disease-level 检验保持 `NOT_TESTED`、`C1_count=null`。
2. **旧 overall 数据不能替代目标 estimand。** `00`、`03`、`99` 均明确把 GCST009131 限定为工程诊断资产。
3. **主创新边界已纠正。** 已发表的 female SSc–SYNGR1 broad-tissue GTEx 共定位不能重新包装成“首次发现 SYNGR1”；新增问题限定为 immune-cell caQTL/eQTL signal-level module。
4. **分子证据没有越级。** exact-CS overlap 仍只是动机，不替代正式 coloc。
5. **性别表述有基本防护。** 协议正确指出“female 显著、male 不显著”不等于 sex difference；非 sex-stratified QTL 不能称 female-specific QTL mechanism。
6. **负结果出口方向正确。** Partial-A、Partial-B、Molecular-only、FALSIFIED 与 UNINFORMATIVE 被分开，且明文禁止通过改窗口、换 primary cell、挑 peak 或删除 kriging outlier 来救结果。

原论文附录说明其复现对象是 sex-stratified GWAS 与 GTEx v8，在 lead 两侧各 500 kb 内使用 COLOC，并按 female/male 分开分析；附表报告 SYNGR1 whole blood 的 female/male PP 为 0.977/0.025，EBV-transformed lymphocytes 为 0.980/0.033。R4A10 把它定位为 D0 正控而非新发现，这一点正确。原论文与附录可由 [PMC13212417](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/) 核对。

## 4. 未修改 H6 v2 的黑箱反例

本轮新建独立黑箱脚本 `adversarial_h6_v2_tests.py`，只调用 ZIP 内原脚本，不修改其代码。机器结果保存在 `adversarial_h6_v2_results.json`。

| 反例输入 | 原脚本结果 | 暴露的问题 |
|---|---|---|
| metadata 写 `phenotype=type 2 diabetes`、`stratum=overall`，provider=`self`、URL=`example.invalid`，checksum 由本地现算 | `PASS_PAPER_GRADE...`，exit 0 | 疾病、分层、来源真实性均未验证 |
| CLI `--label female`，metadata 写 `stratum=male` | `PASS_PAPER_GRADE...`，exit 0 | label 与 stratum 未绑定 |
| 两个 lead rsID 均放到 chr1，同时在 chr6/chr22 各放一个 proxy | `PASS_PAPER_GRADE...`，exit 0 | “exact lead anchor”只按 rsID 全文件计数，不核对 chr/pos/alleles |
| 全文件只有两个变异，每个冻结区域各一个 | `PASS_PAPER_GRADE...`，exit 0 | 区域非空被误命名为 paper-grade；没有覆盖/密度门 |
| chr22 行写 `beta=10, SE=0.01, P=0.5` | `PASS_PAPER_GRADE...`，exit 0 | 只做单字段范围检查，不查统计量内部一致性/模型配对 |
| 冻结区 INFO 缺失 | `CONDITIONAL...`，但 exit 0 | shell/工作流只看退出码时会把 CONDITIONAL 当成功 |

这些反例是软件 QA，不是生物学数据，也没有被用于任何科学结论。它们的作用是证明“16/16 回归测试 PASS”只说明已写入测试的分支按预期运行，不能证明门控已经覆盖错误数据身份、真实 provenance、区域充分性和统计一致性。

## 5. 关键缺口与修复优先级

### P0-1：target study / phenotype / stratum 不是硬门

`inspect_sex_specific_sumstats_base.py` 只检查 `phenotype`、`stratum` 等字段是否非空；`inspect_sex_specific_sumstats_v2.py` 的 `metadata_ok` 也只要求 metadata 不缺且 accession/provider 至少一个非空。`--label` 是任意字符串，并未与 metadata 的 stratum 比较。

因此文本中的“female SSc only”没有机器强制。一个格式完整的 overall 或其他疾病文件可以被重新写 metadata 后通过。R4A11 必须建立 target-study identity manifest，并至少硬编码/冻结：

- PMID/DOI 或最终 GCST accession 必须指向 PMID `41999721`；
- phenotype 必须为 systemic sclerosis，case definition 与论文/提供方一致；
- analysis 必须为 sex-stratified case-control GWAS；
- stratum 只允许 `female` 或 `male`，且必须与 CLI label、文件 manifest 和 provider 说明三方一致；
- sex definition 记录为原研究使用的 genotype-inferred binary sex；
- ancestry、cases、controls、cohort count、分析模型及数据 cutoff 均须来自 provider 文档；
- `overall`、GCST009131、图表逆向数据及未知分析类型一律进入 `HOLD_WRONG_ESTIMAND`。

旧协议 `03_CMM_R3_统计兼容性与冻结分析协议_v1.md` 仍把 2019 overall 写作 secondary/A3 fallback，而 R4A9/R4A10 已禁止替代。最新 master protocol 必须显式写明：**R4A10/R4A11 supersede 旧 A3 fallback；GCST009131 只能用于工程控制，永远不能满足 D0/D1/E1/M1/C1。** 否则历史文件之间仍留有解释空间。

### P0-2：checksum 证明完整性，不证明来源真实性

当前 `expected_sha256`/`expected_md5` 与被检文件匹配即可 PASS；程序无法区分该值来自 provider，还是下载后由操作者自己计算。测试套件本身用 `example.invalid`、`provider=synthetic` 和本地现算 SHA-256 获得 PASS。

R4A11 应把哈希拆成：

- `provider_checksum`：来自 Catalog manifest、FTP checksum 或作者签发 manifest；
- `receipt_sha256`：首次接收后本地冻结，用于后续 chain-of-custody；
- `checksum_evidence_uri_or_file`：保存 checksum 的原始来源；
- `transfer_type=public_catalog|author_transfer`。

公开 Catalog 文件缺 provider checksum 时不能把自算 SHA 冒充 provider checksum。作者直传若没有预先哈希，可用邮件/传输记录建立来源证据，再将本地首次哈希明确标为 receipt hash。

### P0-3：build 与 exact lead anchor 仍可伪 PASS

assembly gate 只读取 metadata 字符串。lead gate 则只要全文件中出现目标 rsID 就计数，不核对它是否位于：

- `rs12203592 = chr6:396321@GRCh38`；
- `rs66578187 = chr22:39328807@GRCh38`；
- 预期的 REF/ALT/等价 left-normalized indel 表达。

黑箱测试把两个 rsID 放到 chr1 仍然 PASS。修复后，anchor 必须按 `chr:pos:REF:ALT@assembly` 判断，rsID 只作辅助；每个 anchor 必须唯一，并用固定版本 GRCh38 FASTA/dbSNP映射核对。若输入是 GRCh37，应先保留原坐标、使用冻结 chain liftover、删除 multi-map/unmapped，再按 FASTA 重新校验，不能通过把 metadata 改写为 GRCh38 解决。

R4A2 的 left-normalization、palindromic SNP、indel、effect orientation 规则方向正确，但 R4A10 包内没有可执行的 normalization spec。R4A11 应冻结 FASTA 文件名与 checksum、bcftools/version、`norm -m-any -f` 或等价命令、multi-allelic 拆分、重复 normalized key、strand-ambiguous 与频率冲突阈值、所有 drop reason。

### P0-4：`PASS_PAPER_GRADE` 没有 coverage 含义

当前代码只要求两个区域各至少一行且 lead rsID 出现；官方 coloc 文档明确要求一个区域内的**稠密 SNP map**，不能用单变异或按显著性筛选的稀疏集合代替。参见 coloc 官方的 [data structures](https://chr1swallace.github.io/coloc/articles/a02_data.html) 与 [FAQ](https://chr1swallace.github.io/coloc/FAQ.html)。

R4A10 文本又说 H6 PASS 只允许进入后续 coverage 检查，所以状态名本身比实际证据高一级。应改为：

`PASS_INTAKE_SCHEMA_READY_FOR_NORMALIZATION_AND_COVERAGE_AUDIT`

coverage 在共同变异、lead/credible-set 保留、区域密度、各源 eligible denominator 均完成前必须是 `PENDING`。它不能包含 `PAPER_GRADE`。任何按 P 值裁剪、只交 top hits、LocusZoom 逆向或只有 anchors 的区域文件均不得进入 coloc。

### P0-5：CONDITIONAL 返回 exit code 0

H6 v2 第 173 行把 PASS 和 CONDITIONAL 都返回 0。文本虽然要求 CONDITIONAL 先补信息，但自动工作流通常把退出码 0 当作允许继续。这是明确的工程旁路。

应采用互斥退出码并在 orchestration 层同时断言 JSON exact status：

- `0 = exact PASS`；
- 非零独立码 = `CONDITIONAL`；
- 非零独立码 = `HOLD/FAIL`。

在 R4A11 回归测试中，任何非 exact PASS 都必须使下游 harmonization runner 停止。

### P1-1：sample design gate 不足以支持 fine-mapping/RSS

当前 wrapper 在 `bare_n_semantics=cohort_count` 时，只要 metadata 有正的 cases/controls 就返回 PASS；它没有把裸 N 的行值重新验证为整数/合理 cohort 范围，也没有核对 total、每变异 cohort composition 或 N 与元数据的关系。R4A10 测试甚至把每行 `N=20150` 声明为 cohort count 后仍期待 PASS。

对 15-cohort meta-GWAS，只有 cohort count 不能恢复每个变异的有效样本结构或协方差。既往 overall 数据已展示变异依赖的 cohort participation 会造成 z–LD/RSS mismatch。因此：

- `cohort_count` 不应等价于 paper-grade sample-size PASS；最多允许进入 `COVERAGE/RSS_PENDING`；
- 必须区分 `N_total`、`N_eff`、cases/controls、contributing cohorts，并冻结各字段含义；
- 若 N 为 cohort count，逐行必须为整数且不超过研究总 cohort 数；
- 若 N 为 sample size/Neff，需核对范围、是否逐变异变化和 provider 定义；
- metadata 需记录 fixed-effect/RE2/Han–Eskin/ASSET 中哪一组 beta、SE、P 被使用，禁止把不同模型的列拼成一行；
- 最理想输入是 cohort participation matrix 或 cohort-level summary；缺失时 external-LD 分支必须经过 RSS 门，失败即 `UNINFORMATIVE/HOLD`。

### P1-2：beta、SE 与 P 没有一致性检查

当前门只分别检查 beta 有限、SE>0、P∈[0,1]。黑箱输入 `beta=10, SE=0.01, P=0.5` 仍然 PASS。这可能代表列映射错误、OR/logOR 混用或 beta/SE 与 random-effect P 来自不同模型。

R4A11 应计算 `z=beta/SE` 与双侧 P 的一致性指标。若 provider 明确说明 P 来自不同模型，则必须为每列记录 model ID，primary fine-mapping 固定使用一套匹配 beta/SE；无法解释的不一致进入 HOLD。OR 必须先按 provider 语义转为 log(OR)，SE 的量纲必须与其相同。

### P1-3：D0 窗口在版本链中漂移

原论文使用 **总长 1 Mb，即 lead ±500 kb**。R4A9 D0 也明确冻结 ±500 kb；R4A10 `04` 的总冻结区却为 ±1 Mb，且没有为 D0 单列窗口。如果直接沿用总冻结区，便不是原论文正控复现，窗口改变还会改变 coloc hypothesis priors 与 posterior。

应同时冻结两个互不混用的对象：

- `D0_REPRODUCTION_WINDOW = rs66578187 ±500 kb`，只复现原文 single-causal COLOC；
- `PRIMARY_MECHANISM_WINDOW = rs66578187 ±1 Mb` 或一个在看结果前确定的 LD boundary，用于 D1/E1/M1；
- ±500 kb/±2 Mb 只能是预先声明的 sensitivity，不能替换 primary 决策。

### P1-4：COLOC/SuSiE 尚未达到可执行规范

`04` 要求 multi-signal handling、H3/H4、priors sensitivity，却没有冻结：软件版本、输入对象、case-control参数、每个 QTL 的 sample size/sdY、`L`、prior variance、convergence、CS coverage/purity、LD 矩阵来源、每个 trait 是否使用自己的 LD、primary priors、sensitivity grid 与 pass/fail rule。

官方 coloc 文档说明 `coloc.abf` 假设每个 trait 在区域内至多一个 causal variant；`coloc.susie` 才允许多信号并要求带正确 SNP 次序/等位基因方向的 LD。参见 [coloc SuSiE vignette](https://chr1swallace.github.io/coloc/articles/a06_SuSiE.html) 和 [`coloc.susie` reference](https://chr1swallace.github.io/coloc/reference/coloc.susie.html)。`coloc` 的默认 priors 是 `p1=1e-4, p2=1e-4, p12=1e-5`，而 prior sensitivity 必须围绕事前可辩护范围判断，不能在结果后选最漂亮的 p12。[官方 sensitivity 文档](https://chr1swallace.github.io/coloc/articles/a04_sensitivity.html)

R4A11 应生成一个机器可读 `analysis_manifest.json`，冻结 D0 与 D1/E1/M1 的所有上述参数。沿用既有项目门时，RSS 至少保留 `estimate_s<=0.1 AND max|kriging standardized residual|<=5`、不删 outlier 的规则；如果要采用新版 susieR 的 finite-reference/mismatch correction，必须在看到 female 结果前完成模拟/正控验证并冻结为 primary 或 sensitivity。官方 susieR 文档强调 external LD mismatch 会制造不可靠/额外信号，并要求检查相应诊断：[RSS diagnostic](https://stephenslab.github.io/susieR/articles/susierss_diagnostic.html)、[`susie_rss` reference](https://stephenslab.github.io/susieR/reference/susie_rss.html)。

### P1-5：三个 pairwise coloc 不自动构成一条三方链

在多信号区域，以下三项可以分别由三个不同 signal pair 通过：

- disease signal 1 ↔ eQTL signal A；
- disease signal 2 ↔ caQTL signal B；
- caQTL signal C ↔ eQTL signal D。

三个 pairwise `PP.H4` 都高，也不必然存在同一个 disease–caQTL–eQTL 三方 signal。C1 当前使用“形成一致解释”，仍有主观升级空间。

必须建立 signal registry，记录每个 trait 的 signal ID、CS、PIP 分母、LD、signal-pair posterior；C1 只在同一组兼容 signal 构成闭合三角时通过，或由预冻结的 multi-trait joint model支持。只取每条边最大 H4 再拼接，禁止计 C1。

建议在 R4A11 正式冻结 edge 状态：

- `SHARED`：primary prior 下 `PP.H4>=0.80`，同时 H4 相对 H3 的条件证据达到预冻结阈值，且合理 prior grid 不翻转结论；
- `DISTINCT`：两个 trait 均有充分信号与覆盖，且 H3 达到预冻结阈值；
- `INCONCLUSIVE`：H0/H1/H2、低功效、覆盖或 LD 使 shared 与 distinct 都不能确定；
- `UNTESTABLE`：技术硬门失败。

仅 `H4/(H3+H4)` 高而绝对 H4 低不能算通过。

### P1-6：primary eQTL、cell mapping 与 candidate set 未完全冻结

R4A10 冻结了 FinnGen `l2.NK` caQTL peak，但 C1 的 “SYNGR1 eQTL” 没有唯一指定 primary resource：FinnGen l2.NK、TenK10K NK 与 GTEx broad-tissue 承担不同角色。若数据结果出来后再选择资源，会形成结果后选择。

R4A11 必须在 disease data 到达前选择一条唯一 primary triangle，例如：

`2026 female GWAS + FinnGen l2.NK target-peak caQTL + 预指定的 NK/SYNGR1 eQTL dataset`

并为每条边冻结 release、phenotype ID、cell definition、sample size、summary/CS 文件 hash。GTEx whole blood/EBV 只属于 D0；它不能单独满足 cell-resolved C1。TenK10K 若作为 independent replication，就不能在 primary FinnGen 失败后临时改成 primary。FinnGen l2.NK 与 TenK10K NK 应保持“可比 lineage、非完全同义标签”。

NK 和 target peak 是依据已观察的强分子 QTL 选择的，因此 M1/QTL coherence 是 selection-conditioned 支持；真正尚未观察、可证伪的新增检验是 female disease signal 对预定分子信号的共享。报告必须披露这一点。

CD8 TEM 必须无论 NK 成败都按 secondary 层报告，且不能在 NK 失败时升级成 primary C1。`source-linked genes` 应在看 disease 结果前把现有 peak-link 文件中的完整名单、gene ID、纳入规则和 hash 冻结；不能在结果后改变“bounded”集合。SYNGR1、RPL3、PDGFB 需按同一窗口/QC/框架比较，但 `NOT_RETURNED` 和低覆盖不能当作对 SYNGR1 的阴性竞争优势。

### P1-7：male comparator 有正确原则，但没有客观状态机

“male control 与 power 差异合理解释”不是可重复的判据。应预先定义：

- male 使用同一 target study、窗口、normalization、variant eligibility、LD/RSS、priors 和模型；
- lead/区域效应差异使用正式 heterogeneity/interaction 统计，不能用显著/不显著之差；
- female shared、male 无 shared 但 male power不足时，状态为 `SEX_DIFFERENCE_UNRESOLVED`；
- female 和 male 均 shared 时，仍可称 “immune regulatory module at a female-associated locus”，但不能称 female-specific mechanism；
- 只有正式 effect heterogeneity/interaction 与可比技术门支持时，才允许 female-predominant/specific 主张。

原研究已经采用 Cochran Q、genotype×sex interaction、ASSET 与 PPR 来定义 sex-specific locus；新项目应明确是复用原论文性别定位，还是另外检验机制层 sex difference，不能把两者混为一项。

### P1-8：FALSIFIED 仍缺“充分检验”的数值定义

R4A10 把 technical failure 归为 UNINFORMATIVE 是正确的，但“coverage/LD/allele/model 均充分”与“不共享”没有机器阈值。低 H4 可能来自 H0/H1/H2，而不是 H3；不能一律称 falsified。

最终状态应由 edge-level 状态组合：

| Disease↔eQTL | Disease↔caQTL | caQTL↔eQTL | 允许结论 |
|---|---|---|---|
| SHARED | SHARED | SHARED，且同一 signal triangle | C1 候选；仍需 peak→gene、competition、male/claim gate |
| SHARED | DISTINCT | 任意 | Partial-A；禁止 chromatin cascade |
| DISTINCT | SHARED | 非 SHARED | Partial-B；不确认 SYNGR1 effector |
| 非 SHARED | 非 SHARED | SHARED | Molecular-only；禁止 SSc mechanism |
| 两条 disease edge 均为 DISTINCT，且所有技术/功效门充分 | — | — | chr22 hypothesis FALSIFIED |
| 任一必需 edge 为 INCONCLUSIVE/UNTESTABLE | — | — | UNINFORMATIVE/NOT_TESTED，不能记阴性 |

此外，历史协议允许在 chr22 与 IRF4 都被充分否定后进行一次 all-8 rescue，而 R4A10 又强调不得通过 all-8 无限救结果。最新版需明确二选一。最稳妥的主论文规则是：chr22 primary 与 IRF4 secondary 都失败后进入 `PIVOT_NOVELTY_INSUFFICIENT`；all-8 若保留，只能成为预先列出 8 loci、固定方法和多重性控制的独立探索分析，不能反向升级原 primary claim，也不能无独立验证直接 GO_R4B。

## 6. 分项结论

| 审计域 | 当前结论 | 是否可直接执行 | 主要原因 |
|---|---|---:|---|
| 发布包完整性 | PASS | 是 | ZIP/sidecar/内部 hash 均一致 |
| 科学状态与 claim boundary | PASS | 是 | HOLD、NOT_TESTED、C1 null 均正确 |
| 输入 schema/数值范围 | PARTIAL PASS | 否 | 已有基础门，但身份、统计一致性可绕过 |
| phenotype/sex/estimand identity | FAIL | 否 | metadata 只检查非空，label 不绑定 stratum |
| provenance/checksum | PARTIAL | 否 | 完整性可证，provider真实性不可证 |
| build/allele/anchor | PARTIAL | 否 | assembly 自报；lead 不核对坐标/alleles；normalization未冻结 |
| sample design | FAIL_FOR_RSS | 否 | cohort count 可直接 PASS，未恢复有效 N/参与结构 |
| regional coverage | PENDING | 否 | 一行/区域即可得到 “paper-grade” 状态 |
| LD/RSS | CONCEPTUALLY CORRECT | 否 | 禁删 outlier 正确，但 target branch参数/版本未完整冻结 |
| D0 published coloc reproduction | PARTIAL | 否 | 角色正确；±500 kb 与 ±1 Mb 版本冲突需拆开 |
| D1/E1/M1 multi-signal coloc | NOT EXECUTABLE | 否 | resource、LD、SuSiE、priors、signal aggregation未定 |
| candidate/cell selection | PARTIAL | 否 | NK/peak已冻；eQTL resource及 bounded gene registry未完全冻 |
| male comparator | PARTIAL | 否 | 原则正确，缺客观状态/interaction规则 |
| C1/GO/HOLD | PARTIAL | 否 | 边齐全，但三方 signal identity 与数值门未闭合 |
| falsification/negative policy | STRONG BUT INCOMPLETE | 否 | 分类合理，adequate evidence/edge-negative 未量化 |
| old overall substitution防护 | TEXT PASS / CODE FAIL | 否 | 文本禁止，机器不能验证 target study/stratum |
| post hoc rescue防护 | PARTIAL | 否 | 禁改 window/cell/peak；all-8 最终角色仍需定案 |

## 7. R4A11 可执行目标

下一阶段不应直接跑疾病 coloc，而应冻结为：

> **R4A11 — H6 v3 Identity/Anchor/Coverage Hardening + Analysis Manifest Lock**

### A. 先修 H6 v3，完成以下验收

1. target study、phenotype、analysis type、female/male stratum、label、sample counts 与 provider evidence 建立交叉硬门；明确拒绝 overall。
2. provider checksum 与本地 receipt hash 分开；保存 checksum 原始证据。
3. exact anchor 改为 GRCh38 coordinate+normalized alleles+rsID 联合校验。
4. PASS 状态更名为 schema/intake ready；coverage 在下一门完成前保持 PENDING。
5. `CONDITIONAL` 返回非零，runner 只接受 JSON exact PASS。
6. sample/cohort count 按声明语义重新验证，不能只看 metadata 正数。
7. 新增 beta–SE–P/model coherence 审计。
8. 将本轮六个黑箱反例全部加入回归套件，期望错误 trait/overall、label mismatch、错位 anchors 与自报不可信 provenance 均被 HOLD；两行区域不得得到 paper-grade；CONDITIONAL 不得触发下游。

### B. 冻结唯一 master analysis manifest

manifest 应显式 supersede R3–R4A10 中冲突条款，并包含：

- D0 精确 ±500 kb，D1/E1/M1 精确 primary window 与 sensitivity windows；
- female/male 文件身份、source、hash、build、model、N semantics；
- primary caQTL/eQTL release、cell、peak、gene IDs；
- secondary CD8 TEM 与 TenK10K 的固定角色；
- 全部 bounded competitors 列表与 hash；
- FASTA/normalization、variant matching、palindromic/indel/drop rules；
- coverage denominators与 PASS/HOLD 阈值；
- disease/QTL 各自 LD 来源、reference sample数、variant顺序与 signed-allele规则；
- RSS、SuSiE、coloc 的软件版本和全部非默认参数；
- p1/p2/p12 primary 与 sensitivity grid；
- signal-pair到三方 triangle 的聚合规则；
- male heterogeneity/interaction 与 claim wording gate；
- C1、Partial、Molecular-only、FALSIFIED、UNINFORMATIVE 的机器表达式；
- 明确 all-8 rescue 是取消，还是独立探索且不能救 primary。

### C. 数据尚未到达时的完成条件

- H6 v3 hostile tests 全部按预期拦截；
- master manifest 写入 SHA-256 并只允许通过版本化 amendment 修改；
- 使用合成数据跑通状态机，但不生成生物学 posterior；
- 项目继续 `HOLD_EXTERNAL_ACCESS`、`C1_count=null`。

### D. 真实 female/male 字节到达后的固定 DAG

```text
raw-byte receipt freeze
  → target-study/stratum/provenance identity gate
  → H6-v3 schema gate
  → GRCh38 FASTA normalization + allele orientation
  → dense regional coverage gate
  → study-specific/specified external signed-LD gate
  → z–LD/RSS diagnostics
  → D0: original ±500 kb single-causal COLOC reproduction
  → female disease fine-mapping
  → D1: disease↔primary NK caQTL
  → E1: disease↔primary NK SYNGR1 eQTL
  → M1: primary caQTL↔eQTL
  → same-signal triangle check
  → frozen candidate competition
  → matched male analysis + heterogeneity/claim gate
  → C1 / Partial / FALSIFIED / UNINFORMATIVE
```

D0 只验证输入与原论文方向可复现，不能满足 cell-resolved C1。任何上游 HOLD 都必须把所有下游状态保持为 `NOT_RUN/NOT_TESTED`，不能写 0，也不能用 GCST009131、改窗口、换 primary cell、选 secondary 阳性或删除异常变异继续。

## 8. 本轮产物与可复核性

- 主报告：`H:\SCI2\YR1\R4A11\protocol\R4A10_protocol_hostile_audit.md`
- 黑箱测试脚本：`H:\SCI2\YR1\R4A11\protocol\adversarial_h6_v2_tests.py`
- 黑箱机器结果：`H:\SCI2\YR1\R4A11\protocol\adversarial_h6_v2_results.json`
- 审计副本：`H:\SCI2\YR1\R4A11\protocol\r4a10_zip_extracted\`；仅用于逐行核对，原下载文件未修改。

本轮没有运行 female/male fine-mapping、COLOC、SuSiE 或 C1 计数，因为目标 summary-statistics 字节仍未取得。所有反例仅用于验证门控是否能拒绝错误输入。
