# Fig5：PBC细胞上下文与模型敏感性

整理日期：2026-10-12。按实际图义、疾病、阶段、分母及证据上限分类。

Fig1–Fig6沿当前PBC六图论证顺序；Fig7、Fig8是MG、IgAN历史归档，**不是论文第7、第8张主图**。

`00_当前投稿候选_R7C3B_校验副本`中的PDF/PNG与稿件目录逐字节一致，仅供统一导航。投稿权威原件仍位于 `5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/02_Figures`。这些副本不构成新版作者批准或已投稿。

同组PNG/PDF/SVG保留为栅格预览/矢量导出，不删同图多格式。历史原型不能因归入Fig目录而升级为当前论文结论。

## R7C3B/Figure_5

状态：`CURRENT_SUBMISSION_CANDIDATE_REFERENCE_COPY`；主职责：`ROBUSTNESS_DIAGNOSTIC`。

内容：B-cell sharing、跨QTL资源、CD8_ET A0/A1/A2/PF10/PF50对照及claim boundary。

数值锚点：FCRL3 B_IN≈0.9937、B_MEM≈0.9910、TenK≈0.9916；CD8_ET PF10≈0.003636 vs PF50≈0.991894。

证据边界：**独立分子QTL资源复用同一疾病GWAS；PF50高H4不证明恢复真值；FinnGen未返回不等于有power阴性复制。**

后续价值：当前阅读/核对入口；门户上传仍以5_manuscript中的正式文件为准。

生成代码/来源记录：[来源](<../../5_manuscript/R7C3B_QiTeng_WPS_SubmissionRefinement_20261011/07_Reports/02_npj_Production_Source_Conservation_and_Upload_Map.md>)

文件：[PDF](<00_当前投稿候选_R7C3B_校验副本/R7C3B_Fig5_细胞上下文与PF10_PF50敏感性.pdf>) · [PNG](<00_当前投稿候选_R7C3B_校验副本/R7C3B_Fig5_细胞上下文与PF10_PF50敏感性.png>)

## R7B1B_v2/Figure_R7B1B_3_cell_context_reclassification

状态：`HISTORICAL_PROTOTYPE`；主职责：`STATISTICAL_EVIDENCE`。

内容：十四细胞按stable H4/H3、H4→H3、H3→H4四类水平条形分布。

数值锚点：只展示历史strict/stable四类499比较；NK H3→H4=4，CD4_NC=2，Mono_NC=2；不展示全部143其它结局。

证据边界：**跨细胞计数不是样本量独立复制；未对每个cell universe做新的多重检验；阶段历史定义。**

后续价值：可作为cell-context异质性图法与旧版补充图，不替代当前模型特异Fig5。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7b1/15_build_r7b1b_v2_figures.py>)

文件：[PDF](<10_历史细胞重分类分布_R7B1B/01_R7B1B_14细胞_历史稳定与严格重分类分布.pdf>) · [PNG](<10_历史细胞重分类分布_R7B1B/01_R7B1B_14细胞_历史稳定与严格重分类分布.png>)

配套源表：[Figure_R7B1B_3_cell_reclassification_counts.tsv](<90_源数据/R7B1B_v2/Figure_R7B1B_3_cell_reclassification_counts.tsv>)

## R7A1B/R7A1B_PBC_signal_gate_summary

状态：`HISTORICAL_PROTOTYPE`；主职责：`ROBUSTNESS_DIAGNOSTIC`。

内容：左：九比较ABF smoke；右：七比较PF/L配置的最佳signal-pair H4。

数值锚点：IL12RB2/NK≈0.998；FCRL3/B_IN≈0.994；CD8_ET≈0.004；INAVA弱/无信息。

证据边界：**图中的历史PF10/PF50列不能代表当前同源双模型。R7B0A记录历史PF10字节身份未恢复，后续current-release de novo结果才是当前依据。**

后续价值：保留从早期双基因机制路线转向来源/模型可靠性论文的历史证据；不上传为当前Fig5。

生成代码/来源记录：[来源](<../../2_code/06_intake/r7a1b/11_build_r7a1b_summary_assets.py>)

文件：[PNG](<20_历史正控门_来源身份需按R7B0A解释/01_R7A1B_PBC_IL12RB2_FCRL3_INAVA_历史模型门.png>)

## 配套源表与状态

- [Figure_R7B1B_3_cell_reclassification_counts.tsv](<90_源数据/R7B1B_v2/Figure_R7B1B_3_cell_reclassification_counts.tsv>)

R7B1B三图的共同状态保存在Fig2，细胞图与其源表在Fig5；状态文件原文保持不变。
