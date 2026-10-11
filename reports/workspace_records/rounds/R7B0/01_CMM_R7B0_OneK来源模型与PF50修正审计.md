# CMM R7B0：OneK1K 来源模型与 corrected PF50 审计

## 审计问题

历史分析把 PF10 summary 与 PF10 residualized LD 作为 primary，把 PF50 residualized LD 与同一 PF10 z-score 作为 sensitivity。研究计划书 v2 要求纠正后者，并先证明 PF10 summary 的来源模型。

## 输入与实现

来源脚本快照为 `OneK1K_eQTL_source_1316d01.py`，SHA-256：`F17A84B31876963AAE2827881DEC89850FE367FA188794E68364B48BE984893B`。脚本明确使用 TensorQTL nominal cis mapping、`sex + age + genotype PCs + PF1–PF10`、MAF 0.05、约 ±1 Mb cis window，并将 BIM A1 作为 effect allele。

本轮 NumPy 程序严格复现 TensorQTL 1.0.10 `Residualizer`、sample variance、correlation、slope、t statistic、SE 和 two-sided t P-value 公式，名称为 `TensorQTL_1.0.10_formula_compatible_numpy`。它是公式兼容实现，不应被写成实际运行 TensorQTL/PyTorch binary。

## PF10 复现结果

| 组合 | donors | PF10 slope 最大绝对误差 | z 与 frozen beta/SE 相关 | 判定 |
|---|---:|---:|---:|---|
| IL12RB2–NK | 980 | 8.39×10⁻⁸ | 0.999999999999988 | PASS |
| FCRL3–B_IN | 975 | 5.39×10⁻² | 0.998340 | FAIL |
| FCRL3–B_MEM | 970 | 1.02×10⁻¹ | 0.990317 | FAIL |
| FCRL3–CD4_NC | 980 | 4.46×10⁻⁵ | 0.999999994 | FAIL strict tolerance |
| FCRL3–CD8_ET | 980 | 9.32×10⁻⁸ | 0.999999999999995 | PASS |
| FCRL3–NK | 980 | 8.25×10⁻⁸ | 0.999999999999995 | PASS |
| FCRL3–NK_R | 750 | 5.08×10⁻² | 0.995838 | FAIL |

所有目标的 active-donor 顺序与冻结清单一致；AF 与 source-LD 构建输入一致。失败组合的差异不能安全地归因于 allele/build 错误，但也不能在没有历史 PF10 文件的前提下强行视为“仅四舍五入”。因此 G1 为 `HOLD_PARTIAL`。

## corrected PF50

对同一 phenotype、同一 active donors、同一 PLINK A1 dosage 使用 `sex + age + PC1–6 + PF1–50` 重新计算 PF50 beta/SE/z，并分别输出 7 个压缩文件和 QC JSON。PF50 与 PF50 residualized LD 成对进入 `susie_rss`/`coloc.susie`；PF10_L5、PF10_L10、PF10_L20 继续使用原 frozen PF10 summary/LD。

`R7B0_targeted_reclassification.tsv` 的 p12=10⁻⁵ 最高信号摘要显示：IL12RB2–NK、FCRL3–B_IN、B_MEM、NK 和 NK_R 的 H4-dominant 类别未改变；FCRL3–CD8_ET 从 PF10 H3-dominant 变为 PF50 H4-dominant；FCRL3–CD4_NC 的 PF50 没有可用 coloc summary。这个结果提高了模型不确定性的可见度，不能被压缩为“四配置稳定”。

## 结论与边界

历史 PF10 结果继续作为 archived primary evidence；当前公开 PF50 archive 只足以支持 corrected-PF50 sensitivity。必须取得历史 PF10 covariate identity 或重新生成完全同源的 PF10 summary，才可把 G1 标为 PASS，并决定是否启动 G3 full posterior。
