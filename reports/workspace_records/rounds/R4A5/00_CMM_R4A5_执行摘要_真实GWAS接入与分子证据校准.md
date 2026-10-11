# R4A5 执行摘要：真实 GWAS 接入与分子证据校准

日期：2026-09-09，Asia/Hong_Kong。UTC 原始日志显示前一天属于时区差异。

## 判定

SSc 项目维持 CONDITIONAL GO；R4B HOLD；2026 female/male disease gate NOT_TESTED；C1_count=null。本轮完成了 R4A4 独立审计和 overall SSc 实际数据接入，尚未完成端到端 LD / multi-signal coloc。

## 新增的真实进展

1. 从原始 TenK10K SuSiE ZIP 重算 736 条四候选基因 CS 成员，与附件逐项匹配（基因、细胞、变异、CS编号、PIP，计入重复次数）。NK/SYNGR1 CS4 两个成员各 PIP=0.5；39351775:G>A 出现在11种细胞，结论得到验证。
2. 补全 FinnGen NK CS 分母：l2.NK caQTL CS1 是 **3成员**，第三个 chr22:39343182 C>T 的源概率为 **0.7470959011**；另外两个与 TenK10K CS4 交集的概率合计仅 **0.2529040989**。原“两个成员全部重叠”是单向集合覆盖，不是双方 CS 相同。
3. peak 页 PIP≈0.998823 为跨细胞汇总字段，不能移植为 NK PIP。l2.CD8_TEM 对39351775的 CS1 概率确实高达0.988389，但 TenK10K SYNGR1 在 CD8_TEM gene-level 未列出，因此也不能据此拼成同细胞独立复制。
4. 已下载官方 GCST009131 overall SSc 完整文件：**472,336,600 字节**，官方 MD5 **bd1823dc8ff0564c362dc60765c58ba8** 匹配；扫描 **4,723,365 行**。正式疾病数据接入从“有链接”推进到“有真实校验字节”。这是2019 overall数据，不能替代2026女性GWAS，也不证明独立于2026队列。
5. 接入验收发现 A2 未知 **4,723,365 行**，无直接 SE / EAF / 每变异样本人数列。当前文件不能无条件送入此前计划的严格 harmonization 与 LD 分析。

## 对下一阶段的影响

下一阶段定义为 **R4A6 — 可用 summary 字段恢复与 disease-anchor readiness**。优先获得2026 female数据；同时对已下载overall文件核实参考版本和等位基因、取得原始SE或设计并验证近似SE方案、准备匹配LD。只有这些输入过关才运行真实coloc。无需再次下载相同450MiB文件，也不必重复归档已有分子结果。

SYNGR1仍是优先候选，但将“PASS_STRONG”改为更可核验的状态：**exact-CS overlap confirmed，signal colocalization untested**。这是校准证据强度，不是否定该候选。

详见01分子审计、02接入验收与99行动记录；所有机器可读结果位于R4A5/results。
