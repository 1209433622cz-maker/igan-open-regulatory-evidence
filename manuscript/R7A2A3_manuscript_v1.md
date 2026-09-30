# Source-matched multi-signal colocalization resolves independently replicated immune-cell regulatory signals in primary biliary cholangitis

**Authors:** [AUTHOR NAMES TO BE COMPLETED]

**Affiliations:** [AFFILIATIONS TO BE COMPLETED]

**Correspondence:** [CORRESPONDENCE TO BE COMPLETED]

## Abstract

### Background and aims

Primary biliary cholangitis (PBC) genome-wide association studies have identified many susceptibility loci, but assigning local genetic signals to genes and immune-cell contexts remains difficult when a region contains multiple association signals. We tested whether established PBC loci could be resolved into reproducible cell-specific regulatory signals while preserving negative and non-generalizing evidence.

### Methods

We applied a prespecified, bounded analysis to three established non-HLA PBC loci and nine gene–cell combinations. European PBC genome-wide association summary statistics (8,021 cases and 16,489 controls) were paired with study-derived disease linkage disequilibrium (LD). Cell-specific cis-eQTLs and genotype data from OneK1K were used to construct donor-matched QTL LD after covariate residualization. Single-causal-variant colocalization was used as a screening step, followed by SuSiE-RSS fine-mapping and signal-pair colocalization under four model configurations and three shared-signal priors. Prespecified signals were tested in the independent TenK10K single-cell eQTL resource. Orthogonal liver-tissue evaluation used a bounded target panel in five untreated PBC donors and five non-lesion liver controls from HRA008003, with donor-level exact permutation tests.

### Results

IL12RB2 showed stable PBC–eQTL signal sharing in NK cells across all OneK1K configurations (minimum default posterior probability for a shared signal [PP.H4], 0.9980; minimum low-prior H4/[H3+H4], 0.9806) and replicated in TenK10K NK cells (396 variants; default PP.H4, 0.9975; low-prior H4/[H3+H4], 0.9760). FCRL3 showed context-dependent sharing in OneK1K, with stable evidence in intermediate B, memory B, naïve CD4 T, NK, and resting NK cells. Its B-cell signal replicated in TenK10K intermediate B cells (343 variants; default PP.H4, 0.9916; low-prior H4/[H3+H4], 0.9217). A single-causal analysis suggested sharing for FCRL3 in effector T cells (PP.H4, 0.9413), but source-matched multi-signal analysis reversed this interpretation (minimum PP.H4, 0.0036; PP.H3 approximately 0.992). INAVA remained uninformative because its OneK1K QTL evidence was weak. Both prespecified target–lineage pairs were detectable in all five PBC and all five control livers. FCRL3–B was directionally lower in PBC, whereas IL12RB2–NK was directionally higher; neither passed the two-target corrected enrichment threshold (both q=0.1111).

### Conclusions

Established PBC loci resolve into replicated IL12RB2–NK and FCRL3–B regulatory signal-sharing axes when disease and QTL LD are modeled from their source cohorts and multiple local signals are separated. The liver analysis supports lineage detectability but does not establish disease-specific expression enrichment, mediation, or causality.

**Keywords:** primary biliary cholangitis; colocalization; single-cell eQTL; linkage disequilibrium; SuSiE; FCRL3; IL12RB2; immune cells

## Introduction

Primary biliary cholangitis (PBC) is a chronic autoimmune cholestatic liver disease in which immune-mediated injury to small intrahepatic bile ducts can progress to fibrosis and cirrhosis [1]. Large genetic studies have expanded the map of PBC susceptibility, including many non-HLA loci and immune pathways [2]. This progress creates a narrower but consequential problem: association at a locus does not identify the regulated gene, the cellular setting in which regulation occurs, or whether an apparent disease–expression overlap represents one shared signal rather than two correlated signals.

Population-scale single-cell expression quantitative trait locus (eQTL) resources provide a route to cell-resolved interpretation. OneK1K mapped cis-regulatory effects across approximately 1.27 million peripheral blood mononuclear cells from 982 donors [3]. TenK10K subsequently profiled more than 5.4 million cells from 1,925 donors across 28 immune cell types, using whole-genome sequencing and single-cell expression measurements [4]. These resources substantially increase the range of testable immune contexts. However, their scale alone does not resolve three recurrent sources of error: linkage disequilibrium (LD) that differs between the disease and molecular-QTL samples, multiple causal signals within a locus, and selective emphasis on cell types that yield a favorable posterior.

The PBC loci containing FCRL3, IL12RB2, and INAVA offer a stringent setting in which to address these problems. All three have prior genetic or molecular support, so their analysis cannot be presented as gene discovery [2]. Disease-side multi-signal fine-mapping has also been reported for established PBC loci [5]. The unresolved question is whether study-matched disease LD and donor-matched cell-QTL LD, combined with multi-signal decomposition and independent single-cell eQTL replication, can distinguish stable cell-context signals from misleading single-signal results. A further question is whether prioritized target–lineage pairs are observable in PBC liver without converting a small tissue dataset into an unsupported case–control expression claim.

We therefore performed a preregistered, bounded evaluation of three PBC loci and nine gene–cell combinations. We used single-causal colocalization only as a screening step, reconstructed source-matched LD for each eligible OneK1K cell type, and required stability across SuSiE model configurations and shared-signal priors before replication in TenK10K. We retained a weak-QTL control and a cell-context reversal in the evidence hierarchy. Finally, we evaluated FCRL3 in B-lineage cells and IL12RB2 in NK-lineage cells in five PBC and five control livers using donor-level inference. Our aim was to resolve reproducible regulatory signal sharing and its cellular context, while keeping the claim ceiling below biological mediation or causality.

## Results

### A bounded, source-aware workflow interrogated established PBC loci

The analysis began from frozen eligibility rules rather than a genome-wide search for the largest posterior (Figure 1). The disease input was the European component of the international PBC genome-wide association meta-analysis, comprising 8,021 cases and 16,489 controls (N=24,510) [2]. The harmonized genome-wide file contained 5,054,572 valid numeric variant rows. Study-derived locus summary statistics and LD matrices were available for the 56 analyzed non-HLA regions [5]. We selected locus 2 for IL12RB2, locus 4 for FCRL3, and locus 6 for INAVA according to the prespecified positive-control and falsification design.

Nine OneK1K comparisons were frozen before signal-level analysis: IL12RB2 in NK cells; FCRL3 in intermediate B (B_IN), memory B (B_MEM), naïve CD4 T (CD4_NC), effector T (CD8_ET), naïve CD8 T (CD8_NC), NK, and resting NK (NK_R) cells; and INAVA (source symbol C1orf106) in CD4_NC cells. All nine were testable, yielding 24,001 QTL rows. Harmonization retained 1,098 eligible variants at IL12RB2, 958 at FCRL3, and 1,248 at INAVA before comparison-specific intersections. The single-causal screen identified seven candidate shared-signal comparisons. FCRL3/CD8_NC and INAVA/CD4_NC remained uninformative and were not promoted to source-LD analysis (Supplementary Tables S2 and S3).

For the seven triggered comparisons, cell-specific active donors were used to build QTL-side LD: 975 for FCRL3/B_IN, 970 for FCRL3/B_MEM, 980 for FCRL3/CD4_NC, 980 for FCRL3/CD8_ET, 980 for FCRL3/NK, 750 for FCRL3/NK_R, and 980 for IL12RB2/NK. The corresponding genotype matrices contained 2,667–2,687 variants at FCRL3 and 2,386 variants at IL12RB2. Residualized LD accounted for sex, age, six genotype principal components, and either 10 or 50 expression factors. All 28 disease and QTL SuSiE fits—seven comparisons across four prespecified configurations—converged, providing a complete signal-level analysis rather than a selected subset (Supplementary Tables S4–S6).

### IL12RB2 showed stable NK-cell regulatory signal sharing

The single-causal screen for IL12RB2 in NK cells included 1,081 variants and yielded PP.H4=0.9982 under the default shared-signal prior (Figure 2; Supplementary Table S3). Because the PBC disease region was known to contain multiple signals, promotion did not depend on this result. Source-matched multi-signal analysis included 1,016 common variants and resolved two disease credible sets and one QTL credible set in every configuration.

The best disease–QTL signal pair was stable across PF10_L5, PF10_L10, PF10_L20, and PF50_L10. The minimum default PP.H4 across these configurations was 0.9980, the minimum default H4/(H3+H4) was 0.9980, and the minimum ratio under the skeptical p12=1×10−6 prior was 0.9806. Thus, the interpretation did not depend on a single assumed number of effects, on the choice between 10 and 50 expression factors, or on the default shared-signal prior. We classified IL12RB2–NK as robust disease–eQTL signal sharing in the OneK1K resource, an E2 replicated/sensitivity-supported association rather than evidence of expression mediation.

### FCRL3 signal sharing was cell-context dependent

FCRL3 showed a wider but non-uniform cellular pattern (Figure 3). The source-matched multi-signal gate passed in B_IN, B_MEM, CD4_NC, NK, and NK_R cells across all four configurations. The minimum default PP.H4 values were 0.9938 for B_IN, 0.9912 for B_MEM, 0.9914 for CD4_NC, 0.9396 for NK, and 0.9712 for NK_R. At p12=1×10−6, the corresponding minimum H4/(H3+H4) values were 0.9411, 0.9187, 0.9244, 0.6086, and 0.7715. The lower skeptical-prior ratios in NK and NK_R indicate stronger prior sensitivity than in the B and CD4_NC contexts, although all prespecified configurations retained the same pass classification.

The CD8_ET comparison exposed the principal reason for separating screening from adjudication. Under the single-causal model, FCRL3/CD8_ET appeared strongly supportive of a shared signal (PP.H4=0.9413; H4/[H3+H4]=0.9415). Source-matched SuSiE analysis instead resolved one disease credible set and two QTL credible sets. Across configurations, the minimum default PP.H4 for the tested signal pair was 0.0036, the H4/(H3+H4) ratio was 0.0037, and PP.H3 was approximately 0.992. This reversal favored distinct disease and eQTL signals. It was retained as a primary methodological result rather than hidden as a failed cell type.

Two prespecified comparisons did not enter the multi-signal stage. FCRL3/CD8_NC had single-causal PP.H4=0.1314 and was classified as uninformative. INAVA/CD4_NC had a minimum QTL P value of 3.92×10−4, PP.H4=0.0262 under the default prior, and PP.H4=0.0027 at p12=1×10−6. We therefore retained INAVA as an uninformative weak-QTL control. This result does not exclude a role for INAVA in PBC; it limits what this OneK1K cell–gene comparison can establish.

### TenK10K independently replicated the two primary regulatory axes

We next tested the two prespecified compatible-cell axes in TenK10K, an independent single-cell eQTL cohort [4]. The replication analysis used exact variant intersections with the same PBC disease summary statistics and evaluated p12 values of 1×10−6, 1×10−5, and 1×10−4 (Figure 4; Supplementary Table S7).

For IL12RB2 in TenK10K NK cells, 396 variants were shared with the disease locus. PP.H4 was 0.9975 under the default prior, with H4/(H3+H4)=0.9975. Under the skeptical prior, PP.H4 and the H4 ratio were both 0.9760; under p12=1×10−4, PP.H4 was 0.9998. This independently reproduced the IL12RB2–NK signal-sharing pattern observed in OneK1K.

For FCRL3 in TenK10K intermediate B cells, 343 variants were shared. The default PP.H4 was 0.9916 and H4/(H3+H4)=0.9916. The skeptical-prior PP.H4 was 0.9216 and the corresponding H4 ratio was 0.9217; PP.H4 rose to 0.9991 at p12=1×10−4. Twenty-four of 45 variants in the TenK10K source credible set overlapped the disease comparison, including the frozen shared variants. Because donor-level TenK10K genotypes were not used to reconstruct source LD in this analysis, these results are classified as robust single-causal molecular replication supported by source credible-set identity, rather than unique causal-variant resolution.

### Liver tissue supported detectability but not disease-specific enrichment

The orthogonal tissue analysis addressed a narrower question: whether FCRL3 could be detected in a prespecified hepatic B-lineage gate and IL12RB2 in a prespecified hepatic NK-lineage gate. It did not attempt full tissue reclustering or transcriptome-wide differential expression. We analyzed publicly accessible HRA008003 single-cell BAMs from five untreated PBC liver donors and five non-lesion liver controls obtained during surgery for hepatic hemangioma [6]. Across the ten donors, 49,637 cells passed the frozen called-cell procedure (23,809 PBC and 25,828 control cells), with 2,981–7,316 called cells per donor.

Both target–lineage pairs passed lineage adequacy and detectability gates in every donor (Figure 5; Supplementary Tables S8 and S9). Donors, rather than cells, were treated as biological replicates. For FCRL3 in the B-lineage gate, median target counts per million lineage UMIs were 5.48 in PBC and 12.45 in controls. The PBC-minus-control difference in mean log1p CPM was −0.7863, with an exact two-sided 5-versus-5 label-permutation P=0.1111 and two-target Benjamini–Hochberg q=0.1111. The negative direction was preserved in all ten leave-one-donor-out comparisons.

For IL12RB2 in the NK-lineage gate, median CPM was 6.66 in PBC and 4.24 in controls. The PBC-minus-control difference in mean log1p CPM was +0.3300, with exact P=0.06349 and q=0.1111. The positive direction was preserved in all ten leave-one-donor-out comparisons. Both prespecified target–lineage pairs were detectable in all five PBC and all five control donors. FCRL3–B showed a lower direction in PBC, whereas IL12RB2–NK showed a higher direction; neither target passed the prespecified two-target corrected case–control enrichment threshold.

### The integrated evidence supports replicated signal sharing with a strict claim ceiling

The completed evidence chain supports two replicated regulatory axes (Figure 6). IL12RB2–NK met the source-matched OneK1K multi-signal gate and independently replicated in TenK10K NK cells. FCRL3 met the OneK1K multi-signal gate most strongly in B_IN and B_MEM cells, showed additional supported contexts, and independently replicated in TenK10K intermediate B cells. The CD8_ET reversal demonstrated that a favorable single-causal posterior did not guarantee signal-specific sharing. INAVA remained visibly uninformative. Liver data showed that the two target–lineage pairs were observable across all donors, while corrected case–control enrichment was not supported.

Accordingly, the highest evidence tier reached by the central claims is E2: replicated or sensitivity-supported association. No inference is made about expression mediation, novel gene discovery, or therapeutic validity.

## Discussion

Using a bounded analysis that preserved study-specific LD and separated local signals, we resolved two established PBC loci into reproducible immune-cell regulatory axes. IL12RB2 showed a stable shared signal in NK cells across OneK1K model configurations and replicated in TenK10K NK cells. FCRL3 showed the strongest and most prior-resistant evidence in B-cell contexts, with independent replication in TenK10K intermediate B cells, while the broader OneK1K pattern remained context dependent. The same workflow rejected an apparently positive FCRL3/CD8_ET result after multi-signal decomposition and retained INAVA as an uninformative weak-QTL control. Tissue analysis then established target–lineage observability in liver without supplying evidence for corrected PBC-specific enrichment.

Because FCRL3 and IL12RB2 have previously been implicated by PBC genetics and molecular-QTL studies, the contribution of this study lies in source-matched, cell-context-resolved multi-signal inference and independent single-cell eQTL replication rather than gene discovery. The international PBC meta-analysis already nominated FCRL3 and reported extensive molecular colocalization across susceptibility loci [2]. Subsequent disease-side fine-mapping applied SuSiE-RSS and h2-D2 to 56 non-HLA loci [5]. More recently, Han and colleagues integrated genetic and molecular-QTL data for FCRL3, localized expression predominantly to B cells in PBC liver, and performed Raji-cell experiments [7]. A separate cross-tissue study combined PBC genetics with immune traits, blood transcriptomics, and liver single-cell data [8]. These studies rule out broad claims of first gene implication, first B-cell localization, or first PBC multi-omics integration. Our narrower contribution is the explicit pairing of source-derived disease LD with donor- and cell-matched QTL LD, the requirement for agreement across multi-signal configurations, and replication in a second population-scale single-cell eQTL resource.

The IL12RB2 result links a well-established PBC immune pathway to a specific regulatory context. IL12 signaling has long been implicated in PBC susceptibility and Th1-skewed immune biology [1,2]. The present data refine that background by showing stable disease–IL12RB2 eQTL sharing in NK cells in two independent molecular cohorts. This convergence makes the NK context a rational setting for functional follow-up, but it does not show that the disease allele changes IL12RB2 expression in hepatic NK cells or that this change mediates disease. The decisive next test would edit the prioritized regulatory haplotype in donor-derived or induced NK cells, quantify allele-specific IL12RB2 expression and IL12-responsive signaling, and test whether the direction agrees with the QTL and disease-risk alleles.

FCRL3 illustrates why cell-type resolution must be paired with signal resolution. The strongest OneK1K results occurred in intermediate and memory B-cell contexts, and the compatible intermediate B-cell result reproduced in TenK10K. This is consistent with prior B-cell localization [7], but the value added here is statistical discrimination rather than anatomical discovery. The additional OneK1K signals in CD4_NC, NK, and NK_R cells suggest that local genetic regulation is not confined to one annotated cell class. Their biological interpretation should remain secondary because TenK10K replication was prespecified only for the compatible B-cell axis and because the NK results were more sensitive to the skeptical prior. Targeted functional work should therefore begin in B cells and treat the other contexts as ranked hypotheses rather than equivalent conclusions.

The FCRL3/CD8_ET reversal is a direct stress test of the analysis design. A conventional single-causal analysis produced PP.H4=0.941, which could easily have been reported as a positive cell-specific colocalization. Once one disease signal and two QTL signals were modeled with source-matched LD, PP.H4 fell to 0.0036 and H3 dominated. This result does not imply that single-causal colocalization is generally invalid; it shows that its assumption can be decision-changing in a multi-signal region. The finding supports a practical workflow in which inexpensive ABF analysis screens comparisons, while any promoted claim is adjudicated with source-appropriate LD and multi-signal models when the required genotype information exists [9-11].

The liver analysis changes the interpretation by adding a boundary rather than a new positive claim. Both target genes were detectable in their prespecified immune-lineage gates in all ten donors, which establishes that the proposed cell contexts are observable in the disease organ. The case–control directions were opposite for the two genes and remained stable to leave-one-donor-out analysis, but neither comparison passed the corrected threshold. Given the five-versus-five donor design, these results are compatible with effects too small or heterogeneous to detect, as well as with no disease-specific expression difference. They cannot be used to label FCRL3 as downregulated or IL12RB2 as upregulated in PBC liver. This separation between genetic signal sharing and cross-sectional tissue abundance is biologically plausible: a cis-regulatory effect relevant to risk may be state dependent, modest in average abundance, or active before established disease and treatment-independent tissue sampling.

Several limitations define the claim ceiling. First, the disease GWAS and source LD were European, and OneK1K and TenK10K predominantly sampled donors of European ancestry. Generalizability to other ancestries remains untested. Second, the analysis was intentionally bounded to three genes and nine cell–gene combinations. It estimates the strength of prespecified hypotheses and controls selection, but it does not exhaustively nominate genes at the two loci. Third, the TenK10K replication used exact-overlap summary statistics and source credible-set membership without reconstructing donor-level QTL LD; it therefore provides strong independent molecular replication under the single-causal approximation rather than a second source-LD multi-signal proof. Fourth, the liver target-panel gate used predefined lineage markers and molecule counts from ten donors. It was designed for donor-level detectability and two targeted comparisons, not for full cell-state discovery, compositional analysis, or differential-expression inference. Fifth, colocalization distinguishes shared from distinct association signals probabilistically; it does not establish the direction of mediation, the effector transcript, or a biochemical mechanism.

These limitations define specific next experiments. Priority 1 is allele-aware perturbation of the shared FCRL3 regulatory signal in primary or induced B-cell models and of the IL12RB2 signal in NK-cell models, with target expression and receptor-pathway responses measured in the same cells. Priority 2 is replication of signal-specific colocalization using ancestry-diverse PBC summary statistics and matching ancestry-specific QTL LD. Priority 3 is a larger liver cohort with genotype, treatment, disease-stage, and cell-state information, analyzed at the donor level to test genotype-by-state effects rather than only mean case–control abundance. A positive result in these experiments would raise the evidence from replicated association toward mechanism; absence of an allele-dependent functional effect would falsify the current regulatory interpretation.

In conclusion, source-matched multi-signal analysis resolved established PBC loci into independently replicated FCRL3–B and IL12RB2–NK disease–eQTL signal-sharing axes. The workflow also rejected a misleading cell-context result and preserved weak-QTL and tissue-null evidence. These results prioritize cell contexts for mechanistic testing while stopping short of causal mediation, disease-specific liver expression, or therapeutic claims.

## Methods

### Study design and frozen evidence gate

This study was designed as a bounded, open-data analysis of established PBC susceptibility loci. Before signal-level modeling, we froze the disease dataset, three target/control genes, nine OneK1K cell–gene combinations, shared-signal priors, model configurations, replication rule, and tissue target–lineage pairs. No new locus, gene, or cell type was added after outcome inspection. The evidence sequence was: byte and schema validation; allele and build harmonization; single-causal screening; source-matched LD construction; SuSiE-RSS and signal-pair colocalization; independent TenK10K replication; and a donor-level liver target-panel analysis. Negative or uninformative results remained part of the final evidence set.

### PBC genome-wide association data and disease LD

PBC association statistics were obtained from GWAS Catalog accession GCST90061440, using the GRCh37 European five-panel meta-analysis from Cordell et al. [2]. This dataset included 8,021 cases and 16,489 controls (N=24,510). After byte-level and schema validation, 5,054,572 rows contained valid numeric association data. Study-derived regional summary statistics and LD matrices were obtained from the public GJOKA archive accompanying the disease fine-mapping analysis [5]. The IL12RB2 analysis used locus 2 and the FCRL3 analysis locus 4; INAVA used locus 6 for the initial comparison. File byte counts, SHA-256 hashes, and harmonization receipts were recorded before analysis.

### OneK1K eQTL inputs and frozen comparisons

OneK1K provides cell-specific cis-eQTL summary statistics, genotype data, and covariates for a population-scale single-cell PBMC cohort [3]. The frozen analysis included IL12RB2/NK; FCRL3/B_IN, B_MEM, CD4_NC, CD8_ET, CD8_NC, NK, and NK_R; and INAVA/CD4_NC, for which the source symbol was C1orf106. Cell labels follow the source resource. Cell-specific active-donor lists were required for QTL LD construction; a global donor set was not substituted for cell types with fewer active donors. The complete frozen QTL extraction contained 24,001 rows.

### Variant identity and allele harmonization

All disease and QTL variants were represented by chromosome, GRCh37 position, and alleles. Effect alleles were aligned to the OneK1K PLINK BIM A1 allele. Strand complements were permitted only when allele identity remained unambiguous. Palindromic variants were excluded when orientation could not be resolved from allele frequency and source metadata. Duplicate or conflicting variant identities, nonnumeric effects or standard errors, and variants absent from the relevant LD matrix were removed. Harmonization was completed before any posterior was calculated. The eligible regional disease tables contained 1,098 variants for IL12RB2, 958 for FCRL3, and 1,248 for INAVA; comparison-specific overlap counts differed after intersection with QTL and LD inputs.

### Single-causal-variant colocalization screen

Approximate Bayes factor colocalization was performed according to Giambartolomei et al. [9]. Case–control disease effects used a prior standard deviation of 0.20, and quantitative-trait QTL effects used 0.15×sdY. The primary priors were p1=1×10−4, p2=1×10−4, and p12=1×10−5. Shared-signal prior sensitivity used p12=1×10−6 and 1×10−4. The principal posterior quantities were PP.H3, representing two distinct signals, PP.H4, representing one shared signal, and H4/(H3+H4), which conditions on the alternatives of distinct or shared association. A default PP.H4≥0.80 and H4/(H3+H4)≥0.80 identified screening candidates, but did not by itself establish a final result. Python implementation was cross-validated against the official R `coloc` implementation; the maximum absolute posterior difference was 1.44×10−15.

### Source-matched QTL LD

For each of the seven promoted comparisons, genotype dosage was extracted only for donors active in the relevant OneK1K cell type. Sample sizes were 975 for B_IN, 970 for B_MEM, 980 for CD4_NC, CD8_ET, NK, and IL12RB2/NK, and 750 for NK_R. Genotype dosage matrices were standardized using the aligned A1 allele. Raw correlation matrices were calculated and then residualized for sex, age, six genotype principal components, and expression factors. PF10, using 10 expression factors, was the primary specification; PF50, using 50 factors, was a covariate sensitivity analysis. Matrix identity, dimension, symmetry, diagonal, finite values, rank behavior, and positive-semidefinite tolerance were checked before SuSiE fitting.

### Multi-signal fine-mapping and signal-pair colocalization

Disease and QTL summary statistics were fine-mapped with SuSiE-RSS [10]. Four configurations were required for every promoted comparison: PF10 with L=5, L=10, and L=20, and PF50 with L=10. Models used `estimate_residual_variance=FALSE`, `estimate_prior_variance=TRUE`, `max_iter=2000`, `tol=1×10−4`, 95% credible sets, and minimum absolute within-set correlation of 0.5. The disease sample size was fixed at 24,510; QTL sample sizes followed the cell-specific donor counts. A fit was eligible only if both disease and QTL models converged and yielded auditable signal and credible-set outputs.

Signal-pair colocalization used `coloc.susie` [11] and the same three p12 values. For each cell–gene comparison and configuration, all eligible disease–QTL signal pairs were evaluated. A robust shared signal required the same adjudication across all four configurations, default PP.H4≥0.80, default H4/(H3+H4)≥0.80, and continued H4 predominance under p12=1×10−6. Results that favored H3, failed convergence, or were driven by weak QTL evidence were not promoted.

### TenK10K replication

TenK10K phase 1 includes matched whole-genome and single-cell RNA sequencing from 1,925 individuals of European ancestry and more than 5.4 million PBMCs across 28 immune cell types [4]. Common-variant cis-eQTLs were mapped within ±100 kb using SAIGE-QTL. Replication was restricted to the two frozen compatible-cell axes: FCRL3 in intermediate B cells and IL12RB2 in NK cells. Exact variant intersections with the PBC disease locus yielded 343 and 396 variants, respectively. ABF colocalization used the same disease input and p12 sensitivity series. Source TenK10K SuSiE credible-set membership was audited for the FCRL3 comparison. Because donor-level TenK10K LD was not reconstructed, the replication layer was described as independent single-cell eQTL replication under a single-causal model with credible-set support, not as source-LD multi-signal adjudication.

### HRA008003 liver target-panel analysis

HRA008003 is an open-access single-cell study of liver and blood in PBC [6]. The present analysis used liver BAM files from five treatment-naïve PBC donors (HRR1849459–HRR1849463) and five non-lesion liver controls from hepatic hemangioma surgery (HRR1849454–HRR1849458). Source sizes and checksums were verified, and each BAM passed `samtools quickcheck` and a tag-schema preflight.

Molecule representatives were counted from records carrying the 10x `xf` bit 8 flag, corrected cell barcode (`CB`), gene name (`GN`), and unique molecular identifier (`UB`). Called cells were defined with a frozen order-of-magnitude procedure: an expected upper rank of 6,000 cells per library and a threshold equal to 10% of the 99th percentile UMI count among the top 6,000 barcodes. Libraries were required to contain 2,500–7,500 called cells and a median of at least 500 UMIs per cell.

B-lineage cells required at least two of CD79A, CD79B, MS4A1, CD37, CD74, HLA-DRA, CD19, and CD22, at least three B-marker UMIs, and a B-marker sum greater than the maximum NK-, T-, or myeloid-marker sum. NK-lineage cells required at least two of NKG7, GNLY, KLRD1, PRF1, GZMB, XCL1, and XCL2, at least three NK-marker UMIs, an NK-marker sum greater than the B- and myeloid-marker sums, and at least the T-marker sum. T-cell markers were CD3D, CD3E, TRBC1, TRBC2, and IL7R; myeloid markers were LST1, TYROBP, FCER1G, CTSS, AIF1, and LYZ. Each donor–lineage combination required at least ten cells.

Target detectability required at least three target UMIs and at least two target-positive lineage cells per donor. Target CPM was calculated as target UMIs divided by total lineage UMIs ×10^6. These thresholds and the two target–lineage pairs, FCRL3–B and IL12RB2–NK, were frozen before the control BAMs were analyzed.

### Tissue statistical analysis

The biological unit was the donor. The primary endpoint was log1p target CPM within the prespecified lineage. For each target, the difference in group means was compared with the exact distribution of all 252 assignments of five of ten donors to the PBC label. Two-sided exact P values were corrected across the two prespecified targets with the Benjamini–Hochberg method. Leave-one-donor-out analyses assessed whether the estimated direction changed after removal of each donor; they were sensitivity analyses rather than independent replication. Cell-level tests were not used for case–control inference.

### Reproducibility and quality control

Every external input was recorded with its accession, URL, byte count, and available MD5 or locally calculated SHA-256 value. Large third-party inputs and donor-level genotype or molecule tables were not mirrored to the public repository; compact aggregate results, manifests, and code were retained. The OneK1K multi-signal workflow produced 28 of 28 converged disease/QTL fit pairs and passed 21 of 21 independent checks. The tissue analysis passed 19 of 19 independent quality checks. Software versions for the signal-level R analysis were R 4.6.1, `susieR` 0.14.2, and `coloc` 5.2.3.

## Data availability

The PBC GWAS summary statistics are available from the NHGRI-EBI GWAS Catalog under GCST90061440. PBC locus summary statistics and study-derived LD matrices are available from the public GJOKA archive accompanying the PBC fine-mapping study. OneK1K cell-specific cis-eQTLs, genotypes, and covariates are available from Zenodo record 18910121. TenK10K eQTL and fine-mapping resources are available from Zenodo record 18221260. HRA008003 is openly accessible through GSA-Human. The public project repository records exact source objects, hashes, and the local paths expected by the reproducible workflow; it does not redistribute restricted-by-size third-party files or donor-level derived matrices.

## Code availability

Analysis code, frozen protocols, aggregate result tables, data manifests, checksums, and figure source files are available at [https://github.com/1209433622cz-maker/igan-open-regulatory-evidence](https://github.com/1209433622cz-maker/igan-open-regulatory-evidence). The repository preserves stage-specific evidence states and separates large external inputs from publishable aggregate artifacts.

## Ethics statement

This study reanalyzed de-identified, publicly accessible summary-level and single-cell sequencing data. Ethical approval and informed-consent procedures for the original cohorts are reported in the source publications and repositories. [VERIFY TARGET-JOURNAL WORDING AND INSTITUTIONAL REQUIREMENTS BEFORE SUBMISSION.]

## Author contributions

[AUTHOR CONTRIBUTIONS TO BE COMPLETED USING CRediT ROLES.]

## Funding

[FUNDING INFORMATION TO BE COMPLETED AND VERIFIED.]

## Competing interests

[COMPETING-INTEREST DECLARATION TO BE COMPLETED AND VERIFIED.]

## References

1. Gulamhusein AF, Hirschfield GM. Primary biliary cholangitis: pathogenesis and therapeutic opportunities. *Nat Rev Gastroenterol Hepatol.* 2020;17:93–110. doi:10.1038/s41575-019-0226-7.
2. Cordell HJ, Fryett JJ, Ueno K, et al. An international genome-wide meta-analysis of primary biliary cholangitis: novel risk loci and candidate drugs. *J Hepatol.* 2021;75:572–581. doi:10.1016/j.jhep.2021.04.055.
3. Yazar S, Alquicira-Hernandez J, Wing K, et al. Single-cell eQTL mapping identifies cell type-specific genetic control of autoimmune disease. *Science.* 2022;376:eabf3041. doi:10.1126/science.abf3041.
4. Cuomo ASE, Spenceley E, Tanudisastro HA, et al. Impact of rare and common genetic variation on cell type-specific gene expression in human blood. *medRxiv.* 2025. doi:10.1101/2025.03.20.25324352. Dataset: Zenodo record 18221260.
5. Gjoka A, Cordell HJ. Fine-mapping the results from genome-wide association studies of primary biliary cholangitis using SuSiE and h2-D2. *Genet Epidemiol.* 2025;49:e22592. doi:10.1002/gepi.22592.
6. Jin C, Jiang P, Zhang Z, et al. Single-cell RNA sequencing reveals the pro-inflammatory roles of liver-resident Th1-like cells in primary biliary cholangitis. *Nat Commun.* 2024;15:8690. doi:10.1038/s41467-024-53104-9.
7. Han Z, Ran Y, Liu R, et al. FCRL3 as a potential link between Benzo[a]pyrene exposure and primary biliary cholangitis: insights from comparative toxicogenomics and multi-omics analysis. *BMC Gastroenterol.* 2026;26:101. doi:10.1186/s12876-026-04614-x.
8. Wang Q, Yan H, Wang N, Yuan J. Causal genetics prioritizes therapeutic targets and blood signatures in primary biliary cholangitis. *npj Syst Biol Appl.* 2026. doi:10.1038/s41540-026-00817-w.
9. Giambartolomei C, Vukcevic D, Schadt EE, et al. Bayesian test for colocalisation between pairs of genetic association studies using summary statistics. *PLoS Genet.* 2014;10:e1004383. doi:10.1371/journal.pgen.1004383.
10. Wang G, Sarkar A, Carbonetto P, Stephens M. A simple new approach to variable selection in regression, with application to genetic fine mapping. *J R Stat Soc Series B Stat Methodol.* 2020;82:1273–1300. doi:10.1111/rssb.12388.
11. Wallace C. A more accurate method for colocalisation analysis allowing for multiple causal variants. *PLoS Genet.* 2021;17:e1009440. doi:10.1371/journal.pgen.1009440.

## Figure legends

**Figure 1. Prespecified evidence architecture for resolving established PBC loci.** The workflow begins with validated European PBC summary statistics and study-derived disease LD, proceeds through a frozen OneK1K gene–cell screen, reconstructs cell-specific QTL LD for triggered comparisons, and requires multi-signal stability before independent TenK10K replication. HRA008003 liver data provide an orthogonal target–lineage detectability and case–control boundary. Negative and uninformative results remain in the final hierarchy.
**Abbreviations:** eQTL, expression quantitative trait locus; LD, linkage disequilibrium; PBC, primary biliary cholangitis.

**Figure 2. IL12RB2–NK disease–eQTL signal sharing is stable and independently replicated.** OneK1K source-matched multi-signal analysis remained supportive across PF10/PF50 and L=5/10/20 configurations and under the skeptical shared-signal prior. TenK10K NK cells reproduced the result across 396 exact-overlap variants. Posterior probabilities quantify signal sharing and do not demonstrate expression mediation.
**Abbreviations:** H3, posterior hypothesis of distinct association signals; H4, posterior hypothesis of a shared signal; NK, natural killer; PP, posterior probability.

**Figure 3. FCRL3 regulatory signal sharing depends on cellular context and multi-signal resolution.** Stable OneK1K support was observed in intermediate B, memory B, naïve CD4 T, NK, and resting NK cells. The effector T-cell comparison changed from single-causal PP.H4=0.9413 to multi-signal PP.H4=0.0036 with H3 predominance, showing that an apparently favorable screen can represent distinct local signals. The uninformative CD8_NC comparison was not promoted.
**Abbreviations:** B_IN, intermediate B cell; B_MEM, memory B cell; CD4_NC, naïve CD4 T cell; CD8_ET, effector T cell; CD8_NC, naïve CD8 T cell; NK_R, resting NK cell.

**Figure 4. Cross-resource single-cell eQTL replication of the two primary axes.** TenK10K replication used 343 exact-overlap variants for FCRL3 in intermediate B cells and 396 for IL12RB2 in NK cells. Bars or points display PP.H4 and H4/(H3+H4) under p12=1×10−6, 1×10−5, and 1×10−4. The low-prior result is the principal stress test.
**Abbreviations:** H3, distinct signals; H4, shared signal; p12, prior probability that a variant is associated with both traits.

**Figure 5. Donor-level PBC liver target-panel results preserve the tissue null boundary.** FCRL3 CPM within the prespecified B-lineage gate and IL12RB2 CPM within the NK-lineage gate are shown for five PBC and five non-lesion liver control donors. Both targets were detectable in all donors. Exact 5-versus-5 label-permutation tests yielded P=0.1111 for FCRL3–B and P=0.06349 for IL12RB2–NK; both two-target BH-adjusted q values were 0.1111.
**Abbreviations:** BH, Benjamini–Hochberg; CPM, counts per million lineage UMIs; UMI, unique molecular identifier.

**Figure 6. Integrated evidence hierarchy and claim ceiling.** FCRL3–B and IL12RB2–NK reach replicated disease–eQTL signal sharing across independent single-cell eQTL resources. Liver data support target–lineage observability but not corrected disease-specific enrichment. CD8_ET and INAVA results constrain generalization. The highest evidence tier is replicated association; mediation, mechanism, and therapeutic utility remain untested.

## Supplementary table and figure legends

**Supplementary Table S1. Data-source, accession, byte-count, and checksum manifest.**

**Supplementary Table S2. Frozen candidate/control universe and selection rationale.** The table lists the three genes, nine OneK1K cell–gene comparisons, cytobands, disease-locus indices, GRCh37 regions, and prespecified force-multi-signal status.

**Supplementary Table S3. Single-causal ABF colocalization results for all nine frozen comparisons.** Results include common-variant counts, QTL donor counts, minimum P values, posterior hypotheses, p12 sensitivity, and frozen classification.

**Supplementary Table S4. Source-matched QTL LD construction and quality control.** Cell-specific active-donor counts, variant counts, covariate specifications, matrix identity, symmetry, diagonal, rank, finite-value, and positive-semidefinite checks are reported.

**Supplementary Table S5. SuSiE-RSS fit and signal-pair colocalization results.** All 28 disease/QTL model configurations and all evaluated signal pairs are retained with convergence, credible-set counts, posterior probabilities, and prior sensitivity.

**Supplementary Table S6. Disease and QTL credible-set members.** Variant identifiers, aligned alleles, posterior inclusion probabilities, credible-set membership, and source-file provenance are reported.

**Supplementary Table S7. TenK10K independent replication results.** Exact-overlap counts and posterior probabilities under all three p12 values are shown for FCRL3/intermediate B and IL12RB2/NK, with source credible-set membership where available.

**Supplementary Table S8. HRA008003 donor-level target-panel metrics.** Called cells, lineage-cell counts, target-positive cells, target UMIs, lineage UMIs, CPM, and technical QC are reported for all ten donors.

**Supplementary Table S9. Exact permutation and leave-one-donor-out tissue sensitivity analyses.** Primary log1p CPM comparisons, unadjusted exact P values, two-target BH q values, and direction stability are shown.

**Supplementary Table S10. Claim–evidence ledger.** Each central claim is linked to its evidence layer, evidence tier, allowed wording, prohibited wording, and falsifying next test.

**Supplementary Figure S1. INAVA remains uninformative in the frozen OneK1K comparison.** The weak CD4_NC eQTL and prior-sensitive low PP.H4 are displayed without interpreting the result as evidence against any role for INAVA in PBC.

**Supplementary Figure S2. Agreement between the Python ABF implementation and official R coloc.** Posterior differences for all frozen comparisons demonstrate numerical agreement, with a maximum absolute difference of 1.44×10−15.

**Supplementary Figure S3. Source-LD and residual-LD quality-control diagnostics.** Raw, PF10-residualized, and PF50-residualized matrices are compared for all seven promoted cell–gene combinations.

**Supplementary Figure S4. Leave-one-donor-out sensitivity of liver target directions.** The PBC-minus-control mean log1p CPM difference is recalculated after removing each donor. Directional stability is shown separately from statistical significance.

## Draft status note

This is the R7A2A3 scientific manuscript draft v1. Author metadata, funding, competing interests, contribution statements, target-journal formatting, and final supplementary table assembly remain to be completed. Numerical claims are constrained to the frozen R7A2A2 evidence package and its upstream validated result tables.
