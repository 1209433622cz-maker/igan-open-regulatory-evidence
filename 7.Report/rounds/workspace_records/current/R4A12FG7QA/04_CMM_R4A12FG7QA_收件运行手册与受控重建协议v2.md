# CMM R4A12FG7-QA：收件运行手册与受控重建协议 v2

日期：2026-09-13

## A. 作者直接提供 `.bim/.ld`

将两个文件放到本地非公开工作目录后，在PowerShell运行：

```powershell
& 'H:\SCI2\YR1\2_code\06_intake\source_ld\RUN_VALIDATE_RECEIVED_TENK10K_IL12RB2_LD.ps1' `
  -Bim 'D:\secure\TenK10K\ENSG00000081985.bim' `
  -Ld  'D:\secure\TenK10K\ENSG00000081985.ld'
```

输出：

- `source_ld_validation.json`
- PASS时的 `ENSG00000081985.requested1366.bim/.ld`

只有JSON状态为 `PASS_SOURCE_LD_STRUCTURAL_GATE` 且进程返回0，才可触发FG8。HOLD返回2；输入或执行错误返回3。

## B. EGA受控VCF获批

在机构批准的Linux安全环境中安装/提供：

- Python 3、pandas、numpy
- bcftools、tabix
- PLINK 2
- PLINK 1.9
- GRCh38参考FASTA及索引

若安全环境允许conda/mamba，可用包内环境文件一次创建：

```bash
mamba env create -f tenk10k_source_ld_environment.yml
conda activate cmm-tenk10k-source-ld
```

环境文件提供Python、numpy、pandas、bcftools/htslib、PLINK 1.9和PLINK 2；参考FASTA和受控VCF不在环境包中。

把三个manifest和两个v2脚本复制到受控环境，在脚本目录运行：

```bash
bash build_il12rb2_source_ld_from_approved_vcf_v2.sh \
  /secure/EGAD50000002377/chr1.vcf.gz \
  /secure/reference/GRCh38.fa \
  IL12RB2_TenK10K_100kb_native_variants_1366.tsv \
  IL12RB2_four_cell_source_CS_manifest.tsv \
  IL12RB2_required_anchors.tsv \
  /secure/project/IL12RB2_source_ld
```

脚本会：截取GRCh38区域、规范化多等位位点、重建MarkerID、验证1,366个ID和allele pair、只提取冻结1,366个变异、生成signed r、调用严格validator并写checksum和工具版本。

## C. 数据治理

- 原始VCF、BED/BIM/FAM、LD及日志全部留在授权安全环境；
- 不得把受控产物复制到 `6_release`、`7.Report`、public或shared目录；
- 对外release仅包含代码、公共manifest、验证规则和允许披露的聚合统计结果；
- 重建产物标记为 `native-manifest reconstruction`，因为公共原代码对整个基因窗口取bfile变异，而v2受控脚本显式限制到冻结的1,366个公共eQTL变异。

## D. 与正式multisignal分析的关系

本手册只解决TenK10K eQTL LD。疾病GWAS LD仍需独立验收；不能因本脚本PASS而把 `R4B` 或 `C1_count` 改为阳性。
