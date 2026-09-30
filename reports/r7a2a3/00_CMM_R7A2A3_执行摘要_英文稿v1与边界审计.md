# CMM R7A2A3 执行摘要：英文稿 v1 与证据边界审计

**日期：2026-09-30**
**写作系统：QiTeng Academic Writing Skill v0.3.24.2**
**模式：QITENG_Q1_GUARDED + FULL_MANUSCRIPT**

## 本轮结论

R7A2A3 已把 R7A2A2 冻结证据重构为一篇完整英文 original-research manuscript v1。主论文的最强可辩护结论固定为：

> 采用疾病侧 study-derived LD、OneK1K 细胞/供者匹配 QTL LD、多信号分解及独立 TenK10K 单细胞 eQTL 复制后，两个既有 PBC 位点可被解析为 **IL12RB2–NK** 与 **FCRL3–B** 的重复 disease–eQTL signal-sharing axes。

证据等级最高为 **E2：重复或敏感性支持的关联**，没有升级为表达介导、直接机制、疾病特异表达或治疗靶点。

## 关键正文结果

- IL12RB2/NK：OneK1K 四配置最小默认 PP.H4=0.998027，最小低先验 H4/(H3+H4)=0.980618；TenK10K NK 396 个精确交集变异，默认 PP.H4=0.997544，低先验比值=0.975973。
- FCRL3：OneK1K 稳定支持 B_IN、B_MEM、CD4_NC、NK、NK_R；TenK10K B_intermediate 343 个精确交集变异，默认 PP.H4=0.991562，低先验比值=0.921714。
- FCRL3/CD8_ET：单信号 PP.H4=0.941339，但 source-LD 多信号最小 PP.H4=0.003636，H3 约0.992。该反转作为主方法学证伪结果保留。
- INAVA/CD4_NC：OneK QTL 较弱，默认 PP.H4=0.026243，保持 `UNINFORMATIVE`，不解释为排除 INAVA。
- HRA008003：两个 target–lineage pair 均在 5/5 PBC 与 5/5 对照中可检测。FCRL3–B 方向较低，IL12RB2–NK 方向较高；两者 BH q 均为0.111111，没有通过校正富集门。

## 新颖性定位

FCRL3、IL12RB2、PBC 分子 QTL 共定位以及 FCRL3 的 B 细胞定位均已有文献基础。本文不能宣称新基因或首次定位。可保留的新颖性为：

1. 疾病和细胞 QTL 两侧分别使用来源匹配 LD；
2. 使用多信号模型终裁，而不把单信号 smoke result 直接升级；
3. 要求第二个 population-scale 单细胞 eQTL 资源独立重复；
4. 把 CD8_ET 反转、INAVA 弱 QTL 和组织非显著结果保留在最终证据链中。

## 当前完成度

已完成：

- 完整英文稿 v1；
- Claim Ledger；
- Reference Ledger；
- Methods–Results mirror；
- Reviewer Risk Map；
- Figure Role Map；
- R7A2A4 敌意审稿协议；
- 数字、引用、边界词和必需章节自动 QA。

投稿前仍阻塞：作者/单位/通讯作者、CRediT、基金、利益冲突、目标期刊格式，以及 Figure 1 与 Figure 3 的视觉修复。

## 状态与下一阶段

```text
R7A2A3 = COMPLETE_MANUSCRIPT_DRAFT_V1
PBC_PRIMARY_PROJECT = GO
CENTRAL_EVIDENCE_TIER = E2_ROBUST_ASSOCIATION
NEW_GENE_DISCOVERY_CLAIM = PROHIBITED
TISSUE_ENRICHMENT = NOT_SUPPORTED
AUTHOR_METADATA = BLOCKER_FOR_SUBMISSION

NEXT = R7A2A4_HOSTILE_MANUSCRIPT_AUDIT
```

下一阶段不新增位点、基因或细胞；只做逐句证据审计、最新文献重查、两类敌意审稿模拟、数字/引用复核和 Figure 1/3 修复。
