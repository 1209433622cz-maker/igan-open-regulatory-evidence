# R7C2 期刊现实适配矩阵

## npj Genomic Medicine

官方范围明确覆盖基因组学在医学中的应用、整合表型与基因组分析、免疫基因组学、疾病特异变异与计算方法。当前研究的最强匹配点是调控归因可靠性、细胞语境和外部疾病研究系统验证。主要编辑风险是临床转化仍为间接、方法只在一个疾病中完成系统 benchmark。判定：`CONDITIONAL_GO_ONE_ATTEMPT`。

## Communications Biology

期刊接收二次数据分析与计算方法，但要求带来新的生物学认识。当前最强贡献是归因可靠性与统计边界，功能机制并未闭环。主文还需要压缩至约 5,000 字，压缩成本会削弱方法透明度。判定：`HOLD_NOT_PREFERRED`。

## Genome Medicine

期刊要求对理解、诊断或治疗疾病具有广泛意义的突出研究。当前单疾病、有限外部病例数与无功能验证的证据上限不适合以此作为首投。判定：`NO_GO`。

## Human Genomics

官方范围直接覆盖 GWAS、调控基因组学、统计遗传学、转录组和整合多组学。原冻结包已满足其格式和证据层级。判定：`FROZEN_FALLBACK_GO`。

详细机器表见 `results/R7C2_journal_fit_matrix.tsv`，官方来源见 `results/R7C2_official_journal_source_ledger.tsv`。
