# CMM R4A12FG6：三细胞完整成员接入与精确协调

## 1. 选择性成员接入

源为 Zenodo `common_all_cis_pvalues_100kb.zip`，归档大小 16,559,137,990 bytes，provider MD5 `dd54714b2effb91160ac171ccb941534`。本轮只取预注册三个成员，不下载整个 ZIP，不扩展第四细胞或 1 Mb 窗口。

| Cell | compressed bytes | uncompressed bytes | CRC32 | 源行数（含header） | IL12RB2 rows | extract SHA-256 |
|---|---:|---:|---|---:|---:|---|
| CD8_TEM | 552,936,197 | 2,257,959,637 | 77a34e9f | 15,499,933 | 1,366 | 41bbce95042b1209e98193fa3821a38032470137c3d270569de56bca26ba96e9 |
| CD4_CTL | 542,521,530 | 2,208,020,074 | 252cf0c0 | 15,301,331 | 1,366 | 4579cebb9448a5ed318156b0d008131defa7044c2f7522319724047fe56f9e12 |
| CD4_TCM | 568,995,615 | 2,323,568,170 | 2d997c2d | 15,924,083 | 1,366 | 3f44040c02484ca11ba4879eb38b6a90ed0afec042bc53fa09b342663d5d1110 |

每个成员均验证 local header、HTTP Content-Range、压缩范围长度、raw DEFLATE EOF、无额外流、完整解压字节数、source CRC32、字段数、gene 精确匹配和输出 SHA-256。全归档 MD5 标为 `NOT_RUN_SELECTIVE_MEMBERS_ONLY`，未将成员级验证冒充全 ZIP 验证。

## 2. 与 FinnGen 精确协调

R12/R13 的每个 cell 均为：

- QTL 1,366 条；
- exact REF/ALT overlap 891（65.23%）；
- 5 个同位置反向等位基因对排除；
- 无 strand complement 推断；
- QTL top 与 disease regional lead 均覆盖；
- AF median |Δ|≈0.030，P95≈0.122–0.123。

source CS 的疾病 exact 覆盖：

| Cell | CS | PIP mass fraction |
|---|---:|---:|
| CD8_TEM | 1 / 2 | 92.93% / 95.72% |
| CD4_CTL | 1 | 96.81% |
| CD4_TCM | 1 / 2 | 100% / 100% |

CD8_TEM CS1 与全窗口 65.23% 覆盖未达冻结充分性，因此三细胞统一保持 `HOLD_EXACT_COVERAGE`；这不是生物学阴性。

## 3. External LD 对三细胞 source CS 的覆盖

同一 764-variant external panel 对 source CS 的 PIP mass：CD8_TEM 92.93%/93.06%，CD4_CTL 78.17%，CD4_TCM 77.14%/75.85%。没有任何一个细胞的全部 source CS 达到 95%，进一步确认不能用该面板做正式多信号判定。
