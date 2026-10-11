# CMM R4A — 三位点 Pre-Smoke Test

**目的**：在完整molQTL文件取得前，对3个预注册位点进行“遗传可信度 + 调控先验 + 技术风险 + 潜在创新收益”审计。  
**重要限制**：这是 pre-smoke，不是colocalization结果。

---

# 1. 总览

| Rank | Locus | Lead | Sex | SSc effect | Regulatory prior | 技术难度 | C1潜力先验 |
|---:|---|---|---|---|---|---|---|
| 1 | IRF4 | rs12203592 | Female | OR 0.78, P=2.36e-8 | **Very strong** | Low–moderate | **Highest** |
| 2 | BCL11A | rs2540100 | Male | OR 1.32, P=8.39e-9 | Moderate | Moderate | High-value/uncertain |
| 3 | RPL3-PDGFB | rs66578187 | Female | OR 1.19, P=3.18e-8 | Moderate, target ambiguous | **High** | High if resolved |

---

# 2. IRF4 / rs12203592

## 2.1 Genetic facts
- chr6:396321 hg38
- effect allele in SSc paper: T
- female OR = 0.78
- female P = 2.36 × 10^-8
- male OR ≈ 1.01
- strong between-sex contrast

## 2.2 Regulatory prior
rs12203592:
- is intronic in IRF4;
- lies in regulatory chromatin;
- has repeatedly been linked to IRF4 expression;
- was a very strong IRF4 cis-eQTL in primary melanocyte work;
- has direct enhancer-function and allele-specific regulatory evidence in mechanistic studies.

## 2.3 Why this is useful rather than “already solved”
The melanocyte mechanism does **not** answer:

- which immune cell carries the SSc-relevant molecular effect;
- whether the female SSc regional GWAS signal and immune-cell caQTL/eQTL share the same causal signal;
- whether the risk/protective allele changes accessibility and expression in a direction consistent with SSc;
- whether this cell program is present in diseased SSc tissue.

Therefore the novel question is **context specificity**, not “is rs12203592 regulatory at all?”

## 2.4 R4A expected chain

```text
female SSc locus
→ FinnGen caQTL at rs12203592/proxy/CS
→ peak overlapping IRF4 regulatory region
→ IRF4 eQTL in defined immune cell
→ caQTL/eQTL shared fine-map
→ female-SSc GWAS shared signal
→ TenK10K same gene/lineage/direction
→ SSc tissue concordance
```

## 2.5 Kill criteria
IRF4降级 if:
- FinnGen has no relevant caQTL/eQTL coverage;
- fine-mapped molQTL signal clearly differs from SSc signal;
- peak links robustly to another gene rather than IRF4;
- cell context is irrelevant and cannot replicate.

### Current verdict
**FIRST UNIT TEST**

---

# 3. BCL11A / rs2540100

## 3.1 Genetic facts
- chr2:59,523,629 hg38
- effect allele: A
- male OR = 1.32
- P = 8.39 × 10^-9
- female OR ≈ 0.99
- original study called this the first male-specific SSc locus.

## 3.2 Existing functional support
Original SSc study prioritised BCL11A mainly because:
- it is the nearest gene;
- associated region has chromatin interaction evidence with BCL11A in IMR90 fibroblasts.

BCL11A also has strong biology in hematopoiesis / pDC development, but biological plausibility is not equivalent to locus causality.

## 3.3 Why this locus is scientifically valuable
The original evidence leaves precisely the gap our design wants to resolve:

> Is the male SSc signal actually an immune-cell regulatory effect on BCL11A, a fibroblast regulatory effect, or a different target altogether?

FinnGen population immune multiome can either:
- upgrade BCL11A from C4/C3-like annotation to C1/C2;
or
- falsify the nearest-gene interpretation.

Both outcomes are publishable information if handled honestly.

## 3.4 Required caution
Do not use the famous erythroid BCL11A enhancer literature as evidence that `rs2540100 → BCL11A` in SSc.
The BCL11A locus is highly regulatory and lineage-dependent; this increases the need for cell-specific evidence rather than decreasing it.

### Current verdict
**SECOND UNIT TEST / HIGH DISCOVERY VALUE**

---

# 4. RPL3–PDGFB / rs66578187

## 4.1 Genetic facts
- chr22:39,328,807 hg38
- effect allele reported: `AT`
- female OR = 1.19
- P = 3.18 × 10^-8
- male association absent
- signal lies near RPL3 with PDGFB nearby.

## 4.2 Main scientific risk
PDGFB is highly attractive biologically because SSc is fibrotic/vascular and PDGFR biology is therapeutically relevant.

That is exactly why this locus is vulnerable to confirmation bias.

The correct question is:

> Which gene does the sex-specific causal signal regulate?

not:

> Can we find evidence supporting PDGFB?

## 4.3 Technical risk
`AT` indel requires:
- correct REF/ALT recovery;
- left alignment;
- normalization;
- source-build confirmation;
- allele orientation check;
- multi-allelic handling if present.

This locus therefore becomes the best harmonization stress test.

## 4.4 Candidate target universe
At minimum retain:
- RPL3
- PDGFB
- other peak-linked / eQTL-linked genes in the fine-mapped region

until data resolve the target.

Do not use nearest gene or pathway attractiveness as final target assignment.

## 4.5 Why it may ultimately be very valuable
Independent 22q13.1 literature shows this region can influence multiple nearby genes, including PDGFB/RPL3/SYNGR1 in context-dependent eQTL analyses.

Therefore a clean FinnGen caQTL→peak→gene solution here would add considerable value.

### Current verdict
**THIRD UNIT TEST / HARMONIZATION STRESS LOCUS**

---

# 5. Recommended execution order

```text
1. IRF4
   ↓
2. BCL11A
   ↓
3. RPL3-PDGFB
```

不是按SSc P值排序，而是按：

> **信息增益 / 技术可解释性 / 失败诊断能力**

排序。

IRF4如果都无法在已经具有强调控先验的条件下形成可解释molQTL链：
- 首先检查coverage/schema/power；
- 再判断项目是否真的适配FinnGen细胞体系。

BCL11A用于测试是否能把“nearest-gene annotation”升级成真正的cell-specific mechanism。

RPL3-PDGFB用于测试pipeline是否能够在indel + target ambiguity下仍保持严格、不发生主观定靶。

---

# 6. Smoke test不允许的捷径

- 不允许单SNP p-value拼接成“colocalization”；
- 不允许lead SNP overlap ATAC peak就叫causal enhancer；
- 不允许“PDGFB与fibrosis有关”替代peak-gene evidence；
- 不允许“BCL11A参与免疫”替代GWAS/eQTL shared signal；
- 不允许只用GTEx whole blood给cell-specific结论；
- 不允许用TenK10K已做过的MR atlas替代本项目的regulatory cascade。


## 关键来源（核查日期：2026-09-08）

1. Rodriguez-Martin I, et al. *Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study.* Lancet Rheumatology. 2026;8(6):e438-e450. PMID: 41999721. DOI: 10.1016/S2665-9913(25)00376-5.
2. FinnGen. *Access results — FinnGen single-nucleus multiome*, public release 2026-08-13. https://www.finngen.fi/en/access_results
3. Cuomo ASE, et al. TenK10K Phase 1 sc-eQTL data. Zenodo record 18221260. DOI: 10.5281/zenodo.18221260.
4. Praetorius C, et al. Functional studies of IRF4 rs12203592 and subsequent cell-type-specific eQTL work (Genome Research / related mechanistic studies).
5. Existing R3 frozen protocol in this project: `03_CMM_R3_统计兼容性与冻结分析协议_v1.md`.

> 注：本轮严格区分“网页声明可用”“已确认文件清单”“已实际取得文件字节”。未实际取得的数据不会被写成已完成分析。
