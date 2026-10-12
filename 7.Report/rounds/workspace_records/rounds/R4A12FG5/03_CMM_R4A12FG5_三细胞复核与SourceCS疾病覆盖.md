# CMM R4A12FG5：三细胞预注册复核与不越级判定

## 冻结细胞

FG4已提前固定：
1. `CD8_TEM`
2. `CD4_CTL`
3. `CD4_TCM`

本轮未根据结果增加其他细胞。

## Source-level eQTL / SuSiE证据

| Cell | IL12RB2 ACAT P | QTL top marker | top P | source CS |
|---|---:|---|---:|---:|
| CD8_TEM | 5.169e-17 | 1:67326053:A:C | 1.457e-19 | 2 |
| CD4_CTL | 9.770e-15 | 1:67327248:G:A | 3.060e-17 | 1 |
| CD4_TCM | 3.053e-14 | 1:67332644:T:G | 1.796e-16 | 2 |

对应R13 disease P：
- CD8_TEM top marker：9.25e-4
- CD4_CTL top marker：1.39e-3
- CD4_TCM top marker：1.38e-3

这些只是同位点疾病关联背景，不是共定位。

## Source CS与R13 disease exact coverage

| Cell/CS | source members | exact disease members | retained PIP mass | 最小R13 disease P |
|---|---:|---:|---:|---:|
| CD8_TEM CS1 | 8 | 7 | 0.9139 / 0.9834 | 4.21e-4 |
| CD8_TEM CS2 | 10 | 8 | 0.9580 / 1.0008 | 8.38e-2 |
| CD4_CTL CS1 | 13 | 12 | 0.9882 / 1.0208 | 3.05e-4 |
| CD4_TCM CS1 | 13 | 13 | 0.9690 / 0.9690 | 3.05e-4 |
| CD4_TCM CS2 | 7 | 7 | 0.9614 / 0.9614 | 5.26e-1 |

source PIP和略高于1的情况按源文件数值原样保留，不强行重归一化。

## 与当前archived LD的关系

当前329-variant archived LD子集对这些source signals覆盖极差：
- CD8_TEM CS1：0个成员
- CD8_TEM CS2：1个成员，仅0.1665 PIP
- CD4_CTL CS1：0个成员
- CD4_TCM CS1：0个成员
- CD4_TCM CS2：3个成员，约0.3658 PIP

因此即使三种细胞的full beta/SE已经到手，当前archived LD也不能完成预注册multi-signal adjudication。

## 为什么本轮没有跑三细胞coloc.abf

上传包中没有这三个细胞的完整variant-level beta/SE字节。公开Zenodo ZIP已知包含这些成员，但当前执行沙箱不能通过外网Range把约1.66 GB的三个压缩成员真实拉取；本轮没有用source CS/PIP反算不存在的beta/SE。

为避免把技术环境限制变成开放性任务，本轮已生成：
- resume-safe、member-CRC验证的三细胞选择性下载/提取脚本；
- 只允许三个预注册细胞；
- 每个成员通过完整解压字节数与CRC后才晋升正式输出。

## 本轮三细胞分类

> **`PARTIAL_SOURCE_SUMMARY_ONLY`**

这不是negative。source-level结果反而说明三个预注册细胞都有值得继续测试的IL12RB2信号，但正式replication仍等待full-summary字节与合格LD。
