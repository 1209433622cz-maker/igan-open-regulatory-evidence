# R7C0 → R7C1 下一阶段冻结目标

## 阶段名称

```text
R7C1 — IL12RB2 External Validation Module + Manuscript Fork
```

## 启动理由

R7C0 同时通过了 RP v4 的两个核心升级条件：

1. 不同研究系统的疾病信号通过：FinnGen R13 × OneK NK/IL12RB2 `PP.H4=0.9977`，低先验仍通过，OneK QTL CS 2/2 进入 R13 disease CS；
2. 多模态增量通过：预冻结 IL12RB2-linked peak 同时具备 PBC–eQTL 与 PBC–caQTL sharing，并有 promoter-proximal peak–gene link。

因此允许创建升级稿分支，但不覆盖 R7B4B2。

## 允许的工作

1. 复制 R7B4B2 manuscript/figure/supplement 到独立 `r7c1` 目录；
2. 新增 FinnGen R13 数据来源、rsID build bridge、ABF 外部验证和 source-CS audit 的 Methods；
3. 新增 R12/R13 稳定性、R13×OneK 结果、chromatin triangle 的 Results；
4. 新增“跨疾病研究系统 + 跨 molecular-QTL resource + 有界染色质三角”的 Discussion；
5. 生成一幅 source-bound external-validation figure 及 source data；
6. 更新 abstract 但保持主论文为 attribution reliability / calibration framework；
7. 进行 hostile claim audit、numeric audit、reference audit、reader-facing QA。

## 禁止的工作

```text
NEW_GENE_LOCUS_CELL_FISHING = NO
FULL_642_RERUN = NO
REOPEN_FCRL3_AS_FINNGEN_POSITIVE = NO
OMIX_AS_INDEPENDENT_REPLICATION = NO
DIRECT_MEDIATION_CLAIM = NO
OVERWRITE_R7B4B2 = NO
```

## R7C1 退出门

### 升级稿继续

需同时满足：

- 新增所有数字都能回指机器表；
- 对 FinnGen 独立性使用 study-system boundary；
- `single-causal external validation` 与 `source-LD multi-signal discovery` 清楚区分；
- 图文不宣称 eQTL–caQTL direct posterior 已计算；
- hostile audit 不发现核心过度推断；
- 新稿的创新性增量足以支持重新评估目标期刊。

### 退回原稿

如升级稿需要夸大中介链、OMIX 或 FinnGen 独立性才能成立，则停止 R7C1：

```text
RETAIN_R7B4B2_Q2_BASELINE
NO_PROJECT_PIVOT
```

## 与 DOI/投稿的关系

GitHub/Zenodo DOI 与期刊投稿是独立发布轨道。当前 Zenodo token 不存在，DOI 仍为 `AUTHENTICATION_REQUIRED`；这不阻塞 R7C1 科学稿件制作，也不得把 GitHub release 误称为期刊投稿。
