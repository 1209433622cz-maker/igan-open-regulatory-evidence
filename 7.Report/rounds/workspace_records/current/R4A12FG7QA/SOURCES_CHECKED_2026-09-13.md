# R4A12FG7-QA 外部来源记录

核查日期：2026-09-13

## TenK10K公开代码

- Repository README: <https://github.com/powellgenomicslab/tenk10k-effector-genes/blob/v3/README.md>
- eQTL LD builder: <https://github.com/powellgenomicslab/tenk10k-effector-genes/blob/v3/workflow/rules/snakescripts/make_ld/eqtl/tenk10k_phase1.R>
- multivariant coloc: <https://github.com/powellgenomicslab/tenk10k-effector-genes/blob/v3/workflow/rules/snakescripts/coloc/run_multivariant_coloc.R>
- v3 resolved commit: `ce21efd78798271f3cafa38c4a7fa0a1e4c5b89e`

本地归档位于 `3_results/00_audit/R4A12FG7QA/tenk10k_public_code`。源码核查用于确认流程接口和LD来源；未把预期的IL12RB2派生文件路径误写为已公开下载。

## EGA

- Dataset `EGAD50000002377`: <https://ega-archive.org/datasets/EGAD50000002377>
- DAC `EGAC50000000931`: <https://ega-archive.org/dacs/EGAC50000000931>

页面核查到：GRCh38多样本VCF、1,925 samples、89 files、475.1 GB、需要Request Access；数据使用条件包括健康/医学/生物医学研究以及非营利、非商业使用限制。

