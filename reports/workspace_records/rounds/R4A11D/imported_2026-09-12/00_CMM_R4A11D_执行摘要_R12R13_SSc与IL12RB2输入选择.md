# R4A11D 执行摘要：FinnGen R12/R13 SSc endpoint 与 IL12RB2 输入选择

日期：2026-09-12

## 最终判定

本轮对 FinnGen R12 与 R13 中直接与 systemic sclerosis (SSc) 相关的 endpoint、病例数、core/non-core 状态、GWAS 字段结构、sex-specific 资源和 IL12RB2 下游方法适配性进行了逐项复核。

**主结论：**

1. **IL12RB2 的主 disease outcome 应使用 core endpoint `M13_SYSTSLCE`。**
2. **R13 `M13_SYSTSLCE` 是当前 all-sex coloc / SMR / 自建 SuSiE-RSS 的首选疾病输入**：它是最新 release 的 core SSc endpoint，R13 有 883 例（727 female / 156 male），标准 FinnGen GWAS 提供 GRCh38 `REF/ALT/beta/sebeta/af_alt`。
3. **R12 `M13_SYSTSLCE` 是与 FinnGen immune multiome 对接的首选桥接输入**：R12 有 881 例（728 female / 153 male），而 2026 FinnGen immune multiome 官方明确提供的是 **against FinnGen R12** 的 GWAS colocalization。因此 R12 适合复核/解释已有 multiome colocalization，并与 R13 自建结果做跨 release consistency check。
4. **R12 sex-specific GWAS 是当前唯一被官方文档明确发布的 female/male SSc 候选资源**。它包含 female-only、male-only 和 female–male heterogeneity meta 文件，字段包括 `REF/ALT`, female/male `beta`, `SE`, `AF` 和 Cochran Q heterogeneity P。**但 `M13_SYSTSLCE` 是否在 2,207 个可分析 endpoint 中、还是落在 262 个 exclusion endpoint 中，仍必须读取真实 exclusion-list / object bytes 后才能宣布可用。**
5. **没有找到官方 R13 sex-specific GWAS release 的文档证据。** R13 当前应作为 all-sex 最新疾病输入；不能把 R12 sex-specific 的目录规则自动套到 R13。
6. `SYSTSCLE_FG` 与 `SYSTSCLE_ICD10` 在 R12/R13 Risteys 都明确标注为 **non-core endpoint：only basic statistics are computed**，因此不适合作为公开 full-GWAS 主输入。
7. `SYSTSCLE_STRICT` 与 `CREST` 是更窄的 core phenotype，可用于 specificity/subtype sensitivity，但样本量显著低于 `M13_SYSTSLCE`，不应取代 IL12RB2 主分析。
8. drug/chemical-induced SSc 仅 9 例；R13 progressive SSc 161 例。二者均不适合承担 IL12RB2 主 coloc/SMR/SuSiE-RSS。

## 当前推荐优先级

**All-sex disease analysis：**

`R13 M13_SYSTSLCE` > `R12 M13_SYSTSLCE` >> `R13/R12 SYSTSCLE_STRICT` / `CREST` sensitivity

**Sex-stratified replication：**

`R12 M13_SYSTSLCE female/male`（需先通过 exclusion-list + object-byte 验收） > 2026 Lancet female/male 主GWAS（仍等待正式summary bytes）

**FinnGen multiome 兼容性：**

`R12 M13_SYSTSLCE` 最优，因为官方 multiome colocalization 以 R12 为疾病GWAS层。

## 项目状态更新

- `PROJECT = CONDITIONAL_GO`
- `R4B = HOLD`
- `R13_M13_SYSTSLCE = RECOMMENDED_PRIMARY_ALL_SEX`
- `R12_M13_SYSTSLCE = RECOMMENDED_MULTIOME_BRIDGE`
- `R12_SSc_SEX_SPECIFIC = HIGH_PRIORITY_ACQUISITION / BYTE_NOT_YET_VERIFIED`
- `R13_SSc_SEX_SPECIFIC = NOT_OFFICIALLY_DOCUMENTED_IN_CHECKED_RELEASE_NOTES`

下一阶段建议：**R4A12-FG：R12/R13 M13_SYSTSLCE 真实对象接入 + IL12RB2 区域级 smoke test。**
