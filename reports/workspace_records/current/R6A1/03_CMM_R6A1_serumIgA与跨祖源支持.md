# CMM R6A1：serum IgA 与跨祖源支持

## Serum IgA

25 个非 HLA lead signal 中 9 个 serum IgA `P<0.05`，且 9 个 effect 均与 IgAN risk allele 同向：

| locus | lead | serum IgA P | risk-allele beta |
|---|---|---:|---:|
| TNFSF4/18 | rs4916312 | 0.0012 | 0.0373 |
| REL | rs842638 | 0.000219 | 0.0393 |
| IRF4/DUSP22 | rs12201499 | 0.0221 | 0.0339 |
| TNFSF8/15 | rs13300483 | 3.17e-10 | 0.079 |
| REEP3 | rs57917667 | 0.0217 | 0.0696 |
| OVOL1/RELA | rs10896045 | 2.57e-22 | 0.0659 |
| TNFSF12/13 | rs3803800 | 9.4e-08 | 0.0647 |
| TNFRSF13B | rs57382045 | 0.00474 | 0.0456 |
| LIF/OSM | rs4823074 | 6.75e-17 | 0.0531 |

这构成 disease-related trait support；它不是多重校正后的独立 serum-IgA locus 声明，也不是 mediation 证据。R6A2 的 `B_TRAIT_CONCORDANT_CROSS_RESOURCE` 分层只用它排序，不改变共定位阈值。

## European 与 Asian 分层

- 25/25 lead 在 European-only 中 risk-allele beta 同向；24/25 nominal `P<0.05`，3/25 达 `P<5e-8`。
- 25/25 lead 在 Asian-only 中 risk-allele beta 同向；25/25 nominal `P<0.05`，7/25 达 `P<5e-8`。

这些数据允许在 R6A2 检查 combined shared signal 是否同时得到两个祖源层的方向支持。不同祖源的 LD 与统计功效不同，因此不能把未达 genome-wide significance 简化为 replication failure，也不能把 trans-ancestry combined 的 H4 直接当作 European-QTL 的 ancestry-matched 结果。

`TRAIT_AND_ANCESTRY_SUPPORT_GATE = PASS`。
