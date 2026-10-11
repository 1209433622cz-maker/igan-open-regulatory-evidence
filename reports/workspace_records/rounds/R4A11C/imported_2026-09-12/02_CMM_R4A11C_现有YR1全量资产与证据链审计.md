# CMM R4A11C — YR1 全量资产与证据链审计

## 1. 审计输入

本轮逐成员检查：

- `/mnt/data/YR1.zip`
- `/mnt/data/YR1 (2).zip`

两包均通过ZIP CRC检查。分析不把历史报告中的自述自动当作真值；当前状态以 `0_admin/protocol/current/analysis_manifest_v11.*`、`R4A11_state.json`、当前catalog及可复核结果为主，历史R2–R4A10仅用于追溯。

## 2. 两个归档的职责划分

### YR1.zip：执行与审计工作区

包含：

- `0_admin`：current protocol、candidate registry、validation、workspace mapping；
- `2_code`：81项catalog条目，当前H6 v2.1与历史代码snapshot；
- `3_results`：129项catalog条目，包括分子证据、LD/RSS工程结果和访问审计；
- `6_release`：14项release catalog；
- `7.Report`：114项报告catalog；
- `9.Version`：冻结阶段工作区和旧布局追踪。

当前最重要协议：`analysis_manifest_v11`。当前科学状态明确冻结为：

```text
PROJECT = CONDITIONAL_GO
R4B = HOLD
2026 female/male disease bytes = NOT_OBTAINED
disease-level analysis = NOT_TESTED
molecular exact-CS overlap = CONFIRMED_DESCRIPTIVE_ONLY
molecular signal-level coloc = NOT_TESTED
C1_count = null
```

### YR1 (2).zip：知识库与写作骨架

包含：

- 54篇论文PDF文献库；
- target 2026 SSc论文、supplement和web snapshots；
- `5_manuscript`：54篇论文写作母版 + frozen statistical methods；
- `4_figures`：Fig1–Fig8/Supplementary模板目录；
- 目前没有经过疾病层gate的正式Results正文或正式主图。

## 3. 原始数据归档缺口

一个非常重要的可复现性问题：上传的规范化 `YR1.zip` 中 `1_data` 没有实际文件成员。

这并不等于分析结果不可信，因为`3_results`保存了大量派生数据和矩阵，例如：

- TenK10K candidate CS；
- FinnGen exact lead / gene-region snapshots；
- IL12RB2 harmonization表；
- 1555×1555 signed LD矩阵；
- z向量、kriging、RSS gate；
- GWAS Catalog访问快照；
- candidate registry等。

但它意味着：

> **现在这两个上传包不是从原始GWAS/QTL/reference到最终结果的自包含复现包。**

投稿前需要建立一个`RAW_INPUT_PROVENANCE`层，至少记录：

- source URL / accession / bucket object；
- release/version；
- download timestamp；
- bytes；
- SHA256/MD5；
- genome build；
- schema/version；
- access/license；
- 如不能合法重分发，提供获取脚本与校验值。

## 4. 当前科学证据链：已经完成什么

### 4.1 Disease discovery背景：已发表，但本项目尚无summary bytes

2026 sex-specific SSc论文已经确立：

- BCL11A male-associated；
- IRF4 female-associated；
- RPL3–PDGFB chr22区域 female-associated；
- total 10,653 cases / 18,043 controls；
- female 9,097 cases；male 1,556 cases。

本地有论文全文和supplement，但没有female/male full summary bytes，因此本项目的疾病层仍是`NOT_TESTED`。

### 4.2 SYNGR1新颖性边界：已被原论文占据一部分

Supplementary Table 2明确报告：

- SYNGR1 / whole blood：female coloc posterior 0.977；
- SYNGR1 / lymphocytes：female coloc posterior 0.980；
- male对应后验很低。

因此不能再写：

- “首次发现SYNGR1”；
- “首次把RPL3–PDGFB重分配给SYNGR1”。

可写的新问题只能是：

> 对已发表的broad-tissue eQTL共定位进行**cell-resolved chromatin-to-expression signal refinement**。

### 4.3 molecular exact-CS overlap：真实且可复核

冻结分子结果显示：

- TenK10K NK / SYNGR1 eQTL CS4；
- FinnGen l2.NK / peak `chr22-39351520-39352777` caQTL CS1；

共同包含：

- `22:39351666:T:A`
- `22:39351775:G:A`

TenK10K PIP各0.5；FinnGen l2.NK CS概率分别约0.2006、0.0523。FinnGen NK CS还有第三成员占约0.7471，因此不能称“两个CS相同”或“强共定位”。

正确状态：

> `EXACT_CS_OVERLAP_CONFIRMED / SIGNAL_COLOCALIZATION_NOT_TESTED`

### 4.4 candidate competition：已冻结，避免结果后挑基因

当前candidate registry固定20基因：SYNGR1 primary；RPL3、PDGFB强制保留；其余17个来自冻结peak-link snapshot。所有候选必须使用相同window、coverage、LD、fine-map、prior和edge classifier。

这是项目非常好的设计资产，应保留。

## 5. 工程证据链：已经解决什么

### 5.1 H6 v2.1

YR1中当前生产脚本已冻结，并通过大量回归/hostile tests；本对话随后R4A11B又发现并修复一个identity binding边界：PMID/DOI不能使用“任一匹配”逻辑，provider文件必须与目标study/stratum绑定。

建议正式主协议在下一版整合：

> **P0 Provider Identity Binding → H6 v2.1 → normalization**

而不是只运行H6。

### 5.2 2019 overall engineering branch

R4A5–R4A9完成了非常有价值的“失败也可解释”工程审计：

- GCST009131真实文件曾完整下载并MD5匹配；
- 原始文件A2缺失、无SE；
- signed-Z可工程恢复；
- GRCh37已判定；
- 1000G EUR503 IL12RB2区域参考构建成功；
- 1555个共同变异LD矩阵数值QC通过；
- 外部LD下RSS gate失败：estimate_s约0.1918，最大标准化kriging residual约5.3614；
- 主要原因更符合meta-analysis中variant-dependent cohort composition mismatch，而不是简单allele flip。

因此没有强行SuSiE，是正确的。

### 5.3 为什么FinnGen R12现在尤其重要

R12单cohort REGENIE的直接beta/se/alleles/GRCh38，可以绕开2019 meta文件的大多数历史格式和meta-covariance障碍。它是目前最自然的下一步工程与科学数据源。

## 6. disease tissue层：设计正确，但尚未触发

冻结角色：

- **GSE312129**：primary disease-tissue multiome，10 untreated dcSSc + 4 HC，snRNA+snATAC+Visium；
- **GSE249279**：独立skin scRNA/spatial replication；
- **GSE236111**：IFN/endothelial条件性验证；
- **GSE312932**：Xenium空间定位；
- **GSE312591**：RUNX1条件性perturbation，不是主atlas。

当前不应下载/重跑这些大数据，因为遗传C1尚未形成。这个停止规则应继续保留。

## 7. 写作与Figure状态

### 优点

- 54篇论文母版分析很完整；
- Introduction/Methods/Results/Discussion逻辑已提前设计；
- Nature-style Figure结构已设计；
- 关键negative-state语义（NOT_TESTED / UNTESTABLE / FALSIFIED）处理成熟。

### 尚缺

- 正式Results数据；
- disease-gate-approved主图；
- final figure source data；
- raw-input provenance release；
- 可直接投稿的Methods/Results prose；
- R12 branch尚未纳入master protocol。

## 8. 竞争环境对新颖性的影响

2026年已经出现：

1. 原sex-specific SSc GWAS本身已经做GTEx eQTL/sQTL/pQTL/chromatin/V2G/drug层；
2. JCI Insight发表early untreated SSc skin snRNA+snATAC+spatial研究；
3. Nature Immunology发表lung tissue-resident immune-cell eQTL与SSc等自身免疫病GWAS共定位；
4. Mediators of Inflammation发表SSc single-cell + MR（RAC1/pericyte）研究。

因此以下卖点已不够新：

- “SSc + single-cell”；
- “SSc + MR”；
- “SSc + eQTL coloc”；
- “SSc + skin multiome”；
- “发现SYNGR1”。

真正还能形成高价值新贡献的是：

> **published sex-associated disease locus + same-signal disease/caQTL/eQTL triangle + cell-resolved peak→gene + independent sex-stratified disease replication + disease-tissue concordance。**

## 9. 项目成熟度评分

|维度|当前评分|说明|
|---|---:|---|
|问题定义|9/10|已经从宽泛SSc多组学收窄到明确可证伪机制|
|新颖性边界|9/10|已纠正SYNGR1“首次发现”风险|
|分子前置证据|8/10|exact CS overlap + peak link很有价值，但signal coloc未做|
|疾病层证据|3/10|2026原文存在，但本项目summary bytes未取得|
|独立疾病复制|4→8/10潜力|FinnGen R12新增可执行方向|
|工程可复现性|8/10|H6/LD/RSS审计成熟；raw-input归档仍需补|
|疾病组织验证|2/10|设计好，尚未触发|
|手稿/图件|3/10|骨架完整但无正式结果|
|总体|**CONDITIONAL GO**|R12使项目从等待型转成可执行型|
