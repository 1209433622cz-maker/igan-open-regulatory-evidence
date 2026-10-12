# R7B1A：Eligibility、Harmonization 与完整比较宇宙

## 结果前冻结规则

纳入规则在读取 PBC-wide 后验之前写入协议：

1. 疾病 universe 为 56 个 GJOKA non-HLA regions；
2. 细胞 universe 为 OneK 的 14 个冻结 cell labels；
3. 基因 TSS 必须位于 locus boundary ±1 Mb；
4. 基因在至少一个冻结细胞中 source q<0.05；
5. 对已纳入基因，保留每个具有 source top-summary 的冻结细胞，不因该细胞 q≥0.05 而删除；
6. disease–QTL 交集至少 200 variants 才执行 ABF；
7. 不得使用 posterior 增删 gene、cell 或 locus。

## Universe

```text
disease loci                         56
cells                                14
source-significant genes genomewide  5,712
mapped locus–gene pairs              589
frozen comparisons                   6,923
loci with >=1 eligible gene          55
locus without eligible gene          19
```

`589 locus–gene` 在当前数据中对应 589 个唯一基因。6,923 个比较中有 1,553 个 cell-specific source q<0.05；其余细胞按预冻结的“gene-level ascertainment, all available cells”规则保留，用于测量 cell-context specificity，而非暗中增加阳性机会。

## GWAS harmonization

GCST90061440 GRCh37 GWAS 与 OneK BIM 按位置、非歧义 allele/strand 和 BIM A1 effect orientation 对齐。输出 51,772 条 locus-level eligible rows：

- 56/56 loci ≥200 variants；
- 最小 locus 243 variants；
- 最大 locus 1,724 variants；
- conflicting duplicate variants：按 locus 排除并记录；
- palindromic unresolved variants：排除。

输入身份：

```text
GWAS SHA-256  439aa72c59b876236de2b8172c443a447cefa6868ace535183cec8b758a05921
BIM SHA-256   6e28edad34d5930ca99f7be873e4684a885e26433d13ddba3d970bb8f8ad0bb6
ranges SHA-256 403366d805060824672e615e024255d46e30d05678943fcf3ed57fa60336ff5d
combined SHA-256 7f06b1e302a2d9244af53128806964a8563895216cb18b2972f1aeffb67a8a40
```

## comparison-level overlap

TSS±1 Mb 被应用到每个 gene，而不是简单把整个疾病 locus 复制给所有基因。结果：5,460 个比较达到 ≥200 variants；1,463 个比较因基因 cis-window 与疾病区域的有效交集不足而标记 `INSUFFICIENT_VARIANT_OVERLAP`。这些记录保留在 master table 中，不解释为生物学阴性。
