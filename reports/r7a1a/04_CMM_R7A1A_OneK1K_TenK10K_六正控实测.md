# R7A1A：OneK1K/TenK10K 六正控实测

## 输入与方法

- OneK1K：`OneK1K_TensorQTL_top_eQTL_summary.zip`，617 members，ZIP CRC PASS；原作者 q-value<0.05 定义源数据显著。
- TenK10K gene-level：29 members，ZIP CRC PASS；在每个 cell 内对可数值 ACAT-p 重建 BH q<0.05。
- TenK10K SuSiE：29 members，ZIP CRC PASS；存在 source credible set 作为独立证据层。
- 基因仅限预注册 3+3；唯一名称修正是 INAVA←C1orf106。

## 结果

| candidate | gene | OneK observed/sig cells | TenK observed/sig cells | TenK CS cells | 双资源源阳性 |
|---|---|---:|---:|---:|---|
| PBC | IL12RB2 | 7/1 | 26/15 | 11 | 是 |
| PBC | FCRL3 | 12/7 | 18/17 | 14 | 是 |
| PBC | INAVA | 1/0 | 1/1 | 1 | 否 |
| CeD | CSK | 14/0 | 28/5 | 3 | 否 |
| CeD | TRAFD1 | 14/0 | 28/1 | 0 | 否 |
| CeD | UBASH3A | 11/4 | 19/13 | 11 | 是 |

## 解释边界

1. `observed` 只证明该 gene-cell 有 top-level 记录，不证明疾病与 QTL 共定位。
2. `source positive` 仍只证明存在 cis-QTL，不证明它与疾病 signal 相同。
3. OneK 与 TenK build、cell label、donor 与 fine-mapping 方法不同；只有 R7A1B 的变异级 harmonization 和 signal-level test 可以升级结论。
4. CSK/TRAFD1 不能写成“CeD 机制阴性”；当前只说明 OneK PBMC 层缺少强 source eQTL。
