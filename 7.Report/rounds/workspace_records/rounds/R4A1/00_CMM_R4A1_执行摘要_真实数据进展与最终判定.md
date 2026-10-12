# CMM R4A.1：执行摘要、真实数据进展与最终判定

日期：2026-09-08。项目：SSc sex-aware cell-resolved regulatory genetics。

## 最重要结论

**项目已从纯预检推进到真实分子数据筛查。TenK10K naïve B细胞中，IRF4的可信集仅含SSc lead rs12203592，PIP=0.9993086；但续推进取得的FinnGen同pair nominal P=0.6728，显示跨资源支持尚不一致。**

这值得继续追踪，但它是eQTL精细定位证据，不是SSc共定位。当前仍缺male/female SSc完整区域统计，以及支持正式信号分析的区域molQTL/LD或可兼容fine-mapping输入。

```text
R4A1 = PARTIAL_ACCESS_UNLOCK + REAL_MOLQTL_SCREEN_COMPLETED
TENK10K_MINIMAL_PACKAGES = ACQUIRED_AND_VERIFIED
FINNGEN_BROWSER_RESULTS = ACQUIRED_AND_PARSED
SEX_GWAS_FULL_REGIONAL_STATS = NOT_ACQUIRED
SSC_COLOCALIZATION = NOT_COMPUTED
C1_CASCADE = NOT_TESTABLE
R4B_FULL = HOLD
NEXT = R4A1B_GWAS_AND_REGIONAL_QTL_ACCESS_IRF4_B_CELL_SIGNAL_TEST
```

**不能把本轮称为完整R4A.1端到端PASS，也没有SSc生物学NO-GO证据。**

## 本轮真正完成了什么

| 工作 | 可核查结果 |
|---|---|
| 历史文件审计 | 22份输入逐项梳理；区分历史计划与本轮指令 |
| 54篇矩阵核查 | 54行、54唯一ID；年份4/37/13；当前目录缺少矩阵引用的54份逐篇MD，不沿用旧交付声明 |
| TenK10K下载 | 两ZIP合计69,806,851 bytes；官方MD5与ZIP CRC均通过 |
| 基因级解析 | 28细胞、403,011行；401,999个有效ACAT值、1,012条失败/无窗口标签 |
| SuSiE解析 | 28细胞、4,193,682行；提取6个主/探索候选的1,064条CS成员记录 |
| FinnGen实测 | 4 gene、3 lead与IRF4区域的结构化JSON；输出134条精确lead nominal记录、11条CS成员记录 |
| 补充区域查询 | 11,604条IRF4 B系nominal记录；发现浏览器默认P<0.05过滤，显式pmax=1后恢复lead记录 |
| 源追踪 | 40个response/数据产品纳入source manifest；保留错误响应，区分字节/结构/分析用途 |
| 验证 | 6项有针对性的测试通过：BH、缺失值、rsID假阴性、原始IRF4 CS、默认P过滤和科学状态边界 |

## 四个会改变下一步的发现

### 1. IRF4值得继续，但理由已从先验变为实际数据

TenK10K IRF4–B_naive：top nominal P=1.27614e-10；95% CS仅含6:396321:C:T，PIP≈0.9993。B_intermediate/B_memory也以同一变异作为gene-level top。

续推进后，FinnGen B_naive该pair的beta=-0.015405、SE=0.036478、P=0.6728；需要先核查效应定义、细胞映射与功效，再检验是否与SSc female/male区域信号共享。当前不能直接宣布跨资源复制。

### 2. rsID查询曾产生可验证的假阴性

FinnGen `rs12203592` 查询返回empty；dbSNP确认后用 `chr6_396321_C_T` 查询成功。已保留两个原始响应和回归测试。这使canonical key从纸面规范变成实际避免错误判定的措施。

### 3. BCL11A窗口需要修订

BCL11A gene起点距GWAS lead 933,565 bp，旧±500kb获取窗口会漏掉候选基因。强近端BCL11A eQTL并不自动解释该远端疾病lead；需要有记录地扩展获取范围，查清cis定义和LD。

### 4. chr22必须保留多靶基因竞争

rs66578187源表示为A>AT，已有SYNGR1及AL031590.1等分子证据。PDGFB gene页面代表的是另一个变异，并被标注caQTL+eQTL但无link。不能因为PDGFB符合纤维化故事就提前定靶。

## 当前硬阻塞与下一目标

GWAS Catalog官方v2按PMID查询返回0条studies；阳性控制正常。这个结果只说明当前Catalog查询未找到目标研究，不等于数据不存在。已准备Catalog和作者求助草稿，没有发送。

FinnGen浏览器入口已部分解除；完整release的nominal/fine-map/peak–gene和说明仍需取得。官方表单涉及真实申请人信息，本轮没有代填或提交。

**下一阶段：取得male/female完整区域GWAS和IRF4 B系区域molQTL，完成明确区分技术PASS与科学PASS的信号级检验。** 不先扩到8位点、全33细胞或大规模组织分析。

## 报告导航

1. [历史文件逐项审计与逻辑重构](01_CMM_R4A1_历史文件逐项审计与项目逻辑重构.md)
2. [三位点真实数据筛查与关键纠错](02_CMM_R4A1_三位点真实数据筛查与关键纠错.md)
3. [统计协议修订v3](03_CMM_R4A1_统计协议修订_v3_证据粒度与性别主张.md)
4. [数据接入报告与请求草稿](04_CMM_R4A1_数据接入报告与待办请求草稿.md)
5. [下一阶段任务与验收](05_CMM_R4A1B_下一阶段任务与验收标准.md)
6. [行动记录与复现质控](99_CMM_R4A1_行动记录与复现质控.md)
7. [续推进：IRF4跨资源不一致与区域接口陷阱](06_CMM_R4A1_续推进记录_IRF4跨资源不一致与区域接口陷阱.md)
8. [数据与代码说明](R4A1/README.md)

外部原始资源：[TenK10K](https://zenodo.org/records/18221260)、[FinnGen CASCADE](https://cascade.finngen.fi/)、[目标GWAS论文](https://pubmed.ncbi.nlm.nih.gov/41999721/)。本轮对科学主张保持“遗传支持的候选调控路径”，不写“证明性别特异因果机制”。
