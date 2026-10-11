# CMM R5A1：MG 单细胞组织资源验收

日期：2026-09-13

## GEO metadata 审计

| Series | 样本结构 | 本轮判定 | 合理用途 |
|---|---|---|---|
| GSE227835 | 10 AChR+ MG、10 healthy、10 seronegative pre、10 paired post | PASS | PBMC disease/control 与配对治疗分析 |
| GSE233180 | 12 untreated AChR-Ab+ EOMG thymus scRNA + 同供者 12 BCR | PASS with scope limit | EOMG disease-state localization；无健康对照 |
| GSE297547 | 10 C-prefix RNA、9 MG-prefix RNA、6 VDJ；series 声明 MG/healthy | PASS with label anomaly | RNA/AbSeq/repertoire 资源；须先获得论文或公开 sample map 消解标题异常 |

GSE233180 不能被写成健康对照差异研究。GSE297547 的 9 个 MG-prefix 样本标题含有“control”，在标签消解前不得用于 disease differential。

## GSE227835 实矩阵 spot-check

本轮下载并完整读取：

| Sample | Group | Bytes | Genes | Cells | TNIP1 nonzero cells |
|---|---|---:|---:|---:|---:|
| GSM7266236_A1 | AChR-positive MG | 14,169,551 | 36,601 | 5,776 | 1,482（25.66%） |
| GSM7266246_H1 | healthy control | 18,445,765 | 36,601 | 8,552 | 1,839（21.50%） |

两份矩阵 gzip 均完整，TNIP1 及本轮 15 个候选基因全部存在且有非零计数。因此“至少一个公开 MG 组织可检测主候选基因”门通过。

这只是技术可检测性检查。两例 spot-check 不能用于差异表达、细胞组成、机制或疾病方向判断。正式组织分析应下载完整 cohort，恢复 cell annotation，以 donor/patient 为推断单位，并按原研究设计建模。

## 后续使用顺序

1. 先完成 disease–eQTL 区域共定位；
2. 仅对 molecular gate 通过的 gene/cell 运行 GSE227835 donor-level 验证；
3. 若指向 EOMG 相关细胞，再用 GSE233180 做胸腺 disease-state localization；
4. GSE297547 只有在标签公开消解后才进入疾病对照分析。

## 来源

- `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE227835`
- `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE233180`
- `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE297547`

