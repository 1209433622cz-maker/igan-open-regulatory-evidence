# CMM R4A — GO / NO-GO 与下一阶段决策

---

# 1. Gate matrix

| Gate | Requirement | R4A result | Consequence |
|---|---|---|---|
| G1 | sex-SSc full regional summary stats acquired | **FAIL / unresolved access** | blocks C1 |
| G2 | FinnGen multiome files acquired | **FAIL in current session** | blocks C1 |
| G3 | TenK10K open replication resource exists | **PASS** | ready after file acquisition |
| G4 | 3 loci have valid genome coordinates/effects | **PASS** | pre-smoke possible |
| G5 | ≥1 locus has credible regulatory prior | **PASS, IRF4** | scientific rationale retained |
| G6 | ≥1 actual C1 cascade computed | **NOT TESTABLE** | R4B not authorized |
| G7 | novelty survives original-paper overlap | **PASS with narrow claim** | continue project |

---

# 2. Why status is HOLD rather than FAIL

A proper NO-GO would require demonstrating:

> the loci are covered, the data are harmonized, the statistical analysis runs, and the biology is negative.

We have not reached that state.

Current failure is:

> **ACCESS / BYTES / SCHEMA availability**, not biological falsification.

Therefore:

```text
NO_GO_SSC = FALSE
GO_R4B_FULL = FALSE
HOLD_FOR_ACCESS = TRUE
```

---

# 3. R4A.1 next target

## Name
**R4A.1 — External Access Unlock + IRF4-first Pipeline Unit Test**

## Priority A — sex GWAS
Resolve by one or more:
1. GWAS Catalog accession discovery once indexed;
2. direct corresponding-author request for male/female summary stats;
3. author/project repository if released elsewhere.

Accept only full statistics with:
- variant;
- alleles;
- beta/OR;
- SE or enough fields for inference;
- P;
- sample size;
- build.

## Priority B — FinnGen
Complete official public-access form and obtain download instructions.

Acquire the **smallest region-queryable or summary packages first**.

## Priority C — TenK10K
Acquire:
1. 10.1 MB gene-level;
2. 59.7 MB SuSiE;
before any 16.6GB+ full summary archive.

---

# 4. Execution order after access

```text
IRF4 only
→ technical QC
→ scientific shared-signal test
→ cascade tier
```

If pipeline works:
```text
BCL11A
→ RPL3-PDGFB
```

Only then:
```text
all 8 sex-specific loci
→ R4B
```

---

# 5. Decision thresholds after R4A.1

### Branch A
IRF4 C1 or BCL11A C1:
> **GO_R4B_FULL**

### Branch B
No C1, but strong C2/C3 + coverage good:
> **R4A.2_EXPAND_TO_8_LOCI_BEFORE_DECISION**

Reason: 3 novel loci may be unrepresentative.

### Branch C
All 3 have good coverage, clear different signals, and expanded sex loci also negative:
> **NO_GO_SSC_SEX_CASCADE**

Then return to TOP2 disease.

### Branch D
sex stats cannot be obtained but FinnGen pipeline works:
> evaluate **PIVOT_OVERALL_SSC** only with a verified full-summary overall SSc source.

Do not silently change primary hypothesis while keeping the old manuscript framing.

---

# 6. What not to do in the next stage

- 不写full manuscript；
- 不提前做drug repurposing；
- 不跑大规模PheWAS；
- 不做docking；
- 不用MR显著性填补coloc失败；
- 不提前下载高分辨Xenium；
- 不把SSc tissue DE当成遗传机制。

---

# 7. Next-stage success deliverables

R4A.1结束时必须产出：

1. `ACCESS_UNLOCK_REPORT.md`
2. `source_manifest.tsv`
3. `checksums.sha256`
4. `schema_audit.md`
5. `celltype_mapping.tsv`
6. `IRF4_locus_QC.md`
7. `IRF4_coloc_and_cascade.tsv`
8. `R4B_GO_NO_GO.md`

---

# 8. Final decision

> **NEXT TARGET = R4A1_ACCESS_UNLOCK_AND_IRF4_FIRST_UNIT_TEST**

项目继续，但不授权R4B全量扩展。


## 关键来源（核查日期：2026-09-08）

1. Rodriguez-Martin I, et al. *Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study.* Lancet Rheumatology. 2026;8(6):e438-e450. PMID: 41999721. DOI: 10.1016/S2665-9913(25)00376-5.
2. FinnGen. *Access results — FinnGen single-nucleus multiome*, public release 2026-08-13. https://www.finngen.fi/en/access_results
3. Cuomo ASE, et al. TenK10K Phase 1 sc-eQTL data. Zenodo record 18221260. DOI: 10.5281/zenodo.18221260.
4. Praetorius C, et al. Functional studies of IRF4 rs12203592 and subsequent cell-type-specific eQTL work (Genome Research / related mechanistic studies).
5. Existing R3 frozen protocol in this project: `03_CMM_R3_统计兼容性与冻结分析协议_v1.md`.

> 注：本轮严格区分“网页声明可用”“已确认文件清单”“已实际取得文件字节”。未实际取得的数据不会被写成已完成分析。
