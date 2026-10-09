# CMM R7B1C：协议、模板、引擎与失败恢复

## 预结果冻结

R7B0 的 486-row grid 原样保留。R7B1C 在任何正式结果前补充了模板身份、效应量、因果索引、PSD 修正、判定阈值与 pilot gate。实现使用标准 summary-statistic 模型 `z ~ N(sqrt(N) Rb, R)`，SuSiE 配置与 R7B1B 真实数据主分析一致。

## 两次被门控拦截的实现问题

1. v1 cross-locus mismatch 使 S6 长时间贴近最大迭代上限，并混合不同区域的索引语义。未汇总 posterior 即停止；v1.1 改为同一位点 PF10 z + PF50 QTL LD。
2. v1.1 首次 pilot 的 z/LD 未设置共同 variant names，导致有 credible set 但 `coloc.susie` 无 eligible pair。该纯实现错误修复后重新执行完整双重 pilot，没有改变统计规则。

最终 pilot 两次 300-replicate replay 逐字节一致，12/12 gate PASS。完整运行按 486 个 grid row checkpoint，可安全续跑。

## 计算身份

- R 4.6.1；susieR 0.14.2；coloc 5.2.3。
- 每格两个模板各 500 次；固定上游 seed。
- 原始 486 个压缩结果文件和合并 486,000-row truth table 留在本地；release 仅收录聚合表、代码、协议、模板和精确 hash manifest。
