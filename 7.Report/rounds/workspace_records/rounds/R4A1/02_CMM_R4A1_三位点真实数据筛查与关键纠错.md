# CMM R4A.1：三位点真实数据筛查与关键纠错

日期：2026-09-08。性质：本地数据实测；不是GWAS共定位结果，不是完整级联PASS。

**续推进更新**：本文件的gene/lead筛查后，又取得FinnGen IRF4 B系区域数据。B_naive同lead–IRF4 P=0.6728，未得到与TenK10K相称的nominal支持；默认区域接口还隐藏P≥0.05记录。当前最终解释必须结合[06补充报告](06_CMM_R4A1_续推进记录_IRF4跨资源不一致与区域接口陷阱.md)，不能只引用本文件的TenK10K阳性结果。

## 1. 已执行的数据工作

- GWAS Catalog新版REST v2按PMID=41999721查询返回HTTP 200、`totalElements=0`。用GCST009131作阳性控制，API正常返回研究及full-summary地址。因此只能说“当前此API未索引到目标论文”，不能说数据全球不存在。
- FinnGen公开CASCADE浏览器的身份端点明确 `authenticationEnabled=false`。按前端实际调用的公开接口读取4个gene、3个lead及IRF4区域，并保存JSON响应。没有提交表单、代填身份或绕过登录。
- TenK10K gene-level包取得10,137,272字节，官方MD5匹配，ZIP CRC测试通过；逐个解析28份细胞文件。
- TenK10K SuSiE包取得59,669,579字节，官方MD5及ZIP CRC通过；逐个解析28份可信集文件。两包共69,806,851字节。
- dbSNP核查IRF4与indel参考表示；解析原GWAS Table 2核查性别交互。

完整URL、HTTP状态、字节及哈希在 `R4A1/evidence/` 和 `R4A1/source_manifest.tsv`。本报告所有结果可用 `R4A1/scripts/audit_data.py` 重建。

## 2. IRF4：一个可避免的假阴性，与一个值得追踪的B细胞信号

### 查询问题已实际复现并修复

`/api/cascade/variant/rs12203592` 返回empty，并声称没有该位置记录。

但dbSNP给出GRCh38 chr6:396321 C>T（同rsID另含C>G）；用精确键 `/api/cascade/variant/chr6_396321_C_T` 查询，得到14,348字节的真实分子关联结果。因此该返回文本不能当作“FinnGen未检测此位点”的证据。保留原空响应和成功响应作为回归测试夹具。

### TenK10K gene-level实测

| 细胞 | IRF4 top variant | 原始top nominal P | 原始gene ACAT P |
|---|---|---:|---:|
| B_naive | 6:396321:C:T | 1.27614e-10 | 1.49006e-7 |
| B_intermediate | 6:396321:C:T | 5.37617e-6 | 0.00562650 |
| B_memory | 6:396321:C:T | 6.08570e-6 | 0.00328399 |
| CD4_Naive | 6:396321:C:T | 1.16729e-5 | 0.01275933 |

这是“同一个疾病lead在外部资源中成为IRF4 top eQTL”的具体支持，优于仅引用黑色素细胞功能先验。但它不解决SSc区域共享、效应方向或染色质中介。

### SuSiE精细定位实测：本轮最强的新增分子证据

`susie_summary/B_naive_all_credible_snps.tsv` 中，IRF4（ENSG00000137265）的CS=1仅含 **6:396321:C:T一个变异，PIP=0.999308641371514**。它与原GWAS lead位置和T效应等位一致。

这比“top SNP重合”进一步支持该变异的IRF4表达调控作用，但PIP是TenK10K eQTL fine-mapping后验，不是SSc–eQTL的PP4。可信集名为1也仅在同gene、同cell内有意义，不可跨研究按CS数字相等合并。

本轮遍历SuSiE包所有细胞及基因，三个精确lead中仅上述IRF4 lead被命中；另两个lead未见于该包CS。后者不代表不存在QTL：CS包只包含可信集成员，且±100kb范围对BCL11A远端假说可能不适用。

IRF4在NK另有两个不同变异集（12与20成员），进一步提示“IRF4有eQTL”不应与“所有细胞共享rs12203592”混为一谈。

本轮gene-level筛查的26个可测试细胞中，7个通过探索性within-cell BH<0.05；ILC/MAIT未列出，不能写作不表达或无QTL。

### FinnGen不能被简单写成同一细胞复制

gene页面显示IRF4在部分细胞有gene-level QTL支持，但未列出gene top CASCADE variants。精确lead在CD4_T的IRF4关联P=0.1515、beta=0.043489；gene q却为0.003479。这两个统计量衡量的对象不同。

在DC该lead–IRF4 nominal P=0.0063797，在CD4_Naive为0.088498。B_naive的exact-lead top-feature摘要选中了其他基因；这不代表完整variant–IRF4 pair为阴性，也不允许将TenK10K naïve B信号与FinnGen CD4_T信号称为exact-cell replication。

**下一步**：保留IRF4-first，首先取得B_naive/B_intermediate/B_memory与对应FinnGen B系的完整variant–IRF4 stats及caQTL/peak links，和female/male SSc区域统计。预先报告不同细胞/平台之间的不一致，不能只挑最显著的细胞讲故事。

## 3. BCL11A：远距离归属不能用近端eQTL替代

GWAS lead为chr2:59523629 C>A。FinnGen返回该lead的nominal molecular records，但没有其CASCADE机制分类或CS细胞条目；top-feature主要涉及AC007381.1、AC007100.1。

BCL11A在源注释的gene区为60457194–60553654，距lead最近端933565 bp、最远端1030025 bp。旧±500kb获取窗口截至60023629，会漏掉候选基因本身。

此外，FinnGen BCL11A gene页面的强eQTL代表变异位于约60323570附近；TenK10K B_naive的top variant为2:60356067:T:C，nominal P=2.76134e-17。这一TenK10K变异距GWAS lead 832438 bp。**强BCL11A eQTL存在，并不代表解释了rs2540100疾病信号。**

TenK10K ±100kb包还可能根本不覆盖远离BCL11A的疾病lead；不能把“同gene在两个队列有eQTL”作为该远端信号复制。

**下一步**：获取范围扩展至lead、gene及源cis定义的联合范围；分别核查lead→BCL11A、lead→其他转录本和远处BCL11A eQTL的LD/信号关系。扩大的是数据检索范围，不是事后为阳性调统计窗口。

## 4. RPL3–PDGFB：应扩充候选，而非锁定PDGFB

源返回规范化样式 `chr22_39328807_A_AT`，与原论文效应等位AT相容。dbSNP的SPDI以39328808处重复T描述事件；尚需同一FASTA下本地normalization验证。

该lead在FinnGen可见eQTL/caQTL CS成员条目，包含：

- `l1.Mono`：AL031590.1，PIP≈0.0292；
- `l1.other`：SYNGR1，PIP≈0.0175；
- 多个细胞中的caQTL峰，PIP多数较低。

在nominal记录中，lead–SYNGR1可出现很强关联，例如CD8_T P=5.7834e-69。低P与低PIP并不矛盾：前者说明关联，后者反映同一LD区域内对具体变异的定位不确定性。

PDGFB gene页面代表variant为chr22_39237617_C_T（距疾病lead 91190 bp），源模式是`caQTL + eQTL (no link)`，不是完整级联。没有计算LD或SSc共定位，不能把这条gene-level事件归到疾病lead。

**下一步**：RPL3、PDGFB仍保留；SYNGR1、AL031590.1作为本轮结果导出的探索候选加入，之后按所有真实peak/eQTL links扩充候选全集。不能以纤维化生物学偏好排除其他基因。

## 5. TenK10K基因级覆盖总览

分母是28份实际文件。“有效测试”表示该gene有数值ACAT_p；“显著”是本轮按各细胞文件内所有有效gene重新BH后的探索性结果，不是确认性复制。

| Gene | 有效测试细胞 | 探索性BH<0.05细胞 | 解释 |
|---|---:|---:|---|
| IRF4 | 26 | 7 | 同lead的B系eQTL值得优先检查 |
| BCL11A | 14 | 5 | 远距离疾病lead能否被本包覆盖未解决 |
| RPL3 | 27 | 9 | 基因QTL不等于疾病信号 |
| PDGFB | 11 | 9 | 表达覆盖有选择性，不能把未列出视作阴性 |
| SYNGR1 | 20 | 18 | 本轮新增探索候选 |
| AL031590.1 | 16 | 11 | 本轮新增探索候选 |

没有任何一行可以直接解释为“疾病causal target”或“独立级联已复制”。

## 6. 真实schema问题

TenK10K压缩包内文件后缀是`.tsv`，实际使用**逗号分隔**。header仅四列：`gene,ACAT_p,top_MarkerID,top_pval`。强行按制表符读取会得到错误单列。

尾部存在 `convergence_failure`、`no_variant_in_window` 字符串，不能强制数值转换后当作P=1、P=0或静默删除。已逐文件记录失败数量/标签。该包缺beta、SE、效应等位定义和区域全量统计，因此不能判方向或运行coloc。

SuSiE文件同样是逗号分隔，六列为 `SNP,Index,PIP,Credible_Set,gene,celltype`，没有beta、SE、完整Bayes factor或LD。因此两小包加在一起仍不能完成方向复制或独立运行多信号coloc。

本轮脚本还保留实际JSON中的null情况；例如gene页面 `marginal_per_ct=null`，不能假设每个gene都有相同嵌套结构。

## 7. 当前结论

三个locus均已进入真实分子证据筛查，仍无SSc区域共定位结果。最有价值的进展是：IRF4查询假阴性修复、IRF4同lead外部eQTL支持、BCL11A获取窗口修订、chr22多靶基因证据。

状态：`DESCRIPTIVE_MOLQTL_SCREEN_COMPLETE`；`SSC_COLOCALIZATION_NOT_COMPUTED`；`R4B_HOLD`。

## 来源

- [GWAS Catalog查询](https://www.ebi.ac.uk/gwas/rest/api/v2/studies?pubmed_id=41999721)；[阳性控制GCST009131](https://www.ebi.ac.uk/gwas/rest/api/v2/studies/GCST009131)
- [IRF4源浏览器](https://cascade.finngen.fi/gene/IRF4)、[BCL11A](https://cascade.finngen.fi/gene/BCL11A)、[PDGFB](https://cascade.finngen.fi/gene/PDGFB)
- [IRF4精确variant源JSON](https://cascade.finngen.fi/api/cascade/variant/chr6_396321_C_T)、[chr22 lead源JSON](https://cascade.finngen.fi/api/cascade/variant/rs66578187)
- [TenK10K Zenodo](https://zenodo.org/records/18221260)
- [dbSNP IRF4](https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/12203592)、[dbSNP indel](https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/66578187)
