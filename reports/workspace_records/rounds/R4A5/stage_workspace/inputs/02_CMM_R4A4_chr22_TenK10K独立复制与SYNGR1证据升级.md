# R4A4 chr22：TenK10K 独立复制与 SYNGR1 证据升级

日期：2026-09-09

## 1. 问题

R4A3已经证明 rs66578187 在FinnGen公共接口中对SYNGR1存在强边际eQTL，并且目标ATAC peak存在source-defined peak→SYNGR1 link；但SYNGR1区域CS在该接口中缺失，因此当时不能判断分子 fine-mapping 是否跨资源复现。

本轮使用YR1(1)内已经归档的TenK10K正式下载文件，独立检查SYNGR1/RPL3/PDGFB。

## 2. TenK10K gene-level结果

| cell | SYNGR1 | RPL3 | PDGFB |
|---|---:|---:|---:|
| NK | ACAT 5.20994979502215e-230 | 0.000344332542672188 | NOT_LISTED |
| NK_CD56bright | 2.36201342725275e-97 | 0.0616047204365868 | NOT_LISTED |
| B_naive | 2.53577051352952e-39 | 0.0139373046972839 | NOT_LISTED |
| CD8_TEM | NOT_LISTED | 0.000198783550843906 | 6.23003426625246e-10 |

这说明候选基因之间不是简单“一个有信号、另两个完全没有”，而是存在不同细胞、不同局部调控模块。真正关键的是fine-mapped signal是否与FinnGen target peak对齐。

## 3. 最关键的新结果：NK同一credible-set变异完全重叠

TenK10K NK / SYNGR1 CS4：

| variant | TenK10K PIP |
|---|---:|
| 22:39351666:T:A | 0.5000 |
| 22:39351775:G:A | 0.5000 |

FinnGen l2.NK / `chr22-39351520-39352777` caQTL CS1包含：

| shared variant | FinnGen source probability |
|---|---:|
| 22:39351666:T:A | 0.2006173 |
| 22:39351775:G:A | 0.0522868 |

所以 **TenK10K eQTL CS4 的两个成员均精确出现在 FinnGen l2.NK caQTL CS1**。这不是仅仅“两个top SNP距离很近”，而是 coordinate+REF+ALT 完全一致的credible-set交集。

此外，FinnGen peak页把 `chr22_39351775_G_A` 标为 top variant，source PIP≈0.998823，并列入18类cell的caQTL CS；TenK10K则把同一变异放入11类cell的SYNGR1 eQTL CS，包括NK、NK_CD56bright、CD8_Naive、CD8_TCM、MAIT、cDC1/cDC2等。

## 4. 这能证明什么

可以支持：

> 在NK细胞中，独立TenK10K eQTL fine-mapping与FinnGen chromatin caQTL fine-mapping收敛到同一局部变异集合；结合FinnGen source-defined peak→SYNGR1 link，SYNGR1成为chr22 locus非常有力的分子效应基因候选。

目前仍不能支持：

- rs66578187 与 39351666/39351775处于同一疾病因果信号；
- accessibility 改变“导致”SYNGR1表达改变；
- SYNGR1已经是SSc causal gene；
- female-specific SSc效应已经被证明由NK介导。

原因：female-SSc区域summary与匹配LD仍未取得，疾病层没有coloc。

## 5. RPL3与PDGFB的竞争地位

### RPL3

- gene-level在多类细胞可测试；
- 本轮SuSiE文件中未发现RPL3 credible-set成员；
- FinnGen同lead比较也显著弱于SYNGR1。

因此从“分子fine-map与target peak的一致性”角度降级，但继续作为有界竞争候选保留。

### PDGFB

- TenK10K CD8_TEM存在强gene-level eQTL与credible sets；
- 其fine-mapped区域主要约39.22–39.24 Mb，与SYNGR1/target-peak约39.35 Mb模块不同；
- FinnGen exact disease-lead/CD8_TEM PDGFB边际关联此前为弱/阴性。

因此PDGFB目前更像该广义区域内的另一独立调控模块，而不是现有证据下最自然的rs66578187效应基因。

## 6. chr22当前证据等级

建议拆成两个互不混淆的门：

**Molecular gate：PASS_STRONG**

- same-cell NK
- exact-variant CS overlap
- independent resource replication
- source peak→gene link

**Disease gate：PENDING / NOT_TESTED**

- female SSc summary missing
- LD missing
- disease↔eQTL/caQTL coloc not run

只有两门都过，才能升级为正式C1 cascade。
