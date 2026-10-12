# R4A4 详细行动记录与下一阶段目标

日期：2026-09-09

## 本轮实际完成

1. 解包并审计用户上传的R4A3正式release与YR1(1)。
2. 核对R4A3 ZIP SHA256与YR1内部release_validation声明，完全一致。
3. 确认YR1(1)没有新增2026 female/male SSc summary或LD文件。
4. 重新核验公开SSc论文、GWAS Catalog可见性与FinnGen official access页面。
5. 从YR1(1)已有TenK10K raw下载文件重新解析28类cell的gene-level结果与SuSiE credible sets。
6. 对SYNGR1/RPL3/PDGFB/IRF4进行全cell extraction，而非只读旧target screen。
7. 发现TenK10K NK/SYNGR1 CS4与FinnGen l2.NK target-peak caQTL CS1有两个 exact variant+allele重叠。
8. 确认FinnGen peak top variant `22:39351775:G:A`同时是TenK10K SYNGR1 eQTL credible-set member，并在11个TenK10K cell types出现。
9. 输出机器可读candidate CS、gene-level、peak-overlap和cross-resource表。
10. 更新统计协议为v6，明确Molecular Gate与Disease Gate不得混用。

## 本轮没有做

- 没有伪造/模拟female SSc summary；
- 没有计算疾病PP4；
- 没有用单lead p值冒充coloc；
- 没有发送邮件或代用户填写FinnGen表单；
- 没有启动all-8 rescue；
- 没有开始SSc组织表达验证，因为疾病锚定仍未完成。

## 当前状态

`PROJECT = CONDITIONAL_GO`

`chr22 molecular gate = PASS_STRONG`

`disease gate = NOT_TESTED`

`R4B = HOLD`

## 下一阶段：R4A5 — Disease-anchor gate

### 首选路径 A

取得2026 female-SSc summary statistics后，立即仅跑：

1. chr22/SYNGR1；
2. IRF4；
3. 必要的RPL3/PDGFB bounded candidate competition。

先判定是否出现至少一个C1，再决定是否扩全8 sex-specific loci。

### 备选路径 B

若sex-specific summary继续不可得：

使用GCST009131做一个严格标注为 `PIPELINE_VALIDATION_ONLY` 的overall SSc测试，完成真实文件下载、harmonization、LD和multi-signal coloc工程验证。该结果不能改写为sex-specific发现。

### R4A5验收标准

**GO_R4B_FULL**：至少1个sex-specific locus形成完整C1，并通过technical QC。

**HOLD_EXTERNAL_ACCESS**：分子门已过，但female/male GWAS仍不可获取。

**PIVOT_OVERALL_METHODS_ONLY**：只能得到overall SSc，适合技术验证但不足以维持sex-specific主标题。

**NO_GO_SSC**：sex-specific数据最终取得、覆盖充分，双位点+有界all-8仍无可信C1，且组织验证无法形成新的正交证据链。
