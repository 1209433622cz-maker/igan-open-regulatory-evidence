# CMM R7B0：模拟 benchmark 协议冻结

模拟的任务不是制造阳性，而是衡量来源匹配 LD、多信号结构和错误 LD 的分类偏差。六个核心情景已在结果前冻结：一对一共享、相关但不同 causal、疾病两信号/QTL 一信号、两对两信号仅一对共享、两对两信号均不共享但高 LD、以及 matched versus deliberately mismatched LD。

核心情景每格 1000 次重复，次级敏感性 500 次；固定 seed base `20261002`。参数网格包括 MAF 0.05/0.20/0.40、causal r² 0.2/0.5/0.8、SuSiE L 5/10/20、p12 1e-6/1e-5/1e-4，疾病 N=24,510，QTL N=750；LD template 只能来自已审计的 GJOKA locus 2/4 或 OneK source-LD。

每次模拟输出 signal classification、H4 bias、coverage、convergence 和 false-stability rate。S6 中故意错配 LD 只作为诊断，不得被重新包装成 primary evidence。机器协议见 `3_results/00_audit/R7B0/R7B0_simulation_grid.tsv` 和 `R7B0_simulation_freeze.json`。
