# R4A7 EUR LD 接入与 SuSiE-RSS Readiness v9

## 已核验参考资源

1000 Genomes Phase 3最终数据基于GRCh37。Zenodo 6614170提供按superpopulation拆分的PLINK文件：EUR bed/bim/fam以及MD5。该镜像的fam公开内容为503行。

当前运行环境中能核验网页元数据/小文本，但大bed/bim没有成功materialize。因此：

**REFERENCE SOURCE = VERIFIED**

**REFERENCE BYTES = NOT PRESENT**

**LD = NOT_RUN**

不能把“存在下载地址”写成“LD已经准备好”。

## R4A8 LD硬门

1. bed/bim/fam MD5通过；样本数与预期一致。
2. 只保留EUR参考中实际存在且与GWAS唯一harmonize的双等位variants。
3. 计算的是signed correlation r，不是r²。
4. SNP顺序严格与z向量一致。
5. R矩阵对称；diag≈1；特征值/PSD检查通过，必要时仅做有记录的小数值修正。
6. 运行susie_rss前做z-LD诊断；如果外部LD明显不匹配，不为了得到CS而强行继续。
7. 第一测试窗：IL12RB2；通过后才测试ULK3复杂区域。

## Ensembl REST角色

Ensembl提供单variant和≤500 kb region的1000G population LD接口，适合小规模诊断和lead附近交叉检查；生产级多信号fine-mapping仍优先使用本地可冻结、可校验的EUR基因型panel。

## 结论

R4A7已把“LD不知道去哪取”变成“来源、build、文件、MD5都已冻结，只差真实字节落地”。这是工程阻断，不是统计阴性。
