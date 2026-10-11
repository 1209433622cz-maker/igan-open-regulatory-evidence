# Fig2：PBC同输入归因与双向重分类

整理日期：2026-10-12。按实际图义、疾病、阶段、分母及证据上限分类。

Fig1–Fig6沿当前PBC六图论证顺序；Fig7、Fig8是MG、IgAN历史归档，**不是论文第7、第8张主图**。

`00_当前投稿候选_R7C3B_校验副本`中的PDF/PNG与稿件目录逐字节一致，仅供统一导航。投稿权威原件仍位于 `5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/02_Figures`。这些副本不构成新版作者批准或已投稿。

同组PNG/PDF/SVG保留为栅格预览/矢量导出，不删同图多格式。历史原型不能因归入Fig目录而升级为当前论文结论。

## R7C3B/Figure_2

状态：`CURRENT_SUBMISSION_CANDIDATE_REFERENCE_COPY`；主职责：`STATISTICAL_EVIDENCE`。

内容：支持匹配、三段归因、状态矩阵、A2分母、PF敏感性及signal-pair并存。

数值锚点：15/19/139；H4=113、H3=452；8/10严格转移；491/4/25 PF结局。

证据边界：**不称真实数据的错误修正率；32个H4比较可同时有distinct pair。**

后续价值：当前阅读/核对入口；门户上传仍以5_manuscript中的正式文件为准。

生成代码/来源记录：[来源](<../../5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/07_Reports/02_npj_Production_Source_Conservation_and_Upload_Map.md>)

文件：[PDF](<00_当前投稿候选_R7C3B_校验副本/R7C3B_Fig2_同输入归因与双向重分类.pdf>) · [PNG](<00_当前投稿候选_R7C3B_校验副本/R7C3B_Fig2_同输入归因与双向重分类.png>)

## R7B2A/R7B2A_Figure2_attribution_prototype

状态：`HISTORICAL_PROTOTYPE`；主职责：`STATISTICAL_EVIDENCE`。

内容：三热图：A0→A1支持集、A1→A2疾病统计、A2→M全推断流程。

数值锚点：三个矩阵各642；状态改变15/19/139；同输入strict H4→H3=8、H3→H4=10、stable H4=79、H3=413。

证据边界：**15+19+139不能简单相加为唯一受影响比较；真实数据无因果真值；A2→M不是只改变因果变异个数的纯对照。**

后续价值：当前Fig2源原型/源表，适合核查同输入分母与18条严格方向变化。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b2a/05_build_r7b2a_manuscript_lock_assets.py>)

文件：[PDF](<10_同输入三段归因_R7B2A/01_R7B2A_642_支持集_疾病统计_推断流程转移.pdf>) · [PNG](<10_同输入三段归因_R7B2A/01_R7B2A_642_支持集_疾病统计_推断流程转移.png>) · [SVG](<10_同输入三段归因_R7B2A/01_R7B2A_642_支持集_疾病统计_推断流程转移.svg>)

配套源表：[Figure2_adjacent_transition_matrices.tsv](<90_源数据/R7B2A/Figure2_adjacent_transition_matrices.tsv>) · [Figure2_attribution_summary.tsv](<90_源数据/R7B2A/Figure2_attribution_summary.tsv>) · [Figure2_historical_12_direction_changes.tsv](<90_源数据/R7B2A/Figure2_historical_12_direction_changes.tsv>)

## R7B1B_v2/Figure_R7B1B_1_bidirectional_reclassification

状态：`HISTORICAL_PROTOTYPE`；主职责：`STATISTICAL_EVIDENCE`。

内容：四类历史ABF行到五类PF10多信号列；每格计数及行百分比。

数值锚点：行总数112/72/455/3；历史stable H4=78，H4→H3=4，H3→H4=8，stable H3=409；列和92/428/59/63/0。

证据边界：**尚未采用R7B2A同输入A2对照；不能把4/8直接写成当前8/10。642是高信息子集，不是全部6923比较。**

后续价值：保留对照设计演进与历史四类筛查来源；当期主图使用00目录当前参考版。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b1/15_build_r7b1b_v2_figures.py>)

文件：[PDF](<20_历史筛查到多信号_R7B1B/01_R7B1B_642_ABF到多信号_历史双向转移矩阵.pdf>) · [PNG](<20_历史筛查到多信号_R7B1B/01_R7B1B_642_ABF到多信号_历史双向转移矩阵.png>)

配套源表：[Figure_R7B1B_1_ABF_to_multisignal_matrix.tsv](<90_源数据/R7B1B_v2/Figure_R7B1B_1_ABF_to_multisignal_matrix.tsv>)

## R7B1B_v2/Figure_R7B1B_2_cohort_separated_outcomes

状态：`HISTORICAL_PROTOTYPE`；主职责：`STATISTICAL_EVIDENCE`。

内容：按184 primary、455 H3 rescue、3 borderline分开堆叠PF10结局。

数值锚点：Primary 83/19/52/30；H3队列8/409/7/31；borderline 1/0/0/2；总计642。

证据边界：**角色是预冻结筛查队列，不是匹配后A2 H4=113/H3=452分母；不同层级数字不能互换。**

后续价值：保留对称证伪设计与队列分开报告逻辑，可用于补充说明。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b1/15_build_r7b1b_v2_figures.py>)

文件：[PDF](<20_历史筛查到多信号_R7B1B/02_R7B1B_184_455_3_分队列多信号结局.pdf>) · [PNG](<20_历史筛查到多信号_R7B1B/02_R7B1B_184_455_3_分队列多信号结局.png>)

配套源表：[Figure_R7B1B_2_role_state_counts.tsv](<90_源数据/R7B1B_v2/Figure_R7B1B_2_role_state_counts.tsv>)

## 配套源表与状态

- [figure_assembly_state.json](<91_阶段状态/R7B1B_v2/figure_assembly_state.json>)
- [Figure_R7B1B_1_ABF_to_multisignal_matrix.tsv](<90_源数据/R7B1B_v2/Figure_R7B1B_1_ABF_to_multisignal_matrix.tsv>)
- [Figure_R7B1B_2_role_state_counts.tsv](<90_源数据/R7B1B_v2/Figure_R7B1B_2_role_state_counts.tsv>)
- [Figure2_adjacent_transition_matrices.tsv](<90_源数据/R7B2A/Figure2_adjacent_transition_matrices.tsv>)
- [Figure2_attribution_summary.tsv](<90_源数据/R7B2A/Figure2_attribution_summary.tsv>)
- [Figure2_historical_12_direction_changes.tsv](<90_源数据/R7B2A/Figure2_historical_12_direction_changes.tsv>)

R7B1B三图的共同状态保存在Fig2，细胞图与其源表在Fig5；状态文件原文保持不变。
