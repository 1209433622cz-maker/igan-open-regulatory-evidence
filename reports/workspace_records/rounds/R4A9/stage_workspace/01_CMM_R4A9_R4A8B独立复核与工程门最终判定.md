# CMM R4A9：R4A8B 独立复核与工程门最终判定

日期：2026-09-10

## 1. 审计目的

R4A8B 使用自写 Python BED 解码器生成 1000G EUR 剂量与 signed-LD。若随后 RSS 失败，必须先排除参考来源、样本选择、BED 解码和效应等位基因方向错误。本轮没有简单重跑原脚本，而是用 PLINK2 作为独立实现导出全部剂量，再比较矩阵。

## 2. 源参考的可追溯性

完整源文件：`ALL.chr1.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz`。

| 项目 | 实测值 | 外部公布值 | 判定 |
|---|---|---|---|
| VCF bytes | 1,216,886,729 | 约 1.2 GB | 一致 |
| VCF MD5 | `609b38c12de89175b3d85c1588e4905c` | `609b38c12de89175b3d85c1588e4905c` | PASS |
| VCF SHA-256 | `ae0eb80ea07c19033332d17de28fb05128a3f5778d9e16dc8eadcab7e3c21987` | 本轮本地冻结 | 记录 |
| 原始 TBI MD5 | `5fa609a13f662d7abacfb6f2dc208410` | `5fa609a13f662d7abacfb6f2dc208410` | PASS |
| 原始 TBI SHA-256 | `08f3d07bcbb0df60ed8054e077d293bae9b21af5a39881e97bf09433cc41dc54` | 本轮本地冻结 | 记录 |

外部校验源为 [Zenodo record 3359882](https://zenodo.org/records/3359882)。VCF header 指向 `hs37d5.fa.gz`，因此该分支为 GRCh37。

这个结果证明完整 v5a chr1 VCF 的字节来源与 Zenodo 记录一致。区域 EUR503 BED/BIM/FAM 是由该 VCF 重新派生的分析资产；不能把它写成与其他 Zenodo 预制 PLINK 包逐字节等价。

## 3. EUR 样本与区域 VCF

- 官方 panel 总人数：2,504。
- `super_pop=EUR`：503。
- panel 中 EUR 顺序 = `EUR.samples` 顺序 = FAM IID 顺序 = 区域 VCF sample columns：精确相同。
- 区域：GRCh37 chr1:67,306,207–68,306,207。
- 区域双等位 SNP：27,067。
- 区域 VCF 的 CHROM/POS/ID/REF/ALT 与 `IL12RB2_variant_manifest.tsv`：27,067 行逐行相同。
- 缺失 rsID：0；重复 rsID：0。

## 4. 区域 VCF、BED 与第三方剂量解码交叉验证

独立工具为 `PLINK v2.00a3 SSE4.2 (18 Feb 2022)`。对 `IL12RB2_order.tsv` 的 1,555 个变异生成 `--extract` 和 `--export-allele` 文件，强制 PLINK2 按每个 GWAS A1 导出剂量。

除 PLINK2 导出外，本轮还直接解析区域 VCF 的 503 人 GT 字段，按每个变异的 REF/ALT 与 GWAS A1 将基因型转换为 A1 dosage。结果：

- PLINK2 `.raw`：503 样本 × 1,555 变异。
- 区域 VCF GT→A1 dosage 与 PLINK2 BED→A1 dosage：`503 × 1555` 全矩阵最大绝对差 `0.0`，差异单元 0，缺失模式一致。
- 1,555 个列头的 counted allele 全部等于冻结 GWAS A1。
- PLINK2 样本顺序与 FAM 完全一致。
- 缺失基因型单元：0。
- PLINK2 剂量与 R4A8B 自写 BED 解码剂量最大绝对差：`0.0`。
- 差异大于 `1e-12` 的单元：0。

因此 1,555 个保留变异的区域 VCF→BED、BED 解码、BIM allele1/allele2 处理及 GWAS-A1 翻转全部通过独立实现检查。源 chr1 VCF 的字节 provenance 已由官方 MD5 关闭，但本轮没有从该完整 VCF 重新派生全部 27,067 个区域基因型；结论限定在已审计的 retained-variant engineering path。

## 5. signed-LD 独立复算

用 PLINK2 导出的 A1 剂量和 `numpy.corrcoef` 计算相关矩阵，不复用 R4A8B 的标准化矩阵乘法实现。

- 独立 LD 与冻结 LD 最大绝对差：`6.994405055×10^-15`。
- rs3790566/rs3790567：`r=0.994613984366635`，`r²=0.989256977897672`。

该误差为浮点计算级差异。R4A8B 的 signed-LD 工程门最终判为 `PASS_INDEPENDENTLY_REPRODUCED`。

## 6. RSS 门复算

以冻结 z、signed-LD、`n_engineering=26679` 和 susieR `0.14.2` 独立运行 `estimate_s_rss` 与 `kriging_rss`：

| 指标 | R4A9复算 | 预冻结阈值 | 判定 |
|---|---:|---:|---|
| variants | 1,555 | — | — |
| `estimate_s` | 0.191784922366631 | ≤0.1 | FAIL |
| max |z_std_diff| | 5.36142564359804 | ≤5 | FAIL |
| 与原 kriging 最大绝对差 | 4.88×10^-15 | <1×10^-10 | PASS复现 |

`N_STUDIES=14` 的 134 个变异中 `estimate_s=0.00296319947`、最大 residual `4.02464071`。全体 residual 与 `N_STUDIES` 的 Spearman rho 为 `-0.167421375`，p=`3.06×10^-11`；`N_STUDIES≤5` 的平均绝对 residual 为 `1.03674`，高于其余变异的 `0.605951`，单侧 Wilcoxon p=`6.04×10^-17`。

这些结果支持“变异依赖的 cohort/sample composition 是协方差错配的重要来源”，但 `N_STUDIES` 只是代理量，不能证明唯一原因。高覆盖子集只作根因诊断，不能作为过滤后强行通过 SuSiE-RSS 的依据。

## 7. 终局结论

- Source VCF provenance：PASS。
- EUR sample selection/order：PASS。
- Regional VCF/manifest：PASS。
- 1,555 retained regional-VCF GT↔BED A1 dosage：PASS。
- BED decoding and GWAS-A1 dosage：PASS。
- signed-LD：PASS。
- 2019 overall public meta-summary RSS compatibility：HOLD。
- SuSiE-RSS：NOT_RUN。
- 工程管线可复用；当前 2019 public summary + external LD 组合不能产生 paper-grade credible sets。

机器可读结果见 `repro/R4A9_independent_reference_ld_audit.json` 与 `repro/R4A9_independent_rss_gate.json`。
