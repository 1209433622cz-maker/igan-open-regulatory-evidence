# CMM R4A12FG4：R12/R13 Harmonization、覆盖与锚点审计

## 冻结门与结果

本轮在读取 harmonization 结果前把 coverage 门写入代码：QTL 与 overlap 均至少 100；QTL exact overlap fraction ≥0.80；exact reference alignment ≥0.99；AF 绝对差中位数 ≤0.10、P95 ≤0.20；QTL top、disease regional lead、rs6662198 必须保留；每个 source CS 全成员且 PIP mass ≥0.95。

R12 与 R13 结果相同：1,366 个 QTL 变异中 891 个 exact overlap（65.23%），5 个 reverse-allele 同位置对象排除。AF 中位差约 0.02994，P95 约 0.12226，三个锚点全部覆盖。门失败来自总体 exact coverage 和 CS1 PIP coverage，不来自 schema、坐标、AF 或锚点。

| Source CS | 成员覆盖 | PIP mass 覆盖 | 判定 |
|---|---:|---:|---|
| CS1 | 11/12 | 0.73106/1.01433 = 72.07% | HOLD |
| CS2 | 3/4 | 0.95485/0.97526 = 97.91% | 成员不全；质量大体保留 |

CS1 缺失 `1:67322669:A:G`（rs5022165，PIP=0.283267），FinnGen 两版区域文件中该位置都不存在。CS2 缺失 `1:67306704:AG:A`（rs3834764，PIP=0.020407）。NCBI Variation Services 完成两个 RefSNP 映射。

外部 1000G EUR503 诊断发现 rs5022165 与同一 CS、已覆盖的 `1:67326053:A:C`（rs11209050）`r²≈1.0`。这说明主要缺失 PIP 很可能有强代理，但不能恢复缺失变异的 disease statistic，也不能替代 TenK10K source-matched LD。exact coverage 状态继续为 HOLD。

三个锚点在 exact allele 下方向一致：QTL top、rs6662198、R12/R13 regional disease lead rs1954118 均同时具有很强 eQTL 和名义/区域疾病信号。这是继续做 LD-aware adjudication 的理由，不是 shared causal 结论。
