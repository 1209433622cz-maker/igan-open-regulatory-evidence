# R5A2B chr5 数据接入与 harmonization

## OneK1K

10.34 GB raw eQTL archive 经单次流式读取完成身份和结构复核：

- bytes：10,344,009,571；
- MD5：`e42239480f40abd21f221c0d77c82cc3`，MATCH；
- SHA-256：`63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea`；
- 622 个总成员、311 个科学成员、311 个 AppleDouble metadata、308 个 Parquet；
- 14 个细胞 × chr1–22 网格完整；
- 仅提取 14 个 chr5 Parquet及 README/BIM，共 851,615,030 bytes。

固定窗口 `5:149447128–151447128` 内：

```text
bounded QTL rows = 355,926
cells = 14
genes = 8
actual cell–gene pairs = 106
source-significant frozen pairs = 32
```

## 三套 MG GWAS

三套原始 GRCh37 GWAS 的 bytes、MD5 和 header 均重新核验，通过后定向至 OneK1K BIM A1。窗口内 BIM 变异为 4,028。

| 表型 | inference-eligible | excluded | rs6861227 beta(A1=G) | P |
|---|---:|---:|---:|---:|
| MG overall | 3,677 | 39 | 0.15490 | `7.439×10^-8` |
| EOMG | 3,938 | 87 | 0.37101 | `1.053×10^-9` |
| LOMG | 2,483 | 51 | 0.03830 | 0.4205 |

rs6861227 的 GWAS EAF(A1) 与 OneK1K AF(A1=0.14235) 差值分别为 0.01386、0.00309 和 0.00233。三个 lead 均唯一、可定向并进入推断。

每个 coloc 比较有 1,855–3,914 个共同变异，远高于冻结的 500 变异最低门。
