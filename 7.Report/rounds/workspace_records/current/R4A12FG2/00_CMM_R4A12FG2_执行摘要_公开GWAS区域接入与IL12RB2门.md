# CMM R4A12FG2 执行摘要：公开 GWAS 区域接入与 IL12RB2 门

执行窗口：2026-09-12—2026-09-13（Asia/Hong_Kong）

## 最终判定

本轮已完成 **R4A12FG2 — FinnGen R12/R13 `M13_SYSTSLCE` 公开对象验收、IL12RB2 区域接入和描述性 smoke gate**。

- `PROJECT = CONDITIONAL_GO`
- `R4B = HOLD`
- `C1_count = null`
- 2026 female/male SSc 主 GWAS 字节仍为 `NOT_OBTAINED`
- FinnGen all-sex IL12RB2 分支为 `PASS_REGIONAL_INPUT_AND_DESCRIPTIVE_SMOKE_GATE`
- 正式 disease↔QTL coloc、SMR/HEIDI、SuSiE-RSS 均为 `NOT_TESTED`

FinnGen all-sex 分支是有边界的工程与敏感性分析，不能替代 2026 sex-stratified chr22/SYNGR1 主线，也不能把 IL12RB2 加入已冻结的 chr22 20-gene competition registry。

## 本轮取得的真实数据

官方 public analysis manifest 显示：

| Release | Endpoint | Cases | Controls | 角色 |
|---|---|---:|---:|---|
| R12 | `M13_SYSTSLCE` | **854** | 484,260 | FinnGen multiome release bridge |
| R13 | `M13_SYSTSLCE` | **883** | 483,310 | 最新 all-sex sensitivity input |

R4A11D 中 R12 的 881 来自 Risteys phenotype 页面，不能写成 public GWAS analysis N；本轮以 manifest 的 854 为最终值。

12 个预注册对象（两版 × 三个 endpoint × summary/index）全部 HEAD=200。R12/R13 主 endpoint 的两个 summary 和两个 index 合计 1,587,342,434 bytes，完整对象尚未下载；已提供安全续传与 provider MD5 验证脚本。

通过远程 Tabix 只读取冻结区域 `GRCh38 chr1:66,840,524–67,840,524`：

| 项目 | R12 | R13 |
|---|---:|---:|
| 区域记录 | 6,855 | 6,855 |
| 唯一位置 | 6,727 | 6,727 |
| 精确 rs6662198 anchor | 1 | 1 |
| P0-FG | PASS | PASS |
| 二次查询 SHA 是否与首次一致 | 是 | 是 |

## 区域信号判定

R12/R13 区域 lead 均为 `rs1954118`，GRCh38 `1:67448804:T:A`：

| Release | beta_ALT(A) | SE | P |
|---|---:|---:|---:|
| R12 | -0.316577 | 0.0753064 | 2.62404×10^-5 |
| R13 | -0.310664 | 0.0742242 | 2.84564×10^-5 |

rs6662198 的精确 GRCh38 键为 `1:67340524:T:C`。R12 beta_ALT(C)=-0.219964、P=6.50145×10^-4；R13 beta_ALT(C)=-0.234512、P=2.09508×10^-4。与 2019 overall SSc 中 T-risk 的方向在效应等位基因翻转后相容。

6,855 个共同变异的 beta Pearson r=0.956608，ALT AF r=0.999999998；任一版本 P<0.05 的 497 个变异中 99.799% 方向一致。这是 **跨 release 稳定性**。两版样本高度嵌套，不能称为独立复制；区域 lead 也没有达到全基因组显著。

## TenK10K IL12RB2 结果

对两个原始 ZIP 逐成员重算得到：

- 28 个细胞类型中 26 个有 IL12RB2 gene-level 记录；缺少的是 CD14 Mono、CD16 Mono。
- 11 个细胞类型返回 source-provided SuSiE credible set，共 17 个 CS、201 条成员、76 个唯一精确变异键。
- 76 个唯一 CS 变异中 68 个可与 R12/R13 区域按 `chr:pos:ref:alt` 精确匹配，覆盖 89.47%。
- FinnGen 区域 lead 与 rs6662198 均不在这些 IL12RB2 CS 中。

现有 TenK10K 小包没有完整 variant-level beta/SE，因而不能从这些 CS 摘要直接运行新的 signal-level coloc。精确重叠只作为输入可用性和描述性证据。

## 下一阶段

下一阶段冻结为：

> **R4A12FG3 — Molecular QTL and LD Feasibility Gate**

目标是取得 IL12RB2 完整 variant-level molecular QTL、相容的 LD、INFO/QC 和冻结的 GRCh38 reference identity，先决定 bounded all-sex coloc 是否技术上可测试。任何输入、coverage 或 LD 门失败均记为 `UNTESTABLE/UNINFORMATIVE`，不能写成 IL12RB2 阴性。

原主线触发条件保持不变：2026 female/male 真实字节到达后，继续 chr22/SYNGR1 的 H6 v2.1、harmonization、coverage 和 C1 主分析。

## 官方依据

- [FinnGen R12 public manifest](https://storage.googleapis.com/finngen-public-data-r12/summary_stats/finngen_R12_manifest.tsv)
- [FinnGen R13 public manifest](https://storage.googleapis.com/finngen-public-data-r13/summary_stats/finngen_R13_manifest.tsv)
- [FinnGen GWAS 字段说明](https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/gwas-results-format)
- [FinnGen sex-specific GWAS 格式与访问说明](https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/sex-specific-gwas-results-format)
- [FinnGen fine-mapping 输出范围与格式](https://docs.finngen.fi/finngen-data-specifics/green-library-data-aggregate-data/core-analysis-results-files/finemapping-results-format)


