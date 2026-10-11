# CMM R4A.1B：下一阶段任务与验收标准

承接日期：2026-09-08。不是R4B，也不是自动定时任务。

## 唯一主目标

**获得可分析的SSc male/female区域统计，并检验IRF4–B细胞分子信号与疾病是否共享。**

本轮最强新证据是TenK10K B_naive中rs12203592的单变异可信集。这个结果可以确定下一步最值得取哪些数据，不能免除FinnGen与SSc的共享信号门槛。

续推进已取得FinnGen B系pmax=1区域slice，同pair在B_naive的P=0.6728。故新增优先问题是**核查跨资源不一致**。IRF4作为技术测试保留，完整C1成功率先验不再乐观外推；详细证据见06报告。

## 任务A：解除GWAS硬阻塞

优先使用作者或Catalog提供的真实accession/文件地址；请求草稿见04。接受完整区域文件作为烟雾测试输入，不强制先下载全基因组。要求male/female均有phenotype、ancestry、build、variant/allele、beta或OR、SE、P、N、频率/INFO（若有）及样本重叠说明。

交付：原始文件、SHA256、README/header、按sex的QC及区域完整性。若只有一个sex，明确另一sex缺失；技术探索可单独进行，但不能做两性差异结论。

## 任务B：IRF4区域分子输入

已有FinnGen B_naive、B_intermediate、B_memory及上层B的未按P阈值筛选浏览器slice；下一步核对源release完整性并补候选峰caQTL。保留CD4/DC作为预定义的上下文比较，不拿最显著的不同细胞强行复制。

同时需要：所有候选peak links、source SuSiE per-signal数据、必要LD/参考版本、gene/peak cis窗口定义、effect coding、donor N。完整molQTL输入不应局限于source-CS里的变异。

取得TenK10K对应pair的beta/SE、effect allele、regional summary；当前两个小包不能提供方向。只有必要时才扩大下载，并优先区域/分块提取。

## 任务C：正式统计前锁定检查

1. GRCh38参考验证、完整canonical key、相同等位归一与日志。
2. 冻结cell mapping，区分exact定义、lineage proxy与不可匹配。
3. 锁定locus/signal范围、LD版本/有符号顺序和可接受覆盖定义；关注低MAF与两性功效。
4. 冻结主模型、先验敏感性、三方signal一致性以及复制检验家族。
5. 有效SNP数和CS覆盖的分母来自完整来源，不从显著命中集合倒推。

## 任务D：IRF4-first执行

输出GWAS↔eQTL、GWAS↔caQTL、caQTL↔eQTL的信号级结果，保留全部H0–H4、signal IDs、变异集合、peak–gene定义和不确定性。区分两性的疾病关联比较与分子QTL性别交互，后者当前没有相应设计。

### 技术PASS

真实输入完整、字段和reference可校验、LD/variant顺序正确、模型收敛、source-ID可追踪、负结果能被明确分类。即便科学上不同信号，技术测试仍可PASS。

### 科学PASS

至少一条同细胞/相容信号的GWAS–caQTL–eQTL链及peak–gene关系满足C1候选门槛并经敏感性审查。单个eQTL PIP=0.9993不能替代此条件。

## 后续分支

| 结果 | 下一动作 |
|---|---|
| 仍缺GWAS或完整分子输入 | 保持HOLD；记录具体入口/字段阻塞，不反复写同一类概念报告 |
| 技术通过且有C1 | 完成BCL11A、indel兼容性检查后评估R4B；更新创新重复审计 |
| IRF4不同信号或低功效 | 如实报告；执行BCL11A扩展获取范围和chr22多基因检验，不能立即判全项目NO-GO |
| 3位点无C1但有可靠C2/C3、覆盖良好 | 条件性扩展8位点，再判定核心假说 |
| 充分覆盖/功效下3位点及扩展位点均缺疾病共享 | 评估生物学NO-GO或重构问题 |
| sex数据长期不能取得、overall真实链可行 | 单独记录PIVOT决策并重写主命题；不沿用sex-specific标题 |

## BCL11A和chr22的特别要求

BCL11A不能只下载lead±500kb；必须根据gene位置、TSS与source cis定义包含远距离候选路径，同时保留其他可能靶基因。

chr22先在同一FASTA下核验A>AT与dbSNP重复表示，再让所有eQTL/peak-linked候选竞争。SYNGR1/AL031590.1为本轮新增探索候选，应保留选择时间，避免事后假装预注册。

## 不提前开展的工作及原因

暂不开展大规模组织重算、空间定位、PheWAS和药物排序：遗传target尚未确定，下游结果无法替代上游共享信号。可以继续维护元数据，但不应将“有很多分析”当成论文已经具备核心发现。
