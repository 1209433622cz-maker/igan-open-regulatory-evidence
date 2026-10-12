# R7B1A：R7B0A 来源身份与当前模型终裁

## 输入包验收

`CMM_R7B0A_PF10_SourceIdentityRecovery_2026-10-02.zip`：

- ZIP SHA-256：`a16c6fa8fad04ad6be8d236cc4c1ccf2b774f0b323c45e5bf596bc1caf98e7c0`
- ZIP members：12/12 可读
- 包内 checksums：11/11 PASS

## 历史 PF10 追溯

在 YR1 与 Downloads 中执行只读扫描，得到 43 个文件/ZIP 命中和 54 个代码文本引用；真实命中均为当前 `_mx_pf50` 文件或对历史路径的引用，未找到任何可用内容证明历史 `*_covar_peer_factors_PF10.txt` 原始字节身份。

因此：

```text
HISTORICAL_PF10_SOURCE_IDENTITY = HOLD_UNRESOLVED
HISTORICAL_PF10_REPRODUCTION = PASS_3_OF_7
```

这个状态只限制“历史 PF10 文件身份已恢复”的主张，不阻止使用当前公开输入重新建立严格可追溯模型。

## 当前版本双模型门

对 7 个历史 comparisons 使用明确 donor、expression、variant、allele、covariate 与 LD 顺序重新建立 PF10/PF50：

- identity manifest：14/14 PASS；
- SuSiE fits：28/28 完成并通过硬 QC；
- kriging diagnostic review rows：0；
- 当前版本模型身份：PASS。

当前模型的生物学分类为：

- 5 个 `STABLE_H4_ACROSS_CURRENT_PF10_PF50`；
- 1 个 `MIXED_OR_UNINFORMATIVE`（FCRL3/CD4_NC 在 PF50 无 coloc summary）；
- 1 个 `PF_NUMBER_SENSITIVE_H3_TO_H4`（FCRL3/CD8_ET）。

这说明历史文件身份与当前可验证模型是两个不同问题。R7B1 以当前版本 PF10 为 primary、当前版本 PF50 为 sensitivity；不得把未恢复的历史 PF10 身份重新包装成已解决。
