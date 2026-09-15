# CMM R7A1B1：OneK、PBC GWAS 与 ABF Smoke 结果

**日期：2026-09-15**

## 1. OneK1K 原档门

本轮顺序读取完整 `OneK1K_TensorQTL_raw_eQTL_summary.tar.gz`，边读边计算摘要并只提取 chr1 的 7 个冻结细胞成员。

```text
archive bytes = 10,344,009,571
bytes read = 10,344,009,571
MD5 = e42239480f40abd21f221c0d77c82cc3
SHA-256 = 63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea
required cell members = 7
extracted cell members = 7
gate = PASS
```

冻结的 9 个 cell–gene 组合全部可测试，共 24,001 行 QTL。每个细胞使用真实 active donor：B_IN 975、B_MEM 970、NK_R 750，其余本轮细胞 980。

## 2. PBC GWAS harmonization

GCST90061440 GRCh37 数据先与 OneK BIM 做位置与两等位基因匹配，再把效应统一到 BIM A1；回文位点和冲突重复不进入推断。

| 基因 | GJOKA locus | GWAS eligible rows | 区域最小 P |
|---|---:|---:|---:|
| IL12RB2 | 2 | 1,098 | 6.61×10^-63 |
| FCRL3 | 4 | 958 | 2.08×10^-8 |
| INAVA | 6 | 1,248 | 2.06×10^-9 |

三个区域均超过预设的 500 变异覆盖门，无冲突重复变异被排除。

## 3. 单信号 smoke gate

固定 `p1=p2=1e-4`，`p12=1e-6/1e-5/1e-4`。默认先验结果：

| 基因 / 细胞 | overlap SNP | QTL min P | PP.H4 | H4/(H3+H4) | 分类 |
|---|---:|---:|---:|---:|---|
| IL12RB2 / NK | 1,081 | 4.79×10^-12 | 0.9982 | 0.9982 | PASS；强制多信号复核 |
| FCRL3 / B_IN | 929 | 3.45×10^-26 | 0.9929 | 0.9929 | PASS |
| FCRL3 / B_MEM | 930 | 4.68×10^-9 | 0.9899 | 0.9900 | PASS |
| FCRL3 / CD4_NC | 929 | 3.78×10^-7 | 0.9901 | 0.9906 | PASS |
| FCRL3 / CD8_ET | 929 | 1.52×10^-28 | 0.9413 | 0.9415 | PASS |
| FCRL3 / CD8_NC | 929 | 1.09×10^-9 | 0.1314 | 0.1317 | 不触发 |
| FCRL3 / NK | 929 | 1.38×10^-23 | 0.9363 | 0.9364 | PASS |
| FCRL3 / NK_R | 923 | 7.19×10^-9 | 0.9746 | 0.9747 | PASS |
| INAVA / CD4_NC | 1,248 | 3.92×10^-4 | 0.0262 | 0.1710 | 信息不足 |

最终触发 7 个组合：IL12RB2/NK 与 FCRL3 的 B_IN、B_MEM、CD4_NC、CD8_ET、NK、NK_R。没有按结果追加其它细胞或基因。

## 4. 独立实现对照

Python 复现 Wakefield ABF 后，与官方 R `coloc.abf` 对照 9 个组合、5 个后验状态：

```text
max absolute posterior difference = 1.4432899320127035e-15
tolerance = 1e-10
gate = PASS
```

该对照只证明 ABF 计算一致，不把单因果模型的 smoke 结果升级为最终机制证据。
