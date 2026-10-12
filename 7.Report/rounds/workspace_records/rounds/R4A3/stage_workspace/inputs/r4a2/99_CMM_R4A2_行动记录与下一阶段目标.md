# CMM R4A2：行动记录与下一阶段目标

## 本轮目标

对YR1/R4A1进行独立复核，不沿用其结论自动推进；判断三个位点是否需要重新排序，并决定是否可以进入R4B。

## 已完成

1. 解包YR1并核对R4A1目录结构；
2. 读取state、source manifest、locus status、TenK10K SuSiE、FinnGen exact-lead marginal/CS表；
3. 独立重跑关键表格汇总；
4. 复核YR1自带6项测试结果；
5. 对checksums逐项做字节哈希核对；
6. 发现根目录01报告缺失，但其余7份root MD内容哈希匹配；
7. 识别SuSiE transfer cache造成的release体积冗余；
8. 独立确认IRF4为“cross-resource discordance diagnostic”；
9. 新发现chr22 rs66578187对SYNGR1 eQTL与同一gene-body accessibility peak呈极强lead-level双组学关联；
10. 将BCL11A重新定义为需要扩大region/长程调控处理的结构性位点；
11. 使用2026-09-08公开来源复核sex-specific SSc论文、FinnGen multiome public release及关键基因GRCh38坐标；
12. 冻结R4A2统计协议v4与C1门槛。

## 本轮没有做

- 没有伪造或补写缺失的R4A1原始01报告；
- 没有把FinnGen browser marginal p值升级成colocalization；
- 没有运行疾病组织scRNA/spatial；
- 没有因为拿不到sex-GWAS就切换到弱替代数据强行推进；
- 没有使用docking/WGCNA/ML来补偿核心遗传链的缺失。

## 当前状态

```text
PROJECT = SSc sex-aware regulatory cascade
R4A2 = COMPLETE
PROJECT_DECISION = CONDITIONAL_GO
R4B = HOLD
C1 = UNTESTED
PRIMARY_TRACKS = IRF4 + chr22/SYNGR1-competition
BCL11A = DEFERRED_DISTAL_LOCUS
NEXT = R4A3_ACCESS_AND_DUAL_LOCUS_SIGNAL_SMOKE
```

## 下一阶段：R4A3

### 目标1 — 解锁真实GWAS字节

优先只获取female SSc的两个区域：

- chr6 IRF4
- chr22 rs66578187 region

如果GWAS Catalog仍未能解析accession，则执行有边界的数据获取动作：GWAS Catalog技术/curation询问 + 对应作者数据请求。已有论文明确承诺公开，因此这是合理的数据接入纠错，不是另找替代分析。

### 目标2 — 解锁FinnGen正式molQTL输入

完成官方summary-statistics访问流程，归档：

- eQTL region
- caQTL region
- SuSiE fine-map
- peak-gene links
- CASCADE metadata

### 目标3 — 只跑双位点technical smoke

先完成：

`normalize → harmonize → region overlap → LD → SuSiE/credible sets → disease↔eQTL coloc → disease↔caQTL coloc → eQTL↔caQTL coherence → peak-gene → C-tier`

不允许在technical PASS前扩到33细胞全景图或SSc组织图。

## R4A3之后的决策树

### A. 至少一个C1

`GO_R4B_FULL_SEX_LOCUS_SCAN`

扩展到全部8个sex-specific loci；随后才启动SSc tissue validation。

### B. 只有C2

`EXTEND_BOUNDED_TO_ALL_8_LOCI`

一次性测试其余loci。若仍无C1，再重评SSc文章是否降级为target-prioritization而非regulatory-cascade稿。

### C. IRF4与chr22均阴性，但coverage充分

不能直接判SSc全项目NO-GO，因为三位点smoke不是全部8个位点。允许一次**bounded rescue：all-8 sex-specific loci**；禁止无限扩展到全基因组找漂亮信号。

### D. 持续数据不可得

`ACCESS_HOLD`。如果经过合理数据请求仍长期不可得，再回到R3备选疾病池比较Sjögren / MG，而不是用lead-only表格硬写。

## 对论文最有价值的潜在新结果

目前最值得争取的不是“再验证IRF4”，而是以下两种可证伪结果之一：

1. **IRF4 disease signal与TenK10K B-naive fine-mapped eQTL真正共定位**，解释跨资源不一致；或
2. **chr22 female-SSc disease signal与SYNGR1-centered eQTL/caQTL cascade共定位**，支持从“RPL3–PDGFB locus label”到“immune-cell effector gene”的证据驱动重分配。

第二种若成立，可能形成整篇论文最清晰的机制亮点。

## 下一阶段目标冻结

> **R4A3不是扩大分析，而是把两条最有价值的候选链跑到signal-level truth。**
