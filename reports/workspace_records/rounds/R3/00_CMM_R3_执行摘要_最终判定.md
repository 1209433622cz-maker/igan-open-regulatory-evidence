# CMM R3 — Systemic Sclerosis Data & Novelty Preflight

**版本**：R3 / 2026-09-05  
**目标**：在进入任何大规模计算之前，对上一轮 TOP1（sex-biased systemic sclerosis regulatory cascade）进行真实数据入口、统计兼容性、创新性和可执行性审计。  
**本轮性质**：hostile preflight，不以“证明项目能做”为目标，而以尽早发现会导致论文失效的硬伤为目标。

---

## 1. 一句话结论

当前项目判定不是无条件 GO，而是：

> **CONDITIONAL GO — HOLD SEX-SPECIFIC PRIMARY ANALYSIS UNTIL FULL GWAS SUMMARY STATISTICS ARE ACTUALLY RETRIEVED**

中文解释：

> **总体研究方向值得继续，数据生态足够强，创新窗口仍存在；但以“性别特异SSc遗传机制”为主标题的正式主分析必须暂缓，直到 2026 Lancet Rheumatology 性别分层 SSc GWAS 的完整 female/male summary statistics 被真实下载、字段核验并通过 harmonization 预检。**

这不是轻微手续问题，而是一个**硬门（hard gate）**：只有 lead SNP 和论文中的候选基因表，不足以可靠完成 locus-level fine-mapping、multi-signal colocalization、caQTL/eQTL/GWAS三层共享信号判断。

---

## 2. 与 R2 相比，本轮最重要的五个更新

### 2.1 FinnGen multiome 从“未来资源”变成“当前可用资源”
FinnGen 官方页面已明确：single-nucleus multiome 于 **2026-08-13 public release**。资源包括：

- 1,108 individuals；
- 10,612,211 snRNA nuclei；
- 7,100,899 snATAC nuclei；
- 33 immune cell types；
- 27,294 genes；
- 297,024 accessibility peaks；
- 17,167,198 variants；
- cis-eQTL / cis-caQTL；
- SuSiE fine-mapping；
- peak–gene links；
- CASCADE categorization；
- GWAS colocalization；
- per-cell-type ATAC tracks。

因此下一代 `variant → chromatin → gene → cell type` 结构在数据层面是现实的，而不是概念设计。

官方入口：<https://www.finngen.fi/en/access_results>

### 2.2 2026 sex-specific SSc GWAS 的“论文公开”不等于“summary stats 已被我们取得”
论文：Rodriguez-Martin et al., *The Lancet Rheumatology*, 2026；PMID 41999721。

论文明确写道：sex-specific meta-analysis summary statistics 将通过 NHGRI-EBI GWAS Catalog 发布，并建议检索“systemic sclerosis”。本轮多种方式按题名、PMID、DOI、GCST检索，**截至本次审计仍未解析到可确认的该研究 GCST accession / 可直接下载的 male/female 全量 summary statistics**。

因此状态必须写成：

- publication：**GREEN**；
- data availability statement：**GREEN**；
- actual file retrieval in our workflow：**RED/PENDING**。

不能把“作者承诺公开”写成“我们已经有数据”。

论文：<https://pubmed.ncbi.nlm.nih.gov/41999721/>  
全文：<https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/>

### 2.3 R2 对疾病组织数据的一个候选需要纠正：GSE312591 不是主疾病图谱
R2 曾将 GSE312591 列入疾病组织候选。本轮核查后应纠正：它主要是 **SSc fibroblast RUNX1 siRNA perturbation**，不是广泛的 SSc vs healthy case-control atlas。

因此它的正确定位是：

> **如果 RUNX1 恰好成为遗传优先靶点，可作为机制扰动证据；否则不进入主线。**

### 2.4 更强的疾病组织主数据集已经确认：GSE312129
GSE312129 / JCI Insight 2026：

- early, untreated diffuse cutaneous SSc；
- 10 SSc + 4 age/sex-matched healthy controls；
- SSc sex distribution：7 female / 3 male；
- paired snRNA + snATAC；
- 34,525 nuclei（论文QC后）；
- 12 major cell types；
- 10 SSc Visium sections；
- raw GEO tar ~54.3 GB；
- assembly hg38。

这比 R2 原先的单纯 scRNA 候选更适合做**疾病组织层的正交验证**。

但它不能承担 population QTL，因为没有 1,000+ donor genotype-QTL设计；正确角色是：

> **验证 FinnGen 遗传调控级联中优先的 gene/cell program 是否在真实 SSc 组织中呈现 disease-state concordance。**

GEO：<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE312129>

### 2.5 创新性门槛比 R2 判断得更高
2026 的竞争环境已经出现：

- SSc skin snMultiome + spatial；
- SSc-ILD lung multiome；
- SSc GWAS risk SNP × cell-type ATAC overlap；
- population-scale multiome QTL/CASCADE；
- context-dependent single-cell eQTL；
- 28-cell TenK10K causal eQTL atlas；
- tissue-resident immune-cell eQTL disease colocalization。

所以“我们整合了很多组学”本身不是新颖性。

真正可守住的论文中心必须缩成：

> **Sex-biased SSc loci are resolved into cell-type-specific chromatin-to-expression regulatory cascades using population-scale molecular QTLs and then tested for concordance in untreated SSc tissue.**

---

## 3. 当前证据链可行度

| 证据层 | 首选资源 | 状态 | R3判断 |
|---|---|---:|---|
| Sex-specific SSc GWAS | 2026 Lancet Rheumatology | 🔴 PENDING | **硬门：尚未取得全量stats** |
| Overall SSc GWAS fallback | GCST009131 (2019) | 🟢 | 可立即用于非性别主线/管线调试 |
| caQTL/eQTL discovery | FinnGen snMultiome | 🟡→🟢 | 已公开；需表单获取下载说明 |
| Fine-mapped molQTL | FinnGen SuSiE | 🟡→🟢 | 资源声明可用；需真实文件核验 |
| Independent eQTL replication | TenK10K | 🟢 | Zenodo open |
| Disease skin multiome | GSE312129 | 🟢 | 主组织验证首选 |
| Independent skin scRNA/spatial | GSE249279 | 🟢 | 第二疾病组织复制 |
| Small IFN/endothelial skin scRNA | GSE236111 | 🟢 | 小样本、靶向验证 |
| High-res spatial | GSE312932 Xenium | 🟢 optional | 仅10个SSc，无HC；定位而非DE |
| Perturbation | GSE312591 RUNX1 siRNA | 🟡 conditional | 仅在RUNX1命中时加入 |

---

## 4. R3 对论文故事线的重新冻结

### 不再建议
`SSc GWAS → FUMA → eQTL → scRNA → enrichment → docking`

原因：2026 sex-specific GWAS原文已经完成了相当广泛的 positional/eQTL/sQTL/pQTL/chromatin interaction/V2G/colocalization/sex-DEG/drug repurposing；再做一遍会高度重叠。

### 建议冻结为

```text
2026 sex-stratified SSc GWAS
        ↓
Locus harmonization + credible signal definition
        ↓
FinnGen 33-cell caQTL/eQTL + SuSiE
        ↓
variant → peak → gene → immune cell regulatory cascade
        ↓
multi-signal GWAS–caQTL / GWAS–eQTL / caQTL–eQTL colocalization
        ↓
TenK10K independent eQTL direction/target replication
        ↓
GSE312129 untreated SSc skin: gene + accessibility + cell-state concordance
        ↓
GSE249279 / GSE236111 orthogonal replication
        ↓
only then: safety / druggability / therapeutic direction
```

原则：**翻译层只给完成上游遗传+细胞+组织证据链的 Tier-1 targets。**

---

## 5. 最终 GO / NO-GO 规则

### GO-S1：sex-GWAS文件门
必须取得 female 与 male full summary statistics，至少包含：

- chr / position；
- effect allele / other allele；
- beta 或 OR；
- SE；
- P；
- allele frequency（若有优先）；
- genome build；
- sample size / effective N信息。

**不满足 → 不允许以“sex-biased regulatory cascades”作为主论文标题进入R4。**

### GO-S2：signal-resolution门
在预定义的 sex-specific loci 中，至少应出现：

- ≥2 个独立 loci 具有强 GWAS–molQTL shared signal；并且
- 至少 1 个 locus 能完成相对完整的 variant→peak→gene→cell chain。

如果 8 个 sex-specific loci 中只有 0–1 个可以建立完整级联，则 sex-specific main story 强度不足。

### GO-S3：replication门
至少一个 Tier-1 target 在 TenK10K / 其他独立 eQTL 中方向一致或具有合理同细胞系支持。

### GO-S4：disease-context门
至少两个遗传优先 target/cascade 中，有一个在 GSE312129 或独立皮肤数据中呈现：

- target gene disease-state差异；或
- 对应cell state enrichment；或
- target peak/accessibility concordance；或
- downstream program concordance。

注意：组织表达不要求与遗传效应简单同方向，需根据风险等位基因→表达/开放方向预注册解释。

### NO-GO/PIVOT 条件
若 sex GWAS stats持续无法取得：

**Pivot A（可接受）**：以 GCST009131 overall SSc 为主发现，2026 sex-specific loci仅作为重点 case-study / annotation。  
但题目必须删除“sex-biased”作为主命题。

若 molQTL cascade很弱：

**Pivot B**：放弃“regulatory cascade”主张，转成 “cell-state regulatory concordance”；期刊预期需要下调。

若疾病组织层也不支持：

**NO-GO**：停止SSc，不通过堆分析抢救。

---

## 6. 下一阶段目标

### R4A — Access & Harmonization Gate（推荐立即执行）
不是立刻跑全量主分析，而是用最小代价解除最后两个阻塞：

1. 实际取得 2026 sex-specific SSc male/female GWAS files；
2. 实际取得 FinnGen multiome release manifest / eQTL / caQTL / fine-mapping文件；
3. 冻结每个文件的 build、allele schema、variant ID、样本量与hash；
4. 用 BCL11A、IRF4、RPL3-PDGFB 三个新 locus 做 **3-locus smoke test**；
5. 只有 smoke test 能真实建立至少一个高可信 cascade，才进入 R4B 全量分析。

**下一阶段决策**：`GO_R4A_ACCESS_HARMONIZATION_SMOKE_TEST`；不是直接 `GO_FULL_ANALYSIS`。

---

## 7. R3总体状态

> **方向：GO**  
> **sex-specific主分析：HOLD**  
> **数据生态：PASS**  
> **创新性：PASS WITH NARROWED CLAIM**  
> **疾病组织验证：PASS**  
> **正式全量计算：WAIT FOR R4A HARD-GATE**
