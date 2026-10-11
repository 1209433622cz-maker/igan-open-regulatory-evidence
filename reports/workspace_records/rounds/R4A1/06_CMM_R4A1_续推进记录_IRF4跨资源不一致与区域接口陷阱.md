# CMM R4A.1 续推进：IRF4跨资源不一致与区域接口陷阱

日期：2026-09-08。本文件记录用户要求“继续完成之前中断的任务”后的补充执行，接续已有R4A.1结果；没有重启或覆盖历史研究。

## 1. 新发现改变了怎样的判断

**TenK10K中IRF4–naïve B的单变异CS很强，但FinnGen同一variant–gene–cell标签的nominal关联不显著。当前不能声称跨资源复制。**

这使IRF4从“最强外部分子候选”进一步变成“必须解释资源间不一致的首个技术/科学测试”。先前PIP结果本身没有失效，但对整个SSc项目的乐观外推需要降低。

## 2. 执行路径与可重复证据

从FinnGen公开前端的LocusZoom组件追踪其实际读接口：

`/api/cascade/region/eqtl/lz-multi/`

请求trait为ENSG00000137265；cell为l1.B、l2.B_naive、l2.B_intermediate、l2.B_memory；区域GRCh38 chr6:1–896321。

初始默认请求成功，却只返回P<0.05的关联，三个B系都没有lead。再次显式添加 `pmax=1` 后，返回1,386,684字节，出现此前被过滤掉的lead关联。

| FinnGen cell | 默认返回行数 | pmax=1返回行数 | 精确lead是否返回 |
|---|---:|---:|---|
| l1.B | 255 | 3,045 | 是 |
| l2.B_intermediate | 338 | 3,040 | 是 |
| l2.B_naive | 110 | 3,044 | 是 |
| l2.B_memory | 86 | 2,475 | 否 |

共11,604条variant–gene–cell nominal记录。四组CS轨道均为空；这表示本次源查询没有该gene的相应CS记录，不能当作整个区域没有任何调控信号。

**pmax=1去除了这个P值筛选，但仍不是“已证明完整的发布版”。** 浏览器可能存在预先筛选、源文件覆盖范围、缺失变异或其他服务层限制。需要release README/源manifest核对后才允许正式coloc。

原始响应：`R4A1/evidence/cascade_irf4_b_region_nominal.response`、`cascade_irf4_b_region_pmax1.response`。可复现清洗输出：`R4A1/results/finngen_irf4_b_region.tsv`及`finngen_irf4_b_region_qc.tsv`。

## 3. 同一lead的真实数值

variant：chr6_396321_C_T；gene：IRF4。

| FinnGen cell | 源beta | 源SE | nominal P | 源maf字段 |
|---|---:|---:|---:|---:|
| l1.B | -0.028770 | 0.033893 | 0.39597 | 0.027090 |
| l2.B_intermediate | -0.071005 | 0.046373 | 0.12573 | 0.027233 |
| l2.B_naive | -0.015405 | 0.036478 | 0.67280 | 0.027263 |

以上beta/SE按源值报告，效应allele语义仍要由release说明确认，不能只因键里ALT=T就认定beta是每T等位效应。B_memory未见lead，记录为此slice缺失，不给P=1。

相比之下，TenK10K B_naive对IRF4同lead的nominal P=1.27614e-10、CS大小1、PIP=0.9993086。当前小包没有TenK10K beta/SE，故不能计算两资源效应异质性或判定方向相反。

## 4. 允许与不允许的解释

允许说：同一variant–gene在TenK10K有强fine-mapping支持，而FinnGen同名naïve B细胞的该pair未得到nominal支持。

不允许说：FinnGen“证伪”IRF4；两资源已证明相反效应；两资源已复制；女性特异级联成立；项目因此NO-GO。

需要核查的解释包括：不同人群等位频率及功效、单细胞与单核表达检测差异、细胞注释、gene定量、模型/协变量和源variant QC。它们都是待检查原因，本轮没有证实任何一种。源maf约2.7%提示功效必须检查，但不能用它直接解释全部差异。

## 5. 新增回归检查

代码新增对默认阈值接口与pmax=1接口的成对测试：确认默认最大P<0.05、完整请求中最大P>0.99；确认lead从缺失变为P=0.6728；检查数组等长、variant ID唯一、P有效、SE正值。

这与前一轮rsID假阴性形成两类不同错误：

1. 查询标识符解析错误；
2. 浏览器默认统计过滤。

二者都不能被当作覆盖/生物学阴性，也都说明浏览器图形接口不能未经审计直接生成coloc输入。

## 6. GWAS独立summary服务补查

旧的 `https://www.ebi.ac.uk/gwas/summary-statistics/api/studies` 及其docs返回HTTP **410 Gone**。这说明旧服务不可用，不是目标GWAS文件缺失的独立证明。保留v2精确PMID查询0结果与GCST009131阳性控制作为当前最清楚的Catalog证据，不继续反复请求失效接口。

## 7. 本轮结束时的下一阶段目标

继续执行R4A.1B，目标顺序修订为：

1. 获取male/female SSc真实区域summary及对应metadata；
2. 获取TenK10K IRF4 B系beta/SE/方向定义及FinnGen同pair源级记录，审计跨资源不一致；
3. 取得IRF4 caQTL、peak links及可兼容的fine-map/LD输入，执行疾病共享信号检验；
4. 同步准备BCL11A远距离窗口和chr22多gene竞争，作为已限定的候选检查；
5. 只有技术与科学门槛通过后才判断是否扩展R4B。

IRF4仍是首个技术测试，已不应该被表述为“最可能成功形成完整C1”的确定性预期。若FinnGen该cell无可支持的eQTL，允许该路线降级或记录资源特异性；不能直接交换discovery/replication角色而不记录研究设计改变。

本轮未发送邮件、未提交申请、未创建自动化；请求草稿已就绪。详细总行动记录见99报告，最终科学状态见 `R4A1/R4A1_state.json`。
