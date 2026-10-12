# CMM R4A12FG3：LD、coloc、SMR与SuSiE-RSS可行性矩阵

日期：2026-09-13。基于用户提供的 R4A12FG2 真实区域结果，并结合本轮公开数据源复核。外部信息均与附件证据分层记录。

## 1. 关键方法边界

完整TenK10K eQTL summary公开后，`beta/SE/alleles/AF`问题可解决；但IL12RB2存在多个source SuSiE credible sets，说明单因果模型不是自然的唯一主模型。

| 方法 | QTL字节到位后 | LD要求 | 本项目定位 |
|---|---|---|---|
| classic coloc.abf | 可运行 | 无 | **敏感性分析**；必须明确单因果假设 |
| coloc.susie | 仍需LD | 两数据集signed LD | **优先multi-signal方法，但当前HOLD** |
| SuSiE-RSS | 仍需LD | signed LD | **HOLD**，先过z–LD/PSD/order/AF门 |
| SMR/HEIDI | 条件可运行 | HEIDI需要LD | **supporting evidence**，不可单独证明因果 |
| CS/exact-key overlap | 已可做 | 无 | 仅描述输入重叠，绝非coloc |

## 2. TenK10K source-matched LD

TenK10K方法明确：SuSiE-RSS使用SAIGE-QTL Z、effective N以及“为每个gene全部cis variants计算的correlation matrices”。但Zenodo公开文件列表未单独发布这些矩阵。

TenK10K 1,925人WGS genotype数据位于EGA `EGAS50000001654`，GRCh38，属于受控访问。故source-matched LD状态：

`CONTROLLED_ACCESS_NOT_LOCAL`

## 3. FinnGen LD

FinnGen公开SISu v4.2 LD：3,775个样本、1.5 Mb window、BCOR、相关阈值0.05。官方文档明确提示：**不优先用于fine-mapping，因为SuSiE等方法需要in-sample LD才能取得良好结果。**

因此本项目只允许：

- SISu LD作为FinnGen disease侧的工程诊断/敏感性；
- 1000G EUR或其他外部LD同样仅在严格AF、allele、z–LD诊断PASS后使用；
- 不因external LD能跑完软件就称“fine-mapping PASS”。

## 4. 允许的分析顺序

**Stage A — summary-only readiness**

TenK10K full 100kb → NK IL12RB2提取 → schema/normalization → FinnGen exact overlap → coverage/CS mass。

**Stage B — bounded sensitivity**

当A通过时，允许对R13/R12 × NK运行classic coloc.abf，明确标签 `SINGLE_CAUSAL_SENSITIVITY_ONLY`。结果不能单独升级C1。

**Stage C — LD-aware primary signal test**

只有source-matched或严格验证的LD通过后，运行multi-signal coloc / SuSiE-aware comparison / SMR-HEIDI。

## 5. Chromatin layer的触发条件

TenK10K multiome caQTL资源公开覆盖922 donors、28免疫细胞，并提供fine-mapping/coloc；但其2026-06-27更新日志明确提示旧版caQTL↔eQTL coloc曾存在allele flipping问题，必须使用修正版。

IL12RB2 chromatin层暂不先行扩张。只有disease↔IL12RB2 eQTL至少达到预注册“值得继续”的signal-level证据后，才进入caQTL/peak→gene层，避免因为eQTL结果不理想而用ATAC数据救故事。
