# R7C3 全工作区文件规模与完整性审计

## 审计范围与方法

审计根目录为 `H:\SCI2\YR1`。盘点脚本记录相对路径、绝对路径、大小、修改时间、类型、扩展名、内容标题或结构摘要、公开边界和 SHA-256。大于 256 MiB 的 18 个研究文件由第二遍流式哈希补算；因此所有 49,565 个非 Git 内部研究文件均有完整 SHA-256。

对文本、Markdown、JSON、TSV/CSV、DOCX、XLSX、PDF 和 ZIP 进行结构或内容元数据检查。对于 ZIP 使用 `ZipFile.testzip()`；对于 GZIP 逐块解压到流末尾，以验证完整性而不是仅验证文件头。`.git` 内部对象、工具运行时和 QiTeng skill 不作为科研内容结论的来源。

## 数量和空间

| 分区 | 文件数 | 大小（GiB） | 主要内容 |
|---|---:|---:|---|
| `1_data` | 906 | 31.046 | GWAS、OneK1K、TenK10K、GJOKA、reference LD |
| `3_results` | 7,787 | 4.450 | QTL、LD、coloc、simulation、audit outputs |
| `9.Version` | 3,168 | 3.787 | 冻结快照、导入包、回滚版本 |
| `2_code` | 18,151 | 0.644 | Python/R/PowerShell 与本地依赖 |
| `tools` | 13,051 | 0.608 | 本地工具链，不属于论文产物 |
| `6_release` | 1,956 | 0.517 | 阶段发布包及 checksum |
| `5_manuscript` | 828 | 0.464 | 稿件、图、补充材料、WPS QA |
| `8.Reference` | 91 | 0.322 | 文献与参考附件 |
| GitHub worktree | 2,431 | 0.190 | 公共仓库及 `.git` |

按扩展名，`.gz` 为 14.29 GiB、`.bin` 为 5.34 GiB、`.parquet` 为 4.80 GiB、`.ld` 为 3.64 GiB、`.zip` 为 2.83 GiB、`.txt` 为 2.81 GiB。这一分布与项目的 GWAS/QTL/LD/模拟数据结构一致。

## 大文件身份

全部 18 个最初因大小跳过的文件已完成 SHA-256。关键字节身份包括：

- OneK1K raw eQTL archive：10,344,009,571 bytes，SHA-256 `63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea`。
- OneK1K 980-donor BED：1,305,096,628 bytes，SHA-256 `75a2ebd613b9c63b7a283722180aeef871d08490cb75ba1bce52deec6a19eb63`。
- 1000 Genomes chr1 VCF：1,216,886,729 bytes，SHA-256 `ae0eb80ea07c19033332d17de28fb05128a3f5778d9e16dc8eadcab7e3c21987`；canonical 与历史快照内容一致。
- PBC GRCh37 GWAS：373,673,109 bytes，SHA-256 `439aa72c59b876236de2b8172c443a447cefa6868ace535183cec8b758a05921`。
- OneK1K pseudobulk ZIP：376,109,718 bytes，SHA-256 `92b38f54e1dd77cdac6d1c814db30ff0e83eaff209825f020839402b90e027e5`。
- 根目录 `YR1.zip`：434,577,141 bytes，SHA-256 `662c0e82d061c33c7c10ed5efb0654ba161b4a3eb541ea86fd6ffc65d26817b1`。

完整 18 文件清单位于 `inventory/R7C3_large_file_hash_receipts.tsv`。

## 压缩与结构完整性

```text
ZIP targets    = 122
GZIP targets   = 4,211
PASS           = 4,333
FAIL           = 0
expanded bytes = 173,974,898,239
```

这证明当前研究用 ZIP/GZIP 均可完整读取。它不证明第三方数据的生物学正确性，但排除了截断压缩流和 CRC 损坏这一工程风险。

## 内容解析异常

盘点记录 293 个 FileNotFoundError，全部位于 `.qiteng_v03242_runtime/.../90_ARCHIVE/...` 的超长历史路径。它们属于技能运行时的嵌套旧快照，不属于数据、结果、稿件、报告或发布包。科研内容解析异常为 0。当前使用的 QiTeng v0.3.24.2 核心 skill 文件可读取且已用于本轮写作治理。

## 精确重复与清理边界

共有 11,375 个重复哈希组、28,893 个重复成员，理论重复占用 6,587,241,870 bytes（6.13 GiB）。主要来源包括：

- canonical data 与 `9.Version` 冻结快照；
- working results 与 `6_release` 发布包展开目录；
-本地稿件与 GitHub 公共副本；
- OneK1K BIM、QTL parquet、GJOKA LD 在不同阶段的冻结复制；
- WPS 渲染中间页和最终接触表。

这些重复不能按“空间浪费”统一处理。版本、发布、GitHub 和 canonical copy 承担回滚与可验证 provenance。本轮未删除文件。将来如需回收空间，只能先处理 `REVIEW_FOR_CANONICALIZATION` 组，并保留 checksum、release ZIP 和至少一个 canonical source。

## 未完成片段

22 个 `.part`/`.redownload` 共 426,460,399 bytes。最大的 `GCST90432157.h.tsv.gz.redownload` 与正式 `.gz` 字节和 SHA-256 完全一致，可作为后续人工清理候选。其余包括历史 TenK10K 分段下载、SSc 旧快照、64 MiB BAM schema 预检样本和小型缓存片段。它们均不进入当前论文主证据；本轮未删除。

## 磁盘状态

H: 卷健康状态为 `Healthy`，总容量约 1.024 TB，剩余 353,771,831,296 bytes。当前没有因为磁盘空间必须立即清理的压力。
