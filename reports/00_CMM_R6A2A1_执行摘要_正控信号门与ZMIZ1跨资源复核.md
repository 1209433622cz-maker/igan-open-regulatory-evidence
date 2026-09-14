# CMM R6A2A1 执行摘要：正控信号门与 ZMIZ1 跨资源复核

日期：2026-09-14  
判定：**R6A2A1 COMPLETE；IgAN 继续，但进入有界扩展而非直接全24-locus**

## 核心结果

R6A2A0 冻结的 10 个 OneK1K cell–gene benchmark × 3 个 IgAN GWAS 已全部运行，共 30 个比较。combined primary benchmark 的 locus 结果为：

| locus | 状态 | 最佳组合 | PP.H4 | H4/(H3+H4) | QTL min P |
|---|---|---|---:|---:|---:|
| IRF4/DUSP22 | UNINFORMATIVE_WEAK_QTL | IRF4 / Mono_C | 0.0963 | 0.4301 | 0.00056 |
| ITGAM/ITGAX | UNINFORMATIVE_WEAK_QTL | ITGAX / Mono_C | 0.1037 | 0.3338 | 0.00138 |
| ZMIZ1 | PASS_ROBUST_SHARED_SIGNAL | ZMIZ1 / NK | 0.9306 | 0.9341 | 3.51e-07 |

严格的 `>=2/3 published-cell locus PASS` 门没有通过：目前为 **1/3 PASS，2/3 weak-QTL uninformative，0/3 distinct-signal failure**。因此不能写成“三个已发表细胞特异机制已复制”，也不能直接把全24-locus无条件放行。

## 可冻结的阳性

`ZMIZ1 × NK` 在 OneK1K 中通过冻结单信号门：

```text
combined PP.H4 = 0.9306
H4/(H3+H4) = 0.9341
p12=1e-6 PP.H4 = 0.5728
Asian PP.H4 = 0.9669
```

疾病 risk allele A 在 OneK1K lead row 对 ZMIZ1 表达的方向为 down，与 published direction 一致。

TenK10K 作者预计算的 `kiryluk_IgAN × NK × ZMIZ1` 结果进一步给出：

```text
826 SNPs
PP.H4 = 0.998255
H4/(H3+H4) = 0.998268
top SNP = chr10_79287258_G_A (GRCh38)
```

而 `NK_CD56bright × ZMIZ1` 为 `PP.H3=0.9268, PP.H4=0.0194`，提示信号具有 NK context specificity。

该 TenK 结果可称为**支持性的独立单因果模型复制**。作者 CSV 没有携带完整输入 provenance 与 prior sensitivity；TenK SuSiE 又显示两个 source credible sets，因此目前不升级为最终多信号 Tier A。

## 方法校验

- OneK archive：10,344,009,571 bytes 全部读取，MD5 与冻结值一致。
- 10/10 benchmark 可测；7/7 primary benchmark 可测。
- Python ABF 与官方 R coloc 在 90 个 prior-specific 结果上最大 PP.H4 绝对差 `1.33×10^-15`。
- R6A2A0 的 R 验证脚本存在 `gene==gene` 自比较错误，可能混合 locus 内多个基因；本轮已修正并重跑。

## 下一阶段

进入 **R6A2B0 — bounded positive-yield expansion**。只分析其余 8 个 serum-IgA 同向 locus、183 个已经同时满足 OneK source significance 与 TenK compatible support 的 OneK cell–gene 组合，最多 549 个三表型 ABF tests。

若新增至少 2 个独立 locus 通过 robust 或 signal-specific 门，则 ZMIZ1 + 新增2 locus 达到三条独立证据链，放行全24-locus。若新增为0且覆盖充分，则暂停全景扩展并重审论文设计。
