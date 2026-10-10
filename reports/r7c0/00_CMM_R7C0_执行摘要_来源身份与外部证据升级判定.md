# R7C0 执行摘要：来源身份与外部证据升级判定

日期：2026-10-11
阶段：`R7C0_SOURCE_IDENTITY_EXTERNAL_EVIDENCE_UPGRADE_PREFLIGHT`
依据：RP v4 双轨硬门
写作治理：QiTeng Academic Writing Skill v0.3.24.2

## 最终裁决

```text
PBC_PRIMARY_PROJECT = GO
R7C0 = COMPLETE
R7B4B2_Q2_BASELINE = FROZEN_SUBMISSION_READY_UNCHANGED
Q1_UPGRADE_TRACK = GO_BOUNDED_MANUSCRIPT_FORK
NEXT = R7C1_IL12RB2_EXTERNAL_VALIDATION_MODULE_AND_MANUSCRIPT_FORK
```

R7C0 找到了真实、可复核且具有论文增量的外部证据，因此允许建立独立的 SCI 一区升级稿分支；现有 R7B4B2 投稿候选稿和投稿包保持字节级冻结，继续承担可随时恢复的 SCI 二区基线。新证据集中于 IL12RB2–NK，不支持重开基因、细胞或位点筛选。

## 1. 统计模型来源门：通过

Gjoka/Cordell 原始方法明确使用 8,021 例病例、16,489 例对照，总样本量 24,510，并以同一欧洲样本的 logistic-regression summary statistics 与研究内相关矩阵运行 SuSiE-RSS。本项目疾病侧同样使用 GJOKA z 值、同一研究 LD 和 `n=24510`。

因此：

```text
GJOKA_N_24510 = PASS_SOURCE_MATCHED_N_TOTAL
N_EFF_REPLACEMENT = NOT_JUSTIFIED
FULL_642_RERUN = NO
```

`N_eff≈21,584` 是另一种病例对照标准化约定，不能在没有新的来源证据时反推原作者及本项目实现错误。

来源：[Gjoka/Cordell fine-mapping paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11656035/)，[official GJOKA data page](https://www.staff.ncl.ac.uk/heather.cordell/GjokaPaper.html)。

## 2. FinnGen R13 独立疾病信号与 OneK 分子信号：通过

FinnGen R13 `CHIRBIL_PRIM` 包含 795 例病例和 368,758 例对照。IL12RB2 区域 lead 为 `1:67336688:A:C / rs6659932`，`P=2.63×10^-9`。R13 的 17 个疾病可信集成员全部包含于 R12 的 19 变异可信集中：

```text
R12 CS size = 19
R13 CS size = 17
intersection = 17
Jaccard = 0.895
shared lead = YES
shared-variant beta direction concordance = 100%
```

进一步使用公开 R13 summary statistics 与冻结的 OneK NK/IL12RB2 PF10 输入进行 rsID 跨 build 对齐：

```text
harmonized variants = 1,175
qtl N = 980
PP.H4 @ p12=1e-6 = 0.9772
PP.H4 @ p12=1e-5 = 0.9977
PP.H4 @ p12=1e-4 = 0.9998
H4/(H3+H4) @ p12=1e-5 = 0.9977
shared top = rs6702599
```

OneK 主 QTL 可信集的 2/2 变异均属于 FinnGen R13 疾病可信集，累计 OneK PIP≈0.99896。共享 top `rs6702599` 的方向在等位基因对齐后同向。

这允许写：

> OneK NK/IL12RB2 molecular signal shares the FinnGen R13 PBC signal under the frozen single-causal external-validation gate, with complete membership of the OneK primary QTL credible set in the FinnGen R13 disease credible set.

限制：该结果不是第二套 disease source-LD multi-signal fit，也不取代原 GJOKA multi-signal 分析。

## 3. 预冻结 92 比较的 FinnGen/CASCADE 全量覆盖：通过且高度集中

在任何新 CASCADE 查询前，冻结了原稿中的 92 个 stable-H4 comparisons（27 genes、12 cells、19 loci）。查询结果：

```text
27/27 gene endpoints = PASS
22/27 genes = relevant broad-cell eQTL coverage
PBC–eQTL coloc genes = 1
PP.H4 >= 0.8 genes = 1
唯一基因 = IL12RB2
```

IL12RB2 出现 7 条 FinnGen R12 PBC–eQTL 记录；其中预冻结的 NK 轴 `PP.H4≈0.9703`。FCRL3 仍无 FinnGen PBC–eQTL coloc，不得借强 eQTL 本身替代疾病证据。

## 4. IL12RB2 染色质层：由“未建立”纠正为“有界三角一致性”

对预冻结 peak `chr1-67307618-67308670` 的完整区域查询显示：

```text
PBC disease ↔ IL12RB2 eQTL, l1.NK:
PP.H4 = 0.9703; eQTL CS 9/9 contained in disease CS

PBC disease ↔ linked peak caQTL, l1.NK:
PP.H4 = 0.9695; caQTL CS 11/11 contained in disease CS

peak → IL12RB2:
distance to TSS = 239 bp
fasthurdle link beta = 0.1406
```

这会取代 R7B1D 中“该 peak 的 PBC–caQTL colocalization 尚未建立”的旧表述。允许写“PBC-eQTL 与 PBC-caQTL 在 NK 的来源整合信号一致性，并有 promoter-proximal peak–gene link”；仍禁止写“唯一因果变异已确定”或“疾病→染色质→表达的方向性中介已证明”。当前公共接口没有直接 eQTL–caQTL coloc posterior；历史 positional top eQTL variant 也不在该 peak caQTL CS 中。

## 5. OMIX001122 空间资源：真实字节通过，独立验证门失败

34.63 MB 开放 archive 的“6”代表 6 个 Matrix Market 组件文件，不是 6 名供者。实际只有：

```text
CTR4_2 = 1 control matrix, 3,573 spots
PBC5_2 = 1 PBC matrix, 1,365 spots
```

archive 未携带组织图像坐标或 spot annotation。IL12RB2 与 FCRL3 在两套矩阵中可检测，但只能作为描述性 detectability；不能进行供者级复制、病例对照推断或新的空间定位。该数据亦来自已发表 PBC 研究。[OMIX001122](https://ngdc.cncb.ac.cn/omix/release/OMIX001122)，[original publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC9911648/)。

## 6. 下一阶段

下一阶段冻结为：

```text
R7C1 — IL12RB2 External Validation Module + Manuscript Fork
```

R7C1 只建立一个从 R7B4B2 派生的新稿分支：加入 FinnGen R13×OneK 外部共定位、R12/R13 credible-set 稳定性和有界 chromatin triangle；不重写原始 642 benchmark，不扩充新基因/位点，不把 OMIX 写成验证阳性。完成新 Figure/Methods/Results/Discussion 后必须进行一次 hostile claim audit。若升级稿在创新性或因果边界上无法通过，该分支停止，R7B4B2 SCI 二区基线继续有效。

## 7. QA

```text
R7C0 independent QA = 25/25 PASS
RP v4 package checksum = 12/12 PASS
R7B4B2 baseline commit = db20068e700b9c1ded8fb9171dab7e8da6aa33b7
baseline modification = NO
Zenodo DOI = NULL (AUTHENTICATION_REQUIRED)
```
