# HRA008003 公开字节、called-cell 与肝组织门

## 公开输入

五个 PBC liver BAM 均可通过 GSA-Human 直接下载，合计 152,488,497,199 bytes（约 142 GiB）。官方 MD5 已与运行 manifest 5/5 对齐：

| run | bytes | MD5 |
|---|---:|---|
| HRR1849459 | 26,041,030,352 | 18555d257e844d10b40f13788830a49b |
| HRR1849460 | 33,332,591,265 | 978529c1f0dde9a98194bac6310b1446 |
| HRR1849461 | 28,873,594,843 | cb76945428f220d4618f12dfe924a88b |
| HRR1849462 | 28,323,326,606 | 79de18396f58543f649f2931d4a067eb |
| HRR1849463 | 35,917,954,133 | 08cfac6a2824567d1e5f88cea3e4e3bf |

数据入口：[HRA008003 download root](https://download.cncb.ac.cn/gsa-human/HRA008003)。原研究为 5 PBC 与 5 control liver，报告 51,943 cells；其公开补充表中，FCRL3 已是 naive B 和 memory B marker，但这不等于预注册的 3/5 donor 检测门已通过。[原始论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC11458754/)

## called-cell 加固

10x 官方说明 raw matrix 包含 background 与 cell-associated barcodes，而 filtered matrix 才是 called cells；BAM 的 `xf bit 8` 标记 UMI-counted molecule representative。[BAM tag 文档](https://www.10xgenomics.com/support/software/cell-ranger/latest/analysis/cr-outputs-bam)；[matrix 文档](https://www.10xgenomics.com/support/software/cell-ranger/latest/analysis/cr-outputs-mex-matrices)

v2 因此冻结：

1. `xf bit 8` molecule representatives；
2. total UMI order-of-magnitude called-cell；
3. 2500–7500 cells、median UMI ≥500；
4. B/NK marker competition，谱系至少 10 cells；
5. target ≥3 UMIs、≥2 positive lineage cells；
6. 同一 target 达到 ≥3/5 donors 才允许项目升级。

## 环境与预计运行

已安装并验证：WSL Ubuntu 22.04、Python 3.10.12、pysam 0.23.3、aria2 1.37.0；PowerShell runner parser 和合成五供者判定测试 PASS。实测公网下载约 3.7–4.7 MiB/s，完整串行任务预计 9–12 小时，取决于网络重试。runner 可恢复，并在每个供者完成后释放 BAM 空间。

## 创新性约束

2026 年已有研究使用同一 HRA 数据报告 FCRL3 主要位于 B cells，并进行了 PBC/FCRL3 multi-omics。后续论文不得声称首次发现 FCRL3 或首次 B-cell localization；可保留的贡献是 source-aware 双调控轴、严格信号级复制、阴性对照及预冻结的 donor-level gate。[重叠研究](https://link.springer.com/article/10.1186/s12876-026-04614-x)
