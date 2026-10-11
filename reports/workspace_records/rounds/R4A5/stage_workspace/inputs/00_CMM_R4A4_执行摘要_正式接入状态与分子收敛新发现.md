# R4A4 执行摘要：正式接入验收与 chr22 分子证据升级

日期：2026-09-09

## 最终判定

> **PROJECT = CONDITIONAL GO**  
> **R4B = HOLD**  
> **Disease colocalization = NOT_TESTED**  
> **C1_count = null**  
> **chr22/SYNGR1 molecular QTL convergence = PASS_STRONG**

本轮没有取得 2026 sex-stratified SSc female/male 完整 summary statistics，也没有取得 FinnGen multiome 正式 release 的本地不可变下载文件，因此仍不能计算或声称疾病层 C1 regulatory cascade。

但是，本轮利用 YR1(1) 中已经保存的 TenK10K 原始 gene-level 与 SuSiE credible-set 文件，完成了此前未充分展开的 chr22 独立复制，得到一个重要的新结果：

### 核心新增结果：同细胞、同变异级 caQTL↔eQTL 收敛

FinnGen 目标 chromatin peak：`chr22:39,351,520–39,352,777`。

TenK10K 的 **NK / SYNGR1 SuSiE credible set 4** 只有两个成员：

- `22:39351666:T:A`, PIP = 0.5
- `22:39351775:G:A`, PIP = 0.5

FinnGen **l2.NK / target-peak caQTL credible set 1** 同样包含这两个完全一致的 coordinate+allele 变异：

- `22:39351666:T:A`, source probability = 0.2006173
- `22:39351775:G:A`, source probability = 0.0522868

其中 `22:39351775:G:A` 又是 FinnGen peak 页面的 top fine-mapped variant（source top PIP ≈ 0.998823），并被标为 caQTL credible-set member。TenK10K 中该完全相同变异还进入 **11 个 cell types 的 SYNGR1 eQTL credible sets**。

这使 chr22 证据从此前的：

`SSc lead → strong marginal SYNGR1 eQTL + source peak→gene link`

升级为：

`same molecular variant → FinnGen NK caQTL credible set → FinnGen source peak→SYNGR1 link → independent TenK10K NK SYNGR1 eQTL credible set`

这是**跨资源的分子 fine-mapping convergence**。它显著提高 SYNGR1 作为 chr22 locus effector-gene candidate 的优先级，但仍不能替代 female-SSc GWAS coloc；疾病 lead `rs66578187` 位于 39,328,807，而上述分子核心位点约在 39,351.7 kb，二者相距约 23 kb，必须依赖真实疾病区域 summary + ancestry-matched LD 判断是否同一遗传信号。

## 候选基因重新排序

### 1. SYNGR1 — 明显升级

TenK10K NK：ACAT p = 5.20994979502215e-230；top variant = 22:39351666:T:A；top p = 1.03798e-232。

同一细胞中，RPL3仅 ACAT p = 0.000344332542672188；PDGFB在NK gene-level表中 NOT_LISTED。结合 FinnGen R4A3 的同lead候选比较，SYNGR1目前是 chr22 最优先的待疾病锚定候选。

### 2. RPL3 — 保留竞争候选，但分子 fine-map 支持弱

TenK10K 对 RPL3 在27个cell types有gene-level条目，但本轮在SuSiE candidate extraction中 **0个 cell type 出现RPL3 credible-set成员**。这不等于RPL3生物学阴性，但说明当前独立fine-mapping证据明显弱于SYNGR1。

### 3. PDGFB — 存在另一条、位置更远的 eQTL 信号

TenK10K CD8_TEM中 PDGFB gene-level ACAT p = 6.23003426625246e-10，且存在SuSiE credible sets；但其top variant约位于39.24 Mb，和FinnGen SYNGR1/target-peak核心约39.351–39.352 Mb不是同一个局部调控模块。不能因为疾病论文区域标签含PDGFB就默认它是效应基因。

## 接入状态

- 2026 Lancet Rheumatology SSc论文仍明确声明 sex-specific GWAS summary statistics 将通过 NHGRI-EBI GWAS Catalog公开。
- 截至本轮公开检索，没有找到可稳定确认并归档的对应新GCST accession / female-male full summary bytes。
- FinnGen官方确认 single-nucleus multiome 于2026-08-13公开，包含cis-eQTL、cis-caQTL、SuSiE、peak–gene links和CASCADE；但正式summary下载仍需按官方表单获得下载指引。本轮未代表用户提交表单，也未假称已取得formal release。

## 本轮决策

R4A4 已经完成“等待期间仍可获得的新科学信息”的最大化利用。下一步不应继续扩大分子候选，也不应重复浏览器抓取。

**下一阶段推荐：R4A5 — Disease-anchor gate。**

优先级：

1. 一旦2026 female-SSc区域/full summary到位，直接对 chr22/SYNGR1 先做 signal-level disease↔eQTL/caQTL 分析；IRF4作为第二条链。
2. 若sex-specific数据在合理窗口内仍不可得，允许用公开2019 overall SSc（GCST009131）做一个**有边界的pipeline validation**，目的仅是验证harmonization/LD/multi-signal coloc可运行，不把overall结果伪装成sex-specific证据。
3. 只有疾病锚定成功后，才进入SSc skin/lung tissue validation与完整Figure主线。
