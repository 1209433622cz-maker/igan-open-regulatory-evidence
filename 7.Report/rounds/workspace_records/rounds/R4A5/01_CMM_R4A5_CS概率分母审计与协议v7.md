# CS 概率分母审计与统计协议 v7

本文件为看过数据后的透明修订，不是事前注册。

## 附件核验

R4A4 ZIP CRC通过；内部13项SHA256全部通过。ZIP未正确设置Unicode文件名标志，读取时出现CP437乱码。本轮通过可逆的CP437字节→UTF-8解码恢复中文文件名，内容字节不变；原名、恢复名、内容哈希均保存于import_log.json。不得因此误判科学文件损坏。

TenK10K完整原始CS ZIP独立重算736条候选成员，全部与附件匹配。这里的资源独立指不同数据资源，未额外证明参与者绝无重叠；11种细胞不是11个独立队列。

## 完整 NK credible set

|FinnGen l2.NK caQTL CS1成员|源prob|是否进入TenK10K NK SYNGR1 CS4|
|---|---:|---|
|22:39343182:C:T|0.747095901121027|否|
|22:39351666:T:A|0.200617313138762|是，PIP0.5|
|22:39351775:G:A|0.052286785740211|是，PIP0.5|

该CS源prob总和=1；交集质量=0.252904098878973。l1.NK相应交集质量0.223482214059129。这里的求和只描述源CS记录，不是PP4，也不是新算法的共定位概率。不能把概率乘积或两个CS编号对应直接当共定位；两资源的CS编号没有跨研究语义。

TenK10K两个成员概率各0.5提示该CS在这两个成员之间不能唯一分辨，但不能不经LD验证就断言r²=1。它们都是SNP，坐标/REF/ALT精确匹配比仅rsID接近更有价值，但完整build和参考校验尚待完成。

FinnGen的高PIP汇总变异仍值得保留；应逐细胞报告。CD8 TEM target peak CS1为单成员39351775，概率0.988388537；这属于CD8 TEM caQTL证据，不替代NK caQTL概率。RPL3无CS记录不等于生物阴性；PDGFB位置分离不等于已验证信号独立。

## v7 判定

- 分子描述层：EXACT_CS_OVERLAP_CONFIRMED；保留source peak→gene link及强边际关联。
- 分子共享信号层：NOT_TESTED；需完整信号模型、LD、覆盖、先验敏感性。不能凭集合相交自动提升为强共定位。
- 疾病层：female/male NOT_TESTED；overall仅用于工程验证，另列状态。
- C1仍要求疾病↔eQTL、疾病↔caQTL、QTL↔QTL coherence、peak link、同细胞和技术QC。此前PP4阈值不能代替输入有效性。
- 不预设SYNGR1必须胜出；保留有界候选竞争，不能把SYNGR1 >>>其他基因当作已经确定的疾病因果排序。
- all-8 rescue仍需双位点充分数据检验后触发；缺失输入不是阴性，不触发救援或组织验证。

创新性方面：本轮核实2026肺免疫细胞QTL论文存在，但未完整审计其补充表的SYNGR1覆盖，不把“尚未在摘要看到”当首次发现依据。后续新颖性主张需要基因/位点/细胞/信号层面的补充表排查。

来源：R4A3/evidence/chr22_caqtl.response，R4A1/raw/tenk10k/susie_summary.zip。计算及所有CS分母见R4A5/results/audit.json。
