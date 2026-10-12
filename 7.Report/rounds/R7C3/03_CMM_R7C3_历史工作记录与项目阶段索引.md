# R7C3 历史工作记录与项目阶段索引

## 记录完整性

全工作区找到 202 份符合命名规则的行动记录 Markdown。按 SHA-256 去重后为 85 份唯一内容；117 份为 exact copies，主要位于 `7.Report`、`6_release`、`9.Version`、本地 manuscript 和 GitHub 之间。解析出 73 个阶段 token，另有两份通用记录：早期方法质控记录和 RP v3 制作记录。

本轮不以“文件路径唯一”代替“内容唯一”。canonical ledger 优先选择：

1. `7.Report/rounds`；
2. `7.Report/current`；
3. 其他 `7.Report`；
4. `5_manuscript` 或 `5_analysis`；
5. `6_release`；
6. `9.Version`；
7. GitHub 公共副本。

所有副本路径仍保留在 `records/R7C3_action_record_all_copies.tsv`，不会因为选出 canonical path 而丢失 provenance。

## 阶段逻辑

| 阶段 | 最终状态 | 保留价值 |
|---|---|---|
| R2–R4 SSc | `FROZEN_ARCHIVE` | 数据入口、harmonization、LD、source-CS 与 falsification 工程 |
| R5 MG | `FROZEN_NO_GO_FOR_REGULATORY_MAIN` | 亚型异质性、细胞 donor LD 与 target-specific stop rule |
| R6 IgAN | `FROZEN_PORTFOLIO_BRANCH` | 正控纠偏、跨祖源证伪与 completion-first gate |
| R7A PBC | `GO` | 完整 disease/QTL/tissue evidence chain 与投稿基线 |
| R7B | `COMPLETE_METHOD_AUDIT` | PBC-wide ABF、642 multi-signal、模拟、同输入归因 |
| R7C0–R7C2 | `COMPLETE_BOUNDED_UPGRADE_AND_SUBMISSION_FORMAT` | IL12RB2 外部证据、chromatin boundary、npj/HG 双轨 |
| R7C3 | `COMPLETE_FULL_AUDIT` | 全量资产身份、投稿包、公共同步与下一阶段冻结 |

机器可读阶段总览位于 `assets/R7C3_retained_stage_timeline.tsv`。

## 后续检索建议

- 查科学裁决：优先 `7.Report/rounds/<stage>/99_*.md`。
- 查可复现 release：使用 `6_release/<stage>` 中的 ZIP、`.sha256` 与内部 checksum。
- 查当前主论文：使用 `5_manuscript/R7C2_Q1_JournalRealityCheck_DualTrackSubmission`。
- 查公共可引用版本：使用 GitHub tag/release，不使用本地工作目录作为引用身份。
- 查回滚历史：使用 `9.Version`，不要把其中旧结论当作当前状态。
- 查原始/第三方大数据：使用 `1_data` 及 hash receipt，不上传 GitHub。
