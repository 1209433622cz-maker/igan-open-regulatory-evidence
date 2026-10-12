# R4A4 统计协议 v6：分子门与疾病门分离

日期：2026-09-09

## 目的

R4A3 v5已经要求疾病证据与分子证据分列。本轮新增TenK10K chr22 fine-mapping后，正式把流程冻结成双门控，避免在缺少疾病summary时因为分子证据漂亮而提前宣布C1。

## Gate M：Molecular regulatory convergence

### M-PASS_STRONG（chr22/SYNGR1目前满足）

至少满足：

1. independent resource A：caQTL fine-mapped CS；
2. independent resource B：eQTL fine-mapped CS；
3. 相同/可严格映射cell type；
4. exact coordinate+allele credible-set intersection，或在有可靠LD条件下signal overlap；
5. source-defined peak→gene link；
6. build与allele语义无冲突。

M-PASS只说明“分子调控机制具有强候选性”，不说明疾病因果。

## Gate D：Disease anchoring

必须取得真实疾病区域/full summary，完成：

1. build确认；
2. effect/reference/alternate allele harmonization；
3. indel normalization；
4. ancestry-matched LD；
5. region completeness；
6. multi-signal disease fine-mapping或条件化；
7. Disease↔eQTL与Disease↔caQTL signal-level analysis；
8. H3/H4、H4/(H3+H4)、prior sensitivity等完整报告。

只有D-PASS才能进入C1判定。

## C1冻结定义

C1需要同时：

- Gate M PASS；
- Gate D PASS；
- disease↔eQTL shared signal；
- disease↔caQTL shared signal；
- eQTL↔caQTL coherence；
- peak→gene evidence；
- cell identity一致；
- 技术QC PASS。

## chr22优先顺序

1. female SSc chr22区域summary；
2. rs66578187 indel规范化；
3. disease lead附近±1 Mb完整SNP集合；
4. 与FinnGen caQTL、TenK10K SYNGR1 eQTL共同SNP集合；
5. ancestry-matched LD；
6. multi-signal coloc/fine-map；
7. candidate competition：SYNGR1 / RPL3 / PDGFB及source-linked bounded gene set。

## IRF4

保留第二链。TenK10K B_naive对rs12203592具有近单一高PIP CS，而FinnGen exact-pair边际结果不支持同样强度。因此IRF4用于测试“不同QTL资源中的信号差异是否由疾病shared signal解决”，不能预先作为阳性对照。

## overall SSc fallback

GCST009131只能用于：

- harmonization smoke test；
- LD/coloc pipeline validation；
- 非性别背景参考。

不能用于替代female/male证据或支持“female-specific mechanism”。
