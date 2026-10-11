# CMM R6A1：GWAS 字节、Schema 与非 HLA 位点审计

## 字节对象

官方页面未提供校验和，因此本轮保留 HTTP 传输层与 canonical 分析层，并生成本地 MD5/SHA-256。European-only IgAN 与 serum IgA 的服务器响应使用 Brotli；原始响应以 `.br` 保存，解压后的纯文本作为分析层，二者不能混为一个文件。

| 对象 | 传输编码 | 传输 bytes | canonical bytes | canonical SHA-256 | 门 |
|---|---|---:|---:|---|---|
| igan_combined | identity | 492,016,732 | 492,016,732 | `35b603e9f912ec0ed1a04a9aa6cf76c35b75998161e0d1ccbba4d0ded0d2c140` | PASS |
| igan_european | br | 164,526,659 | 446,493,462 | `e2c4e54bfb0aa60c8572891afa01e1dd7dd31c6dcfb119d4aec053add72e8c0f` | PASS |
| igan_asian | identity | 376,485,006 | 376,485,006 | `f581da26e75e55bd7cb2570e270ba4bf9d57f61a8c65e6ed48c11d181e5af542` | PASS |
| serum_iga_combined | br | 168,662,774 | 596,831,842 | `1ae6806d393eba53ed127af56eb28c8ad08683c7c0abe3baeaba8743b9537c31` | PASS |

## 全文件扫描

| 数据集 | 行数 | 字段 | 非法数值 | `SE<=0` | P 越界 | SNP/坐标不符 | 25 个 lead 坐标 |
|---|---:|---|---:|---:|---:|---:|---:|
| combined | 10,021,045 | `SNP CHR BP_hg19 A1 A2 BETA SE P` | 0 | 0 | 0 | 0 | 25/25 |
| European | 9,094,951 | 同上 | 0 | 0 | 0 | 0 | 25/25 |
| Asian | 7,666,659 | 同上 | 0 | 0 | 0 | 0 | 25/25 |
| serum IgA | 12,230,455 | 同上 | 0 | 0 | 0 | 0 | 25/25 |

`A1` 是 effect allele；build 为 GRCh37/hg19。BETA、SE、P 齐全，满足 coloc.abf 与 effect-direction audit 的输入要求。

## 信号与 locus 计数

论文 Table 1 给出 30 个独立信号：5 HLA + 25 非 HLA。25 个非 HLA 信号对应 24 个 locus，因为 CFH 有两个独立信号。

combined 文件重算得到 523 个非 HLA `P<5e-8` 变异。单纯按相邻 GWS 变异间距 1 Mb 聚类会得到 25 个簇，因为 CFH 的一个远端尾部变异 `1:197921246` 与 CFH lead 相距 1,234,328 bp。本轮保留该工程诊断，不为了复现论文数量而偷偷改变聚类法；再以论文定义 locus、±1.5 Mb 锚定后，523/523 均归入 24 个已发表 locus。

## 跨 build 核验

24/24 locus lead 均经 NCBI RefSNP placement 找到 GRCh38 坐标，且 GRCh37 与论文坐标一致。`rs751081288` 已 retired 并 merge 到 `rs57707137`，normalized placement 相对旧坐标存在 1 bp shift，已在 cross-build manifest 中显式记录。`rs1865097` 只接受 assembled chromosome placement，排除了 scaffold placement。

## 判定

`GWAS_BYTE_SCHEMA_LOCUS_GATE = PASS`。
