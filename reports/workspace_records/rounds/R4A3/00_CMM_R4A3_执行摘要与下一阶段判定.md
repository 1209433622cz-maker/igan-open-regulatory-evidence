# R4A3 执行摘要与下一阶段判定

日期：2026-09-09（Asia/Hong_Kong；原始访问日志使用 UTC，因此显示 09-08）。

本轮完成附件独立审计、chr22 同细胞候选基因比较、source peak–gene link 提取、区域覆盖与 CS 检查，以及公开数据入口复查。SSc 项目维持 **CONDITIONAL GO**；**R4B HOLD**；疾病共定位仍为 **NOT_TESTED，C1_count=null**。

## 本轮实质新增结果

1. rs66578187 对 SYNGR1 的强 eQTL 在非 top-feature 筛选的区域接口中复现：l2.NK p=9.9831e-110，beta=0.49487，SE=0.022123。相同细胞、相同变异对 RPL3 p=0.19127。CD8 TEM 中 SYNGR1 p=4.7553e-83、RPL3 p=0.03407、PDGFB p=0.84948。此比较支持优先测试 SYNGR1；不同基因测量精度不同，不能仅按 P 值直接判定效应基因。
2. peak chr22-39351520-39352777 不只是空间上落在 SYNGR1 内：官方 API 确实返回 fasthurdle peak–gene link，NK、CD8 T、l2.NK、CD8 TEM、PBMC 均有记录。l1.NK joint_p=1.28958e-252；l2.NK joint_p=8.31595e-235。这补上了“来源定义的 peak→gene 关联”证据，但不是因果方向或疾病共定位证明。
3. 目标 peak 共列出 19 个 linked genes，包含 RPL3，也包含远端基因；PDGFB 未列出。未列出不等于阴性。SYNGR1 是优先候选而非唯一候选。
4. SYNGR1 页面将该 peak 标为 is_cascade=false。区域 API 在本次三个细胞中返回强 SYNGR1 eQTL，却没有 SYNGR1 CS。不能据此宣布 fine-mapping 失败或共定位阴性；需要正式 release 解释数据导出与筛选规则。
5. 相同 ±500 kb 请求下，eQTL 每个已返回 pair 有 3113 个 nominal rows，caQTL 每细胞仅 669 个，实际跨度约 200 kb。pmax=1 只排除显著性阈值限制，不证明完整区域覆盖。

## IRF4 与第三位点

IRF4 沿用已归档独立重算：TenK10K B-naive 单成员 CS，PIP≈0.99931；FinnGen exact pair p=0.6728。此次没有重新下载相同 TenK10K 数据，也没有新增 IRF4 疾病信号。保持跨资源差异诊断任务。BCL11A 维持远端调控候选，固定 ±500 kb 不足以覆盖基因，不启动无边界扩展。

## 下一阶段：R4A4 — 正式 release 接入与可检验性验收

最高优先级是取得 2026 SSc female 区域/完整 summary statistics 和 FinnGen 正式 release（含 nominal、SuSiE、LD说明、peak–gene link 方法）。female 数据到位后可先运行 female 信号分析；male 缺失限制性别比较，不必阻止所有 female 探索。当前不能启动正式疾病 coloc，也不进入 all-8 rescue。

随后解决 SYNGR1 强边际关联与 CS 缺失的来源问题，统一 eQTL/caQTL 的实际覆盖、等位基因和 LD，再进行 signal-level QTL↔QTL 与疾病↔QTL 分析。不要为制造一个 PP4 在多信号背景下直接套单因果模型。

## 证据入口

- [FinnGen 官方访问说明](https://www.finngen.fi/en/access_results)：公开不等于本地已取得正式文件；下载说明通过登记后邮件提供。
- [SYNGR1 源 JSON](https://cascade.finngen.fi/api/cascade/gene/SYNGR1)
- [目标 peak 源 JSON](https://cascade.finngen.fi/api/cascade/peak/chr22-39351520-39352777)
- [GWAS Catalog 本轮查询](https://www.ebi.ac.uk/gwas/rest/api/v2/studies?pubmed_id=41999721)：HTTP 200、totalElements=0；只代表这个入口未发现，不能证明全球未发布。

完整原始字节、URL、时间和 SHA256 见 R4A3/evidence；明细表见 R4A3/results。
