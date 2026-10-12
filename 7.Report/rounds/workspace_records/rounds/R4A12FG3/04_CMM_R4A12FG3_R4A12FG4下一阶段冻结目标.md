# CMM R4A12FG3：R4A12FG4 下一阶段冻结目标

日期：2026-09-13。基于用户提供的 R4A12FG2 真实区域结果，并结合本轮公开数据源复核。外部信息均与附件证据分层记录。

## 阶段名称

> **R4A12FG4 — Targeted TenK10K 100-kb Intake + NK-first Signal Gate**

## 目标

把当前`PUBLIC_NOT_LOCAL`的完整variant-level eQTL变成可审计本地输入，并在不改变primary cell和cis窗口的前提下，判断FinnGen all-sex SSc ↔ IL12RB2是否值得进入LD-aware多信号分析。

## 必做顺序

1. 下载 `common_all_cis_pvalues_100kb.zip`（16.6 GB），MD5必须为 `dd54714b2effb91160ac171ccb941534`；记录SHA-256。
2. **只先流式提取NK** `NK_common_all_cis_raw_pvalues.tsv` 中 IL12RB2/ENSG00000081985，不整包解压。
3. 验收真实header：effect allele、other allele、AF、BETA、SE、P及variant key；不以文档推测覆盖真实schema。
4. GRCh38 normalization；与R13/R12 disease summary在IL12RB2 ±100kb窗精确harmonize。
5. 报告common variant count、span、AF偏差、source CS PIP mass、disease lead/rs6662198/QTL anchors保留情况。
6. 若coverage PASS，运行 `coloc.abf` 作为**单因果敏感性**；不据此升级C1。
7. 再提取其他10个预注册CS-positive secondary cells；primary仍为NK。
8. 并行解决LD：优先EGA/source-matched TenK10K genotype；无法取得时，外部LD必须通过严格诊断并标记为secondary。
9. 只有LD gate通过后运行multi-signal coloc / SuSiE-RSS / SMR-HEIDI。
10. disease↔eQTL信号值得继续时，再进入TenK10K multiome caQTL层，并使用2026-06-27之后修正版数据。

## GO / HOLD / STOP

**GO_LD_AWARE**：variant-level QTL、normalization、coverage均PASS且可用LD通过诊断。

**SUMMARY_ONLY**：QTL/coverage PASS但LD仍不足；可保留coloc.abf敏感性，不做multi-signal强结论。

**UNTESTABLE**：真实QTL字节中IL12RB2字段/coverage不足；不得写成生物学阴性。

**STOP_IL12RB2_BRANCH**：只有在输入充分、LD/model通过且多种合理方法稳定支持distinct signal时，才讨论停止这一all-sex分支。主2026 female/male chr22/SYNGR1路线始终独立。
