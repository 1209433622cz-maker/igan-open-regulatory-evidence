# CMM R4A.1：统计协议修订 v3

2026-09-08。此文件是有版本记录的修订，原R3/v1及R4A/v2不覆盖。本轮已看过描述性筛查结果，以下新增规则不能冒充“在任何结果之前预注册”；正式确认性分析前应锁定版本、参数和检验家族。

## 1. 可运行输入不等于可定位的来源

每个数据产品同时记录 `access_state` 和 `analysis_scope`。已下载gene-level CSV可用于presence/ACAT筛查；浏览器JSON可用于source-result审计；仅含CS/PIP的文件可用于CS成员检查。它们都不自动成为完整区域coloc输入。

运行 `coloc.susie` 需要可兼容的SuSiE对象/每信号Bayes factor，或完整区域beta、SE及顺序一致、祖源匹配的有符号LD矩阵以重新拟合。只有95% CS内的PIP不能重建CS外质量或替代全部likelihood。

缺少主GWAS时，`PP.H4` 写为缺失、状态写 `NOT_COMPUTED`，不能填0，更不能根据单SNP重叠生成后验概率。

## 2. 标识符和坐标

统一主键 `chr:pos:ref:alt@GRCh38`，同时保存raw id。IRF4实测证明：rsID endpoint返回空，而 `chr6_396321_C_T` 有数据；因此空rsID结果首先归类 `LOOKUP_FAILURE_UNRESOLVED`，交叉核对后才判断覆盖。

dbSNP对rs12203592提供多个ALT（C>G及C>T）；本项目论文效应等位T对应C>T，不能把整个rsID当双等位记录。NCBI SPDI的position为零基，不能直接拼接一基VCF key。

rs66578187：FinnGen源提供 `chr22_39328807_A_AT`；dbSNP以重复序列的SPDI表达该事件。两者需要参考序列规范化后比较；本轮只确认source allele representation，不宣称已经执行bcftools左对齐或FASTA REF校验。

若REF/ALT已通过同版本参考序列且方向由明确ALT定义，回文SNP可以可判向；只有坐标/等位链向不确定时才用频率排歧。禁止仅因看到A/T或C/G就删除所有已参考验证的记录。

## 3. 窗口必须区分疾病信号区与候选基因检索范围

IRF4初始窗口左端限定为1（396321−500000为负）。

BCL11A：源浏览器gene start 60457194，GWAS lead 59523629，差933565 bp；gene end 60553654，距lead 1030025 bp。原±500kb窗口甚至±1Mb简单窗口都不能保证覆盖候选完整基因/转录端点。

本轮仅修订**获取范围**：联合lead窗口、候选基因区及有文档依据的cis范围，记录各来源覆盖；最终统计区域依疾病LD/信号定义，不能把远处强BCL11A eQTL直接与lead假定为同信号。TenK10K ±100kb包对这条远距离假说可能结构性不覆盖；必要时取得±1Mb资源，但须核实它围绕TSS还是基因边界定义及实际包含该lead。

## 4. 证据粒度

以下项目禁止混列：

- 单个variant–gene/peak的nominal P、beta、SE；
- 聚合后的gene/peak级显著性或ACAT/FDR；
- CS成员、每信号PIP；
- 两性效应异质性、genotype×sex交互；
- region/signal-level共定位；
- peak–gene表达/可及性关联。

真实反例：FinnGen IRF4/CD4_T的该lead P=0.1515，同时gene q约0.00348。后者说明该gene有分子QTL支持，不能证明该lead显著。

浏览器输出常为每细胞“top feature”，不是该变异所有基因/峰的完整结果。未出现在top表中的IRF4/BCL11A/PDGFB不能判为没有关联。

续推进实测补充：区域LocusZoom接口默认返回P<0.05记录；必须显式请求pmax=1并检查返回最大P、精确lead和行数。去除P阈值仍不证明没有其他源/服务过滤，需要发布版覆盖清单审计。严禁把显著SNP子集直接输入coloc。

## 5. 性别主张的三级边界

1. **Sex-stratified association**：分别分析male/female疾病GWAS。
2. **Sex-differential disease association**：正式比较同一变异两性效应，优先使用原研究genotype×sex及异质性结果；需要明确检验家族。
3. **Sex-dependent molecular regulation**：需sex-stratified molQTL或genotype×sex分子模型。静态/sex-adjusted QTL不能达到第3级。

即使女性GWAS与某细胞QTL共定位而男性未共定位，也可能由男性功效不足造成。必须比较GWAS证据强弱和后验分解，不能用“一个PP4>0.8、另一个<0.8”直接证明女性特异机制。

源文献质量问题须保留：IRF4两性异质性在正文出现0.0009、Table 2为0.0090。本轮不选择更显著的版本，应向作者确认；三位点genotype×sex P分别BCL11A 2.14e-7、IRF4 0.0047、RPL3–PDGFB 0.049，不能以同等强度描述。原文已做交互，不应被误写成未做。

## 6. C1与三方链

C1仍要求GWAS–caQTL、GWAS–eQTL、caQTL–eQTL证据相容且有明确peak–gene。必须使用同一细胞上下文及可以串接的signal ID，不能把不同信号的三个高PP4凑在一起。

记录全部H0–H4、每信号配对、区域SNP数、共同变异比例及CS覆盖。强证据候选沿用PP shared≥0.8，并报告对先验的敏感性。若不同来源的模型/先验/输出量不同，不直接横向比较数值。

caQTL/eQTL可能来自相同donors和同一multiome样本：保留误差相关与样本重叠说明，评估所用方法的独立误差假设；同一样本的两种组学不算独立重复。

项目C1与官方CASCADE local/positional/distal等分类建立显式映射；官方“caQTL+eQTL(no link)”不升级为本项目完整链。

## 7. 复制和多重检验

本轮TenK10K筛查对每个cell文件内所有有效ACAT_p计算BH，失败/缺失单独计数。此BH是本项目的探索性重算，不称为作者原始q，也不称为预注册复制阈值。

等正式候选从FinnGen×GWAS冻结后，复制至少满足gene、预定cell correspondence、同一信号/可解释LD代理及可判定方向，按冻结的候选×细胞检验家族控制多重比较。原始小包没有方向时不能补猜。

gene筛查显示同一lead与同一gene关联，是具体的外部分子支持；尚未有主discovery疾病共享信号时，仍不叫“SSc级联已复制”。新增SYNGR1/AL031590.1来自本轮结果，应标exploratory，不能伪装成最初预定义靶点。

## 8. 阴性和分支

新增 `LOOKUP_FAILURE`、`NOT_LISTED`、`OUTSIDE_SOURCE_CIS_WINDOW`、`MODEL_NONCONVERGENCE`、`LOW_POWER`、`SOURCE_METRIC_AMBIGUOUS`。保持NO_QTL与QTL_DIFFERENT_SIGNAL的区分；只有有足够覆盖/功效的不同信号结果才较强反对目标假说。

目前SSc区域GWAS缺失，不能产生C1/C2/C3疾病等级，更不能计入生物学NO-GO。全量R4B继续HOLD。

## 来源及复现

- [原GWAS全文及Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212417/)
- [FinnGen CASCADE方法](https://cascade.finngen.fi/methods)、[数据说明](https://cascade.finngen.fi/data)
- [TenK10K原始数据包](https://zenodo.org/records/18221260)
- [coloc SuSiE说明](https://chr1swallace.github.io/coloc/articles/a06_SuSiE.html)

实际源JSON、网页和版本化前端说明已保存于 `R4A1/evidence/`；分析脚本与结果在 `R4A1/scripts/`、`R4A1/results/`。
