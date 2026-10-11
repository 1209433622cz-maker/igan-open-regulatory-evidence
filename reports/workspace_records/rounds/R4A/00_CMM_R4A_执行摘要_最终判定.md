# CMM R4A — Access + Harmonization + 3-Locus Smoke Test
## 执行摘要与最终判定

**日期**：2026-09-08  
**项目**：SSc_SexBiased_RegulatoryCascade  
**上一阶段**：R3 = CONDITIONAL GO  
**本轮目标**：用最小成本确认 sex-GWAS、FinnGen multiome 与 TenK10K 的真实可执行入口，并对 BCL11A / IRF4 / RPL3-PDGFB 做三位点 smoke test。

---

# 1. 本轮最终状态

```text
R4A = COMPLETE_AS_ACCESS_AND_PRESMOKE_AUDIT
SEX_GWAS_FULL_SUMMARY = NOT_ACQUIRED
SEX_GWAS_GCST_ACCESSION = NOT_RESOLVED
FINNGEN_MULTIOME_RELEASE = VERIFIED_PUBLIC
FINNGEN_MULTIOME_FILES = NOT_ACQUIRED_IN_SESSION
TENK10K_OPEN_DATA_MANIFEST = VERIFIED
TENK10K_FILE_BYTES = NOT_ACQUIRED_IN_SESSION
HARMONIZATION_SPEC = FROZEN_V2
3_LOCUS_GENETIC_PRIOR = PASS
3_LOCUS_FULL_C1_CASCADE = NOT_TESTABLE_WITHOUT_REQUIRED_FILES
R4B_FULL = NOT_AUTHORIZED
NEXT = R4A1_ACCESS_UNLOCK_AND_PIPELINE_UNIT_TEST
```

## 最终判定

> **HOLD_R4B_FULL__GO_R4A1_ACCESS_UNLOCK**

这不是项目 NO-GO。

本轮已经确认：
- 科学问题仍成立；
- 2026 sex-specific SSc GWAS 三个新位点真实、效应方向清晰；
- FinnGen population-scale immune multiome 已于 2026-08-13 公开，并明确包含本项目所需的 cis-eQTL、cis-caQTL、SuSiE、peak-gene link 与 CASCADE；
- TenK10K 的最小复制文件和 SuSiE fine-mapping 文件均公开存在；
- 三个位点中至少 IRF4 具有非常强的外部调控先验，说明“cell-specific regulatory cascade”不是无生物学依据的假设。

但是：

> **R3预注册的 smoke-test PASS 条件是“至少一个位点真实完成 GWAS signal → FinnGen ca/eQTL → peak–gene → cell → shared signal”。本轮没有拿到 sex-GWAS 全量区域统计和 FinnGen multiome 文件字节，因此不能诚实地宣布 C1 PASS。**

---

# 2. 两个真正的硬门

## Gate A — sex-specific SSc full summary statistics

2026论文的数据共享声明明确写明：

- male/female sex-specific GWAS summary statistics 将在发表后通过 NHGRI–EBI GWAS Catalog 提供；
- 检索词建议为 “systemic sclerosis”。

截至本轮多路径检索：
- PMID 已确认：41999721；
- DOI 已确认；
- 论文已正式发表；
- 但**仍未解析到可验证的对应 GCST accession / male与female完整文件**。

因此目前只能使用论文表格中的 lead variants 进行“遗传先验审计”，**不能**用单个lead SNP伪造区域colocalization或fine-mapping。

### Gate A status
**BLOCKING**

---

## Gate B — FinnGen single-nucleus multiome file acquisition

FinnGen官方页面确认：
- public release：2026-08-13；
- n = 1,108；
- snRNA nuclei = 10,612,211；
- snATAC nuclei = 7,100,899；
- 33 cell types；
- 27,294 genes；
- 297,024 ATAC peaks；
- 17,167,198 variants；
- 结果包括 cis-eQTL、cis-caQTL、SuSiE fine-mapping、peak-gene links、CASCADE和GWAS colocalization。

但官方访问方式是：
1. 填写在线表单；
2. 由邮件发送下载说明；
3. 再下载summary statistics。

本会话尚未实际获得这些文件。

### Gate B status
**BLOCKING FOR FULL C1, NOT A RESOURCE-AVAILABILITY FAILURE**

---

# 3. 三个位点的预烟雾测试结果

| Locus | Sex | Lead variant | GWAS evidence | 外部调控先验 | 当前最佳解释 | R4A优先级 |
|---|---|---|---|---|---|---|
| BCL11A | Male | rs2540100 | 强，OR 1.32，P=8.39e-9 | 中等 | 原论文主要是nearest gene + IMR90 chromatin interaction；需要population immune multiome真正定靶 | 2 |
| IRF4 | Female | rs12203592 | 强，OR 0.78，P=2.36e-8 | **很强** | intronic functional regulatory variant；已有IRF4 cis-eQTL和enhancer功能证据；最适合作为首个C1 smoke locus | **1** |
| RPL3-PDGFB | Female | rs66578187 | 强，OR 1.19，P=3.18e-8 | 中等但靶基因不唯一 | `AT` indel + RPL3/PDGFB/附近调控复杂性；必须靠normalize + fine-map + peak-gene，不能按生物学偏好选PDGFB | 3 |

---

# 4. 为什么 IRF4 升级为首个 smoke locus

rs12203592：
- hg38 chr6:396321；
- 位于 IRF4 内含子；
- T allele 是2026 SSc female-specific保护方向（OR < 1）；
- 已有外部研究显示它可以调节IRF4表达；
- 在primary melanocyte eQTL研究中，它是非常强的IRF4 cis-eQTL；
- 既往功能研究直接证明该位点处于增强子环境并具有allele-specific regulatory activity。

这并不证明其在SSc免疫细胞中的作用已经成立。

恰恰相反，这使其成为理想的验证题：

> **已知“variant有调控能力”，但未知“在何种SSc相关免疫细胞、通过何种开放染色质→IRF4级联，与female-specific SSc GWAS信号是否共享”。**

这比从完全没有先验的位点盲目开始更适合R4A单元测试。

---

# 5. 为什么不能现在进入 R4B

若现在直接：
- 下载SSc skin raw data；
- 跑全33类细胞；
- 做全8个sex loci；
- 做MR/PheWAS/drug prediction；

会出现一个研发顺序错误：

> **最脆弱的上游链（GWAS区域统计 + molQTL文件）还没有跑通，就先投入下游几十GB组织数据。**

这违背R3冻结规则，也违背从54篇论文中提炼出的核心原则：

> **先验证最可能让整个故事失败的环节，再扩展容易产生结果的下游分析。**

---

# 6. 下一阶段目标

## R4A.1 — Access Unlock + Pipeline Unit Test

### 必须完成
1. 实际取得 male/female SSc full summary stats；
2. 实际取得 FinnGen multiome 最小必需文件；
3. 下载 TenK10K 10.1 MB gene-level 文件和59.7 MB SuSiE summary；
4. 记录 SHA256/MD5、build、header、allele definition；
5. 先只对 IRF4 跑通端到端；
6. 再跑 BCL11A；
7. 最后用 RPL3-PDGFB indel 做 harmonization stress test。

### R4A.1 PASS
必须至少获得：

```text
GWAS regional stats
→ harmonized variants
→ caQTL/eQTL regional evidence
→ source-provided fine-map
→ signal-aware shared-signal test
→ peak-gene target
→ explicit cell type
```

若IRF4首先形成C1：
- GO_R4B_FULL。

若IRF4失败但BCL11A成功：
- 同样GO_R4B_FULL。

若三个均无C1：
- 区分 biological negative 与 coverage/access failure；
- 只有前者才考虑 NO-GO / TOP2疾病。

---

# 7. 当前论文主张边界

本轮后允许说：

> “We designed a sex-aware, cell-type-resolved regulatory-cascade framework to functionally resolve newly reported SSc susceptibility loci.”

暂时不允许说：

> “We identified causal sex-specific regulatory mechanisms.”

因为真正的shared-signal和C1证据尚未跑出。


## 关键来源（核查日期：2026-09-08）

1. Rodriguez-Martin I, et al. *Sex-specific autosomal susceptibility loci in systemic sclerosis: a genome-wide association study.* Lancet Rheumatology. 2026;8(6):e438-e450. PMID: 41999721. DOI: 10.1016/S2665-9913(25)00376-5.
2. FinnGen. *Access results — FinnGen single-nucleus multiome*, public release 2026-08-13. https://www.finngen.fi/en/access_results
3. Cuomo ASE, et al. TenK10K Phase 1 sc-eQTL data. Zenodo record 18221260. DOI: 10.5281/zenodo.18221260.
4. Praetorius C, et al. Functional studies of IRF4 rs12203592 and subsequent cell-type-specific eQTL work (Genome Research / related mechanistic studies).
5. Existing R3 frozen protocol in this project: `03_CMM_R3_统计兼容性与冻结分析协议_v1.md`.

> 注：本轮严格区分“网页声明可用”“已确认文件清单”“已实际取得文件字节”。未实际取得的数据不会被写成已完成分析。
