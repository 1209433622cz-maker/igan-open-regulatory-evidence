# CMM R6A0R：IgAN Completion-First 重新评估与主项目恢复建议

**日期：2026-09-14**  
**定位：目标函数修正后的项目级重新评估**  

## 1. 用户目标修正

此前 R6A0 将“一区级新颖性”权重设置过高，因此在发现 2023–2026 IgAN 已存在多项 GWAS/QTL/single-cell 工作后执行 novelty early-stop。

本轮重新明确真实目标：

> **分析、质控、图件和写作均按 SCI 一区标准执行，但实际投稿二区或三区也可接受；首要目标是项目能够完整闭环，并具有足够多、相互独立、真实而不过度解释的阳性证据。**

因此项目评价函数改为：

```text
PRIMARY_OBJECTIVE =
  COMPLETION_PROBABILITY
  + POSITIVE_EVIDENCE_DENSITY
  + REPRODUCIBILITY
  + LOGICAL_COHERENCE
  + PUBLIC_DATA_EXECUTABILITY

NOVELTY = IMPORTANT_BUT_NOT_HARD_GATE
Q1_PUBLICATION = NOT_REQUIRED
Q1_QUALITY_STANDARD = REQUIRED
```

---

## 2. 修正后的项目结论

```text
IGAN_PRIMARY_PROJECT = REQUALIFIED_GO
IGAN_NOVELTY = MODERATE
IGAN_COMPLETION_FEASIBILITY = HIGH
IGAN_POSITIVE_EVIDENCE_FEASIBILITY = HIGH
IGAN_PUBLIC_DATA_FEASIBILITY = HIGH
IGAN_Q2_Q3_PUBLICATION_FEASIBILITY = HIGH_IF_EXECUTION_CLEAN

PBC_VITILIGO_HEAD_TO_HEAD = DEFERRED
NEXT_STAGE = R6A1_IGAN_COMPLETION_FIRST_BYTE_LEVEL_AND_POSITIVE_EVIDENCE_PREFLIGHT
```

IgAN 不应再因为“已有类似工作”而淘汰。已有工作反而证明：

1. IgAN GWAS 风险位点数量充足；
2. 多个风险位点已知存在真实 cis-eQTL 与 colocalization；
3. immune-cell biology 与 kidney disease-state biology 都有公开数据；
4. 即使个别 locus 失败，整篇论文不会像 SSc/MG 那样被一个或两个脆弱位点绑架。

---

## 3. 为什么 IgAN 的阳性证据概率明显高于 MG/SSc

### 3.1 GWAS 本身不是单一 locus 项目

2023 Nature Genetics：
- 10,146 biopsy-confirmed IgAN cases；
- 28,751 controls；
- 30 genome-wide significant risk loci；
- 16 个新 locus；
- 30 loci 合计解释约 11% disease risk。

因此不存在“主 locus 一失败整篇论文崩掉”的结构。

### 3.2 已知存在较多真实 eQTL-colocalization 阳性

2023 主研究报告：

- 20 个 independent non-HLA risk loci 中存在 79 个 significant cis-eQTL effects；
- 12 个 loci 在 15 种 primary immune cells 有 27 个 significant cis-eQTL effects；
- 其中 17 个 cis-eQTL 与 IgAN colocalize；
- ITGAM/ITGAX、IRF4/DUSP22、ZMIZ1 等具有明确 cell-type-resolved evidence。

这意味着 OneK1K/TenK10K 分析不是在盲目寻找第一个阳性，而是在更高分辨率上复现、细化和筛选已有真实调控信号。

### 3.3 2026 disease-context QTL 进一步证明存在可用阳性

CureGN 2026 preprint：
- 1,822 glomerular disease patients；
- IgAN n=403；
- disease-context eQTL/sQTL/edQTL；
- IgAN CARD9 sQTL PP4≈0.99；
- IgAN ITGAM/X sQTL PP4≈0.99；
- IgAN ITGAX edQTL PP4≈0.91。

即使这些资源不作为我们的核心输入，它们也说明：
> IgAN risk loci 中存在真实、可重复的 transcript-regulatory biology。

### 3.4 Kidney disease-state 验证资源丰富

至少有：

- GSE127136：13 IgAN kidney biopsies + 6 normal/paracancer controls，另含外周 CD14+；
- 2025 Communications Biology：3 IgAN + 3 normal kidney scRNA，并有空间/肾小球内皮分析；
- GSE286186 / GSE271188：glomerular disease snRNA atlas；
- GSE286184：4 IgAN Xenium samples，可做空间 localization；
- 其它 GSE171314 等 IgAN kidney scRNA 可做独立 replication/sensitivity。

因此 tissue 层不依赖一个小样本数据集。

---

# 4. 新论文不再追求“首次发现基因”，而追求“高质量闭环”

建议主题：

## Cell-type-resolved regulatory convergence and renal tissue validation of genetic risk loci in IgA nephropathy

核心问题：

> **Among established IgAN risk loci, which genetic signals reproducibly converge on immune-cell-specific gene regulation across independent single-cell eQTL resources, and do the prioritized genes map to disease-relevant renal cell states and spatial compartments?**

中文：

> **已知 IgAN 遗传风险位点中，哪些疾病信号能够在两个独立单细胞 eQTL 资源中稳定解析为免疫细胞特异调控效应，并进一步在 IgAN 肾组织的疾病相关细胞状态和空间区室中得到正交支持？**

这种问题：
- 不假装重新发现 IgAN GWAS loci；
- 不假装第一个做 IgAN colocalization；
- 但可以提供更严格、跨资源、source-aware、single-cell-resolved 的证据升级。

对 Q2/Q3 足够；
若结果异常好，仍保留更高投稿上限。

---

# 5. 最推荐的证据架构

## Layer 1 — Disease genetics

Primary:
- Kiryluk 2023 combined IgAN GWAS。

Sensitivity:
- European-only；
- Asian-only；
- optionally non-Immunochip。

主要目的：
- 确认 locus；
- ancestry consistency；
- effect direction；
- region coverage；
- 不把 HLA 作为主机制 showcase。

## Layer 2 — OneK1K source-aware immune eQTL

OneK1K 作为主要 regulatory-discovery / signal-resolution resource：

- full ±1 Mb cis-eQTL；
- 980-donor public genotype；
- exact cell donor subsets；
- source-aware QTL LD；
- 14 immune cell types。

沿用 MG 阶段全部：
- build/allele QA；
- A1 effect semantics；
- exact sample LD；
- coloc prior sensitivity；
- SuSiE / conditioning；
- STOP/HOLD/FAIL 状态机。

## Layer 3 — TenK10K independent molecular replication

TenK10K 不作为“挑阳性”的数据集。

职责：
- same gene；
- compatible cell class；
- direction；
- source SuSiE credible set；
- independent QTL replication。

只有 OneK1K signal-level positive/ambiguous loci进入主 replication tier。

## Layer 4 — Cross-resource evidence tier

### Tier A
- IgAN GWAS signal；
- OneK1K signal-level support；
- TenK10K independent support；
- direction coherent。

### Tier B
- GWAS + OneK1K strong；
- TenK10K gene/cell support但 signal resolution不足。

### Tier C
- strong QTL but H3/distinct disease signal。

### Tier D
- uninformative / technical limitation。

Tier C/D 也保留在 Supplementary，避免只报告阳性。

---

# 6. 如何确保“足够多阳性”但不结果导向

关键不是挑更多 gene，而是从一开始设定宽而有限的候选 universe。

建议：

### Primary universe
全部 **non-HLA genome-wide significant IgAN loci**。

不先选 CARD9/TNFRSF13B/FCAR 等“我们知道会阳性”的基因。

### Analysis entry
对每个 locus：
1. 确认 OneK1K QTL testability；
2. 做所有 source-significant eGenes 的 bounded competition；
3. signal-level adjudication；
4. 按预注册 evidence tier 排序。

### Positive controls
已发表的 strong regulatory loci可以作为 benchmark：
- CARD9；
- ITGAM/ITGAX；
- IRF4/DUSP22；
- ZMIZ1。

它们的职责是验证 pipeline 能恢复已知 biology，而不是冒充新发现。

### Novel/secondary candidates
由完整非-HLA scan 后再定义：
- OneK1K + TenK10K 双资源一致；
- 2023 DICE/bulk paper 未达到同样 cell resolution；
- kidney tissue存在明确 disease-state support。

这样既提高阳性率，又不构成 cherry-picking。

---

# 7. Kidney tissue 设计

## 主验证队列：GSE127136

13 IgAN + 6 control kidney。

必须：
- donor-level pseudobulk；
- cell type × disease model；
- 不使用 cell 作为统计 n；
- predefined genes only；
- effect size + CI；
- batch/sample QC。

职责：
> disease-state expression support。

## 独立组织资源

### 2025 kidney scRNA / spatial
3 IgAN + 3 normal：
- glomerular endothelial；
- mesangial；
- macrophage/monocyte；
- other relevant renal cells。

职责：
> independent cell-state replication。

### GSE286184 Xenium
4 IgAN：
- spatial localization；
- mesangial/glomerular/interstitial compartment；
- 不当作 disease-control DE。

### GSE286186 / snRNA
作为扩展 replication 和 cell-state context。

---

# 8. 建议加入一个非常有价值的“上游 IgA”轴

Kiryluk Lab 还公开 serum IgA GWAS：
- n≈41,263；
- genome-wide summary stats。

可以在 IgAN regulatory loci 中增加：

```text
IgAN GWAS
   ↕
serum IgA GWAS
   ↕
immune-cell eQTL
```

只在预定义 IgAN loci 上做，不做全基因组 fishing。

如果部分 locus 同时表现：
- IgAN risk；
- serum IgA effect；
- immune eQTL；
- kidney disease-state support；

会形成非常自然的：

> systemic IgA regulation → immune-cell regulatory genetics → renal disease-state convergence

这比普通 “GWAS + scRNA” 更完整，而且阳性概率较高，因为原 GWAS 已报告 IgAN 与 serum IgA 的正遗传相关及共享效应。

---

# 9. 推荐主图结构

## Figure 1
IgAN GWAS architecture + EUR/EAS consistency + study design

## Figure 2
OneK1K immune-cell regulatory landscape across non-HLA loci

## Figure 3
3–5 strongest signal-resolved loci
- regional GWAS
- eQTL
- LD
- coloc / SuSiE
- bounded gene competition

## Figure 4
TenK10K independent replication matrix

## Figure 5
Kidney donor-level disease-state validation
- pseudobulk
- cell-specific expression
- cell-state effects

## Figure 6
Xenium/spatial localization + integrated immune–kidney model

Optional:
serum-IgA cross-trait layer can be Figure 2/3 panel or Supplementary depending result strength。

---

# 10. 阳性证据的现实预期

不承诺具体结果，但基于现有外部证据，合理判断：

| Evidence layer | Positive-result outlook |
|---|---|
| 多个 established disease loci | Very high |
| 至少数个 immune eQTL-shared loci | High |
| OneK1K/TenK10K same-gene replication | Moderate–high |
| 至少 2–4 个 Tier A/B regulatory loci | Plausible / high enough to justify project |
| kidney expression/localization of prioritized genes | High |
| all loci simultaneously positive | Neither expected nor required |
| every locus causal-gene resolution | Not expected |
| manuscript with multiple convergent positive lines | High |

真正健康的目标不是 30/30 阳性，而是：

```text
3–5 STRONG EXEMPLAR LOCI
+
several Tier-B supportive loci
+
clear negative/distinct-signal controls
+
independent kidney validation
```

这已经足以组成一篇很完整的论文。

---

# 11. 对发表层级的重新判断

若最终得到：

### Strong outcome
- ≥3 robust signal-level loci；
- OneK1K + TenK10K replication；
- donor-level kidney support；
- spatial localization；
- ancestry / serum IgA supporting layer；

则可以按较高水平期刊标准组织，实际投稿 Q1/Q2 均可讨论。

### Medium outcome
- 1–2 robust loci；
- 另外数个 Tier B；
- kidney tissue明显支持；

依然非常适合 Q2，且部分 Q3期刊会相当稳。

### Conservative outcome
- single-cell QTL signal-level阳性不多；
- 但能严格复现既有 regulatory loci；
- kidney single-cell/spatial层完整；

仍然可以形成较扎实的 Q2/Q3 integrative bioinformatics paper。

因此 IgAN 的“论文完成下限”明显高于 SSc/MG 当前路线。

---

# 12. 下一阶段

正式撤销：

```text
IGAN_PRIMARY_PROJECT = NO_GO_NOVELTY
```

修改为：

```text
PROJECT_OBJECTIVE = COMPLETION_FIRST_WITH_Q1_QUALITY

IGAN_PRIMARY_PROJECT = GO_REQUALIFIED
IGAN_NOVELTY = MODERATE
IGAN_COMPLETION_PROBABILITY = HIGH
IGAN_POSITIVE_EVIDENCE_DENSITY = HIGH

PBC_VITILIGO = DEFERRED_RESERVE

NEXT_STAGE =
R6A1_IGAN_BYTE_LEVEL_AND_POSITIVE_EVIDENCE_PREFLIGHT
```

## R6A1 不应立即跑完整 tissue atlas

先完成：

1. combined/EUR/Asian IgAN GWAS真实字节；
2. non-HLA GWS loci重算；
3. OneK1K exact variant/gene/cell testability；
4. TenK10K same-locus testability；
5. published positive-control recovery；
6. serum IgA GWAS overlap；
7. GSE127136 target-gene detectability；
8. 估计能够形成 Tier A/B 的 locus 数。

### R6A1 GO 门

如果：

```text
NON_HLA_LOCUS_COUNT = sufficient
ONEK1K_TESTABLE_LOCI >= 8
CROSS_RESOURCE_QTL_CANDIDATES >= 4
KNOWN_POSITIVE_CONTROL_RECOVERY >= 2
KIDNEY_TARGET_DETECTABILITY = PASS
EXPECTED_TIER_A_OR_B >= 3
```

则进入：
`R6A2_IGAN_REGULATORY_LANDSCAPE`

如果仅得到 1–2 个可测试 regulatory locus，再重新评估是否切换 PBC/vitiligo。

---

# 13. 导师级最终结论

**在“一区标准做研究，但二区/三区可以接受”的真实目标下，我推荐恢复 IgAN 为主项目。**

它最大的价值不是最高新颖性，而是：

> **数据公开、风险位点多、已有真实调控阳性作锚、可做单细胞 QTL 独立复现、肾组织验证资源丰富、单个 locus 失败不会让整篇论文崩掉。**

与 SSc/MG 相比，这是更适合“尽可能完美地做完，并大概率得到足够多真实阳性证据”的项目结构。

后续应严格避免：
- 为追求新颖性把问题做得过窄；
- 为追求阳性结果挑 gene；
- 只报告成功 locus；
- 把 kidney expression support 当作 genetic mediation；
- 把 replication paper 包装成首次发现。

正确定位是：
> **rigorous cross-resource regulatory refinement and disease-tissue validation of established IgAN genetic risk.**
