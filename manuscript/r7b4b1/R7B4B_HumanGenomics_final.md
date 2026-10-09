# Input-matched multi-signal colocalization clarifies immune-cell regulatory assignments at primary biliary cholangitis risk loci

**Article type:** Research
**Authors:** Zhi Chen¹ (ORCID: 0009-0001-0072-5576); Teng Qi¹* (ORCID: 0009-0007-7648-4776)  
**Affiliations:** ¹ School of Medicine, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Boulevard, Longgang District, Shenzhen, Guangdong 518172, China  
**Corresponding author:** Teng Qi, School of Medicine, The Chinese University of Hong Kong, Shenzhen, 2001 Longxiang Boulevard, Longgang District, Shenzhen, Guangdong 518172, China; tengqi@link.cuhk.edu.cn

## Abstract

### Background

Regulatory assignments at primary biliary cholangitis (PBC) risk loci can change with variant coverage, disease-statistic definitions and local signal architecture. We evaluated whether bidirectional colocalization reclassification persisted after matching inputs while separating statistical sharing from biological mechanism. A PBC-wide registry contained 6,923 locus-gene-cell comparisons; 5,460 met the single-causal overlap requirement and a frozen high-information subset of 642 underwent source-matched multi-signal analysis. Four arms retained the historical screen (A0), restricted variant support (A1), matched disease statistics (A2) and compared A2 with the frozen multi-signal result (M). We also evaluated signal-pair identity, PF10/PF50 sensitivity, 486,000 simulation iterations and bounded molecular-QTL and donor-level liver evidence.

### Results

Support restriction and disease-statistic matching changed 15 and 19 categorical assignments, respectively. With matched inputs, 79 of 113 approximate-Bayes-factor H4 comparisons retained shared-pair support, whereas eight supported distinct pairs; ten of 452 H3 comparisons acquired shared-pair support. Final PF10 states comprised 92 H4-supported, 428 H3-supported, 59 model-sensitive and 63 uninformative comparisons. Thirty-two H4-supported comparisons also contained a qualifying distinct pair. Across the frozen simulation grid, mean false-H4 decisions in distinct-signal scenarios decreased from 12.41% to 8.56%, while shared-signal recovery decreased from 32.99% to 26.66%; only 160,782 iterations (33.08%) formed an evaluable signal pair. IL12RB2-NK and FCRL3 B-cell assignments received bounded cross-resource support. Both target-lineage pairs were detected in all five PBC and five control livers without corrected PBC-specific enrichment (both q=0.111).

### Conclusions

Input matching explained part, but not all, of the differences in PBC regulatory assignments. Shared and distinct signal pairs, covariate-model sensitivity and discovery limitations should be reported separately. The results do not establish causal truth, general method superiority or tissue mediation.

**Keywords:** primary biliary cholangitis; colocalization; single-cell eQTL; fine-mapping; linkage disequilibrium; signal pair; regulatory genomics; statistical genetics

## Background

Primary biliary cholangitis is an autoimmune cholestatic liver disease characterized by progressive injury to small intrahepatic bile ducts [1]. Genome-wide association studies have identified a substantial inherited component and many non-HLA susceptibility loci, creating a strong foundation for mechanistic prioritization [2]. The central interpretive problem is no longer whether associated regions exist. It is whether a regional disease association and a molecular quantitative-trait locus (QTL) implicate the same local signal, in which gene and cellular context, and with what degree of uncertainty.

Single-cell QTL resources make this problem biologically more specific. OneK1K mapped cell-type-specific genetic effects on gene expression in peripheral blood immune populations [3], and TenK10K extends immune-cell molecular-QTL mapping to a larger donor cohort and a broader cellular taxonomy [4]. These resources allow the same disease locus to be compared across genes and cell contexts. That resolution also increases statistical dependence: a locus can contain several disease and expression signals, the same gene can appear in related immune populations, and a comparison-level label can conceal different signal pairs.

Bayesian ABF colocalization provides an efficient first-pass test of whether two association patterns are more compatible with one shared causal variant (H4) or with two distinct causal variants (H3) [5]. Its standard formulation assumes at most one causal variant per trait in the tested region. That assumption can be restrictive in autoimmune loci with allelic heterogeneity. Multi-signal fine-mapping and signal-pair colocalization can instead represent several local components [6,7], but a direct comparison is difficult when the procedures use different variant sets, disease summaries or linkage disequilibrium (LD) inputs. An apparent H4-to-H3 or H3-to-H4 change can then reflect input mismatch as well as inferential structure.

This distinction matters for biological attribution. A stable shared signal pair supports a locus-gene-cell regulatory association, but it does not prove expression mediation or a molecular mechanism. A stable distinct pair does not imply that the entire locus contains no shared signal. Indeed, shared and distinct signal pairs can coexist within one locus-gene-cell comparison. Model sensitivity can also be informative: it identifies assignments that depend on the covariate adjustment used to construct QTL summaries and model-matched LD, rather than providing a reason to select the configuration that yields the most favorable posterior.

We therefore used PBC as a disease-focused setting in which to assess the reliability and limits of immune-cell regulatory assignment. The study had four linked tasks. First, we conducted PBC-wide single-causal screening followed by a bounded multi-signal analysis of a frozen high-information subset. Second, we reconstructed matched-input ABF arms to distinguish changes attributable to the variant support set and disease-statistic definition from changes that remained between the single-causal and multi-signal procedures. Third, we separated credible-set discovery from pair-conditional inference in truth-known simulations. Finally, we examined representative IL12RB2-NK and FCRL3 B-cell assignments across independent molecular-QTL resources and bounded tissue evidence. The objective was not to prove that one method is universally superior, to report every supported comparison as an independent discovery, or to infer tissue mechanism from statistical sharing. It was to determine which regulatory assignments were stable, which were input- or model-dependent, and which evidence boundaries remained unresolved.

## Methods

### Study design and governance

This was a secondary analysis of openly available genetic, molecular-QTL and single-cell transcriptomic data. The disease, resource and analysis scope was fixed before the matched-input comparison was run. Disease analysis used the European PBC meta-analysis and 56 non-HLA regional definitions. The molecular layer used 14 OneK1K immune-cell types. The initial registry contained 6,923 locus-gene-cell comparisons. Multi-signal analysis was restricted to a frozen 642-comparison high-information subset rather than extended to all screened comparisons.

The 642 comparisons retained their prespecified roles: 184 formed the primary ABF trigger-verification cohort, 455 formed a symmetric H3 rescue/falsification layer, and three were borderline high-information calibration cases. These identities were not changed after observing multi-signal or matched-input results. The matched-input A0/A1/A2 analysis was a result-informed methodological audit developed to resolve a documented input-asymmetry problem; it was not described as an external preregistration. No locus, gene or cell type was added in response to its outputs.

The evidence architecture comprised source validation and harmonization, PBC-wide ABF screening, frozen high-information follow-up, cell-specific LD and multi-signal inference, diagnostic and signal-identity audits, matched-input comparison, simulation evaluation, and bounded external and tissue evidence. This is a conceptual organization, not a claim that every layer was generated in that chronological order: the liver analysis preceded the PBC-wide redesign, and signal-semantics and matched-input analyses were post-result audits. Negative, model-sensitive, coverage-limited and uninformative results remained in the final evidence set.

### PBC association data and study-derived disease LD

PBC summary statistics were obtained from GWAS Catalog study GCST90061440, representing the GRCh37 European five-panel meta-analysis reported by Cordell and colleagues [2,8]. The dataset comprised 8,021 cases and 16,489 controls (total N=24,510). After byte-level and schema validation, 5,054,572 rows contained valid numeric association data. Study-derived regional association summaries and LD matrices were obtained from the public GJOKA archive accompanying the PBC fine-mapping analysis [9,10].

The GJOKA resource defined 56 non-HLA regions. Disease-side multi-signal analysis used each region's aligned summary z statistics and study-derived LD after intersection with the comparison-specific QTL input. The regional files, row order, alleles and matrices were tied to stored checksums. We did not substitute a generic external LD reference for the primary disease analysis.

### OneK1K expression-QTL data and PBC-wide comparison registry

The cohort origin was the OneK1K single-cell peripheral-blood study [3]. The present reanalysis used the updated 980-donor genotype, covariate and expression resource associated with Xue et al. and Zenodo record 18910121 [11,12]. The cohort publication and the exact analysis release therefore have distinct provenance roles. We retained the 14 source cell labels used by the frozen workflow. Gene eligibility and locus assignment were inherited from the pre-result manifest: genes were assigned to a disease region when the gene transcription start site fell within the region extended by 1 Mb and the gene met the source-level eGene rule (q<0.05) in at least one cell type. Once a gene entered the registry, available source top-summary records across the retained cells were preserved rather than restricted to cells with the smallest q value.

This procedure yielded 6,923 locus-gene-cell comparisons. Of these, 5,460 had at least 200 aligned variants and were eligible for the ABF screen; 1,463 had insufficient overlap and were retained as technical indeterminates rather than biological negatives. The eligible universe contained repeated cells and genes within loci, so comparisons were not treated as independent discoveries.

### Variant identity, allele alignment and exact support sets

Variants were represented by chromosome, GRCh37 position and alleles. For ABF calculations and cross-resource effect-direction comparisons, disease and QTL effects were aligned to the OneK1K PLINK BIM A1 allele. In the GJOKA multi-signal input, disease z statistics remained in the GJOKA effect-allele orientation paired with the corresponding disease LD; QTL z statistics remained paired with BIM-A1 QTL LD. Variant identities and ordering were matched across traits, whereas each trait retained internally consistent effect and LD signs. Strand complements were allowed only when allele identity remained unambiguous. Palindromic variants were excluded when source metadata and allele frequency did not resolve orientation. Duplicated or conflicting identities, nonnumeric effects or standard errors, and variants absent from the relevant LD matrix were removed before posterior calculation.

Two comparison-specific support sets were distinguished. S_A was the variant support used by the historical ABF screen. S_M was the actual intersection used by the multi-signal analysis after disease, QTL and LD alignment. Across the frozen 642 comparisons, S_M contained 19-114 fewer variants than S_A (median 65; median reduction 7.67%). Exact member identities and row order, rather than variant counts alone, defined equality.

### Historical single-causal ABF screen

Single-causal colocalization followed the approximate Bayes factor framework of Giambartolomei et al. [5]. Case-control disease effects used a prior standard deviation of 0.20. Quantitative-trait QTL effects used 0.15 multiplied by the estimated phenotype standard deviation (sdY). Priors were p1=1x10^-4, p2=1x10^-4 and p12=1x10^-5, with p12=1x10^-6 and 1x10^-4 retained for sensitivity analysis. The primary posterior quantities were PP.H3, representing distinct associated variants, PP.H4, representing one shared associated variant, and H4/(H3+H4), conditioning on the distinct-versus-shared alternatives.

A default-prior H4 screening trigger required PP.H4>=0.80 and H4/(H3+H4)>=0.80. The lower and higher p12 results were retained as sensitivity outputs, not as additional admission conditions. Among comparisons that did not meet the H4 rule, H3/H4 ambiguity required H3+H4>=0.80 and 0.20<=H4/(H3+H4)<=0.80; high-information H3 required H3+H4>=0.80 and H4/(H3+H4)<0.20. The expanded 642-comparison workload retained the high-information H3/H4 subset, including the three borderline cases. These screening rules did not establish final multi-signal support.

### Source-matched QTL LD and current-release model identity

For each OneK1K cell-locus block, genotype dosage was extracted only for donors active in that cell type. A global genotype cohort was not substituted for cell types with smaller active-donor sets. Genotypes were aligned to the expression-QTL effect allele. Raw genotype correlations were retained for diagnostics. Model-matched QTL LD was calculated after projecting the genotype dosage matrix G off the same covariate design C used in the corresponding QTL analysis:

G* = [I - C(C^T C)^-1 C^T]G,

and R_QTL = cor(G*).

The covariate design included sex, age, six genotype principal components and expression factors. PF10, using ten expression factors, was the primary specification; PF50, using 50 factors, was a prespecified sensitivity model. Current-release PF10 and PF50 QTL summaries and LD were generated from matched phenotype, genotype, active-donor and covariate sources. The earlier targeted dual-model gate evaluated 14 comparison-model identity rows from seven frozen comparisons; this count must not be read as 14 independently validated cell types. The expanded study retained 14 cell labels and comparison-specific source manifests. Matrix dimension, variant order, symmetry, diagonal, finite values, rank behavior and positive-semidefinite tolerance were checked before fine-mapping.

### Multi-signal fine-mapping and signal-pair colocalization

Disease and QTL association summaries were fine-mapped with SuSiE-RSS [13], the summary-data extension of the SuSiE model [6]. The primary PF10 model was evaluated at L=5, 10 and 20; PF50 was evaluated at L=10. Fits used `estimate_residual_variance=FALSE`, `estimate_prior_variance=TRUE`, `max_iter=2000`, `tol=1x10^-4`, 95% credible sets and minimum absolute within-set correlation of 0.5. Disease sample size was 24,510; QTL sample sizes followed the cell-specific donor counts.

Signal-pair colocalization used `coloc.susie` [7]. All eligible disease-QTL credible-set pairs were evaluated using the same p12 sensitivity series as the ABF screen. For a given configuration, an H4-qualifying pair required default PP.H4>=0.80, default H4/(H3+H4)>=0.80 and H4/(H3+H4)>=0.50 at p12=1x10^-6 for that same pair. An H3-qualifying pair required default PP.H3>=0.80 and H4/(H3+H4)<=0.20. A stable PF10 comparison required the relevant L=10 support and support in at least one of L=5 or L=20. H4 was assigned before H3 when both were available. Comparisons without stable H4/H3 support but with a high-information pair in any required PF10 configuration were model-sensitive; the remainder were uninformative. The subsequent signal-identity audit added cross-L correspondence without overwriting these historical labels.

In the post-result signal-semantics audit, signal identity was matched across L settings using exact lead-pair identity or a credible-set Jaccard overlap of at least 0.50 for both traits. H4 and H3 pairs were recorded separately. A comparison could therefore support at least one shared pair and still contain a different H3-qualifying pair. Bayesian posterior thresholds were not interpreted as family-wise error or false-discovery-rate control across the correlated comparison universe.

### Multi-signal diagnostic adjudication

Corrected kriging diagnostics were evaluated for every comparison-model-trait unit: 642 comparisons x two QTL covariate models x two traits, for 2,568 units. Returned key structure, expected and observed row counts and finite values were checked. Both the historical logLR>2 count and the source-code plotting flag (logLR>2 and abs(z)>2) were retained. All 2,568 diagnostic units were evaluated and passed the recorded review gate; a reviewed flag was not recoded as no anomaly. One unique official-rule event, rs1800378, was reviewed; it did not enter a disease or QTL credible set and did not trigger a refit. This diagnostic repair occurred after the original multi-signal run and was disclosed as a post-result audit.

### Matched-input A0/A1/A2/M attribution design

We constructed four analysis arms for the frozen 642 comparisons. A0 replayed the historical ABF calculation using the original harmonized GCST disease statistics and S_A. A1 retained those disease statistics but restricted both traits to S_M, isolating the effect of support-set restriction at the categorical level. A2 retained S_M and used the GJOKA matched-z disease definition aligned to the disease LD source. M was the already frozen PF10 multi-signal outcome and was not refitted for this comparison.

A0 replay reproduced the historical posteriors to a maximum absolute difference of 3.55x10^-13. Fixed sdY was used for the primary A1 and A2 contrasts so support-set differences did not also alter the QTL effect scale. Native-sdY sensitivity analyses were reported separately. GJOKA matched-z statistics were primary for A2; an analysis based on the rounded public beta and standard error was retained as a statistic-definition sensitivity analysis.

We counted all adjacent categorical changes for A0-to-A1, A1-to-A2 and A2-to-M, but did not add those counts because the affected comparisons could overlap. Strict bidirectional reclassification was reserved for H4-to-H3 and H3-to-H4 changes between A2 and M. Other transitions to or from ambiguous, model-sensitive or uninformative states were retained as uncertainty changes. Because A2 and M are complete inferential procedures with different assumptions and parameterizations, A2-to-M was not described as a single-factor experiment or as a truth-known correction rate.

### Simulation design and outcome channels

The frozen simulation contained 486 parameter combinations with 1,000 iterations each, for 486,000 primary matched-LD iterations. Summary z statistics were generated with two empirical 128-variant LD templates. Six scenarios were evaluated: one shared signal (S1); correlated but distinct signals (S2); two disease signals and one QTL signal with partial sharing (S3); two signals per trait with one shared pair (S4); two signals per trait with no shared pair under high LD (S5); and a matched-versus-mismatched LD sensitivity scenario (S6). Disease N=24,510 and QTL N=750 were fixed, not varied. The 486 grid rows were six scenarios crossed with three MAF values (0.05, 0.20, 0.40), three target causal-pair r-squared values (0.20, 0.50, 0.80), three L values (5, 10, 20) and three p12 values (1x10^-6, 1x10^-5, 1x10^-4). Each row allocated 500 iterations to each empirical template.

The two templates used disease/QTL LD from locus 2/NK and locus 4/B_IN. Simulated summaries followed z ~ Normal(sqrt(N) R b_std, R), with per-allele effects scaled by sqrt(2 MAF(1-MAF)); the first disease effect was log(1.12), the first QTL effect was 0.30, and second effects were -0.8 times the first. These were summary-z experiments rather than individual-level binary PBC simulations. S6 changed only the analysis QTL LD from the same-locus PF10 to PF50 matrix, preserving trait identities and variant order.

Each simulated comparison was evaluated at one L and one p12. Thus, this component-level experiment did not directly calibrate the real-data composite gate that also required cross-L stability and same-pair low-prior support. Scenario-level rates averaged the frozen MAF, LD, L and prior grid; they were not error rates at a single default-prior operating point.

ABF and matched multi-signal decisions were recorded for every iteration. The multi-signal branch additionally classified each iteration into both traits lacking a credible set, disease-only absence, QTL-only absence, both traits having credible sets but no evaluable pair, an H3 pair, an H4 pair, or a pair-evaluable uninformative result. Technical errors were counted separately. Unconditional decision rates used all iterations; pair-conditional rates used only iterations with an evaluable signal pair. The latter describe estimator behavior after the discovery stage and were not directly compared with the ABF unconditional denominator as if they were the same estimand.

### External molecular-QTL evaluation

External evaluation was bounded to the representative IL12RB2-NK and FCRL3 B-cell axes; it was not used to select new genes. TenK10K common-variant cis-eQTL statistics within +/-100 kb were intersected with the same PBC disease summaries [4,14]. ABF colocalization used the frozen prior series, and source TenK10K credible-set membership was reviewed where available. The PBC GWAS was shared across the OneK1K and TenK10K analyses, and donor-level TenK10K LD was not reconstructed. These results were therefore termed cross-resource molecular-QTL replication, not independent disease replication or a second source-matched multi-signal proof.

FinnGen R12 PBC and molecular-QTL colocalization records were queried through the public outputs of the population-scale immune multiome resource [15] for the two representative genes. Returned IL12RB2 records were summarized by source cell stratum. Multiple strata from the same resource were not counted as independent cohorts. Absence of a returned PBC-FCRL3 pair was treated as a public-output coverage boundary rather than a powered negative result.

For allele-direction analysis, the PBC risk allele was mapped to the QTL effect allele in each compatible resource. Directional agreement was reported without comparing effect magnitudes across different expression scales. A consistent expression direction was not interpreted as mediation or as a therapeutic direction.

### Positional chromatin evidence

For IL12RB2, we reviewed FinnGen immune-multiome eQTL, chromatin-accessibility QTL and peak-gene linkage outputs [15]. We recorded whether the representative eQTL variant overlapped an accessibility peak, whether the peak was linked to IL12RB2, whether the peak had a strong caQTL and whether the eQTL anchor entered the peak caQTL credible set. A complete disease-to-chromatin-to-expression cascade required disease-caQTL sharing and variant-level signal coherence; positional overlap alone did not satisfy that rule.

### Donor-level liver target-panel analysis

HRA008003 is an open-access single-cell study of liver and blood in PBC [16,17]. We analyzed liver BAM files from five treatment-naive PBC donors (HRR1849459-HRR1849463) and five non-lesion liver controls obtained during hepatic hemangioma surgery (HRR1849454-HRR1849458). Source sizes and checksums were verified, and each BAM passed `samtools quickcheck` and tag-schema preflight.

Molecule representatives were counted from records carrying the 10x `xf` bit 8 flag, corrected cell barcode, gene name and unique molecular identifier. Called cells were determined using the frozen library-specific rank rule. B-lineage cells were identified from a prespecified B-marker panel and NK-lineage cells from a prespecified NK-marker panel, with lineage competition against T-cell and myeloid markers. Each donor-lineage unit required at least ten cells. Target detectability required at least three target UMIs and at least two target-positive lineage cells. Target CPM was calculated as target UMIs divided by total lineage UMIs multiplied by 10^6.

The biological unit was the donor. The primary endpoint was log1p target CPM within the prespecified lineage. Group differences were compared with the exact distribution of all 252 assignments of five of ten donors to the PBC label. Two-sided exact P values were adjusted across the two target-lineage pairs using the Benjamini-Hochberg procedure. Cell-level observations were not used as independent case-control replicates. The controls were non-lesion surgical liver samples, not healthy volunteer livers.

### Reproducibility and reporting

External inputs were recorded with accession, URL, byte count and available MD5 or locally calculated SHA-256 values. Large third-party files and donor-level genotype data were not mirrored publicly. Code, compact aggregate results, manifests and evidence ledgers were retained in the project repository [18]. Every central manuscript claim was mapped to a frozen source table, allowed wording, prohibited inference and limitation. Methods commitments were mirrored to corresponding Results statements before manuscript assembly.

OpenAI Codex, using the locally installed QiTeng Academic Writing Skill under author supervision, assisted with argument structure, language editing, file generation and consistency checks. It was not treated as an author or as a source of scientific evidence. The authors remain responsible for data interpretation, declarations and the final submitted text.

## Results

### PBC-wide screening defined a bounded high-information multi-signal analysis

The frozen registry contained 6,923 locus-gene-cell comparisons. Of these, 5,460 met the overlap threshold for ABF screening and 1,463 were coverage-insufficient (Figure 1A). The latter were not interpreted as negative colocalization results. The multi-signal workload contained 642 comparisons: 184 primary trigger-verification comparisons, 455 H3 rescue/falsification comparisons and three borderline calibration cases (Figure 1B). It covered 47 PBC regions, 200 genes, 14 cell types and 286 cell-locus blocks.

The final PF10 multi-signal classification contained 92 H4-supported comparisons, 428 H3-supported comparisons, 59 model-sensitive comparisons and 63 uninformative comparisons (Figure 1C). These are comparison counts, not independent genes or loci. The 92 H4-supported comparisons involved 27 genes and 19 loci. Repeated support for a gene across related cells therefore increased cell-context resolution but did not create additional independent disease associations.

Current-release identity and diagnostic gates closed before manuscript interpretation. The targeted current-release gate passed 14 of 14 comparison-model identity rows (seven comparisons, two covariate models). The expanded registry covered 14 source cell types, a different counting unit. Corrected kriging diagnostics passed for 2,568 of 2,568 comparison-model-trait units. The only unique official-rule event was outside all recorded credible sets and did not alter a claim-bearing result (Figure 1D).

### Matching support and disease statistics explained some, but not all, reclassification

The actual multi-signal support S_M was smaller than the historical ABF support S_A in all 642 comparisons, with 19-114 variants removed per comparison (median 65; median 7.67%; Figure 2A). A0 replay reproduced the historical ABF posteriors to within 3.55x10^-13, establishing numerical identity before attribution.

Restricting the ABF calculation from S_A to S_M changed 15 categorical states (A0-to-A1) while retaining all 112 historical H4 states. Replacing the harmonized GCST disease definition with the matched GJOKA z-statistic definition changed another 19 states (A1-to-A2; Figure 2B). Fixed-versus-native sdY and matched-z-versus-rounded GJOKA sensitivity definitions produced no categorical changes within the frozen 642. Input coordination therefore mattered, but it did not erase the high-information shared-signal screen.

After exact support and disease-statistic matching, comparison with the frozen multi-signal result still showed bidirectional H4/H3 reclassification (Figure 2C). Among 113 A2 H4 comparisons, 79 retained H4, eight changed to H3, four were model-sensitive and 22 were uninformative. Among 452 A2 H3 comparisons, 413 retained H3, ten changed to H4, six were model-sensitive and 23 were uninformative (Figure 2D). Thus, strict matched-input transitions comprised eight H4-to-H3 and ten H3-to-H4 comparisons. The 139 total A2-to-M state changes also included ambiguity and information changes and cannot be interpreted as 139 corrections.

Ten of 12 historical directional transitions remained strict H4/H3 changes under matched inputs. FCRL3-CD8_ET remained H4 in A0, A1 and A2 but was H3 under the primary PF10 multi-signal analysis. Two historical cases entered the multi-signal analysis from matched-input ambiguous states and were no longer counted as strict A2-to-M reversals. This prevented preservation of a historical narrative from overriding the matched-input definition.

Among the 520 comparisons with a definite PF10 H4 or H3 state, PF50 produced the same state in 491 (94.42%), changed four to the alternative supported state and was uninformative in 25 (Figure 2E). The remaining 122 PF10 model-sensitive or uninformative comparisons were not included in this denominator. PF50 concordance was therefore high among definite PF10 states, but it was not 491 of all 642 comparisons.

Signal-pair semantics further limited comparison-level interpretation. All 92 stable-H4 comparisons and all 428 stable-H3 comparisons retained the same qualifying signal-pair identity between PF10 L=10 and at least one other PF10 L setting. However, 32 of the 92 H4-supported comparisons also contained an H3-qualifying pair (Figure 2F). H4 support therefore meant that at least one shared pair was stable, not that every signal in the region was shared. Conversely, H3 support identified a stable distinct pair and did not prove the global absence of another shared pair.

### Simulation exposed a trade-off between false sharing, shared-signal recovery and discovery adequacy

The primary simulation branch completed all 486,000 iterations with no recorded technical errors. Multi-signal inference failed to produce an evaluable signal pair in many iterations because one or both traits lacked a credible set: 130,994 iterations had no credible set for either trait, 16,819 lacked a disease credible set and 177,405 lacked a QTL credible set. No iteration had credible sets for both traits but no eligible pair. A total of 160,782 iterations (33.08%) were pair-evaluable (Figure 3A,D).

This discovery layer materially changed interpretation of unconditional performance. Pair-evaluable rates ranged from 13.29% in S5 to 59.79% in S2. In S1, one true shared signal, the unconditional matched H4 rate was 54.12%, whereas H4 was selected in 94.06% of pair-evaluable iterations. In S4, two signals per trait with one shared pair, the corresponding rates were 9.57% and 66.72%. Conditional performance showed that the estimator often recognized sharing once a signal pair existed, but the unconditional rates captured the combined burden of discovery and pair classification (Figure 3B).

Across the two frozen distinct-signal scenarios, the average false-H4 rate decreased from 12.41% with ABF to 8.56% with matched multi-signal inference, a relative reduction of 31.02%. The gain was not uniform. In S2, which used correlated but distinct variants, the matched false-H4 rate remained 16.00% overall and 26.76% among pair-evaluable iterations. In S5, which contained two high-LD signals per trait without a shared pair, the false-H4 rate fell from 4.32% with ABF to 1.12% with matched multi-signal inference (Figure 3C).

The decrease in false H4 was accompanied by lower recovery in the shared-signal scenarios: average H4 recovery decreased from 32.99% with ABF to 26.66% with matched multi-signal inference, a relative loss of 19.20%. This result precluded a claim of general superiority. The S6 mismatch sensitivity produced few decision flips in the implemented, closely related LD contrast, but the zero-pair branch lacked per-trait credible-set counts. We therefore did not generalize S6 to ancestry mismatch or severe reference-panel mismatch.

### IL12RB2-NK showed cross-resource support with an incomplete chromatin chain

IL12RB2-NK was a representative stable-H4 comparison in OneK1K. Best PF10 signal-pair PP.H4 values were 0.9980 across L=5, 10 and 20; PF50 L=10 yielded PP.H4=0.9965 (Figure 4A). The comparison also contained a distinct signal pair, illustrating why stable H4 did not impose a single global mechanism label on the region.

TenK10K NK-cell eQTL data reproduced the PBC-IL12RB2 sharing pattern under the bounded single-causal replication model (396 overlapping variants; default PP.H4=0.9975; low-prior H4/[H3+H4]=0.9760). FinnGen returned three PBC-IL12RB2 molecular-QTL colocalization records, for l1.NK, l1.PBMC and l2.NK strata. PP.H4 ranged from 0.9698 to 0.9706, with credible-set overlap of five to nine variants (Figure 4B). These strata came from one resource and were not counted as three independent cohorts.

The aligned PBC risk allele was associated with higher IL12RB2 expression in OneK1K, TenK10K and the compatible FinnGen strata (Figure 4C). Effect magnitudes were not compared across resources because the expression transformations and models differed. The concordant direction strengthened the readability of the regulatory association but did not establish expression mediation.

The chromatin layer remained partial. The representative eQTL variant lay inside an accessibility peak linked to IL12RB2; the peak-gene link coefficient was 0.141, and peak caQTL q values were 3.93x10^-13 and 6.02x10^-15 in the two NK strata. The eQTL variant had maximum PIP 0.575 but did not enter the peak caQTL credible set. PBC-caQTL signal sharing was not established. We therefore treated this as positional chromatin support rather than a complete disease-to-chromatin-to-expression cascade (Figure 4D).

### FCRL3 combined reproducible B-cell sharing with a model-sensitive T-cell counterexample

FCRL3 showed stable OneK1K B-cell sharing in intermediate and memory B cells. Under PF10 L=10, best signal-pair PP.H4 values were 0.9937 and 0.9910, respectively (Figure 5A). TenK10K intermediate B cells reproduced the sharing pattern (343 overlapping variants; default PP.H4=0.9916; low-prior H4/[H3+H4]=0.9217; Figure 5B). Because the same PBC GWAS was reused, this was cross-QTL-resource support rather than independent disease replication.

The PBC risk allele was associated with lower FCRL3 expression in the compatible OneK1K and TenK10K B-cell contexts. Current FinnGen public output returned no direct PBC-FCRL3 pair. That non-return was a coverage boundary, not evidence against sharing.

FCRL3-CD8_ET provided the clearest input-matched counterexample to a simple comparison-level interpretation. Its single-causal ABF state remained H4 across A0, A1 and A2 (PP.H4=0.9413347, 0.9413350 and 0.9492605, respectively), whereas the PF10 multi-signal result supported H3, with best PP.H4=0.0036 and PP.H3 approximately 0.992. The same comparison was H4-supported under PF50 (best PP.H4=0.9919; Figure 5C). The result therefore showed that exact input matching did not remove the procedure-dependent classification, while PF-number sensitivity prevented it from being described as a universal CD8-cell falsification. It was evidence about the tested cell-QTL model and adjustment strategy, not evidence that FCRL3 has no role in CD8 T cells.

### Liver expression supported lineage detectability but not corrected PBC-specific enrichment

Both target-lineage pairs passed technical and detectability gates in all five PBC and all five control liver donors. For FCRL3 in B-lineage cells, median target-lineage CPM was 5.48 in PBC and 12.45 in controls; the mean PBC-minus-control difference in log1p CPM was -0.786. The exact two-sided permutation P value was 0.111 and the two-target BH q value was 0.111 (Figure 6A).

For IL12RB2 in NK-lineage cells, median target-lineage CPM was 6.66 in PBC and 4.24 in controls; the mean log1p CPM difference was 0.330. The exact P value was 0.0635 and the BH q value was 0.111 (Figure 6B). The positive direction was descriptive and did not cross the prespecified corrected threshold.

These results established that both genes could be detected in the relevant liver immune-lineage compartments in this dataset. They did not show corrected PBC-specific enrichment, tissue mediation or a disease-state mechanism (Figure 6C). The small donor sample and surgical non-lesion controls further limited generalization. The tissue layer therefore constrained, rather than completed, the regulatory narrative.

## Discussion

This study used a fixed PBC comparison universe to ask why regulatory assignments change when single-causal screening is followed by source-matched multi-signal inference. The central finding was that input coordination explained a measurable portion of the changes but did not eliminate bidirectional H4/H3 reclassification. Restricting the support set changed 15 of 642 states, and matching the disease statistic changed 19. After those steps, eight ABF H4 comparisons supported distinct pairs under the multi-signal procedure and ten ABF H3 comparisons supported shared pairs. The direction was therefore not limited to falsifying favorable ABF results.

The matched-input design changes the interpretation of earlier single-causal-to-multi-signal contrasts. An unmatched comparison could not distinguish the effect of a smaller variant intersection from the effect of a different disease-statistic source or the effect of representing several causal components. A0/A1/A2 did not convert the final comparison into a controlled experiment in which only the number of causal variants changed; ABF and SuSiE-based colocalization still differ in priors, parameterization, signal discovery and decision rules. It did, however, remove two concrete alternative explanations and define the residual reclassification more precisely.

Signal-pair reporting was as important as the comparison-level count. The stability audit showed that all 92 H4-supported and 428 H3-supported comparisons retained the relevant pair identity across PF10 L settings. At the same time, 32 H4-supported comparisons contained a qualifying distinct pair. This coexistence is biologically plausible in loci with several regulatory variants and statistically incompatible with a forced one-label mechanism. The appropriate interpretation of H4 is that at least one disease-QTL signal pair is supported as shared under the tested model. The appropriate interpretation of H3 is that a distinct pair is supported, not that the locus lacks every possible shared component.

PF10/PF50 results provide a second boundary. Among comparisons with a definite PF10 H4/H3 state, 491 of 520 retained the same state under PF50. This high conditional agreement supports the overall stability of many assignments. Yet FCRL3-CD8_ET showed a near-complete change from H3 under PF10 to H4 under PF50. Expression-factor adjustment changes the phenotype model and the residualized LD used for fine-mapping. A more favorable posterior under one specification is not evidence that the specification is biologically true. The counterexample is therefore useful precisely because it remains unresolved: it identifies a cell context in which regulatory attribution depends on a defensible modeling choice.

The simulations clarified both the benefit and the cost of the multi-signal workflow. In the frozen distinct-signal scenarios, matched multi-signal inference reduced false-H4 decisions on average. The improvement was largest in the high-LD two-by-two no-sharing scenario and incomplete in the correlated-distinct scenario. Shared-signal recovery also decreased. This trade-off argues against presenting a lower H4 count as self-validating evidence of better inference.

The channel audit revealed why unconditional and conditional performance differed. Two thirds of the primary iterations never produced an evaluable signal pair, most often because at least one trait lacked a credible set. Conditional H4 rates can be high after a pair is found while overall recovery remains modest. These are different estimands: discovery adequacy asks whether the model generates the components needed for evaluation; pair-conditional inference asks how the estimator classifies an available pair. Reporting only the latter would overstate end-to-end performance, whereas labeling the former as technical failure would misdescribe normal weak-signal behavior.

The external axes demonstrate how a reliability framework can strengthen biological interpretation without inflating mechanism. IL12RB2-NK was stable across OneK1K configurations, reproduced in TenK10K and supported by FinnGen molecular-QTL strata. The risk allele was consistently associated with higher expression. Prior PBC studies have also prioritized IL12RB2 through integrative genetic analyses [19,20], so the contribution here is not first nomination of the gene. It is the source-aware, cell-context-specific and signal-pair-bounded evaluation. The chromatin data remained positional because the eQTL anchor was absent from the peak caQTL credible set and disease-caQTL colocalization was not established.

FCRL3 B-cell sharing was supported in OneK1K and TenK10K, with a consistent lower-expression direction for the risk allele. Independent 2026 work has reported PBC-related FCRL3 evidence in liver B cells and plasma-protein colocalization [21,22]. Those findings increase biological plausibility but do not turn the present same-GWAS molecular-QTL analyses into independent disease replication. The FCRL3-CD8_ET result further shows that support for one gene can be cell-context specific: strong B-cell sharing can coexist with a T-cell assignment that changes under covariate specification.

The liver analysis prevented an equally common inferential jump. Both targets were detectable in the expected lineages in every donor, supporting tissue relevance at the level of presence. Neither target showed corrected PBC-specific enrichment in this bounded 5-versus-5 analysis. Genetic regulatory effects need not produce a large average case-control expression difference in an affected organ, particularly across heterogeneous cell states and disease stages. The null corrected result is therefore not a contradiction of the genetic association, but it also cannot be used as affirmative tissue mediation.

The study has several strengths. It used study-derived disease LD, cell-specific active donors and covariate-matched QTL LD rather than one generic reference matrix. It preserved a prespecified 642-comparison workload, including a large H3 layer that allowed rescue as well as falsification. The matched-input audit retained the same comparison identities and did not select examples after the A2-to-M results. Complete signal-pair, model-sensitivity and uninformative states were retained. Finally, external QTL resources, allele direction and donor-level tissue data were assigned separate evidentiary roles.

Several limitations define the claim ceiling. First, only the high-information subset received multi-signal analysis; the study is PBC-wide screening followed by bounded reclassification, not a multi-signal analysis of all 6,923 comparisons. Second, real data contain no causal truth, so H4-to-H3 and H3-to-H4 changes are reclassifications rather than measured error corrections. Third, the simulation used two empirical 128-variant LD templates and a finite parameter grid. It describes single-configuration operating characteristics over that grid, not end-to-end calibration of the composite real-data gate or performance at every disease architecture, sample size or LD mismatch. Fourth, credible-set discovery limited pair-evaluable iterations; larger or more diverse simulations would not by themselves solve weak information in a given dataset. Fifth, OneK1K and TenK10K analyses reused the same PBC GWAS. Sixth, the liver study contained five donors per group, used non-lesion surgical controls and applied a bounded target panel rather than full-transcriptome state modeling. Finally, no perturbational experiment tested whether changing IL12RB2 or FCRL3 expression alters PBC-relevant immune or biliary phenotypes.

Three next tests follow directly from these limits. The first priority is external disease replication: repeat signal-pair analysis when an independent, well-powered PBC GWAS with compatible ancestry, allele definitions and regional summaries becomes available. The second is model resolution: test PF-sensitive assignments using independent QTL cohorts with donor-level genotypes and prespecified covariate models. The third is mechanism: perturb IL12RB2 in NK cells and FCRL3 in B-cell subsets, then measure defined immune phenotypes and interactions with cholangiocyte-relevant systems. Those experiments would distinguish a reproducible regulatory association from direct biological mediation.

## Conclusions

At PBC risk loci, matching variant support and disease-statistic definitions explained part of the difference between single-causal and multi-signal colocalization, but strict bidirectional reclassification remained. Reliable regulatory attribution required signal-pair identity, coexistence of shared and distinct pairs, covariate-model sensitivity and credible-set discovery to be reported separately. IL12RB2-NK and FCRL3 B-cell assignments received bounded cross-resource support, whereas liver data supported lineage detectability without corrected disease enrichment. The resulting framework improves interpretability without treating statistical signal sharing as causal mechanism.

## List of abbreviations

ABF: approximate Bayes factor; BH: Benjamini-Hochberg; CPM: counts per million; CS: credible set; eQTL: expression quantitative-trait locus; GWAS: genome-wide association study; H3: posterior hypothesis of two distinct associated variants/signals; H4: posterior hypothesis of a shared associated variant/signal; LD: linkage disequilibrium; PBMC: peripheral blood mononuclear cell; PBC: primary biliary cholangitis; PF: expression factor; PIP: posterior inclusion probability; QTL: quantitative-trait locus; RSS: regression with summary statistics.

## Declarations

### Ethics approval and consent to participate

Ethics approval was not required because this study exclusively reanalysed publicly available, de-identified data and involved no new participant recruitment or identifiable data collection. The original studies reported their applicable ethics approvals and participant consent.

### Consent for publication

Not applicable.

### Availability of data and materials

PBC summary statistics are available through GWAS Catalog study GCST90061440. Study-derived PBC regional statistics and LD are available from the GJOKA archive. The OneK1K cohort, updated release and TenK10K resource are identified separately in their cited publications and Zenodo records. HRA008003 is available through GSA-Human. Code, compact aggregate outputs, manifests, frozen protocols, source-bound figures and submission-interface assets are versioned in the public repository at `https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/tree/r7b4a-human-genomics-interface-2026-10-10` [18]. Additional files 1 and 2 contain the released supplementary workbook and machine-readable derived tables. Individual-level genotype, BAM, pseudobulk matrices and source archives governed by third-party licences are not redistributed; their source accessions and conditions are recorded in Supplementary Table S1.

### Competing interests

The authors declare that they have no competing interests.

### Funding

This research received no specific grant from any funding agency in the public, commercial or not-for-profit sectors. No funder had any role in study design, data analysis, interpretation, manuscript preparation or the decision to submit.

### Authors' contributions

ZC: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Visualization and Writing - original draft. TQ: Conceptualization, Methodology, Validation, Supervision, Project administration and Writing - review and editing. Both authors interpreted the results and approved the final manuscript.

### Acknowledgements

Not applicable.

### Authors' information

ZC is an MSc student in Bioinformatics at The Chinese University of Hong Kong, Shenzhen. His research focuses on multi-omics analysis and clinical cancer research, including integrative multi-omics approaches and the tumor microenvironment. He holds a BSc in Biomedical Sciences from Queen Mary University of London and an MB in Clinical Medicine from Nanchang University.

## References

1. Gulamhusein AF, Hirschfield GM. Primary biliary cholangitis: pathogenesis and therapeutic opportunities. *Nat Rev Gastroenterol Hepatol.* 2020;17:93-110. doi:10.1038/s41575-019-0226-7.
2. Cordell HJ, Fryett JJ, Ueno K, et al. An international genome-wide meta-analysis of primary biliary cholangitis: novel risk loci and candidate drugs. *J Hepatol.* 2021;75:572-581. doi:10.1016/j.jhep.2021.04.055.
3. Yazar S, Alquicira-Hernandez J, Wing K, et al. Single-cell eQTL mapping identifies cell type-specific genetic control of autoimmune disease. *Science.* 2022;376:eabf3041. doi:10.1126/science.abf3041.
4. Cuomo ASE, Spenceley E, Tanudisastro HA, et al. Impact of rare and common genetic variation on cell type-specific gene expression in human blood. *medRxiv.* 2025. doi:10.1101/2025.03.20.25324352. Dataset: Zenodo record 18221260.
5. Giambartolomei C, Vukcevic D, Schadt EE, et al. Bayesian test for colocalisation between pairs of genetic association studies using summary statistics. *PLoS Genet.* 2014;10:e1004383. doi:10.1371/journal.pgen.1004383.
6. Wang G, Sarkar A, Carbonetto P, Stephens M. A simple new approach to variable selection in regression, with application to genetic fine mapping. *J R Stat Soc Series B Stat Methodol.* 2020;82:1273-1300. doi:10.1111/rssb.12388.
7. Wallace C. A more accurate method for colocalisation analysis allowing for multiple causal variants. *PLoS Genet.* 2021;17:e1009440. doi:10.1371/journal.pgen.1009440.
8. NHGRI-EBI GWAS Catalog. Study GCST90061440. https://www.ebi.ac.uk/gwas/studies/GCST90061440. Accessed 10 Oct 2026.
9. Gjoka A, Cordell HJ. Fine-mapping the results from genome-wide association studies of primary biliary cholangitis using SuSiE and h2-D2. *Genet Epidemiol.* 2025;49:e22592. doi:10.1002/gepi.22592.
10. Cordell HJ, Gjoka A. PBC fine-mapping summary statistics and study-derived LD archive. https://www.staff.ncl.ac.uk/heather.cordell/GjokaPaper.html. Accessed 10 Oct 2026.
11. Xue A, Yazar S, Alquicira-Hernández J, et al. Genetic variants associated with cell-type-specific intra-individual gene expression variability reveal mechanisms of genome regulation. *Nat Commun.* 2026. Published online September 21, 2026. doi:10.1038/s41467-026-77453-9.
12. Xue A, et al. OneK1K cell-specific cis-eQTL summary statistics, genotypes and covariates. Zenodo. 2026. https://doi.org/10.5281/zenodo.18910121.
13. Zou Y, Carbonetto P, Wang G, Stephens M. Fine-mapping from summary data with the "Sum of Single Effects" model. *PLoS Genet.* 2022;18(7):e1010299. doi:10.1371/journal.pgen.1010299.
14. Cuomo ASE, et al. TenK10K phase 1 molecular-QTL and fine-mapping resources. Zenodo. 2026. https://doi.org/10.5281/zenodo.18221260.
15. Kanai M, Delorey TM, Honkanen J, et al. Population-scale immune multiome atlas reveals regulatory disease mechanisms. *Nature.* 2026. Published online September 30, 2026. doi:10.1038/s41586-026-11078-2.
16. Jin C, Jiang P, Zhang Z, et al. Single-cell RNA sequencing reveals the pro-inflammatory roles of liver-resident Th1-like cells in primary biliary cholangitis. *Nat Commun.* 2024;15:8690. doi:10.1038/s41467-024-53104-9.
17. National Genomics Data Center. GSA-Human HRA008003. https://ngdc.cncb.ac.cn/gsa-human/browse/HRA008003. Accessed 10 Oct 2026.
18. Open Regulatory Evidence Project. Analysis code, frozen protocols and aggregate results. GitHub. https://github.com/1209433622cz-maker/igan-open-regulatory-evidence. Accessed 10 Oct 2026.
19. Wang Q, Yan H, Wang N, Yuan J. Causal genetics prioritizes therapeutic targets and blood signatures in primary biliary cholangitis. *npj Syst Biol Appl.* 2026. doi:10.1038/s41540-026-00817-w.
20. Lin Y, Xu X, Chen H, Tang H, Hua Y, Mei J. Genetic mechanisms of primary biliary cholangitis and its association with immune cells using Mendelian randomization and biological annotation. *Medicine (Baltimore).* 2026;105(22):e49146. doi:10.1097/MD.0000000000049146.
21. Han Z, Ran Y, Liu R, et al. FCRL3 as a potential link between Benzo[a]pyrene exposure and primary biliary cholangitis: insights from comparative toxicogenomics and multi-omics analysis. *BMC Gastroenterol.* 2026;26:101. doi:10.1186/s12876-026-04614-x.
22. Xi J, Wang S, Chen J, et al. Exploration and discovery of treatment targets for primary biliary cholangitis based on plasma and cerebrospinal fluid proteomics: a multicenter Mendelian randomization study. *PLoS One.* 2026;21(2):e0340166. doi:10.1371/journal.pone.0340166.

## Figure legends

**Figure 1. Study scope, bounded follow-up and model-integrity gates.** (A) Flow from the 6,923-comparison PBC-wide registry to 5,460 ABF-eligible comparisons and the frozen 642-comparison multi-signal subset. (B) Prespecified roles within the subset. (C) Final PF10 multi-signal comparison states. (D) The earlier targeted current-release identity gate (14 comparison-model rows across seven comparisons) and the expanded corrected kriging diagnostic closure (2,568 comparison-model-trait units). These denominators describe different audit tasks, not the number of cell types. The official-rule event was reviewed and did not enter a credible set.  
**Abbreviations:** ABF, approximate Bayes factor; CS, credible set; H3, distinct-signal-pair support; H4, shared-signal-pair support; PF10, model using ten expression factors.

**Figure 2. Matched inputs explain part, but not all, of bidirectional reclassification.** (A) Variants removed when the historical ABF support was restricted to the actual multi-signal intersection. (B) Categorical changes for adjacent A0/A1/A2/M arms; these counts are not additive. (C) Full matched-input A2-to-M transition matrix. (D) Correct H4 and H3 denominators after input matching. (E) PF10/PF50 sensitivity among 520 comparisons with definite PF10 H4/H3 states. (F) Stable signal-pair semantics: 60 stable-H4 comparisons had no qualifying H3 pair under the frozen thresholds, whereas 32 contained qualifying shared and distinct pairs.  
**Abbreviations:** A0, historical ABF; A1, support-matched ABF; A2, support- and disease-statistic-matched ABF; M, frozen multi-signal result.

**Figure 3. Simulation separates credible-set discovery from pair-conditional inference.** (A) Primary multi-signal outcome channels by scenario. (B) Pair-evaluable, unconditional H4 and pair-conditional H4 rates. (C) Unconditional ABF and matched multi-signal H4 rates; S2 and S5 are distinct-signal scenarios. (D) Aggregate discovery channels. The primary branch had no recorded technical errors and no both-CS/no-pair events.  
**Abbreviations:** CS, credible set; S1, one shared signal; S2, correlated distinct signals; S3, two disease signals and one QTL signal with partial sharing; S4, two signals per trait with one shared pair; S5, two signals per trait with no shared pair under high LD; S6, matched-versus-mismatched LD sensitivity.

**Figure 4. IL12RB2-NK is supported across molecular-QTL resources within bounded causal claims.** (A) OneK1K best signal-pair PP.H4 across PF10/PF50 and L configurations. (B) FinnGen PBC-IL12RB2 molecular-QTL records. (C) Direction of the PBC risk allele across OneK1K, TenK10K and FinnGen. (D) Separate measured associations and positional chromatin evidence. The eQTL anchor is not a member of the linked peak caQTL credible set, and PBC-caQTL colocalization has not been established. These unestablished relationships are not depicted as causal connections; the evidence map does not assert a complete causal cascade.  
**Abbreviations:** caQTL, chromatin-accessibility quantitative-trait locus; eQTL, expression quantitative-trait locus; L, maximum SuSiE effects; PF, expression-factor model.

**Figure 5. FCRL3 combines reproducible B-cell sharing with a T-cell model-sensitivity counterexample.** (A) OneK1K PF10 best signal-pair PP.H4 for representative cells. (B) Cross-QTL-resource B-cell support. (C) FCRL3-CD8_ET across matched-input ABF arms and PF10/PF50 multi-signal configurations. A0, A1 and A2 use their own unrounded source values (PP.H4=0.9413346827, 0.9413349988 and 0.9492605462); their common H4 classification does not imply identical posterior values. (D) Claim boundary for direction and FinnGen coverage.  
**Abbreviations:** B_IN, intermediate B cell; B_MEM, memory B cell; CD8_ET, effector CD8 T cell.

**Figure 6. Liver data localize target-lineage expression but do not show corrected disease enrichment.** (A) Donor-level FCRL3 B-lineage log1p CPM. (B) Donor-level IL12RB2 NK-lineage log1p CPM. Points are donors; boxes summarize the five donors per group. (C) Tissue evidence ceiling. Exact P values used all 252 possible 5-versus-5 label assignments, followed by BH correction across two targets.  
**Abbreviations:** BH, Benjamini-Hochberg; CPM, counts per million; PBC, primary biliary cholangitis.

## Additional files

**Additional file 1.** `Additional_file_1_Supplementary_Tables_S1-S10.xlsx` (Microsoft Excel workbook). Editable reading interface for Supplementary Tables S1-S10.

**Additional file 2.** `Additional_file_2_Machine_Readable_Supplementary_Data.zip` (ZIP archive). Machine-readable TSV, TSV.GZ and JSON source/derived tables, plus a file-level SHA-256 manifest and README. The archive excludes individual-level genotype, BAM, pseudobulk matrices and licensed source archives.

The two files contain the following prespecified supplementary modules:

**Supplementary Table S1.** Data sources, versions, accessions, checksums and redistribution status. Delivered in `R7B3A_Supplementary_Tables_S1-S10.xlsx` and `supplements/S1/`.  
**Supplementary Table S2.** Complete 6,923-comparison screening registry and 5,460 ABF-eligible subset. Delivered as a compressed machine-readable registry and workbook view in `supplements/S2/`.  
**Supplementary Table S3.** Frozen 642-comparison roles, A0/A1/A2/M trajectories and categorical states. Delivered in `supplements/S3/`.  
**Supplementary Table S4.** Support-set member and identity audit, including removed-variant counts and hashes. Delivered in `supplements/S4/`.  
**Supplementary Table S5.** Source-matched PF10/PF50 LD and SuSiE quality-control metrics. Delivered in `supplements/S5/`.  
**Supplementary Table S6.** Signal-pair posterior results, cross-L identity and mixed H4/H3 semantics. Delivered in `supplements/S6/`.  
**Supplementary Table S7.** Simulation parameter grid, iteration-level channel definitions and scenario summaries, including the compressed 486,000-row channel audit. Delivered in `supplements/S7/`.  
**Supplementary Table S8.** TenK10K and FinnGen external molecular-QTL records and allele-direction mappings. Delivered in `supplements/S8/`.  
**Supplementary Table S9.** Donor-level liver target-panel metrics, exact tests and sensitivity analyses. Delivered in `supplements/S9/`.  
**Supplementary Table S10.** Claim-evidence ledger and Methods-Results mirror. Delivered in `supplements/S10/`.
