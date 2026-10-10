# R7C0 固定 92 比较：CASCADE 与染色质三角审计

## 预结果冻结

在本轮任何 27-gene CASCADE 网络查询前，从 R7B3A S5 机械提取：

```text
PF10_multisignal_state = H4_SUPPORTED_STABLE
comparisons = 92
genes = 27
cells = 12
loci = 19
freeze SHA-256 = a074a66b79215c8f0ee4be4fe77fe5b3a4decc10520ea8688f2555411396920a
```

因此本轮不是看到 FinnGen 结果后再挑 IL12RB2。

## 覆盖与疾病共定位

27/27 gene endpoints 可访问；22/27 在对应 broad cell 中存在 q<0.05 eQTL。完整 disease-coloc region audit 只在 IL12RB2 检出 `CHIRBIL_PRIM–gene eQTL` pairs，共 7 条，PP.H4 约 0.963–0.971。FCRL3 及其余 25 个基因没有返回 PBC–eQTL coloc。

该结果应表达为“在预冻结 stable-H4 gene universe 中，FinnGen PBC disease-coloc 外部证据集中于 IL12RB2”，不能写为 FinnGen 全基因组只有 IL12RB2。

## 预冻结 NK/IL12RB2 三角

### 疾病–表达

`CHIRBIL_PRIM ↔ IL12RB2 eQTL, l1.NK`：

- PP.H4.abf = 0.9703068
- disease CS=19
- eQTL CS=9
- overlap=9

### 疾病–染色质

`CHIRBIL_PRIM ↔ chr1-67307618-67308670 caQTL, l1.NK`：

- PP.H4.abf = 0.9695295
- disease CS=19
- caQTL CS=11
- overlap=11

### peak–gene link

- peak 距 IL12RB2 TSS 239 bp；
- fasthurdle link β=0.140574；
- public endpoint 的 joint p 显示为 0，按数值下溢解释，不能写成数学意义的绝对零。

两个 QTL CS 均为同一 19-variant disease CS 的子集；由集合大小可知二者至少共享 1 个疾病 CS 成员。但当前 endpoint 不提供直接 eQTL–caQTL coloc posterior，因此不能把三角一致性升级为方向性中介。

## 对历史 R7B1D 的纠偏

R7B1D 的 targeted query 正确识别了 positional peak 和 peak–gene link，但旧报告写“PBC–caQTL colocalization is not established”。本轮预冻结 full-region query 实际返回了该 peak 的 l1.NK PBC–caQTL pair，因此这句话应被本轮结果取代。

更新后的边界：

```text
PASS_TRIANGULAR_SIGNAL_COHERENCE_WITHOUT_DIRECT_MEDIATION_PROOF
```

允许：source-integrated disease/eQTL/caQTL/peak-gene coherence。
禁止：unique causal variant、directional mediation、experimental mechanism。
