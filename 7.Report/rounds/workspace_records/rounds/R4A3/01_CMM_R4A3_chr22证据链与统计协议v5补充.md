# chr22 证据链审计与统计协议 v5 补充

日期：2026-09-09。本文件是看过 R4A3 数据后的透明修订，不声称事前注册。

## 候选竞争的实际结果

查询区域 chr22:38828807–39828807，pmax=1；细胞 l1.NK、l2.NK、l2.CD8_TEM。基因 SYNGR1 ENSG00000100321、RPL3 ENSG00000100316、PDGFB ENSG00000100311。查询保留阴性 pair，不只取 top hits。

|细胞|SYNGR1 exact-lead P|RPL3 exact-lead P|PDGFB exact-lead P|目标 peak caQTL P|
|---|---:|---:|---:|---:|
|l1.NK|2.8694e-102|0.41723|NOT_RETURNED|1.42069e-183|
|l2.NK|9.9831e-110|0.19127|NOT_RETURNED|4.13044e-178|
|l2.CD8_TEM|4.7553e-83|0.03407|0.84948|5.32385e-179|

所有 exact rows 在本次源编码中为 chr22:39328807 A>AT；这不是完成了与 GWAS/dbSNP 的 FASTA 左对齐。indel 等价性和 effect allele 仍需正式 harmonization。maf 字段保持源名，未擅自当 EAF。

## Peak link 的支持与竞争

源 gene 注释：SYNGR1 正链、39349991–39385575，MANE ENST00000328933。peak 位于基因内部；按该转录本外显子表位于第一和第二外显子之间。gene 页 dist_tss=1529；peak 顶层 dist_tss=0 是不同层级字段，不拿后者宣称精确启动子重叠。

SYNGR1 peak 条目 fhurdle best_ct=NK，joint_fdr=9.19343e-249。l1.NK beta_zero=0.66167、beta_count=0.17689；模型两个分量不混成遗传效应 beta。PBMC joint_p=0 被保留为数值下溢/源零值待确认，不能写成无限显著；p_zero=null 不补零。来源关联不证明 accessibility 导致 expression，也不替代遗传共定位。

19 个 linked genes 全量保存在 peak_links.json；逐细胞信息保存在 peak_links_per_cell.tsv。接下来保留 SYNGR1/RPL3/PDGFB 三个预先讨论的候选，并将源关联候选作为有界竞争集合记录；不能只保留最支持 SYNGR1 的峰或细胞。

## 信号与覆盖限制

7 个 eQTL pair 共 21791 nominal rows，3 个 caQTL pair 共 2007 rows。PDGFB 在两种 NK 未返回，保持 NOT_RETURNED。eQTL 实际 38828900–39828162；caQTL 实际 39251575–39452254。不能将请求窗口等同有效覆盖。

SYNGR1 与 RPL3 三细胞 CS 皆空。PDGFB/CD8 TEM 提供两个 CS，分别 67、8 条；目标 peak/CD8 TEM 提供三个 CS，分别 14、19、1 条（编号 3、2、1）。6 个集合配对 exact 坐标/等位基因交集均为 0。这只是源 CS 描述性比较，未做参考序列标准化、LD 检查和正式 coloc，不构成 H3 或 NO-GO。

peak top_variants 中 chr22_39351775_G_A 的跨细胞汇总 PIP≈0.998823，源标签 Only caQTL (overlap link)。它和 SSc lead 不同不自动否定 LD 代理可能；没有 LD 不能宣称两个信号独立。SYNGR1 gene top_variants 仅返回 CD14_Mono 的另一个 eQTL，也不能代替 NK 完整 CS。

## v5 判定规则

- 疾病证据与分子证据分列。R4A2 的 C2 表示 disease shared signal；目前两链均无 C2。C3 若使用，仅表示分子/边际可研究性。禁止跨版本沿用模糊 C2/C3 标签给未测试疾病证据升级。
- C1 保留 v4 全链要求：Disease↔eQTL、Disease↔caQTL、eQTL↔caQTL signal coherence、来源明确的 peak→gene link、build/allele/LD/coverage 技术 PASS。PP.H4≥0.80 仅为统计阈值之一，同时报告 H3、H4/(H3+H4)、先验敏感性和多信号处理。
- primary cell-specific C1 要求同一细胞类型三方一致；近缘细胞拼接仅为次级跨细胞假说。l1.NK 与 l2.NK 有嵌套样本，不作为独立复制。
- NOT_RETURNED、CS_NOT_RETURNED、INSUFFICIENT_COVERAGE、NOT_TESTED 与真正充分检验后的 FAIL 分开。
- source is_cascade=false 不等于我们的 SSc C1 已失败；source CASCADE 和新疾病三方链的对象不同。
- 只有双位点在充分数据与技术 PASS 后仍无 C1，才进入一次有界 all-8 rescue；输入缺失时不启动 rescue。预先限定所有候选和多重比较方案，不因结果漂亮改复制资源角色。

本轮没有计算 PP4、MR、性别交互、组织验证或新 causal cascade 数量。
