# CMM R4A — Pipeline DAG 与验收标准

---

# 1. Minimal DAG

```text
A. sex-SSc GWAS acquire
   │
   ├─ schema QC
   ├─ GRCh38 validation
   └─ locus extraction
            │
            ▼
B. FinnGen multiome acquire
   │
   ├─ caQTL
   ├─ eQTL
   ├─ SuSiE CS
   └─ peak-gene
            │
            ▼
C. Harmonize variants
            │
            ▼
D. For each locus/cell
   ├─ GWAS ↔ caQTL shared signal
   ├─ GWAS ↔ eQTL shared signal
   └─ caQTL ↔ eQTL compatibility
            │
            ▼
E. Build variant→peak→gene→cell cascade
            │
            ▼
F. TenK10K independent eQTL replication
            │
            ▼
G. Assign C1/C2/C3/C4 tier
```

Disease-tissue analysis is **not** inside R4A.

---

# 2. Unit-test ordering

## Test 0 — file/schema
PASS if:
- decompression succeeds;
- columns parse;
- build known;
- effect direction known;
- locus can be indexed.

## Test 1 — IRF4
PASS if:
- rs12203592 or credible-set proxies are represented;
- at least one relevant immune cell has interpretable eQTL/caQTL evidence;
- fine-map fields can be joined;
- peak-gene mapping can be resolved.

## Test 2 — BCL11A
Tests:
- nontrivial target mapping;
- lineage specificity;
- nearest-gene hypothesis can be supported or falsified.

## Test 3 — RPL3-PDGFB
Tests:
- indel normalization;
- multi-gene target arbitration;
- robust allele direction.

---

# 3. R4A.1 PASS criteria

A locus is not required to be biologically positive for the code pipeline to pass.

### Technical PASS
- all source files parsed;
- canonical variants generated;
- allele harmonization complete;
- fine-map IDs join;
- coloc input valid;
- peak-gene join valid;
- negative results have explicit reason.

### Scientific smoke PASS
At least one locus reaches:

```text
SSc regional signal
+ cell-specific caQTL
+ linked eQTL/peak-gene target
+ compatible fine-mapped/shared signal
```

and is therefore C1 candidate.

---

# 4. R4B authorization

## GO_R4B_FULL
Only if:
- both technical PASS;
- ≥1 C1 candidate;
- no critical allele/build ambiguity;
- novelty remains intact.

## HOLD
If:
- sex GWAS unavailable;
- FinnGen files unavailable;
- file schema unresolved.

## PIVOT_OVERALL_SSC
Only if:
- sex stats remain unavailable after access-resolution attempt;
- an actual overall SSc full-summary dataset is acquired;
- overall pipeline produces a compelling regulatory cascade;
- manuscript question is rewritten before analysis expansion.

## NO_GO_SSC
Only if:
- source coverage is adequate;
- technical workflow passes;
- 3 novel loci + expanded loci show systematic absence of interpretable SSc-linked regulatory cascade;
- failure is biological rather than access/power/schema.

---

# 5. Expected compute footprint for smoke stage

Goal is intentionally small:
- 3 loci;
- region extraction;
- source-provided SuSiE reuse;
- no full tissue atlas;
- no genome-wide de novo fine-mapping.

Storage is dominated by whichever source format forces full download.

TenK10K staged strategy:
- 10.1 MB gene-level first;
- 59.7 MB SuSiE second;
- 16.6 GB full 100kb only if necessary.

This is preferable to immediately downloading all 170+ GB TenK10K files.

---

# 6. Figure implications

R4A does not create final manuscript figures.

Only if R4B authorized:

- Figure 2 = sex-specific genetic architecture;
- Figure 3 = cell-specific caQTL/eQTL map;
- Figure 4 = variant→peak→gene fine-mapped cascade;
- Figure 5 = independent replication;
- Figure 6 = disease tissue;
- Figure 7 = integrated translational model.

If R4A fails, these figures are never fabricated by substituting WGCNA/PPI/ML.


## 关键来源（核查日期：2026-09-08）

1. Rodriguez-Martin I, et al. *Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study.* Lancet Rheumatology. 2026;8(6):e438-e450. PMID: 41999721. DOI: 10.1016/S2665-9913(25)00376-5.
2. FinnGen. *Access results — FinnGen single-nucleus multiome*, public release 2026-08-13. https://www.finngen.fi/en/access_results
3. Cuomo ASE, et al. TenK10K Phase 1 sc-eQTL data. Zenodo record 18221260. DOI: 10.5281/zenodo.18221260.
4. Praetorius C, et al. Functional studies of IRF4 rs12203592 and subsequent cell-type-specific eQTL work (Genome Research / related mechanistic studies).
5. Existing R3 frozen protocol in this project: `03_CMM_R3_统计兼容性与冻结分析协议_v1.md`.

> 注：本轮严格区分“网页声明可用”“已确认文件清单”“已实际取得文件字节”。未实际取得的数据不会被写成已完成分析。
