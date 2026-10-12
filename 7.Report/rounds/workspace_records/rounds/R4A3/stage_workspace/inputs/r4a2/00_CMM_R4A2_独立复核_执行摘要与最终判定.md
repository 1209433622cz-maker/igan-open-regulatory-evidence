# CMM R4A2 独立复核：执行摘要与最终判定

**日期：2026-09-08**  
**输入：YR1.zip / R4A1真实数据接入与三位点筛查包**  
**阶段：R4A2 = YR1_INDEPENDENT_AUDIT + DUAL_LOCUS_REPRIORITIZATION**

## 1. 最终判定

- **SSc项目：CONDITIONAL GO**
- **R4B全量分析：HOLD**
- **下一运行门：R4A3（Access + Dual-locus signal-level smoke test）**
- 当前状态建议冻结为：`ACCESS_BLOCKED_BUT_HYPOTHESIS_REFINED`

本轮没有发现足以推翻SSc项目的生物学阴性结果。真正的阻塞仍是：**sex-specific SSc完整区域GWAS summary statistics 尚未被实际取得；FinnGen当前主要依赖browser-derived区域/lead记录，而不是已经归档的官方完整summary-statistics release。** 因此不存在可以诚实声称的SSc colocalization、三性状regulatory cascade或C1证据。

## 2. 对YR1最重要的独立复核结论

### 2.1 R4A1的“R4B=HOLD”是正确的

`R4A1_state.json` 明确记录 `ssc_colocalization_computed=false`、`technical_end_to_end_pass=false`、`scientific_smoke_pass=false`、`C1_count=null`。这里的null必须解释为**尚未测试**，不是“0个阴性位点”。这一点在YR1中处理正确。

### 2.2 IRF4仍然值得保留，但职责应该变化

TenK10K在B_naive中对精确lead `6:396321:C:T` 给出IRF4 SuSiE **PIP=0.999309、CS=1且credible set只有1个成员**。然而FinnGen同一B_naive精确variant–IRF4 pair为 **p=0.6728，beta=-0.015405，SE=0.036478**。这不是“复制失败=IRF4错误”的充分证据，但明确说明它是一个非常好的**跨资源不一致诊断位点**：只有拿到SSc区域GWAS后做signal-level colocalization，才知道疾病遗传信号真正支持哪一侧。

### 2.3 chr22 rs66578187应从“第三候选”升级为与IRF4并行的主smoke locus

YR1原始表中，女性特异SSc lead `chr22:39,328,807 A>AT` 对**SYNGR1**存在非常强的精确lead eQTL，同时对一个位于SYNGR1基因内部的ATAC peak存在极强caQTL：

- SYNGR1 eQTL：最强 `l2.NK`, **p=9.983e-110**, beta=0.4949
- caQTL peak：`chr22-39351520-39352777`，最强 `l1.PBMC`, **p=8.079e-218**, beta=1.2064
- 同一caQTL peak在NK、CD8 T、B等多个免疫谱系中也非常强。

这形成了比当前“RPL3–PDGFB”标签更值得测试的**SYNGR1 target-competition hypothesis**。但必须强调：这仍只是lead-level marginal tractability，**不能替代区域fine-mapping、GWAS↔eQTL/caQTL colocalization或正式peak→gene link**。

### 2.4 BCL11A暂时降级，不代表否定

当前GRCh38 BCL11A区间约为chr2:60,450,520–60,553,924，而lead rs2540100为chr2:59,523,629，距离基因起点约0.93 Mb。若使用固定±500 kb区域，天然可能漏掉BCL11A本体。因此BCL11A更像一个**long-range/distal regulatory locus**，不适合继续作为第一轮接口烟雾测试的主要对象。

## 3. 新的三位点优先级

|   priority | locus                                       | current_grade                                       | role_next                                                                              | main_risk                                                                                                                                                         |
|-----------:|:--------------------------------------------|:----------------------------------------------------|:---------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|          1 | IRF4                                        | C2/C3 only; C1 not testable                         | cross-resource discordance diagnostic; primary disease-coloc smoke locus               | TenK10K strong B-naive signal is not reproduced nominally in FinnGen B-naive; could be resource/context/power or false target assignment                          |
|          2 | chr22 RPL3–PDGFB region / SYNGR1 competitor | C1-proximal molecular tractability, not C1 evidence | target-reassignment smoke locus: test SYNGR1-centered eQTL+caQTL shared disease signal | extreme marginal association at the lead does not prove shared causal signal; PDGFB/RPL3/SYNGR1 competition requires regional fine-mapping and peak-gene evidence |
|          3 | BCL11A                                      | structural/distal unresolved                        | defer until long-range region/LD/peak-gene access is established                       | lead is ~0.93 Mb from current GRCh38 BCL11A interval; ±500 kb window can structurally miss BCL11A and create false negative                                       |

## 4. 为什么现在还不能进入R4B

R4B至少需要以下四个硬条件同时满足：

1. male/female SSc区域GWAS真实字节可用，而不是论文中的lead table；
2. GWAS与molQTL统一build、REF/ALT、effect allele，并完成indel规范化与palindromic/strand QC；
3. 每个测试区域具有足够完整的eQTL、caQTL、fine-map/LD或可信替代输入；
4. 至少一个位点完成真正的signal-level疾病共定位并达到预冻结C1门槛。

## 5. R4A2后最值得守住的论文创新点

论文不应再以“sex-specific SSc loci + functional annotation”为创新点，因为2026年原GWAS已经做了较丰富的功能注释和药物再利用。更有价值的新命题应收窄为：

> **sex-specific SSc risk loci是否通过population-scale immune multiome中的variant→chromatin→gene调控级联发挥作用，并且能否在SSc疾病组织中得到正交验证？**

其中chr22位点还形成一个更尖锐的可证伪问题：

> **传统RPL3–PDGFB区域标签是否掩盖了SYNGR1这一更直接的免疫细胞分子QTL候选效应基因？**

## 6. 下一阶段

进入 **R4A3：Dual-locus Access & Signal-level Smoke Gate**，只并行推进IRF4与chr22，不先下载/分析全部疾病组织。

- Track A IRF4：解决TenK10K B-naive高PIP与FinnGen B-naive弱精确pair之间的不一致；
- Track B chr22：对SYNGR1 eQTL + caQTL peak进行区域级shared-signal检验与target competition；
- BCL11A：仅在前两条技术链跑通后，用扩大区域/长程调控策略恢复。

**R4A3通过条件：至少一个位点建立可信C1 regulatory cascade，且技术链可重复。**
