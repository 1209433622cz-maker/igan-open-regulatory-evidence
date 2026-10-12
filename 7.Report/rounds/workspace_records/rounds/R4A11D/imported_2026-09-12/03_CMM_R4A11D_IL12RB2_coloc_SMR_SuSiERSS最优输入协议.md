# IL12RB2：coloc / SMR / SuSiE-RSS 最优 FinnGen 输入方案

## 1. 总体排序

### A. Coloc

**Primary custom disease coloc：R13 `M13_SYSTSLCE` all-sex**

理由：

- core SSc endpoint；
- 当前最新release；
- 883 cases；
- GRCh38；
- REF/ALT、beta、SE、AF完整；
- 不需要旧GCST009131那类A2/SE恢复。

**Bridge / validation：R12 `M13_SYSTSLCE`**

理由：2026 FinnGen immune multiome官方明确包含 **GWAS colocalization against FinnGen R12**。因此R12是把IL12RB2疾病信号与FinnGen multiome现有browser/precomputed结果对齐的最佳release。

**Sensitivity：R13/R12 `SYSTSCLE_STRICT`, `CREST`**

只用来回答“更严格定义/亚型下是否方向一致”，不能用它们取代main endpoint。

### B. SMR

**首选 outcome：R13 `M13_SYSTSLCE`**。

疾病summary具备：effect allele、other allele、beta、SE、AF、P。结合endpoint-level case/control N，可转换为SMR需要的outcome输入。

Molecular exposure建议优先：

1. TenK10K / independent immune eQTL；
2. FinnGen immune eQTL作同生态补充；
3. GTEx只作broad-tissue对照。

注意：

- SMR/HEIDI需要合适LD；
- FinnGen disease + FinnGen molecular QTL不应成为唯一“独立”证据；
- 不把HEIDI通过写成因果证明；
- IL12RB2如果已经被原论文/已有研究定位，应把SMR定位成signal triangulation，而不是“发现基因”。

### C. SuSiE-RSS

**首选 disease summary：R13 `M13_SYSTSLCE`，前提是取得可靠的ancestry-matched LD。**

因为R13直接给 beta/SE，所以可构造 z，不需要近似SE。

但真正的决定因素不是R12还是R13，而是 **LD是否匹配**。当前项目已从2019 GCST009131看到 external-LD mismatch 能导致RSS gate失败，因此R13也必须执行：

- SNP identity/order hash；
- allele orientation；
- AF mismatch；
- z–LD kriging；
- `estimate_s`；
- matrix symmetry / PSD；
- region coverage。

如果没有足够匹配的Finnish/Finngen LD，**不要为了运行SuSiE-RSS而硬用普通EUR LD**。可优先使用FinnGen官方release的fine-mapping结果作为主证据，再把外部RSS作为敏感性分析。

## 2. IL12RB2专用输入决策树

### 主分析

```text
R13 M13_SYSTSLCE all-sex
  -> P0/H6 provenance+schema
  -> chr1 IL12RB2 frozen region
  -> matched molecular QTL
  -> matched LD / or FinnGen native fine-map
  -> disease fine-mapping
  -> disease↔eQTL coloc
  -> disease↔caQTL coloc (若有IL12RB2对应peak)
  -> bounded effector-gene competition
```

### R12 multiome桥接

```text
R12 M13_SYSTSLCE
  -> extract same IL12RB2 region
  -> compare to FinnGen multiome precomputed R12 coloc
  -> independently reproduce key signal where raw QTL stats permit
  -> cross-release concordance R12 vs R13
```

### 性别分层

```text
R12 sex-specific M13_SYSTSLCE
  -> FIRST verify endpoint not in 262-drop list
  -> female / male beta-SE-AF
  -> Cochran Q heterogeneity
  -> do not infer sex specificity from P_female<0.05 and P_male>0.05
```

## 3. 为什么不推荐其他endpoint做IL12RB2主分析

- `SYSTSCLE_FG`：non-core；病例多但没有full core statistics，不能因为case count相同就冒充可分析GWAS。
- `SYSTSCLE_ICD10`：non-core；虽然病例数869/867接近main endpoint，仍缺core full-statistics角色。
- `SYSTSCLE_STRICT`：病例只有约320；适合specificity sensitivity，不适合主fine-mapping。
- `CREST`：亚型、病例546/533；适合subtype sensitivity。
- progressive SSc：R13 161；power弱。
- drug/chemical-induced：9；禁止用于此类遗传信号分析。

## 4. 最终推荐表

| 方法 | 第一选择 | 第二选择 | 关键风险 |
|---|---|---|---|
| coloc | **R13 M13_SYSTSLCE** | R12 M13_SYSTSLCE | LD/多信号；样本重叠 |
| FinnGen multiome cross-check | **R12 M13_SYSTSLCE** | R13 custom reanalysis | multiome预计算使用R12 |
| SMR/HEIDI | **R13 M13_SYSTSLCE + independent eQTL** | R12 + TenK10K | LD、样本量、HEIDI解释 |
| SuSiE-RSS | **R13 M13_SYSTSLCE + matched LD** | R12 + native finemap | LD mismatch是最大风险 |
| phenotype specificity | SYSTSCLE_STRICT | CREST | power显著下降 |
| sex replication | **R12 sex-specific M13_SYSTSLCE（若未被drop）** | 2026 author summary when obtained | R12 availability需字节验收 |
