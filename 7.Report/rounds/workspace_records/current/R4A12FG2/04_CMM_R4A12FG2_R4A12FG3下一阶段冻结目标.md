# CMM R4A12FG2：R4A12FG3 下一阶段冻结目标

执行窗口：2026-09-12—2026-09-13（Asia/Hong_Kong）

## 阶段名称

> **R4A12FG3 — Molecular QTL and LD Feasibility Gate**

## 科学定位

FG3 只判断 FinnGen all-sex SSc ↔ IL12RB2 molecular QTL 的正式 coloc 是否具备可计算、可解释的输入。它是次级工程/敏感性分支，不更改 2026 female/male chr22/SYNGR1 主线。

## 必须取得或冻结的四类输入

1. **完整 molecular QTL signal input**
   - 优先 TenK10K IL12RB2 per-variant beta/SE/AF/N；
   - 或 source-provided、可计算 signal-level coloc 的完整 likelihood/Bayes-factor/fine-map 对象；
   - FinnGen immune multiome 同生态 QTL 只能作为补充，不能成为唯一“独立”证据。

2. **variant identity 与 QC**
   - GRCh38 reference FASTA identity 与 SHA-256；
   - left alignment / multiallelic split / allele orientation；
   - INFO 或资源等价 QC 的预先冻结规则；
   - 完整 drop ledger。

3. **coverage**
   - disease 与 QTL 的 exact normalized key overlap；
   - common fraction、common count、span；
   - retained source CS PIP mass；
   - disease lead、rs6662198、QTL top/CS anchors 的保留状态。

4. **LD / signal model**
   - multi-signal fine-mapping 优先 source-matched signed LD；
   - 若只有外部 LD，必须通过 allele order、AF、PSD、z–LD diagnostics；
   - 不允许删除 discordant variants 以强迫 PASS。

## 分析顺序

```text
Molecular QTL bytes/objects
  -> identity + schema + checksum
  -> reference normalization + INFO/QC
  -> disease-QTL coverage gate
  -> source/matched LD gate where required
  -> bounded all-sex coloc
  -> R12/R13 result stability check
  -> classify SHARED / DISTINCT / INCONCLUSIVE / UNTESTABLE
```

## GO / HOLD

进入正式 bounded coloc 的条件：

- variant-level QTL 输入完整；
- disease/QTL build 和 allele 可统一；
- coverage 与 CS mass PASS；
- 所选方法需要 LD 时，LD gate PASS。

以下任一情况触发 HOLD：

- 只有 gene-level P 或 CS member/PIP 摘要；
- QTL 缺 beta/SE 且没有完整 signal likelihood；
- INFO/QC 或 reference identity 未冻结；
- CS mass/anchors 严重丢失；
- LD mismatch。

HOLD 输出为 `UNTESTABLE/UNINFORMATIVE`。只有技术门全部通过后观察到稳定 H3 型结果，才允许讨论 `DISTINCT`；不能从区域 lead 未进入 QTL CS 直接判阴性。

## 并行等待项

- 2026 female/male summary 到达后立即回到主线 H6 v2.1。
- R12 Green Library 授权到账户后读取真实 exclusion list，再决定 sex-specific object acquisition。
- R13/R12 full all-sex objects可由用户按本轮脚本归档；区域 smoke 的真实字节与可复现性已经 PASS，完整下载主要服务长期复现和后续其他区域。


