# WORKSPACE REORG 详细行动记录

**工作区：** `H:\SCI2\YR1`  
**参考模板：** `C:\Users\Administrator\Desktop\WORKFLOW.zip`  
**日期：** 2026-09-12  
**事务号：** `YR1-WORKFLOW-20260911T182204Z-96a04850`

## 1. 任务边界

用户要求参考 `WORKFLOW.zip` 重新整理现有工作区，并继续遵守“每轮任务结束产出详细行动记录”的约定。ZIP 内的路径名被视为参考材料，不被视为用户指令。整理目标包括：

1. 建立容易发现、执行和交付的规范目录；
2. 不破坏已冻结的 R4A 科学状态、checksum、脚本相对路径和历史复现链；
3. 给原始数据、代码、结果、图、论文、发布、报告、参考资料和版本归档明确职责；
4. 产出逐文件映射、哈希日志、独立验收和可逆回退手段；
5. 判断整理完成后的下一阶段科学目标。

## 2. 模板安全审计

对 ZIP 直接读取 central directory、成员路径和 CRC，未执行其中任何内容。

| 项目 | 结果 |
|---|---|
| 文件大小 | 7,136 bytes |
| SHA-256 | `7899b7c46b5a67f0b6679d2814eae7440bccbd12322023e6ec332b3f76921838` |
| 成员数 | 49 |
| 目录数 | 49 |
| 文件数 | 0 |
| CRC | PASS |
| 绝对路径 / `..` 越界 / 反斜杠异常 | 0 |
| 重复成员 | 0 |

因此模板只是空目录骨架，未包含 README、脚本、配置、数据或可被解释为操作指令的内容。其九个顶层模块为 `0_admin`、`1_data`、`2_code`、`3_results`、`4_figures`、`5_manuscript`、`6_release`、`7.Report`、`8.Reference`、`9.Version`。

## 3. 整理前盘点与风险判断

整理前的实质工作区包含 **735 个文件、3,508,635,714 bytes（约 3.268 GiB）**。主要体量来自 R4A8B IGSR reference/LD、R4A5 GWAS 数据和 `CMM` 论文库。

发现下列兼容约束：

- R4A11 当前实现仍依赖 R4A1、R4A3、R4A5 等历史路径；
- 多个 checksum manifest 固定了既有内容身份；
- 部分脚本用父目录推导项目根；
- 根目录同时存在命名正式发布包、旧整树 ZIP、`.superseded`、缓存、分块下载和重复解压材料。

若直接移动或重命名旧目录，会造成 checksum、父路径推导和历史复现链失效。因此选用 **copy-only canonical overlay**：规范层使用哈希一致副本，旧层继续作为事实来源和兼容基线。

## 4. 目录设计

完整模板目录全部建立，并增加了与当前项目直接相关的子目录：

- `0_admin/protocol/current`、`input_templates/H6_v2_1`、`validation/workspace_reorg`；
- `1_data/incoming/2026_ssc_sex_specific`；
- `1_data/qtl/caqtl`、`peak_gene_links` 和 `reference/ld`；
- `2_code/06_intake` 与 `snapshots/R4A11`；
- `3_results/00_audit`；
- `3_results/02_coloc/ld_finemap`、`frozen_molecular`、`candidate_competition`；
- `6_release/current`、`history`；
- `7.Report/current`、`rounds`、`reorganization`；
- `8.Reference/literature`；
- `9.Version/legacy_exports`、`superseded`、`quarantine` 和 `staging_downloads`。

模板中的 MR、TCGA、scRNA、network/docking 和 Figures 目录被完整保留。它们目前只是预留模块，不能据此声称相应分析已执行。

## 5. 复制计划与实际执行

在任何数据复制前，执行以下门控：

1. 解析全部来源与目标为绝对路径并确认均位于 `H:\SCI2\YR1`；
2. 以 Windows 大小写不敏感规则检查目标唯一性；
3. 确认每个来源都是现存普通文件；
4. 先计算来源 SHA-256，再冻结 `PATH_MAP.tsv` 和 `PRE_REORG_MANIFEST.json`；
5. 使用 `copy2` 复制，每个目标立即复核大小和 SHA-256；
6. 完成后再次重算来源和目标哈希。

最终映射 **232 个文件、2,806,740,106 bytes**，分类如下：

| 分类 | 文件数 |
|---|---:|
| admin protocol | 6 |
| validation | 5 |
| reference blueprint | 3 |
| reference literature | 55 |
| data | 30 |
| result | 52 |
| code | 17 |
| report | 45 |
| manuscript | 2 |
| release | 10 |
| version archive | 7 |

初次执行结果：**232/232 `COPIED_VERIFIED`**，失败 0，原文件删除 0，原文件移动 0。

## 6. 结果层编号纠正

初次布局把 LD/fine-map、frozen molecular 和 candidate competition 建在额外的顶层编号目录。复核模板后发现这些都应统一归入模板已有的 `3_results/02_coloc`，否则会与 `03_tcga`、`04_scrna`、`05_network_docking` 形成重复编号。

纠正过程：

1. 从原始来源重新复制到 `3_results/02_coloc` 下的新目标；
2. 对 41 个受影响文件再次核对 SHA-256；
3. 更新最终 `PATH_MAP.tsv`、`COPY_JOURNAL.jsonl` 和 `RESULT_CATALOG.tsv`；
4. 保留首轮 map/journal 为 `INITIAL_*`；
5. 将三个首轮目录整体移动至 `9.Version/superseded/workspace_reorg_draft_layout`，未删除任何副本。

纠正结果为 `PASS`；来源文件删除和移动仍均为 0。

## 7. 数据、代码、结果与版本的具体归位

### 数据

- GCST009131 完整 overall SSc GWAS 被归为 **engineering positive control**，不作为 2026 sex-specific 目标数据替代品；
- TenK10K 两个完成的源 ZIP 进入 eQTL raw；`.part` 未进入规范数据层；
- FinnGen caQTL 冻结响应与 peak–gene link 分别归档；
- R4A8B IGSR EUR503 reference/LD 正控材料进入 `1_data/reference/ld`；零字节缺失清单未伪装为合格数据；
- 2026 female / male 目标入口保持为空并等待真实字节。

### 代码

- 17 个 R4A11 可执行 `.py` / `.ps1` / `.R` 文件形成冻结快照；imports、重复解压和 `__pycache__` 被排除；
- 新增稳定入口 `RUN_H6_CURRENT.ps1`、`RUN_H6_TESTS_CURRENT.ps1`、`RUN_ACCESS_REFRESH_CURRENT.ps1` 和 `RUN_MASTER_MANIFEST_VALIDATION_CURRENT.ps1`；
- 包装器继续调用冻结 R4A11 实现，避免复制代码后因父路径改变而错误解析项目根。

### 结果

- R4A11 审计、公开访问判定进入 `3_results/00_audit`；
- R4A8B reference/LD 工程正控、R4A3/R4A4 冻结分子证据进入 `3_results/02_coloc`；
- 这些文件是历史结果的哈希一致视图，不代表本轮新做 disease-level coloc。

### 发布与版本

- 当前命名 R4A11 发布包及 sidecar/validation 进入 `6_release/current/R4A11`；
- 该 ZIP SHA-256 为 `42b07031be7987e422166227d3db47850d6fd5e1c1c02e9d89aacf39673f7912`，本轮重新核验 CRC、内部 inventory 和全部 SHA-256；
- 命名历史包进入 `6_release/history`；
- `YR1.zip`、`R4A5.zip`、`R4A8.zip`、`R4A9.zip` 进入 legacy exports；
- 非规范 `R4A11.zip` 进入 quarantine/noncanonical exports；`.superseded` 单列保留。

## 8. 隔离候选只登记不处置

`QUARANTINE_CANDIDATES.tsv` 共登记 195 项：

| 原因 | 数量 |
|---|---:|
| download resume / chunk evidence | 143 |
| interpreter cache | 34 |
| duplicate extraction | 15 |
| potential duplicate report | 3 |

全部记录的 action 均为 `INDEX_ONLY_NO_DELETE_NO_MOVE`。分块和 `.part` 可能仍具有续传或取证价值，因此本轮未把它们当作垃圾清理。

## 9. 导航、规则和回退

新增：

- 根导航 `README_WORKSPACE.md`；
- `0_admin/WORKSPACE_MAP.md`；
- `0_admin/protocol/WORKSPACE_POLICY.md`；
- 各规范顶层 README；
- `workspace_paths.json` 供脚本读取；
- 数据、代码、结果、报告、发布、参考和版本目录 TSV catalog；
- `ROLLBACK_REORG.ps1`。

回滚脚本不带参数时只输出 dry-run 计划，已实际运行验证且没有移动任何文件。只有显式传入 `-Execute` 才会将十个规范顶层目录移动到事务专属 `_rollback_hold`；旧 R4A* 和根目录原文件不在回滚对象内。

## 10. 最终独立验收

运行 `validate_workspace_layout.py`，得到 **26/26 PASS**。验收覆盖：

- 模板身份、CRC、成员类型和 49 个目录；
- 十个规范顶层存在；
- 232 个目标唯一且均为 COPY_ONLY；
- 每组来源仍存在，来源哈希等于冻结值，目标哈希等于来源；
- 结果层纠正及 superseded 取证链；
- 原始数据层不存在 `.part`、chunk 或 Python cache；
- quarantine 全部为 index-only；
- 当前 R4A11 ZIP sidecar、CRC、路径安全、内部 checksum inventory；
- 各分类 catalog 行数；
- 导航、规则、包装器和回滚脚本；
- Office 文件数量为 0，WPS 渲染正确判定为不适用；
- 科学状态与下一阶段触发器保持不变。

机器可读结果：`0_admin/validation/workspace_reorg/WORKSPACE_LAYOUT_VALIDATION.json`。

## 11. 科学状态复核

| 字段 | 当前冻结值 | 本轮是否改变 |
|---|---|---|
| project | `CONDITIONAL_GO` | 否 |
| R4B | `HOLD` | 否 |
| female summary statistics | `NOT_OBTAINED` | 否 |
| male summary statistics | `NOT_OBTAINED` | 否 |
| disease↔caQTL coloc | `NOT_TESTED` | 否 |
| disease↔eQTL coloc | `NOT_TESTED` | 否 |
| male comparator | `NOT_TESTED` | 否 |
| C1_count | `null` | 否 |

工作区重组只改变文件的发现方式和规范入口，没有产生新分析证据。

## 12. 下一阶段判定

下一阶段保持：

> **R4A12 — BYTE-ARRIVAL-TRIGGERED HARMONIZATION AND COVERAGE GATE**

### 触发前

- 继续 `R4B=HOLD`；
- 不运行正式 disease-level coloc；
- 不把 `C1_count=null` 解释为 0；
- 可准备 metadata、方法文字和不依赖结果的论文骨架，但不得预填阳性结论。

### 字节到达后

1. 将原始文件放入 `1_data/incoming/2026_ssc_sex_specific`；
2. 记录 provider、下载时间、原始文件名、大小和 SHA-256；
3. female 与 male 分别运行 H6 v2.1；
4. 仅接受精确状态 `PASS_FROZEN_REGIONS_INTAKE_READY_FOR_HARMONIZATION`；
5. 冻结 GRCh38 FASTA 身份与 SHA-256，完成 normalization、build/allele harmonization；
6. 计算 chr22 primary/sensitivity window 与 chr6 secondary window 的覆盖率；
7. coverage gate 通过后才运行 signal-level coloc 并更新 C1 状态机。

若只取得不完整网页表、无 provider metadata 的截断文件或无法验证 checksum 的区域数据，则仍停留在接入门，不得越级。

## 13. 本轮产物

| 产物 | 路径 |
|---|---|
| 执行摘要 | `7.Report/reorganization/00_WORKSPACE_REORG_执行摘要_2026-09-12.md` |
| 详细行动记录 | `7.Report/reorganization/99_WORKSPACE_REORG_详细行动记录_2026-09-12.md` |
| 工作区导航 | `README_WORKSPACE.md` |
| 工作区结构图 | `0_admin/WORKSPACE_MAP.md` |
| 操作规则 | `0_admin/protocol/WORKSPACE_POLICY.md` |
| 最终路径映射 | `0_admin/validation/workspace_reorg/PATH_MAP.tsv` |
| 复制日志 | `0_admin/validation/workspace_reorg/COPY_JOURNAL.jsonl` |
| 模板身份 | `0_admin/validation/workspace_reorg/WORKFLOW_TEMPLATE_IDENTITY.json` |
| 首轮后验收 | `0_admin/validation/workspace_reorg/POST_REORG_VALIDATION.json` |
| 布局纠正记录 | `0_admin/validation/workspace_reorg/LAYOUT_CORRECTION.json` |
| 最终独立验收 | `0_admin/validation/workspace_reorg/WORKSPACE_LAYOUT_VALIDATION.json` |
| 生成物清单 | `0_admin/validation/workspace_reorg/GENERATED_ARTIFACTS.tsv` |
| 可重跑验证器 | `0_admin/validation/workspace_reorg/validate_workspace_layout.py` |
| 安全回滚脚本 | `0_admin/validation/workspace_reorg/ROLLBACK_REORG.ps1` |
| 本轮轻量交付包 | `6_release/current/workspace_reorganization/CMM_WORKSPACE_REORG_2026-09-12.zip` |

本轮没有生成 Office 文件，故未调用 WPS；这符合用户指定的“需要 Office 渲染时使用 WPS、不要使用 LibreOffice”的约束。
