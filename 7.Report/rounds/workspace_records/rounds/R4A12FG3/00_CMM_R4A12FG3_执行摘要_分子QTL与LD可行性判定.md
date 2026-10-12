# CMM R4A12FG3 执行摘要：Molecular QTL + LD Feasibility Gate

日期：2026-09-13。基于用户提供的 R4A12FG2 真实区域结果，并结合本轮公开数据源复核。外部信息均与附件证据分层记录。

## 最终判定

本轮将 FG2 的“缺少完整 variant-level molecular QTL”进一步拆解。结论是：**完整 TenK10K common sc-eQTL summary 已公开，QTL 可获取性门通过；paper-grade multi-signal 分析的主要瓶颈转为 LD。**

当前状态：

- `PROJECT = CONDITIONAL_GO`
- `R4B = HOLD`
- `C1_count = null`
- `R4A12FG3 = CONDITIONAL_PASS_MOLECULAR_QTL_PUBLIC_LD_PENDING`
- `TENK10K_FULL_VARIANT_EQTL_PUBLIC = PASS`
- `TENK10K_FULL_VARIANT_EQTL_LOCAL_BYTES = NOT_OBTAINED`
- `TENK10K_100KB_WINDOW_SUFFICIENT = PASS`
- `PRIMARY_MOLECULAR_CELL = NK`
- `FORMAL_MULTI_SIGNAL_COLOC = HOLD_LD_AND_QTL_BYTES`

## 决定性新证据

TenK10K v2 Zenodo（DOI `10.5281/zenodo.18221260`）公开：

- `common_all_cis_pvalues_100kb.zip`：16.6 GB，MD5 `dd54714b2effb91160ac171ccb941534`；28个细胞类型的完整 common cis-eQTL summary；
- `susie_summary.zip`：59.7 MB；
- ±1 Mb 七个分包合计约129.8 GB。

TenK10K主分析本身使用基因体±100 kb；±1 Mb结果在主论文中不作为主要分析。IL12RB2 GRCh38基因范围为 `67,307,364-67,398,724`，因此100-kb cis窗为 `67,207,364-67,498,724`。FG2中的FinnGen disease lead `rs1954118` 位于67,448,804，仅距基因末端50,080 bp；`rs6662198` 67,340,524位于基因体内。故当前 bounded IL12RB2 分析无需下载约130 GB的1-Mb资源。

在R12/R13 disease区域中，该100-kb基因窗各包含 **1,918行 / 1,872个唯一位置**，且region内最强疾病信号仍是 `rs1954118`。

## LD结论

TenK10K论文的SuSiE fine-mapping使用每个基因所有cis variants的样本相关矩阵（source-matched LD/correlation）。这些矩阵未在Zenodo公开文件列表中单独发布；1,925人的WGS基因型由EGA `EGAS50000001654` 管理访问。因此：

- classic `coloc.abf`：完整QTL字节到位后可做**单因果假设敏感性分析**；
- SMR/HEIDI：QTL字节到位后仍需验证LD；
- `coloc.susie` / SuSiE-RSS：paper-grade主判定继续 HOLD，优先 source-matched LD；
- FinnGen SISu v4.2（3,775人）可做外部LD诊断/敏感性，但FinnGen官方明确不推荐它替代in-sample LD做SuSiE。

## 细胞冻结

FG2源数据中，IL12RB2在NK细胞的gene-level ACAT最强（`3.42337e-118`），top marker `1:67324915:T:C`、P=`6.80524e-121`，并有2个source SuSiE CS。因此NK冻结为**primary molecular cell**。其余10个CS-positive细胞作为预注册secondary cells，不在看到coloc结果后更换primary cell。

2026 SSc sex-specific论文同时把rs6662198/IL12RB2定为female-specific风险位点，并报告IL12RB2在whole blood和monocytes有显著sex-dependent表达、NK为nominal signal，这为NK优先级提供疾病生物学支持；但它不能替代正式的cell-specific disease↔eQTL signal test。

## 下一阶段

> **R4A12FG4 — Targeted TenK10K 100-kb Intake + NK-first Signal Gate**

先下载并校验16.6 GB 100-kb完整eQTL包，流式只提取IL12RB2（先NK，再预注册10个secondary CS-positive cell types），完成schema、beta/SE/allele/AF、variant normalization、FinnGen R12/R13覆盖和单因果敏感性分析。multi-signal主结论继续等待source-matched或通过严格诊断的LD。
