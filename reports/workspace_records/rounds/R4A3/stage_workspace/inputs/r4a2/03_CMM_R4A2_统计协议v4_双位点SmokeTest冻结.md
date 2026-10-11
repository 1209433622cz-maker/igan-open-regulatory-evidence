# CMM R4A2：统计协议 v4——双位点 Signal-level Smoke Test 冻结

## 1. 目的

R4A3只回答一个问题：**IRF4与chr22两个优先locus中，是否至少存在一个可被完整复现的SSc GWAS→immune caQTL/eQTL→peak→gene signal-level regulatory cascade？**

不允许用更多探索性图表替代这个问题。

## 2. 两条预注册Track

### Track A — IRF4

- disease locus: female-specific rs12203592
- primary question: SSc disease signal是否与IRF4 eQTL共享signal？
- key diagnostic contrast: TenK10K B_naive强fine-map vs FinnGen B_naive弱exact pair
- primary cell hypothesis: B lineage，优先B_naive；其他细胞只能作为secondary context

### Track B — chr22

- disease locus: female-specific rs66578187
- primary target competition: SYNGR1 vs RPL3 vs PDGFB及区域内其他credible genes
- primary molecular observation: exact lead同时显示强SYNGR1 eQTL和强caQTL
- cell contexts: 全33细胞无偏扫描；NK/CD8/PBMC仅作为预先记录的“高分子可追踪性背景”，不能事后据最漂亮coloc选择性报告

## 3. 数据输入硬门

### GWAS

必须获得female SSc区域级完整summary statistics，至少包含：

- chr / pos / rsID或可规范化variant ID
- REF / ALT
- effect allele / other allele
- beta或log(OR)
- SE
- p
- EAF/MAF（若源提供）
- sample size / case-control counts或有效N
- genome build

lead table、Manhattan图、论文Table 1不能用于coloc。

### molQTL

优先使用FinnGen官方public release的summary statistics / fine-mapping / peak-gene/CASCADE文件，而非仅browser筛选响应。TenK10K用于独立eQTL fine-map replication。

## 4. Harmonization冻结规则

1. 全部统一到明确的GRCh38坐标；
2. indel进行left-normalization和parsimonious representation；
3. 优先按`chr:pos:REF:ALT`匹配，不仅靠rsID；
4. effect方向仅在effect allele明确对应后使用；
5. palindromic SNP在MAF不足时不进行方向性判断；
6. strand/build不明确的变异进入`UNRESOLVED`而不是强制匹配；
7. 每个locus输出variant-overlap、MAF差异、allele flips、drop reasons。

## 5. 区域定义

禁止统一使用±500 kb作为唯一规则。

优先顺序：

1. disease GWAS credible set / independent signal boundary；
2. LD-based locus boundary；
3. 若前两者不可得，用±1 Mb作为技术fallback并做±500 kb/±2 Mb敏感性；
4. BCL11A未来恢复时必须覆盖到BCL11A基因及其候选远端regulatory region。

## 6. C1 regulatory cascade硬门

一个candidate只有同时满足以下条件才能标记`C1`：

### Gate A — Disease ↔ eQTL shared signal

- 优先SuSiE-aware colocalization；
- primary：PP.H4 ≥ 0.80；
- 同时报告PP.H3、PP.H4/(PP.H3+PP.H4)及prior sensitivity；
- 多信号locus不能只用single-causal coloc.abf当最终证据。

### Gate B — Disease ↔ caQTL shared signal

同上；并要求caQTL来自同一细胞或预先定义的兼容lineage。

### Gate C — eQTL ↔ caQTL signal coherence

必须有shared-signal或三性状joint evidence；不能因为同一个lead SNP的两个p值都小就推断“chromatin mediates expression”。

### Gate D — Peak → gene link

必须来自FinnGen source-defined peak–gene link/CASCADE，或使用paired multiome以预冻结方法独立重建；物理距离、peak落在gene body内部均只能作annotation。

### Gate E — Technical validity

- build/allele verified
- region coverage adequate
- LD reference ancestry compatible
- credible sets不因缺失关键variant而明显截断
- 不把PIP、marginal p或单一lead overlap当coloc

只有A–E全通过，才能写“cell-specific regulatory cascade supported by genetic colocalization”。

## 7. 证据分级

- **C1**：完整disease↔eQTL/caQTL shared-signal + peak→gene + technical gates
- **C2**：有可靠disease↔eQTL或caQTL shared-signal，但链不完整
- **C3**：lead-level marginal / fine-map tractability / tissue association
- **C4**：仅位置或文献生物学候选
- **UNTESTABLE**：数据缺失，不得当作negative

## 8. R4A3终点

### PASS

至少一个Track获得≥1个C1，且从raw source到final table完全可复现。

### PARTIAL

有C2但没有C1：允许扩展到其余5个female-specific loci，但不进入疾病组织大规模验证。

### FAIL_WITH_ADEQUATE_COVERAGE

IRF4和chr22均在充分覆盖、正确harmonization、可用LD下明确不共定位：进入**bounded rescue**，一次性测试全部8个sex-specific loci；不能用无边界分析救故事。

### ACCESS_HOLD

GWAS或官方molQTL输入仍无法取得：继续HOLD，不把browser descriptive screen包装成论文结果。

## 9. 疾病组织分析的启动条件

只有出现C1后，才解锁GSE312129/GSE249279等SSc tissue validation。组织层只验证**genetically prioritized target/cell state**，不重新从全转录组筛hub genes。
