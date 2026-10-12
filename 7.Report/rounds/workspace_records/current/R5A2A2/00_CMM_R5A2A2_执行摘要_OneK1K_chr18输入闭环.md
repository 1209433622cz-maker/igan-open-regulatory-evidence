
# CMM R5A2A2 执行摘要：OneK1K chr18 输入闭环

日期：2026-09-14  
项目：Myasthenia gravis，EOMG vs LOMG  
阶段状态：`R5A2A2_COMPLETE_INPUT_GATE_PASS`  
下一阶段：`R5A2A3_CHR18_COLOC_ABF_SMOKE_AND_LD_TRIGGER = GO`

## 最终判定

R5A2A2 已把 chr18 / rs7239261 从“文件已经下载”推进到“可以启动信号级检验”的状态。OneK1K 10.34 GB raw cis-eQTL、980-donor genotype、pseudobulk 样本接口，以及 MG overall、EOMG、LOMG 三套同 build 疾病统计量全部通过字节、结构、等位基因和区域共同覆盖门。

关键输入规模如下：

- raw eQTL archive：`10,344,009,571` bytes，官方 MD5 `e42239480f40abd21f221c0d77c82cc3` 与实际值一致；
- 14 个 chr18 Parquet 共 `8,959,978` 个 QTL pairs；固定 chr18:59,005,046–61,005,046 区域有 `241,650` pairs、8 个 archive phenotype、71 个 cell–gene 组合；
- 三套 GRCh37 GWAS 分别得到 `3,854`、`4,153`、`2,596` 个可推断的 OneK1K BIM 匹配变异；三套共同变异为 `2,497`；
- 71/71 个 cell–gene 组合均有至少 `1,124` 个 EOMG∩LOMG∩QTL 共同变异，并且 rs7239261 在所有必要输入中存在。

因此，`INPUT_CLOSURE = PASS`，`SAMPLE_INTERFACE = PASS`，`ALLELE_INTERFACE = PASS`，`ABF_INPUT_GATE = PASS`。MG 主项目保持 `CONDITIONAL GO`。

## 科学边界

本轮没有执行 disease–eQTL colocalization，因此没有产生效应基因结论。PIGN/Mono_NC、KIAA1468/Mono_NC、ZCCHC2/CD4_NC 等只是窗口内最小 nominal eQTL P 的排序；rs7239261 本身在候选基因中的 eQTL P 也不能替代区域共享信号检验。TNFRSF11A 只在 5 个细胞类型中有可用表型，其他细胞的缺失属于不可测试，不能写成阴性。

下一阶段先对 3 个疾病表型 × 71 个 cell–gene 组合运行冻结的 coloc.abf smoke gate。LOMG 是主检验，overall MG 是疾病信号复核，EOMG 是亚型对照。只有出现共享信号或可解决的 H3/H4 歧义，才为相应 cell–gene 生成 source-matched LD 并进入多信号分析；否则 chr18 在充分覆盖下失败，并按既定顺序只转 chr5。
