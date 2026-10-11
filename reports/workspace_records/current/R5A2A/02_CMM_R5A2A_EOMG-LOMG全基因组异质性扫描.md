# CMM R5A2A：EOMG–LOMG 全基因组异质性扫描

## 输入与方法

输入为 R5A1 冻结的 GWAS Catalog harmonised 文件：

- EOMG `GCST90432157.h.tsv.gz`：217,879,063 bytes，SHA-256 `cc3667600a831728b064d736e12665d424683591ba6ee479c61087d394dca5cc`；
- LOMG `GCST90432158.h.tsv.gz`：187,396,334 bytes，SHA-256 `b824861a9e33f83b1af539084f30d54e41dbc4c921295187dd730abc0266b7e6`。

每个变异以 GRCh38 `chromosome_position_REF_ALT` 为唯一身份，效应量与频率均定向至 ALT。排除 GRCh38 chr6:25–35 Mb MHC 区域后，对 EOMG 与 LOMG 的 exact shared variants 计算：

`Zhet = (beta_EOMG_ALT - beta_LOMG_ALT) / sqrt(SE_EOMG^2 + SE_LOMG^2)`。

该检验按两亚型样本独立冻结；Z 分布校准仅作描述，不代替 LDSC intercept，也不用于证明不存在残余样本重叠。

## 全量审计

| 指标 | EOMG | LOMG |
|---|---:|---:|
| 原始数据行 | 7,563,388 | 6,120,145 |
| 重复 canonical key 排除 | 8 | 839 |
| MHC 行排除 | 46,006 | 55,421 |
| 最终单侧非 MHC 唯一行 | 7,517,366 | 6,063,046 |

合并后 exact shared=5,231,937；EOMG-only=2,285,429；LOMG-only=831,109。所有可解析记录的 effect allele 均为 canonical ALT。

## 多重检验结果

- 全共享 Bonferroni 阈值：`0.05 / 5,231,937 = 9.55668999836963e-09`；
- 通过阈值的变异：0；
- Phet≤1e-5：68 个变异，按 1 Mb 距离规则形成 17 个描述性簇；
- Phet<5e-8：1 个，即 rs7596255；其全共享校正 P=0.19218，因此不显著；
- Z 均值=0.04493，Z 方差=1.00636，平均 χ²=1.00838，未见明显整体膨胀。

距离簇只用于压缩浏览，不能解释为 LD 独立 loci。

## 已知四个位点

| 位点 | Phet | 全共享校正 P | 结论 |
|---|---:|---:|---|
| rs7596255 | 3.6732e-8 | 0.1922 | nominal 最强；全基因组门不通过 |
| rs7239261 | 6.4971e-7 | 1 | LOMG 富集；靠独立疾病复制获得主优先级 |
| rs6861227 | 1.6423e-5 | 1 | EOMG 富集；保留次级分子验证 |
| rs2476601 | 0.9545 | 1 | 亚型共享效应正控 |

## 新探索簇

chr8:138,298,285–138,300,192 包含 4 个 Phet≤1e-5 变异，lead rs12542289 的 Phet=`1.4582e-7`。EOMG 与 LOMG 效应方向相反，但该区域未经过独立疾病复制和 LD 独立性验证，所以状态为 `EXPLORATORY_WATCHLIST`，不得替代 chr18 或扩展主故事。

## 结论

本轮解决了候选选择后的统计偏倚，但没有发现全基因组显著的亚型异质性变异。MG 项目的主价值需要来自“经复制的亚型富集疾病位点能否被免疫细胞调控信号解释”，而非把 nominal heterogeneity 排名包装成新发现。
