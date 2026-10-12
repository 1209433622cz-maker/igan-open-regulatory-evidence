# CMM R3 — GO / NO-GO 风险矩阵与决策树

**目的**：把项目是否继续从主观“看起来不错”变成可执行的门控系统。

---

## 1. 风险矩阵

| 风险 | 概率 | 影响 | 当前等级 | 对策 |
|---|---:|---:|---:|---|
| 2026 sex-GWAS full stats未实际取得 | 中高 | 极高 | 🔴 | R4A第一硬门；不可绕过 |
| FinnGen需表单/邮件访问 | 中 | 中 | 🟡 | 先完成access，不先下载大组织数据 |
| sex loci无完整caQTL→eQTL cascade | 中 | 高 | 🟠 | 3-locus smoke test |
| 2026原GWAS已做功能注释导致重复 | 高 | 高 | 🟠 | claim收窄到cell-resolved cascade |
| SSc skin multiome已有强论文 | 高 | 中高 | 🟠 | tissue只做orthogonal validation |
| FinnGen Finnish LD与SSc meta GWAS差异 | 中 | 中高 | 🟠 | source-specific fine-map/LD + sensitivity |
| TenK10K cell label不完全对应 | 中 | 中 | 🟡 | pre-defined lineage mapping |
| GSE312129病例n=10 | 高 | 中 | 🟡 | donor pseudobulk + independent dataset |
| GSE312129男性仅n=3 | 高 | 高（sex tissue claim） | 🔴 | 不做强tissue sex interaction claim |
| spatial无HC（Visium/Xenium主要SSc） | 高 | 中 | 🟡 | spatial只做localization |
| generic sc-eQTL/MR方法饱和 | 高 | 高 | 🟠 | MR降级，cascade+fine-map为核心 |
| context-dependent eQTL新方法抢新颖性 | 中 | 中 | 🟡 | key-locus sensitivity / Discussion |
| target direction与disease DE不一致 | 中 | 中 | 🟡 | 预注册不要求简单同向，解释机制 |
| 无可药物Tier-1 target | 中 | 低中 | 🟢 | druggability不是硬门，不强加docking |

---

## 2. 五个硬门

### Gate A — Data acquisition
**PASS**：male/female full summary stats + FinnGen molQTL/fine-map实际文件拿到。  
**FAIL**：只拿到论文表格/lead SNP。

FAIL → sex-specific main project HOLD。

---

### Gate B — Harmonization
**PASS**：build/alleles/variant IDs能无歧义统一；>95%核心locus variants有合理映射（具体比例按文件覆盖调整并记录）。  
**FAIL**：关键locus不能稳定判向。

FAIL → 修复数据，不进入统计主分析。

---

### Gate C — Regulatory cascade smoke test
BCL11A / IRF4 / RPL3-PDGFB中至少一条出现可信的 cell-specific molQTL shared signal / cascade。

**PASS** → 扩展8个sex loci及全局loci。  
**FAIL** → 不建议全量跑FinnGen×SSc。

---

### Gate D — Independent support
至少一个核心target得到TenK10K或另一独立molQTL方向支持。

**PASS** → 保持“replicated regulatory target”措辞。  
**FAIL** → 降级为discovery-only。

---

### Gate E — Disease-context support
至少一个核心cascade在 GSE312129 / GSE249279 / GSE236111 中得到预定义的 disease-state support。

**PASS** → 完成 genetic→tissue闭环。  
**FAIL** → 不能写“recapitulated in SSc tissue”。

---

## 3. 三条项目路径

### PATH 1 — 最优
所有A–E通过。

**论文类型**：sex-aware cell-resolved regulatory genetics paper  
**潜力**：强Q1  
**主标题可保留**：sex-biased / sex-specific regulatory cascades

---

### PATH 2 — sex GWAS access失败，但overall SSc可做
A中sex stats失败；GCST009131 + FinnGen + tissue可跑。

**重构为**：

> Cell-type-specific chromatin-to-expression regulatory cascades underlying systemic sclerosis susceptibility

2026 sex loci仅作为重点case studies，不做sex-specific主发现。

**潜力**：仍可成文，但新颖性和期刊上限下降。

---

### PATH 3 — molQTL cascade弱
数据能拿到，但多sex loci没有shared signal。

此时不要堆：

- WGCNA
- LASSO
- random forest
- immune infiltration
- docking

来“抢救”。

优先：

1. 判断是否为真实negative biology；
2. 是否因为外周immune QTL无法解释skin/fibrotic cell机制；
3. 如果核心假设不成立，**NO-GO并切换TOP2疾病**。

---

## 4. 论文强度分级

### A级项目
- ≥2 C1 cascades
- independent replication
- disease tissue concordance
- 至少一个sex-specific locus具有清晰、可解释细胞机制

### B级项目
- 1 C1 + 多个C2
- replication部分成功
- tissue有支持

### C级项目
- 主要是eQTL/MR + scRNA DE
- 缺少caQTL/fine-map链

**C级不建议以当前目标继续SSc；与54篇论文里已经饱和的套路差别太小。**

---

## 5. 当前打分（R3结束时）

| 维度 | 分数 | 解释 |
|---|---:|---|
| 科学问题 | 9/10 | sex bias + cell regulatory mechanism明确 |
| 数据资源 | 9/10 | FinnGen/TenK10K/SSc multiome很强 |
| 数据实际可取性 | 6.5/10 | sex GWAS accession未解决 |
| 创新性 | 8.5/10 | 必须严格收窄claim |
| 统计可解释性 | 8.5/10 | fine-map/coloc链可建立 |
| 疾病组织闭环 | 9/10 | GSE312129很强 |
| sex tissue validation power | 4/10 | 7F/3M，不能独立做强sex interaction |
| 可复现性潜力 | 9/10 | 均为public summary/open GEO为主 |
| 总体 | **8.2/10 conditional** | 值得继续R4A，不值得直接全量跑 |

---

## 6. 最终决策

```text
R3_DECISION = CONDITIONAL_GO
PRIMARY_HOLD = SEX_GWAS_FULL_SUMMARY_STATS_NOT_YET_RETRIEVED
NEXT = R4A_ACCESS_HARMONIZATION_SMOKE_TEST
FULL_ANALYSIS = NOT_AUTHORIZED_YET
```

这是一个积极但严格的结论：项目没有被否决，但现在最有价值的动作不是继续扩分析，而是解除最后一个真正会决定论文能否成立的硬阻塞。
