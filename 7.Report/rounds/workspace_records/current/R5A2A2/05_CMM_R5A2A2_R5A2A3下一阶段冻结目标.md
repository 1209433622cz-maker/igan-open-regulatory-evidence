
# CMM R5A2A2：R5A2A3 下一阶段冻结目标

下一阶段固定为 `R5A2A3_CHR18_COLOC_ABF_SMOKE_AND_LD_TRIGGER`。

## 分析矩阵

- 疾病侧：LOMG 为主检验，overall MG 为疾病信号复核，EOMG 为亚型对照；
- QTL 侧：当前 71 个真实存在的 OneK1K cell–gene 组合；
- 坐标与方向：GRCh37 chr18:59,005,046–61,005,046，所有 beta/EAF 定向至 OneK BIM A1；
- 第一层：3 × 71 个 coloc.abf 单信号 smoke tests；
- 第二层：只对共享信号或 H3/H4 可解决歧义的组合建立 cell-specific source LD，并进入条件化或 SuSiE；
- 第三层：只有 OneK1K 信号门通过后才接入 TenK10K 做独立 molecular replication。

## 冻结阈值

每个比较至少 500 个共同变异。默认先验为 `p1=1e-4`、`p2=1e-4`、`p12=1e-5`，同时固定检查 `p12=1e-6` 与 `1e-4`。必须报告 PP.H0–H4、H4/(H3+H4)、共同变异数、两侧区域最小 P 与最大单变异 H4 贡献。

- `PASS_ROBUST_SHARED_SIGNAL`：默认 PP.H4≥0.80，H4/(H3+H4)≥0.80，且先验敏感性不把结论翻转为 H3；
- `HOLD_LD_REQUIRED`：H3+H4 较高但 H3/H4 无法分解，或单信号假设受多峰结构影响；
- `FAIL_SUFFICIENT_COVERAGE`：疾病和 QTL 均有区域信息、共同覆盖充分，但 H4 在冻结先验范围内持续低；
- `UNINFORMATIVE`：某一侧缺乏区域信号，不解释为反向生物学证据。

## 决策顺序

若 LOMG 在至少一个 gene/cell 出现稳健 H4，并且 overall MG 支持同一信号，进入该组合的 source-LD 和 TenK10K 复制。EOMG 是否支持同一信号用于解释共享效应与 LOMG 富集，不要求人为制造 EOMG 阴性。

若没有稳健 H4，但存在明确 H3/H4 歧义，只构建触发组合的 LD，不为全部 71 组合生成大矩阵。若 chr18 在充分覆盖下全部失败，冻结 chr18 为 `FAIL_PRIMARY_LOCUS`，下一轮只测试 chr5 / rs6861227；不调用 chr2 或 chr8 补故事。
