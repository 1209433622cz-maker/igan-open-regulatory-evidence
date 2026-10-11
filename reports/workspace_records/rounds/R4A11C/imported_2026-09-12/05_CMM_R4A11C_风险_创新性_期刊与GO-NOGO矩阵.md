# CMM R4A11C — 风险、创新性、期刊与 GO/NO-GO 矩阵

## 1. 主要风险矩阵

|风险|概率|影响|当前缓解策略|触发动作|
|---|---:|---:|---|---|
|2026 female/male summary长期不公开|高|高|FinnGen R12独立sex branch|继续primary access，同时推进R12|
|R12 SSc在262 excluded endpoints中|低-中|高|先读excluded list|若excluded，R12仅all-sex工程|
|R12 male病例少、低功效|高|中|heterogeneity+CI+power|标记INCONCLUSIVE_LOW_POWER|
|R12 founder population导致signal差异|中|中-高|区域fine-map/LD/方向解释|不把discordance直接判生物反向|
|FinnGen disease与multiome共享生态|中|中|TenK10K独立QTL replication|不称完全独立分子验证|
|chr22 disease不与caQTL共享|中|高|严格FALSIFICATION|降级为expression-linked或停止|
|SYNGR1不胜出20-gene competition|中|高|公平统一分析|接受替代效应基因或否定机制|
|组织层不重现|中|中|GSE312129+GSE249279|保留遗传机制，降低组织主张|
|raw input归档不足|高|中|建立RAW_INPUT_PROVENANCE|投稿前必须补齐|

## 2. 新颖性边界

### 已被现有文献占据

- sex-specific SSc GWAS；
- female SSc–SYNGR1 broad-tissue GTEx colocalization；
- SSc skin snRNA/snATAC/spatial；
- SSc tissue-resident immune eQTL/GWAS integration；
- SSc single-cell + MR。

### 仍可成立的组合创新

**A.** published female locus的cell-resolved chromatin→expression signal refinement；  
**B.** disease/caQTL/eQTL三边same-signal证据，而非简单交集；  
**C.** FinnGen R12独立sex-stratified disease replication；  
**D.** TenK10K独立molecular replication；  
**E.** genetic-priority机制进入untreated SSc tissue验证；  
**F.** negative/untestable/falsified被预先定义并完整报告。

## 3. GO/NO-GO决策矩阵

### Gate FG-1 — R12 endpoint availability

- PASS：`M13_SYSTSLCE`不在excluded list + real female/male/meta bytes可取；
- CONDITIONAL：endpoint存在但对象权限未取得；
- FAIL：明确被excluded且无sex-specific结果。

### Gate FG-2 — R12 data intake

P0 + H6 + GRCh38 + schema + region coverage全部PASS。

### Gate FG-3 — R12 chr22 replication

- REPLICATED_SIGNAL；
- DIRECTIONAL_SUPPORT_ONLY；
- INCONCLUSIVE_LOW_POWER；
- DISCORDANT_WITH_ADEQUATE_POWER；
- UNTESTABLE。

若`DISCORDANT_WITH_ADEQUATE_POWER`，在进入组织层前强制hostile reassessment。

### Gate C1 — Main mechanism

D1 + E1 + M1 + peak-link + QC + candidate competition。

- Full PASS → GO tissue；
- partial → 降级命题；
- adequate-data fail → FALSIFIED；
- missing input → HOLD，不等于FAIL。

## 4. 期刊档次与证据要求

|最终证据|建议目标|
|---|---|
|Full C1 + R12 sex replication + strong untreated tissue validation|Genome Medicine / Cell Genomics / Nature Communications（高门槛尝试）|
|Full C1 + genetic replication，tissue较弱|Rheumatology / Arthritis & Rheumatology相关方向 / Genome Medicine视新颖性|
|Partial disease-eQTL mechanism + R12 support|Arthritis Research & Therapy / Journal of Translational Medicine等|
|仅molecular overlap，无disease signal|不建议围绕该机制单独投稿|

期刊不是当前阶段的优化目标；首先保证C1和独立复制真实成立。

## 5. 当前项目判定

```text
PROJECT                       = CONDITIONAL_GO
PRIMARY_2026_DISEASE_BYTES    = NOT_OBTAINED
FINNGEN_R12_SEX_INFRASTRUCTURE= CONFIRMED
R12_SSC_SEX_BYTES             = NOT_YET_OBTAINED
MOLECULAR_EXACT_CS_OVERLAP    = CONFIRMED_DESCRIPTIVE_ONLY
MOLECULAR_SIGNAL_COLOC        = NOT_TESTED
DISEASE_SIGNAL_COLOC          = NOT_TESTED
C1_count                      = null
R4B                           = HOLD
```

FinnGen R12使项目从“等待型HOLD”转为“可以立即推进独立复制接入”的CONDITIONAL GO，但不允许在真实bytes到位前提前宣布任何R12 SSc结果。
