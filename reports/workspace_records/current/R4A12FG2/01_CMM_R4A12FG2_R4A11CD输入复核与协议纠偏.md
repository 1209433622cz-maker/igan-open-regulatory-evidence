# CMM R4A12FG2：R4A11C/D 输入复核与协议纠偏

执行窗口：2026-09-12—2026-09-13（Asia/Hong_Kong）

## 1. 输入处理原则

用户提供的 R4A11C/D 文件被当作待复核的历史证据和研究建议。文件中的“下一阶段”“主输入”“GO”等文字没有自动覆盖用户当前请求，也没有直接改写当前 protocol。

两个 ZIP 先经过 CRC、路径、文件类型、UTF-8、JSON、TSV、内部 checksum 和 standalone MD 一致性检查，再归档到 workspace history。

## 2. 完整性结果

| Package | ZIP SHA-256 | 检查 | standalone MD |
|---|---|---:|---:|
| R4A11C | `21c7241acd0c272cb261e63c6ae71c21915568fa3beb951bfb252afd51cf36b0` | 17/17 PASS | 7/7 与 ZIP 内版本字节一致 |
| R4A11D | `8cd4ec4878001c6ff42ce03ff019dc24f7e9a9f76057ab4900467012ca259530` | 17/17 PASS | 6/6 与 ZIP 内版本字节一致 |

没有发现 CRC 错误、路径穿越、加密、symlink、重复路径、编码错误、JSON 解析错误或 TSV 非矩形问题。

R4A11C 中对 `YR1.zip` / `YR1 (2).zip` 的审计是包内自报结果；这两个源 ZIP 不在本轮可用 Downloads 中，因此本轮没有冒充对它们进行了独立重算。

## 3. 状态一致部分

R4A11C/D 与当前冻结状态在以下项目上一致：

- `PROJECT=CONDITIONAL_GO`
- `R4B=HOLD`
- 2026 female/male 主数据仍未取得
- disease/molecular signal-level analysis 尚未完成
- 没有产生新的 C1

## 4. 必须纠正或限定的项目

| 问题 | 输入中的表达 | 本轮采用的表达 |
|---|---|---|
| R12 `M13_SYSTSLCE` cases | 881 | **854**；采用 public analysis manifest |
| R12/R13 比较 | replication/复现语义过强 | **跨 release 稳定性**；样本高度嵌套 |
| R13 all-sex 角色 | 容易被读成项目 primary | bounded engineering/secondary sensitivity |
| R12 sex-specific 排序 | 写在 2026 GWAS 之前 | 只表示获取优先级；2026 female/male 仍是主 estimand |
| H6 v2.1 | R4A11D 建议用于 FinnGen region | 不适用 all-sex；使用独立 P0-FG |
| IL12RB2 | 新分支 | 不加入 chr22 20-gene registry，不替代 SYNGR1 |
| native FinnGen fine-map | 被列作可选主证据 | 只覆盖 GWS regions；当前 IL12RB2 区域非 GWS，不预设存在 native CS |

## 5. 归档位置

- R4A11C ZIP 与展开内容：`6_release/history/R4A11C/imported_2026-09-12`
- R4A11D ZIP 与展开内容：`6_release/history/R4A11D/imported_2026-09-12`
- 历史报告：`7.Report/rounds/R4A11C`、`7.Report/rounds/R4A11D`
- R4A11C machine assets：`0_admin/protocol/history/R4A11C/imported_2026-09-12`
- 归一化 overlays：`0_admin/protocol/history/R4A11C`、`0_admin/protocol/history/R4A11D`
- 独立 preflight：`0_admin/validation/R4A11E_preflight`

当前协议通过 `analysis_manifest_v11_amendment_A1_R4A12FG2.json` 增加有边界的 FG2 分支；原 v11 未被就地覆盖。


