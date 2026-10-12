# R4A7 详细行动记录与 R4A8 下一阶段目标

## 本轮执行

1. 对用户再次上传的R4A5四份MD与ZIP做SHA256逐项比较：5/5与此前归档完全相同，因此未当作新版本。
2. 沿用R4A6已冻结的GCST009131=GRCh37、signed-Z可工程使用、female summary未获得等状态。
3. 直接从472,336,600字节真实GCST009131源文件提取IL12RB2和ULK3各±500 kb区域；使用固定效应P与OR方向重建signed-Z，A2保持原始?。
4. 对两个区域计算variant数量、P<5e-8/P<1e-5计数、最强变异、显著信号跨度和top20。
5. 通过历史SSc IL12RB2文献和独立ULK3附近公开summary对少量关键rsID做allele/position sanity control；没有把这些文献值批量填入GWAS。
6. 核验1000G Phase3 GRCh37与EUR PLINK公开镜像的bed/bim/fam文件、大小和MD5；当前运行环境未能取得大二进制文件，因此不伪造LD。
7. 核验UCSC hg19→hg38 chain公开来源；不在缺少本地字节时声称已完成liftOver。
8. 复查2026 female GWAS公开状态；未取得可归档summary bytes。

## 本轮新增判断

- IL12RB2成为primary engineering positive control。
- ULK3降为secondary complex-locus stress test。
- A2恢复规则已冻结，但production恢复尚等待真实reference bytes。
- LD阻断已从“不知道资源”缩小为“已冻结1000G EUR资源、尚未materialize”。

## R4A8

### R4A8A — Local reference materialization
获取并校验1000G_EUR.bed/bim/fam；先在IL12RB2窗口完成A2恢复和variant intersection。

### R4A8B — LD smoke gate
计算IL12RB2 signed-r矩阵并完成z-LD诊断；通过后运行SuSiE-RSS并核对历史rs3790566/rs3790567 LD结构是否方向合理。

### R4A8C — Complex locus stress test
仅在A8B通过后对ULK3区域重复，以检查多信号与窗口敏感性。

### Disease-anchor watch
female summary一旦出现真实accession/file，立即停止继续扩overall工程分析，切入chr22/SYNGR1 disease gate。

## R4B解锁条件不变
至少一个完整C1 + 技术QC PASS。当前仍不满足。
