# Reproducibility contract

The workflow separates four gates:

1. Byte identity: expected size and checksums must pass.
2. Variant identity: genome build, position, alleles and effect direction must harmonize.
3. Single-signal smoke: Python Wakefield ABF output must agree with official R `coloc` within `1e-10`.
4. Multi-signal adjudication: source-matched, cell-donor-specific LD and a stable 95% SuSiE credible set are required before signal-specific colocalization.

The primary disease dataset is combined IgAN. European-only and Asian-only analyses are supportive and cannot silently replace the primary endpoint. Multiple genes or cells within one locus count as one locus-level result.

The R6A2B0 frozen priors are `p1=p2=1e-4` and `p12=1e-6,1e-5,1e-4`. A robust smoke result requires default PP.H4 ≥ 0.80, default H4/(H3+H4) ≥ 0.80, and low-prior H4/(H3+H4) ≥ 0.50.

