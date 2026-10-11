# R4A4 正式数据接入清单与请求草稿

## 本轮可验证状态

GWAS Catalog v2 PMID41999721 查询 HTTP200、0条；GCST009131 正对照 HTTP200。保留两个原始响应。无法据此判断作者是否另有未索引下载。FinnGen 官方公开页可访问，仍要求登记获得下载说明。本轮没有取得 formal release，没有发送邮件或提交身份表单。

## 可直接交付数据方的请求内容

Subject: Regional/full summary statistics and signal-level metadata for SSc sex-stratified GWAS / FinnGen immune multiome

We are conducting a reproducible signal-level analysis of the 2026 systemic sclerosis sex-stratified GWAS (PMID 41999721). Could you provide the public accession or download instructions for female and male summary statistics, including chromosome, position, genome build, reference/alternate and effect allele, beta or log(OR), standard error, P value, allele frequency, per-variant sample size, imputation QC, and cohort overlap information? Female regional data around IRF4 and rs66578187 would permit an initial bounded analysis if the full release is not yet available.

For FinnGen multiome, we need the official release README, nominal cis-eQTL/caQTL, SuSiE credible sets and model outputs, LD reference or reconstruction specifications, and peak–gene links with per-cell definitions. In the public browser, SYNGR1 shows very strong marginal associations in NK/CD8 TEM but empty regional CS responses, while the requested 1 Mb caQTL window returns about 200 kb. Please clarify whether this reflects export filters, cis-window limits, fine-mapping QC or another release rule.

此为草稿，未发送；不要替用户编造姓名、单位、邮箱或研究声明。已有下载说明或本地正式数据可以直接接入，不需要重新申请。

## 接入后的顺序和验收

1. 保存不可变原始文件、release版本、README、URL、获取时间、字节数与官方/本地校验；不只记录“链接可打开”。
2. 提取两个疾病区域，核对女性病例/对照、祖源、效应尺度、build、重复和多等位变异；male 用于后续性别差异，不用单组显著另一组不显著推断交互。
3. 解释 SYNGR1 CS 缺失，核实 caQTL cis 窗口；确认请求集合、可测试集合、实际返回集合和共同 SNP 集合。先冻结覆盖判定规则再看 coloc 结果。
4. 获取匹配 LD 并核验 SNP 顺序、等位基因、矩阵对称和正定性；归档 indel normalization 和 palindromic 排除日志。
5. 再运行多信号 coloc，保留每个 signal pair 的完整结果和先验敏感性。LD 或 full stats 缺失不填入模拟疾病值，不以 exact-lead P 值替代。

R4A4 完成标准是数据可检验性 PASS 或清晰可复核的接入阻断；R4B 启动必须另过 C1 科学门槛。
