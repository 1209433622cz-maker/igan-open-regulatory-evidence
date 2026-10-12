# CMM R3 — SSc 创新性 Hostile Audit：同构论文排雷与可守住的创新边界

**日期**：2026-09-05  
**审计问题**：如果今天把 R2 设计直接投稿，审稿人会不会说“这些事情别人已经做过”？

---

## 1. 总体判断

> **SSc + genetics + single-cell/multiome 本身已经不是空白。**

但是：

> **2026 sex-specific SSc GWAS × population-scale immune caQTL/eQTL regulatory cascade × independent QTL replication × untreated SSc tissue concordance** 这一更窄的交叉问题，本轮没有发现已经被完整做完的直接同构论文。

因此：

**Novelty = PASS, but only after claim narrowing.**

---

## 2. 最危险的直接竞争论文

### 2.1 2026 Lancet Rheumatology sex-specific SSc GWAS

这篇论文不是我们的“数据源文章”这么简单，它已经主动往功能机制走了很远。

原文已包含：

- positional mapping；
- eQTL/sQTL；
- pQTL；
- chromatin interaction；
- Open Targets V2G；
- regulatory colocalization；
- SSc whole-blood sex-DEG；
- drug repurposing。

并报告：

- male-specific BCL11A；
- female-specific IRF4；
- female-specific RPL3-PDGFB；
- 5 previously known loci characterized as female-specific；
- 39 candidate genes；
- 5 sex-DEGs：IL12RB2, ARHGAP31, UBL7, CSK, MPI；
- fostamatinib / dasatinib。

### 审稿攻击
> “The submitted study largely re-annotates loci and candidate genes reported by Rodriguez-Martin et al.”

### 我们的防线
不能用同样的证据层。必须证明：

1. **which immune cell**；
2. **which causal/regulatory peak**；
3. **whether chromatin and expression molecular QTLs share the disease signal**；
4. **whether the same direction/target replicates in an independent population-scale sc-eQTL cohort**；
5. **whether that genetically resolved program is actually remodeled in untreated SSc skin**。

换句话说：从 `candidate gene prioritization` 升级为 `cell-resolved regulatory mechanism resolution`。

---

## 3. SSc疾病组织 multiome 已有人做：不能把“snATAC+snRNA”本身当创新点

### 3.1 JCI Insight 2026 — early untreated SSc skin

10 SSc + 4 controls；snRNA+snATAC；10 SSc Visium；7F/3M SSc。

主要结论：

- proinflammatory vascular niche；
- macrophage–fibroblast interaction；
- PDGF / TGFB；
- PI3K/AKT/mTOR；
- IL6/JAK/STAT；
- disease-specific fibroblast states。

**风险**：如果我们的组织层只是重新找 fibroblast、macrophage、PDGF/TGFβ，会变成“重复已有biology”。

**正确使用方式**：

> 不重新发现该数据集的主题，而是把遗传层事先冻结的 Tier-1 target/cascade 投射进去，问“遗传调控链是否在疾病组织中被观察到”。

---

### 3.2 SSc-ILD lung multiome / chromatin papers (2026)

2026已有SSc-ILD肺脏多组学研究对 AP-1/RUNX/EGR chromatin dynamics、endothelial state等进行深入解析。

**风险**：不能笼统声称“首次使用single-cell chromatin揭示SSc调控机制”。

**防线**：我们的 primary tissue 是skin，primary discovery不是case-control ATAC，而是 population genetic molQTL；组织层只作为疾病环境验证。

---

### 3.3 早期SSc-ILD GWAS × ATAC overlap工作

已有研究把 2019 SSc GWAS（GCST009131）risk SNP/LD proxies 与 cell-type open chromatin peaks做overlap。

**风险**：`risk SNP overlaps ATAC peak` 不够新，也不够因果。

**防线**：必须使用：

- caQTL effect；
- eQTL effect；
- fine-mapped credible signals；
- multi-signal colocalization；
- peak–gene link；

而不是简单bedtools overlap。

---

## 4. 方法学环境也在快速升级

### 4.1 FinnGen CASCADE
FinnGen multiome资源本身已经建立 `chromatin → expression` cascade概念，并将其用于大量疾病colocalization。

因此我们不能声称“提出了CASCADE框架”。

我们真正的增量是：

> 将该高分辨率资源用于**最新sex-stratified SSc genetic architecture**，再与真实疾病组织正交整合，并建立 sex-locus-specific biological interpretation。

---

### 4.2 TenK10K causal atlas
TenK10K团队已经对28类免疫细胞sc-eQTL与大量复杂疾病/biomarkers做了大规模MR/causal mapping。

因此“TenK10K + MR 找SSc靶点”单独不足以构成强新稿。

R3冻结：

> TenK10K = replication，not discovery novelty.

---

### 4.3 CASTIE / context-dependent eQTL（2026-08）
最新方法开始显示 static cell-type eQTL 会遗漏 context-dependent genetic effects，包括sex/context interaction。

这对本项目是双刃剑：

- **风险**：审稿人可能质疑“为什么讨论sex biology，却只用sex-adjusted static eQTL”。
- **机会**：可以把 context-dependent eQTL作为高级 sensitivity / discussion；若公开summary可直接检查关键loci，则更强。

**但不建议**让CASTIE成为主依赖，因为它会再次引入新数据和方法复杂度，削弱主故事。

---

### 4.4 Tissue-resident immune eQTL (Nature Immunology 2026)
组织驻留免疫细胞 eQTL 已证明 disease associations有相当部分无法由外周血静态免疫eQTL完全解释。

**风险**：FinnGen PBMC-like immune multiome并不等于skin-resident immune regulation。

**应对**：

- 明确 FinnGen 定义的是 inherited immune regulatory architecture；
- GSE312129 定义 disease-tissue state；
- 不把外周molQTL说成skin-specific QTL；
- 对关键target检查tissue-resident eQTL/eQTL Catalogue/GTEx作为补充，而不是替换主分析。

---

## 5. 2026可守住的创新陈述

### 推荐主claim
> We resolve sex-biased systemic sclerosis susceptibility loci into cell-type-specific chromatin-to-expression regulatory cascades and test whether these genetically anchored programs are recapitulated in untreated diseased skin.

### 可以声称的新增层（如果数据最终支持）
1. 将 sex-stratified SSc GWAS 与 33-cell population multiome QTL首次系统整合；
2. 从“candidate gene”提升到“variant–peak–gene–cell”调控链；
3. 用独立TenK10K sc-eQTL验证 target/cell direction；
4. 用 early untreated SSc skin multiome 验证 disease-state concordance；
5. 区分 male/female genetic loci 在不同 immune regulatory contexts 中的作用路径。

### 暂时不要声称
- first single-cell study of SSc；
- first multiome study of SSc；
- first GWAS functional study of SSc；
- first colocalization study of SSc；
- first drug repurposing study of sex-biased SSc；
- causal mechanism仅凭expression/ATAC concordance；
- sex-specific tissue mechanism，除非有充分sex interaction统计支持。

---

## 6. 最重要的写作策略变化

### 原R2故事
“性别GWAS发现 → multiome解释 → tissue验证”

### R3建议故事
“**一个新遗传发现已经存在，但其细胞和调控机制仍未被解析** → population molQTL resolution → independent replication → disease-context test”

Introduction要刻意承认Rodriguez-Martin et al.做得很完整：

1. SSc有强sex bias；
2. 2026 GWAS首次解析了sex-specific autosomal loci；
3. **但这些loci如何在具体immune cell中通过chromatin-to-expression regulation作用仍未解决**；
4. bulk/tissue annotations不能等价于cell-resolved inherited regulatory mechanism；
5. 本研究填这个缺口，并在untreated SSc tissue中检验其疾病相关性。

这样不会显得在抢原论文贡献，反而自然站在它上面继续推进。

---

## 7. Hostile-review评分

| 维度 | R2原方案 | R3收窄后 |
|---|---:|---:|
| 数据新颖性 | 8.5/10 | 9/10 |
| 问题新颖性 | 7.5/10 | 8.5/10 |
| 与2026 sex-GWAS重叠风险 | **高** | 中低 |
| 与SSc skin multiome重叠风险 | 高 | 低中 |
| 因果/调控可信度 | 7/10 | 8.5/10 |
| disease-context闭环 | 8/10 | 9/10 |
| 可执行性 | 8/10 | 7.5/10（受GWAS access hard gate影响） |
| 潜在Q1竞争力 | 中高 | **高（若Tier-1 cascades成立）** |

---

## 8. Novelty GO判据

继续SSc需要同时满足：

- [ ] sex-specific full summary stats可获得；
- [ ] 至少2个sex-specific loci存在高可信molQTL共享信号；
- [ ] 至少1个完整 variant→peak→gene→cell cascade；
- [ ] 至少1个独立QTL replication；
- [ ] 至少1个Tier-1 cascade在SSc tissue有正交支持；
- [ ] 文献更新检索未出现“sex-specific SSc × FinnGen multiome cascade × skin validation”直接同构预印本/论文。

如果最后一项在项目过程中变化，必须重新做novelty audit，不能因为已经跑了数据而无视新论文。

---

## 9. 结论

> **SSc仍值得做，但必须从“multiomics paper”升级成“genetically anchored regulatory mechanism paper”。**

这是R3最核心的创新性结论。
