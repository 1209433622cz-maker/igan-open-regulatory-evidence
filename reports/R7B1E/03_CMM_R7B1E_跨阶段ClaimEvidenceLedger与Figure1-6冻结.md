# R7B1E 跨阶段 Claim–Evidence Ledger 与 Figure 1–6 冻结

## Claim ledger

共冻结 22 条 claim。每条均包含 manuscript section、claim text、evidence tier、quantitative anchor、primary/supporting source、允许动词、禁止动词、limitation 和 figure/panel owner。所有 claim 状态均为 `SUPPORTED` 或 `SUPPORTED_BOUNDARY`；没有把待验证假设写成既成事实。

主要证据链如下：

1. **范围与门控**：6,923 个 PBC-wide screen comparisons，5,460 个 ABF eligible，642 个预设 high-information comparisons 进入多信号分析。
2. **双向重分类**：H4→H3=4，H3→H4=8；92/92 stable H4 与 428/428 stable H3 的 signal-pair identity 得到确认。
3. **真值已知校准**：distinct-signal 情景中平均 false-H4 从 12.41% 降至 8.56%，同时 shared-signal recovery 从 32.99% 降至 26.66%；改善具有情景依赖性，S2 matched false-H4 仍为 16.0%。
4. **IL12RB2 外部层**：OneK source-matched、TenK molecular-QTL 和 FinnGen PBC–eQTL 支持一致；risk allele 与更高表达相关；chromatin 仅为 positional layer。
5. **FCRL3 支持与反例**：B-cell sharing 在 OneK/TenK 跨 QTL 资源成立；CD8_ET 保留 H4→H3 counterexample；FinnGen 未返回 PBC–FCRL3 pair，不作阴性解释。
6. **组织边界**：FCRL3-B 与 IL12RB2-NK 在 5/5 PBC 和 5/5 control donors 可检测，但 BH q 均为 0.111，不支持 PBC-specific enrichment 或 tissue mediation。

## Figure 1–6 source freeze

8 个 panel rows 覆盖 Figure 1–6：

| Figure | 科学任务 | 核心边界 |
|---|---|---|
| 1 | universe、eligibility、high-information subset 与 model/diagnostic gates | 不暗示全部 6,923 接受多信号分析 |
| 2 | 双向重分类、PF sensitivity、signal-pair identity | 不把多信号结果当作 causal truth |
| 3 | 真值已知 simulation trade-off | 不宣称一般方法优越性 |
| 4 | IL12RB2 FinnGen、方向与 positional chromatin | 不声称完整 causal cascade |
| 5 | FCRL3 B-cell support 与 CD8_ET counterexample | 不把 FinnGen non-return 写成阴性复制 |
| 6 | exact 5-vs-5 tissue boundary | 不声称 PBC-specific upregulation/mediation |

9 个 source-data assets 已建立 SHA-256。架构图已输出 PNG、PDF、SVG，用于 R7B2 写作与最终图件装配的导航；它本身不是替代主图的结果图。

## 写作治理

本轮使用 QiTeng Academic Writing Skill v0.3.24.2 active Runtime Core，采用 `CLAIM → EVIDENCE → INTERPRETATION → QUALIFICATION → BRIDGE` 结构，并执行 evidence/claim governor。没有调用 CC skill。当前证据最高支持稳健关联、跨资源一致性、情景性校准与明确边界，不支持机制、临床效用或普遍优越性语言。
