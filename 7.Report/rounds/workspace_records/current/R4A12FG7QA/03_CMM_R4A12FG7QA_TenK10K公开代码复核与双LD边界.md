# CMM R4A12FG7-QA：TenK10K公开代码复核与双LD边界

日期：2026-09-13

## 1. 冻结源码版本

- repository: `powellgenomicslab/tenk10k-effector-genes`
- ref: `v3`
- resolved commit: `ce21efd78798271f3cafa38c4a7fa0a1e4c5b89e`
- 本地保存了5个相关源码文件、tree和retrieval receipt及其SHA-256。

## 2. eQTL LD如何生成

`make_ld/eqtl/tenk10k_phase1.R`：

- 输入为 `resources/genotypes/tenk10k_phase1/chr{chr}`；
- 从所有细胞eQTL结果汇总 `gene, snp` 并读取MarkerID的第一个allele作为A1；
- 按基因的GRCh38 gene body ±100 kb运行PLINK `--r square --make-just-bim`；
- 输出一个每基因 `.bim/.ld`，并非四个细胞各一套LD。

代码按窗口选择该bfile中全部变异，没有显式 `--extract` 公共eQTL manifest。因此作者原生未截断矩阵可能包含1,366个公共eQTL变异之外的变异。v2 validator允许额外变异，但要求冻结1,366个全部存在。

## 3. 疾病GWAS LD是独立对象

`run_multivariant_coloc.R`分别执行：

- 从 `{gene}.bim/.ld` 加载eQTL LD；
- 从疾病研究的 `dir_bfile/chr{chr}` 即时生成GWAS LD；
- 只在eQTL结果、GWAS结果、eQTL BIM和GWAS BIM四者交集上运行SuSiE/coloc。

因此有两道独立工程门：

| 对象 | 来源 | 当前状态 |
|---|---|---|
| IL12RB2 eQTL LD | TenK10K source genotype / 作者派生对象 | 未收到 |
| SSc GWAS LD | 疾病研究匹配基因型 | 未满足source-matched门；EUR503仅为external reference |

即使TenK10K LD到达并PASS，也只能开始分子QTL侧source-LD复现和受限敏感性分析；在疾病侧LD没有充分依据前，不得把结果升级为“source-matched双侧正式multisignal coloc”。

## 4. 可观察事实与推断分开

公开源码能观察到 `{OUTPUT$ld}/{gene_name}.bim/.ld` 的生成规则。具体路径 `resources/ld/eqtl/tenk10k_phase1/chr1/ENSG00000081985.*` 是根据Snakemake规则推断出的预期对象；本轮没有在公共仓库观察到这两个文件本身。

