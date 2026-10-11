# R7C3 科学成果与可复用资产总账

## 当前论文的核心成果

### 1. PBC-wide 筛查与有边界的多信号重分类

冻结的 6,923 个 locus–gene–cell 比较中，5,460 个满足 ABF 覆盖门；642 个 `H3+H4 ≥ 0.80` 的高信息比较进入来源匹配多信号层。原始 184 比较继续作为 primary trigger-verification cohort，455 个 H3 比较构成对称 rescue/falsification layer，另有 3 个阈值边界 calibration cases。

PF10 主模型的 642 项终裁为 92 stable H4、428 stable H3，其余为 ambiguity、model-sensitive 或 uninformative。8 个历史 H4 转为 H3，10 个历史 H3 转为 H4，说明单向“验证阳性”会遗漏双向重分类。

### 2. 同输入方法对照

A0/A1/A2/M 设计把支持集合、疾病统计定义和剩余推断结构分开：

- A0→A1：15 个分类变化，反映实际 multi-signal 支持集合限制；
- A1→A2：19 个分类变化，反映疾病统计来源定义；
- A2→M：79 个 H4 与 413 个 H3 稳定，同时出现 8 个 H4→H3 与 10 个 H3→H4。

该结果支持“输入匹配后仍存在实质推断差异”，但不能把 A2→M 当作单因素实验或真值校正率。

### 3. 模拟校准

486 参数格、每格 1,000 次，共 486,000 次 primary matched-LD 模拟全部完成且无技术失败。distinct truth 下 false H4 从 12.41% 降至 8.56%；shared truth 下 H4 recovery 从 32.99% 降至 26.66%。因此可靠性提升伴随灵敏度代价，论文必须同时报告两者。

325,218 次迭代因至少一侧没有 credible set 而没有可评估 signal pair；160,782 次可进行 pair-conditional 评价。pair-conditional 指标属于发现成功后的估计器行为，不能与 ABF 的 unconditional 分母直接等同比较。

### 4. 生物学示例与证据边界

- IL12RB2–NK：OneK1K、TenK10K 和 FinnGen 分子 QTL 资源形成跨资源支持；FinnGen R13 × OneK1K 默认 PP.H4=0.9977，skeptical prior 为 0.9772。
- FinnGen R12/R13 disease credible set 高度稳定，17 个成员交集、Jaccard 0.895、lead 一致。
- IL12RB2-linked peak 同时具有 disease–eQTL 与 disease–caQTL 共享记录及 peak–gene link。由于缺少直接 eQTL–caQTL posterior 和 mediation estimate，仅能称 triangular signal coherence。
- FCRL3 B-cell 结果具有跨 molecular-QTL 支持；FCRL3/CD8_ET 是单信号支持在多信号/模型审计后不稳定的关键反例。
- 5 vs 5 donor liver 分析支持相关 lineage 中的可检测性，没有校正后 disease enrichment；OMIX001122 只有一例 PBC 和一例 control processed matrix，仅作描述性边界。

## 可复用方法资产

1. **Byte-level intake 与 provenance**：URL、size、MD5/SHA-256、字段、build、effect allele、压缩完整性、release/source identity。
2. **Variant harmonization**：GRCh37/38、rsID/position、A1/A2、palindromic ambiguity、effect/LD sign consistency。
3. **Source-matched LD**：disease study-derived LD、cell-active donor、covariate-residualized QTL LD、PF10/PF50 model identity。
4. **双向多信号重分类**：同时允许 H4→H3 和 H3→H4，保留 shared/distinct signal pair coexistence。
5. **同输入 A0/A1/A2/M**：支持集合、疾病统计与剩余模型差异的可审计拆分。
6. **Simulation discovery channel**：将 credible-set availability、pair-evaluable inference 与技术失败分开。
7. **Bounded external validation**：固定 gene/cell 后再接入不同疾病 study system、source CS 与多模态边，不重新 fishing。
8. **证据状态机**：PASS、HOLD、FAIL、FALSIFIED、UNINFORMATIVE、MODEL_SENSITIVE 与退出规则。
9. **发布工程**：checksum、ZIP CRC、machine QA、WPS full-page QA、GitHub release 和公开边界。

## 旧项目仍有价值的内容

- SSc 阶段保留 reference-LD、H6、source-CS coverage 与远端/局部调控鉴别工程；生物学主线继续冻结。
- MG 阶段保留 subtype heterogeneity、cell-specific donor LD、targeted source-LD 与“充分覆盖后停止救故事”的裁决框架。
- IgAN 阶段保留 positive-control correction、bounded expansion、cross-ancestry falsification 和 completion-first portfolio gate。
- 这些资产可用于下一篇疾病研究或方法补充，但不得回写成当前 PBC 稿件的新发现。

## 资产定位

机器可读总账为 `assets/R7C3_high_value_asset_ledger.tsv`，包含 26 类当前论文、核心数据、结果、方法、记录和版本资产。第三方大数据明确标为 `THIRD_PARTY_NO_REUPLOAD`；GitHub 只接收原创代码、聚合结果、稿件、图和去敏 provenance。
