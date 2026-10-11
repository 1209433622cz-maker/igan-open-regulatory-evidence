# CMM R5A2A：日本 MG 与 OneK1K 字节级接入验收

## 日本 MG GWAS

来源：NBDC Human Database `hum0197.v29.MG-gwas.v1`，公开 unrestricted access。官方说明为日本人群 1,434 cases、42,913 controls，SAIGE，GRCh37/hg19，9,034,566 个常染色体与 X 染色体变异；Allele2 为 ALT 和效应等位基因，BETA 为 Allele2 的效应。

接入结果：

| 项目 | 结果 |
|---|---|
| ZIP bytes | 229,751,515 |
| ZIP SHA-256 | `2b93e8832b1fd6f13dbe66f60373da544bcff72bd9b8a716e4f60a2cb6b6b67f` |
| ZIP MD5 | `7842babcbb87e64e5072771cbe3aec88` |
| CRC | PASS |
| 唯一数据成员 | `hum0197.v29.MG-gwas.v1.txt` |
| 解压后 bytes | 727,739,223 |
| 数据成员 SHA-256 | `aed57ce92ed1ed724d5f36e042a66e9e94175f52ea5669267fac8e4b757110ab` |
| 行数 | 9,034,566 / 9,034,566 PASS |
| header 与字段范围 | PASS |
| 最小 P | 1.717064e-10，chr5:1,296,255 A>AG |

目标位点结果：

| 位点 | 日本文件状态 | ALT β | P | 复制解释 |
|---|---|---:|---:|---|
| rs7239261 | PRESENT | -0.129494 | 0.001253072 | 与欧洲 LOMG C 等位基因方向一致，exact-variant replication PASS |
| rs6861227 | PRESENT | -0.0662169 | 0.2840654 | 不显著且与欧洲 EOMG G 效应方向不一致 |
| rs7596255 | ABSENT |  |  | 可能受日本文件 MAF/INFO 过滤影响；不是阴性结果 |
| rs2476601 | ABSENT |  |  | 同上；不是阴性结果 |

日本数据是总体 MG，不是 EOMG/LOMG 分层，因此它增强 rs7239261 的疾病位点可信度，但不能独立复制亚型差异。

## OneK1K genotype

Zenodo 续传在多次 HTTP 504 后完成。已冻结：

- 文件：`plink_genotype_merged_980_donors.zip`；
- 233,198,074 bytes；
- MD5 `be1053e34fa023bc808388d4e0bf2aa1`，与官方记录一致；
- SHA-256 `ad58b4f3015ccb15ee53e370ba46137412a5b788e191f0a5a34b80feefa7d97d`；
- ZIP CRC PASS；
- 真实科学成员恰为一个 BED/BIM/FAM 集合；`__MACOSX/._*` 是 AppleDouble metadata，保留在 CRC 清单但排除出科学成员计数；
- FAM=980 donors；BIM=5,326,925 variants；BED magic=`6c1b01`，SNP-major；
- 坐标由三个精确 lead 判定为 GRCh37。

Lead coverage：rs2476601、rs6861227、rs7239261 存在；rs7596255 缺失。后者 EAF 约 2%，与 OneK1K 公共 genotype 仅保留 MAF>5% 的设计相符。

## 工程修正

原脚本要求 ZIP 中只能出现一个扩展名为 BED/BIM/FAM 的成员，因此把 AppleDouble 资源分支计为额外数据集。本轮修改为：所有成员继续参加 CRC；仅不位于 `__MACOSX/` 且 basename 不以 `._` 开头的成员参加科学数据集判定。修正后完整验收通过。

## 结论

`OneK1K source-aware LD availability` 已从“公开列表存在”升级为“本地真实 genotype 字节与结构 PASS”。当前唯一主要输入缺口是 OneK1K 10.34 GB raw cis-eQTL；信号推断仍须等待该文件。
