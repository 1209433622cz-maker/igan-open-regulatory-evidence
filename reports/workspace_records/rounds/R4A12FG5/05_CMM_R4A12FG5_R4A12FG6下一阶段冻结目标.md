# CMM R4A12FG5：R4A12FG6 下一阶段冻结目标

## 阶段名称

> **R4A12FG6 — Full EUR503 Reference Completion + Three-cell Full-summary Intake Gate**

## 为什么不是现在直接跑更多coloc

FG5已经证明：
- archived 1555-variant EUR503矩阵只覆盖current exact set的36.9%；
- NK两个source CS在该矩阵中PIP mass均为0；
- QTL top与FinnGen regional lead缺失；
- 因此external-LD multi-signal没有合格输入。

同时三个secondary cells的source evidence值得继续，但full beta/SE尚未在本轮归档中。

## Track A：Full regional EUR503 completion

使用用户本地历史full regional panel（27,067 biallelic SNPs，EUR503），**在看新LD结果之前冻结**以下通过条件：

1. current 891 exact variants的LD可用覆盖率 ≥80%；
2. NK每个source CS保留PIP mass ≥95%；
3. `rs17129789 / rs6662198 / rs1954118` 三个anchor全部保留；
4. ALT allele orientation逐项通过；
5. LD对称、对角≈1、最小特征值容差 ≥ -1e-7；
6. AF和z–LD诊断必须完整报告；
7. 不允许删除高residual variant以强迫PASS。

只有这些门通过，才允许external-LD multi-signal sensitivity。

## Track B：三细胞full-summary intake

只下载：
- CD8_TEM member
- CD4_CTL member
- CD4_TCM member

仍只提取 `ENSG00000081985 / IL12RB2`；每个成员必须通过：
- local header identity；
- compressed range completeness；
- full uncompressed bytes；
- source CRC32；
- exact gene field提取；
- output SHA-256。

不得增加第四个细胞，不得扩1 Mb。

## Track C：三细胞信号复核

full-summary到位后：
1. 与R13/R12采用相同exact REF/ALT harmonization；
2. 使用FG4同一p12网格做single-causal sensitivity；
3. 若Track A LD通过，再做multi-signal external-LD sensitivity；
4. 如果external LD不通过，则结果保持 `SUMMARY_ONLY`，不以ABF高H4升级。

## 决策

- `SECONDARY_SIGNAL_SUPPORTED`：full EUR503门PASS，multi-signal结果稳定，且三个secondary cells中至少两个与NK结构/方向一致。
- `SUMMARY_ONLY`：LD仍不充分、source LD缺失或multi-signal不稳定。
- `STOP_IL12RB2_ALLSEX_BRANCH`：只有充分输入+充分LD下，NK和三个secondary均稳定支持distinct/unshared才允许停止。
- 2026 female/male chr22/SYNGR1字节一旦到达，优先级高于本分支。

## Source-matched LD

若full EUR503 external gate仍无法支持paper-grade adjudication：
- 不再继续换external panel；
- 转向TenK10K EGA `EGAS50000001654 / EGAD50000002377`申请或作者提供source correlation matrix；
- external结果降为sensitivity，不作为最终signal identity证据。
