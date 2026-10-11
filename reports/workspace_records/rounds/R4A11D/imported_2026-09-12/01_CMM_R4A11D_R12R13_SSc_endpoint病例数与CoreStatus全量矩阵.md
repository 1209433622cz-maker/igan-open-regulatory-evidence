# FinnGen R12 / R13：SSc 相关 endpoint 全量矩阵

## 1. 直接 SSc phenotype

| Endpoint | 定义/角色 | R12 cases (F/M) | R13 cases (F/M) | Core status / full GWAS | IL12RB2用途 |
|---|---|---:|---:|---|---|
| `M13_SYSTSLCE` | 主 systemic sclerosis；ICD-10 M34 + 历史 ICD-9/8；controls exclude `M13_SYSTCONNECT` | **881 (728/153)** | **883 (727/156)** | **Core；首选 full GWAS** | **PRIMARY** |
| `SYSTSCLE_FG` | include `M13_SYSTSLCE`，但 controls exclude `RHEUMA_ENDPOINTS` | 881 (728/153) | 883 (727/156) | **Non-core；Risteys明确“only basic statistics”** | 不作为主GWAS；仅定义敏感性背景 |
| `SYSTSCLE_ICD10` | 仅 ICD-10 M34 | 867 (716/151) | 869 (715/154) | **Non-core；无完整Risteys统计** | 表型定义参考，不作为公开主输入 |
| `SYSTSCLE_STRICT` | 更严格 SSc 定义 | **323 (280/43)** | **320 (277/43)** | Core related endpoint | specificity sensitivity；power较低 |
| `CREST` | limited/CREST subtype | **533 (467/66)** | **546 (477/69)** | Core related endpoint | subtype sensitivity；不替代overall SSc |
| `SYSTEMIC_SCLEROSIS_INDUCED_DRUGS_CHEMIC` | 药物/化学诱导SSc | **9 (6/隐私抑制)** | **9 (6/隐私抑制)** | 无有效GWAS用途 | **NO-GO** |
| `M13_PROGRESSIVE_SYSTEMIC_SCLEROSIS` | ICD-10 M34.0 progressive SSc | R12归档页当前无法可靠读取；不填假值 | **161 (133/28)** | R13页面可见；需manifest确认full object | 低power次级探索，不用于IL12RB2主分析 |

### 重要解释

- `M13_SYSTCONNECT` 是 **systemic connective tissue disorders** 的更宽 phenotype，在 `M13_SYSTSLCE` 中主要作为 control exclusion。它不是 SSc-specific disease outcome，因此不列入 IL12RB2 主分析候选。
- R12→R13 主 endpoint 病例数只增加 2 例（881→883），所以 R13 对 IL12RB2 的优势主要是**更新release和更现代、干净的标准输入链**，而不是样本量的巨大跃升。
- `SYSTSCLE_STRICT` 牺牲 power 换 specificity；应作为 sensitivity，而不是因为“更严格”就默认优于 `M13_SYSTSLCE`。
- `CREST` 是临床亚型，不应当与 general SSc risk locus 的主分析混为一谈。

## 2. Core vs non-core 是本轮最关键的文件可用性分界

Risteys 对 `SYSTSCLE_FG` 和 `SYSTSCLE_ICD10` 明确写明：**This is a non-core endpoint: only basic statistics are computed** / **Not a core endpoint, no data to show**。因此病例数虽然与主endpoint接近，但这并不等于存在一个可用于 coloc/SMR/SuSiE-RSS 的标准 full GWAS 文件。

相反，`M13_SYSTSLCE`, `SYSTSCLE_STRICT`, `CREST` 属于直接可进入 core-analysis 体系的相关 endpoint；最终是否在 public manifest 中有具体对象，应以 R12/R13 manifest 行为最终下载验收依据。

## 3. Release变化

| Endpoint | R12→R13 cases变化 | 解释 |
|---|---:|---|
| M13_SYSTSLCE | +2 | 主SSc稳定；最适合跨release复现 |
| SYSTSCLE_FG | +2 | non-core；不因病例数接近而升级为主输入 |
| SYSTSCLE_ICD10 | +2 | non-core |
| SYSTSCLE_STRICT | -3 | 小样本波动；不表示疾病减少或定义更差 |
| CREST | +13 | 亚型病例略增加，但仍明显小于main SSc |
| Drug/chemical-induced | 0 | 极低病例数，禁用 |
| Progressive SSc | R12未可靠核实 → R13 161 | 仅次级探索 |
