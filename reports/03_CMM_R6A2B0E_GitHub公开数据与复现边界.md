# R6A2B0E GitHub 公开数据与复现边界

日期：2026-09-14

公共仓库：<https://github.com/1209433622cz-maker/igan-open-regulatory-evidence>

## 公开仓库纳入内容

- 冻结协议与 8-locus manifests；
- Python/R/PowerShell 执行代码；
- 小型派生结果表、机器判定 JSON 和图；
- R6A2A1 正控结论与本轮报告；
- 软件环境、运行顺序和校验说明；
- 大文件下载 URL、字节数、MD5/SHA-256 和期望本地相对路径。

## 不提交到 GitHub 的对象

- OneK1K 10.34 GB full cis-eQTL archive；
- 980-donor PLINK genotype；
- 三套 376–492 MB IgAN GWAS；
- donor-level genotype/dosage 和 LD 矩阵；
- 原始单细胞表达对象；
- 任何受限、需申请或作者请求数据。

这些文件的公开来源与校验信息保存在 `data/LARGE_DATA_MANIFEST.tsv`。仓库的 `.gitignore` 同时阻止 raw data、基因型、压缩大文件、矩阵和密钥类文件被误提交。

## 许可边界

仓库代码使用 MIT License。第三方数据继续受各自来源许可与引用要求约束；仓库不重新授权或镜像第三方原始数据。派生结果只包含公开 summary statistics 所产生的非个体级汇总值。

## 可复现层级

1. 无大数据：可查看冻结矩阵、结果、报告与图。
2. 下载三套 GWAS 和 OneK1K full cis-eQTL：可复现 549-test smoke matrix。
3. 再下载 OneK1K genotype 与 covariates：可复现 targeted source-LD 和 SuSiE-RSS。
4. TenK10K 仅在预定 signal gate 通过时进行定向复制，不在本轮公开代码中批量扫描。

远端验收结果：仓库为 `PUBLIC`，默认分支 `main`，发布基线 commit 为 `b72bdf1b8c992360b9fcd6cec79b16c5c6cb7a4b`；README 的 GitHub blob 对象已通过 API 读取。后续报告回填 commit 只改变发布元数据，不改变统计结果。
