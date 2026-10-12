# Fig3：PBC模拟校准与可评价性

整理日期：2026-10-12。按实际图义、疾病、阶段、分母及证据上限分类。

Fig1–Fig6沿当前PBC六图论证顺序；Fig7、Fig8是MG、IgAN历史归档，**不是论文第7、第8张主图**。

`00_当前投稿候选_R7C3B_校验副本`中的PDF/PNG与稿件目录逐字节一致，仅供统一导航。投稿权威原件仍位于 `5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/02_Figures`。这些副本不构成新版作者批准或已投稿。

同组PNG/PDF/SVG保留为栅格预览/矢量导出，不删同图多格式。历史原型不能因归入Fig目录而升级为当前论文结论。

## R7C3B/Figure_3

状态：`CURRENT_SUBMISSION_CANDIDATE_REFERENCE_COPY`；主职责：`ROBUSTNESS_DIAGNOSTIC`。

内容：通道占比、发现/推断分母、方法trade-off及no-CS原因。

数值锚点：486000；160782 pair-evaluable；325218 no-CS；0记录技术错误。

证据边界：**跨场景误共享与共享恢复同时呈代价；未证明通用算法优越。**

后续价值：当前阅读/核对入口；门户上传仍以5_manuscript中的正式文件为准。

生成代码/来源记录：[来源](<../../5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/07_Reports/02_npj_Production_Source_Conservation_and_Upload_Map.md>)

文件：[PDF](<00_当前投稿候选_R7C3B_校验副本/R7C3B_Fig3_模拟校准与可评价性分母.pdf>) · [PNG](<00_当前投稿候选_R7C3B_校验副本/R7C3B_Fig3_模拟校准与可评价性分母.png>)

## R7B2A/R7B2A_Figure3_simulation_channels_prototype

状态：`HISTORICAL_PROTOTYPE`；主职责：`ROBUSTNESS_DIAGNOSTIC`。

内容：左六场景pair/no-CS通道占比；右pair-evaluable、H4 unconditional和H4 conditional-on-pair。

数值锚点：486000迭代；160782 pair-evaluable=33.08%；325218 no-CS；场景可评价率13.29%–59.79%。

证据边界：**no-CS不等于软件错误；conditional H4不等于总体检出率；不遗漏共享场景的恢复代价。**

后续价值：当前Fig3的重要源原型；补充方法与审稿分母问答。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b2a/05_build_r7b2a_manuscript_lock_assets.py>)

文件：[PDF](<10_发现通道与条件分母_R7B2A/01_R7B2A_模拟发现通道_可评价率与条件H4.pdf>) · [PNG](<10_发现通道与条件分母_R7B2A/01_R7B2A_模拟发现通道_可评价率与条件H4.png>) · [SVG](<10_发现通道与条件分母_R7B2A/01_R7B2A_模拟发现通道_可评价率与条件H4.svg>)

配套源表：[Figure3_discovery_vs_estimator_performance.tsv](<90_源数据/R7B2A/Figure3_discovery_vs_estimator_performance.tsv>) · [Figure3_simulation_channel_summary.tsv](<90_源数据/R7B2A/Figure3_simulation_channel_summary.tsv>)

## R7B1C/Figure_R7B1C_1_scenario_H4_decisions

状态：`HISTORICAL_PROTOTYPE`；主职责：`STATISTICAL_EVIDENCE`。

内容：S1–S6真值已知场景；ABF与source-matched多信号H4决策率柱形对照。

数值锚点：S2 distinct：20.50%→16.00%；S5 distinct：4.32%→1.12%；S1 shared：65.94%→54.12%。

证据边界：**这是全部replicates无条件决策率；没有pair时不构成可评价的模型分类。共享恢复同时下降，不能宣称普遍优越。**

后续价值：模拟trade-off原型；与R7B2A可评价性图及当前Fig3并读。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b1c/07_build_r7b1c_figures.py>)

文件：[PDF](<20_六场景H4决策率_R7B1C/01_R7B1C_六场景_ABF与多信号_无条件H4决策率.pdf>) · [PNG](<20_六场景H4决策率_R7B1C/01_R7B1C_六场景_ABF与多信号_无条件H4决策率.png>)

配套源表：[Figure_R7B1C_1_decision_rates.tsv](<90_源数据/R7B1C/Figure_R7B1C_1_decision_rates.tsv>)

## R7B1C/Figure_R7B1C_2_LD_stratified_decisions

状态：`HISTORICAL_PROTOTYPE`；主职责：`ROBUSTNESS_DIAGNOSTIC`。

内容：六小面板；r²=0.2/0.5/0.8；两方法无条件H4率曲线。

数值锚点：S2 distinct在r²升高时误共享上升；复杂共享S4/S6在高r²下H4恢复很低。

证据边界：**只涵盖冻结模拟模板/参数网格；不等于真实人群所有LD情形或经验错误率。**

后续价值：补充稳健性与模拟场景解释，可引用具体source TSV。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b1c/07_build_r7b1c_figures.py>)

文件：[PDF](<21_LD相关度分层_R7B1C/01_R7B1C_六场景_因果变异r2分层决策率.pdf>) · [PNG](<21_LD相关度分层_R7B1C/01_R7B1C_六场景_因果变异r2分层决策率.png>)

配套源表：[Figure_R7B1C_2_r2_stratified.tsv](<90_源数据/R7B1C/Figure_R7B1C_2_r2_stratified.tsv>)

## R7B1C/Figure_R7B1C_3_same_locus_LD_mismatch

状态：`HISTORICAL_PROTOTYPE`；主职责：`ROBUSTNESS_DIAGNOSTIC`。

内容：左matched/mismatch的MAF分层H4率；右mean absolute best-H4变化。

数值锚点：MAF0.4/r²0.2：H4 0.4828 vs 0.4803，mean|ΔH4|≈0.005665；仅9个MAF×r²汇总。

证据边界：**同位点PF10→PF50的有边界错配压力测试，不是跨祖源LD基准，也不是所有LD不匹配损害的估计。**

后续价值：保留低成本同位点错配反例；主类别按模拟而非真实数据Fig5。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b1c/07_build_r7b1c_figures.py>)

文件：[PDF](<22_同位点LD错配模拟_R7B1C/01_R7B1C_S6_PF10到PF50_LD错配与H4扰动.pdf>) · [PNG](<22_同位点LD错配模拟_R7B1C/01_R7B1C_S6_PF10到PF50_LD错配与H4扰动.png>)

配套源表：[Figure_R7B1C_3_S6_mismatch.tsv](<90_源数据/R7B1C/Figure_R7B1C_3_S6_mismatch.tsv>)

## R7B1C/Figure_R7B1C_4_credible_set_coverage

状态：`HISTORICAL_PROTOTYPE`；主职责：`ROBUSTNESS_DIAGNOSTIC`。

内容：疾病和QTL在六场景的95% credible-set all-causal coverage曲线。

数值锚点：Disease S1/S2≈0.95、复杂场景≈0.40；QTL S1–S3≈0.56、S4–S6≈0.05。

证据边界：**名义95% credible set不是观察到95% all-causal覆盖；all-causal判据和拟合可评价性须保留。**

后续价值：补充可信集发现瓶颈与power界定；配合当前Fig3分母分析。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b1c/07_build_r7b1c_figures.py>)

文件：[PDF](<23_可信集全因果覆盖_R7B1C/01_R7B1C_疾病与QTL_95pctCS全因果覆盖.pdf>) · [PNG](<23_可信集全因果覆盖_R7B1C/01_R7B1C_疾病与QTL_95pctCS全因果覆盖.png>)

配套源表：[Figure_R7B1C_4_credible_set_coverage.tsv](<90_源数据/R7B1C/Figure_R7B1C_4_credible_set_coverage.tsv>)

## 配套源表与状态

- [figure_assembly_state.json](<91_阶段状态/R7B1C/figure_assembly_state.json>)
- [Figure_R7B1C_1_decision_rates.tsv](<90_源数据/R7B1C/Figure_R7B1C_1_decision_rates.tsv>)
- [Figure_R7B1C_2_r2_stratified.tsv](<90_源数据/R7B1C/Figure_R7B1C_2_r2_stratified.tsv>)
- [Figure_R7B1C_3_S6_mismatch.tsv](<90_源数据/R7B1C/Figure_R7B1C_3_S6_mismatch.tsv>)
- [Figure_R7B1C_4_credible_set_coverage.tsv](<90_源数据/R7B1C/Figure_R7B1C_4_credible_set_coverage.tsv>)
- [Figure3_discovery_vs_estimator_performance.tsv](<90_源数据/R7B2A/Figure3_discovery_vs_estimator_performance.tsv>)
- [Figure3_simulation_channel_summary.tsv](<90_源数据/R7B2A/Figure3_simulation_channel_summary.tsv>)

R7B1B三图的共同状态保存在Fig2，细胞图与其源表在Fig5；状态文件原文保持不变。
