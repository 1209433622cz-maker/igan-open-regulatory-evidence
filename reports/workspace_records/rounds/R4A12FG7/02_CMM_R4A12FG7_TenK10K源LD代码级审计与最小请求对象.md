# CMM R4A12FG7：TenK10K source-LD 代码级审计与最小请求对象

## 1. 公共代码给出的直接答案

TenK10K effector-gene v3 workflow 的 `coloc.smk` 定义 `make_ld_eqtl`：对每个染色体、以100 kb为窗口生成eQTL LD目录。对应 `make_ld/eqtl/tenk10k_phase1.R`：

- 将所有cell的eQTL `(gene, snp)` 合并去重；
- 从 `resources/genotypes/tenk10k_phase1/chr{chr}` PLINK genotype读取；
- 对每个gene用 `plink --r square` 生成signed correlation；
- 通过 `--a1-allele` 固定MarkerID中的allele-1；
- 输出prefix为 `{LD_DIR}/{gene_name}`。

`run_multivariant_coloc.R` 随后按gene读取 `{gene_name}.bim` 和 `{gene_name}.ld`，并将该LD用于各biosample的SuSiE/coloc。

因此 **LD是per-gene、不是per-cell**。四个预注册细胞（NK、CD8_TEM、CD4_CTL、CD4_TCM）理论上共享同一原生IL12RB2 LD矩阵。

## 2. IL12RB2最小请求对象

优先直接请求原管线派生物：

`resources/ld/eqtl/tenk10k_phase1/chr1/ENSG00000081985.bim`

`resources/ld/eqtl/tenk10k_phase1/chr1/ENSG00000081985.ld`

请求**native/untruncated**版本，不要求作者按我们891或1366列表重新裁剪。收到后由本地validator再做交集。

## 3. 为什么优于直接申请WGS

- 与原论文SuSiE/coloc的LD完全同源；
- 不涉及个体级基因型；
- 文件量预计远小于WGS；
- 避免再次选择外部reference；
- 可先用公开eQTL z重现source SuSiE credible sets，再允许疾病整合。

## 4. 仍然不能提前宣称什么

即使得到该LD，也只解决eQTL侧source-matched LD。FinnGen disease侧仍是external-LD问题；因此FG8首先是**source-SuSiE复现 + fixed sensitivity adjudication**，不是自动升级C1。
