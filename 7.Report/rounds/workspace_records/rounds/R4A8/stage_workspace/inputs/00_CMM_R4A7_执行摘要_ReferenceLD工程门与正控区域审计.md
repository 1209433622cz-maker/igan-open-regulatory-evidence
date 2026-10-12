# R4A7 执行摘要：Reference/LD 工程门与正控区域审计

日期：2026-09-09。

## 最终判定

项目继续 **CONDITIONAL GO**，**R4B HOLD**。本轮没有运行 SuSiE-RSS 或疾病共定位，因为 EUR LD 二进制参考仍未在当前运行环境中实际落地；但工程前置条件已进一步收敛，且正控位点职责已重新排序。

## 输入核验

用户本轮再次上传的 R4A5 四份 Markdown 与增量 ZIP，经 SHA256 与此前归档逐一比较，**5/5 完全相同**。因此它们不是新增科学版本，不重复计算R4A5；本轮直接沿用已经完成的R4A6 build/signed-Z结论进入R4A7。

## 新增真实结果

1. **IL12RB2/rs6662198 被正式确定为首个工程正控。** GCST009131 GRCh37 中，以 rs6662198=67806207 为中心 ±500 kb 共 1842 条记录，其中 9 条 P<5e-8、16 条 P<1e-5。区域最强为 rs3790566，P=3.84e-10。GWAS显著变异仅跨约20.9 kb，结构相对集中。
2. **ULK3/rs2290572 更适合作为复杂区域压力测试而非第一正控。** ±500 kb 共 1121 条，52 条 P<5e-8、118 条 P<1e-5，最强 rs1378942 P=1.84e-14。GWAS显著变异跨约358 kb，提示明显更复杂的多信号/长LD结构。
3. historical IL12RB2 SSc follow-up 提供了可用的 allele/LD sanity control：rs3790566 T/C、rs3790567 A/G，并报告 rs3790566 为 rs3790567 的 tag-SNP。当前GCST009131中相应A1分别为T与A，方向编码与历史文献兼容。此证据用于验证harmonization逻辑，**不替代完整1000G A2恢复**。
4. 已核验可用的 GRCh37 EUR LD 参考来源：1000 Genomes Phase 3 EUR PLINK mirror 提供 bed/bim/fam 与MD5，fam公开内容为503个个体。当前运行时未能实际materialize bed/bim，因此LD矩阵仍为 **NOT_RUN**。
5. 2026 female SSc summary statistics 本轮公开检索仍未取得可归档的 accession/full file；论文及摘要可确认female分析存在约9.60M variants，但这不等同于summary字节已经接入。

## 状态冻结

- GCST009131 build: **GRCh37 PASS**
- signed-Z: **ENGINEERING READY**
- IL12RB2 positive-control window: **READY**
- ULK3 stress-test window: **READY**
- A2 production recovery: **PARTIAL / NOT COMPLETED**
- EUR LD bytes: **SOURCE VERIFIED / LOCAL BYTES NOT MATERIALIZED**
- SuSiE-RSS: **NOT_RUN**
- overall coloc: **NOT_RUN**
- female disease anchor: **NOT_OBTAINED / NOT_TESTED**
- C1_count: **null**

## 下一阶段

进入 **R4A8 — Local Reference Materialization + IL12RB2 LD Smoke Gate**。只要EUR panel实际落地，第一任务是用IL12RB2完成A2恢复、common-SNP intersection、LD矩阵QC、z-LD一致性和SuSiE-RSS；ULK3随后用于复杂区域压力测试。female summary一旦接入，再将已验证管线直接迁移到chr22/SYNGR1。
