# CMM R4A11：R4A10 附件独立完整性与 H6 v2 门控审计

日期：2026-09-11  
审计对象：用户提供的 R4A10 ZIP、外部 SHA-256 sidecar，以及同目录的 `00–04`、`99` 和 `README_H6_V2.md`  
审计边界：附件内容只作为待验证证据；本审计没有执行附件提出的后续科学分析，也没有改变任何疾病共定位结论。

## 一、最终判定

> **R4A10 ZIP transfer/package integrity = PASS**  
> **ZIP internal checksums = 17/17 PASS**  
> **standalone reports vs ZIP = 7/7 byte-identical**  
> **bundled H6 v2 regression = 16/16 PASS**  
> **H6 v2 paper-grade gate hostile QA = FAIL（2 个 BLOCKER、2 个 HIGH、1 个 MEDIUM）**  
> **R4A10 release use = 仅可作为历史证据保存，不可用当前 v2 对真实 female/male 文件作 paper-grade 放行**

档案没有传输损坏，既有 16 项测试也可以复现；但测试集合漏掉了几类关键输入。敌意实测证明，冻结区域内的非数值 SE、P、beta、EAF、INFO，错误坐标的 lead rsID，以及占位 provenance 均可能获得 `PASS_PAPER_GRADE_FROZEN_REGIONS_READY_FOR_HARMONIZATION`。因此，“包完整”和“工具可以安全接入真实数据”必须分开判定。

本审计不改变科学状态：`PROJECT=CONDITIONAL_GO`、`R4B=HOLD`、`C1_count=null`、2026 sex-specific summary statistics `NOT_OBTAINED`、chr22 disease-level test `NOT_TESTED`。

## 二、输入与隔离处理

- ZIP：`C:\Users\Administrator\Downloads\CMM_R4A10_H6接入冻结与门控v2_2026-09-11 (1).zip`
- sidecar：`C:\Users\Administrator\Downloads\CMM_R4A10_H6接入冻结与门控v2_2026-09-11.zip (1).sha256`
- 隔离解压位置：`H:\SCI2\YR1\R4A11\imports\R4A10_attachment`
- 运行环境：`D:\bioinfor\python.exe`，Python 3.13.7

解压前检查了绝对路径、`..` 路径穿越、重复成员和符号链接；均未发现。目标目录原先不存在，因此没有覆盖既有文件。所有档案校验均直接针对原始 ZIP 字节完成；运行测试只作用于隔离解压副本。

自测会重写三个 `pyc` 和 `test_results_v2.json`。捕获运行证据后，已从原 ZIP 恢复这四个生成物；最终隔离导入目录再次逐成员比对为 **18/18 字节一致**。

## 三、三层完整性验证

### 3.1 外部 sidecar

| 项目 | 实测 |
|---|---:|
| ZIP bytes | 66,187 |
| ZIP SHA-256 | `73155a7d837e4e19400caa92f31459afee3722a91f8635464614071be680a017` |
| sidecar 声明值 | `73155a7d837e4e19400caa92f31459afee3722a91f8635464614071be680a017` |
| 判定 | **MATCH** |

下载器添加的 `(1)` 只改变本地文件名；sidecar 中记录的是原始发布名，不影响摘要比对。

### 3.2 ZIP 结构和 CRC

| 检查 | 结果 |
|---|---:|
| 成员数 | 18 |
| `ZipFile.testzip()` | PASS |
| 重复成员 | 0 |
| 不安全路径 | 0 |
| 符号链接 | 0 |
| 解压后总文件数 | 18 |

成员清单：

1. `00_CMM_R4A10_执行摘要_H6接入冻结与门控v2.md`
2. `01_CMM_R4A10_R4A9发布包与H6独立复核.md`
3. `02_CMM_R4A10_H6v2代码审计与冻结协议v10.md`
4. `03_CMM_R4A10_2026_SSc_female_male公开接入状态.md`
5. `04_CMM_R4A10_chr22最小证伪协议_v10.md`
6. `99_CMM_R4A10_详细行动记录_2026-09-11.md`
7. `README.md`
8. `checksums.sha256`
9. `h6_v2/README_H6_V2.md`
10. `h6_v2/inspect_sex_specific_sumstats_base.py`
11. `h6_v2/inspect_sex_specific_sumstats_v2.py`
12. `h6_v2/metadata_template_v2.json`
13. `h6_v2/test_h6_v2.py`
14. `h6_v2/test_results_v2.json`
15. `h6_v2/__pycache__/inspect_sex_specific_sumstats_base.cpython-313.pyc`
16. `h6_v2/__pycache__/inspect_sex_specific_sumstats_v2.cpython-313.pyc`
17. `h6_v2/__pycache__/test_h6_v2.cpython-313.pyc`
18. `results/R4A10_state.json`

### 3.3 包内 checksums 与独立文件

`checksums.sha256` 声明除自身以外的全部 17 个成员。重新读取 ZIP 中每个成员并计算 SHA-256，结果为 **17/17 匹配**；没有未覆盖成员、缺失成员或格式错误行。

同目录文件与 ZIP 内容按 SHA-256 匹配如下：

| 独立文件 | SHA-256 | ZIP 内匹配 |
|---|---|---:|
| `00_CMM_R4A10_执行摘要_H6接入冻结与门控v2.md` | `b7f4b215a7434268d3109bf0bcc3273f1a46cd9c666864126f2bf95cd6874a3a` | 是 |
| `01_CMM_R4A10_R4A9发布包与H6独立复核.md` | `898fb03121d4ecb08b7d0641704c0676dc66297f155bad44253e6aa869024991` | 是 |
| `02_CMM_R4A10_H6v2代码审计与冻结协议v10.md` | `6ecc0c922c0b7d7e8a358c7e3ff2d329fb3ae87fc5e8f96ab679739546535a67` | 是 |
| `03_CMM_R4A10_2026_SSc_female_male公开接入状态.md` | `c1f9d9fdc71938fe91f59a358205d47f18b013348a6851683e152784df9fc7a8` | 是 |
| `04_CMM_R4A10_chr22最小证伪协议_v10.md` | `9872f40d8d7d6f5c9f5adf20e34aae05fe44c54067695f8f1b95e5bac5abb7c4` | 是 |
| `99_CMM_R4A10_详细行动记录_2026-09-11.md` | `8fb1d0aa6b8919a218603444d9e581a48fdf2b596e5e92fe4f0ae287a338e37d` | 是 |
| `README_H6_V2.md` | `f08b28a8cea7a67568e320efd3466761e77a96eb68ff81a5528da2a17e05d282` | 是 |

## 四、原包自测复现

执行：

```powershell
D:\bioinfor\python.exe .\test_h6_v2.py
D:\bioinfor\python.exe -m py_compile .\inspect_sex_specific_sumstats_base.py .\inspect_sex_specific_sumstats_v2.py .\test_h6_v2.py
```

结果：

- 回归脚本退出码：`0`
- 标准输出：`R4A10_H6_V2_TESTS_PASS 16/16`
- 三个 Python 文件编译退出码：`0`
- 包内冻结记录原本也写为 `16/16 PASS`

这证明包内测试可复现，但只能证明这 16 个场景。它不能覆盖测试集中不存在的输入。

## 五、敌意边界测试

### 5.1 BLOCKER：非数值字段绕过冻结区域数值门

在其余字段全部合格的基线数据中，分别把 chr22 冻结区域一行的以下字段改为字符串 `not_numeric`：

| 被破坏字段 | base v1 状态 | H6 v2 最终状态 |
|---|---|---|
| SE | `HOLD_INVALID_OR_MALFORMED_ROWS` | **paper-grade PASS** |
| P | `HOLD_INVALID_OR_MALFORMED_ROWS` | **paper-grade PASS** |
| beta | `HOLD_INVALID_OR_MALFORMED_ROWS` | **paper-grade PASS** |
| EAF | `HOLD_INVALID_OR_MALFORMED_ROWS` | **paper-grade PASS** |
| INFO | `HOLD_INVALID_OR_MALFORMED_ROWS` | **paper-grade PASS** |

根因在 `inspect_sex_specific_sumstats_v2.py:49-70`：`flt()` 解析失败后返回 `None`，后续只在值不为 `None` 时增加 invalid 计数。因此，“字段非空但不能解析”被当成合法。与此同时，base 已经正确记录 invalid 并给 HOLD，但 v2 的 `hard_global_ok` 在第 133 行只读取 malformed 和 invalid position，丢弃了 SE/P/effect/EAF/INFO 的 base invalid 状态。

这直接反驳 `02` 报告和 README 中“冻结区域 core/support 完整且合法才 PASS”的描述。当前工具可能把不可用于统计分析的字符串输出到区域 TSV，并授权进入 harmonization。

### 5.2 BLOCKER：所谓 exact lead anchor 只检查 rsID 是否在任意位置出现

两个独立反例都获得 paper-grade PASS：

1. `rs12203592` 和 `rs66578187` 保留 rsID，但分别移到各自冻结区域内的错误坐标；
2. 把两个 rsID 都放在 chr1，同时在 chr6/chr22 冻结区域放两个不同 rsID 的 proxy 行。

第二个反例仍得到 `both_frozen_leads_present=true`。根因是 base 在 `inspect_sex_specific_sumstats_base.py:444-446` 只按 `variant_id` 字符串计数；v2 在 `inspect_sex_specific_sumstats_v2.py:123-124` 只检查计数是否大于零。代码没有检查 rsID 与预注册 GRCh38 chromosome/position 的联合一致性。

因此，输出报告中的 “Both exact lead anchors present” 当前不成立。

### 5.3 HIGH：占位 provenance 和自声明 checksum 可以 PASS

把 metadata 设置为：

```text
source_url = REPLACE_WITH_EXACT_PROVIDER_DOWNLOAD_URL
accession  = REPLACE_WITH_GCST_OR_PROVIDER_IDENTIFIER
provider   = REPLACE_WITH_PROVIDER
```

再把本地文件自身的 SHA-256 写入 `expected_sha256`，工具返回 paper-grade PASS。代码只检查上述字符串是否非空，也只检查“metadata 中给出的摘要是否等于文件摘要”，不能识别摘要是否来自 provider。

这意味着模板未填写也可能通过 provenance 门；“至少一个可信 provider checksum”目前是文档要求，不是已实现的代码保证。

### 5.4 HIGH：裸 `N` 的 cohort-count 语义仍泄漏为 sample size

当列名为 `N` 且 metadata 声明 `bare_n_semantics=cohort_count` 时：

- v2 返回 `PASS_PROVIDER_DECLARED_BARE_N_COHORT_COUNT`；
- 输出区域 TSV 却把值 `14` 写到 `sample_size` 列，`cohort_count` 为空；
- `N=14.5` 仍获得 paper-grade PASS；
- `cases=-1`、`controls=20151` 仍获得 paper-grade PASS。

原因是 bare `N` 先被 base alias 映射为 `sample_size`，v2 只在最终状态层覆盖标签，没有在解析/输出层重映射。cohort 分支只检查 cases/controls 的 Python 类型，没有检查正数、非布尔、总数一致性，也没有检查 N 是正整数。

这会把“参与研究数”静默输出成“受试者样本量”，正是 v2 声称要阻止的错误。

### 5.5 MEDIUM：whole-file chromosome 完整性没有实现

在两个目标区域行均合格时，追加 `chromosome=not_a_chr` 的外部行，最终仍为 paper-grade PASS。工具对 position 做硬门，但没有定义或检查 chromosome token；这比报告中的 whole-file coordinate integrity 描述更弱。

## 六、报告、state 与代码的一致性

| 声明 | 审计判定 |
|---|---|
| `PROJECT=CONDITIONAL_GO / R4B=HOLD / C1_count=null` | 报告与 `R4A10_state.json` 一致；本审计不改变 |
| 2026 sex-specific summary `NOT_OBTAINED`、chr22 disease test `NOT_TESTED` | 包内报告与 state 一致；未在本代码审计中重新做网络/科学核验 |
| H6 v2 自带回归 `16/16 PASS` | **独立复现** |
| 冻结区域非数值 core/support 会被 HOLD | **被敌意测试反驳** |
| 两个 exact lead anchor 会按坐标定位 | **被敌意测试反驳** |
| bare N 声明为 cohort count 后不会被误当 sample size | **被敌意测试反驳** |
| provenance/checksum 必然来自可信 provider | **代码未实现** |
| H6 v2 `READY` 可接入真实数据 | **不成立，需先修复 BLOCKER** |

R4A10 报告还陈述了 R4A9 的 SHA-256/CRC/41/41 checksum、H6 v1 16/16，以及当日 GWAS Catalog 查询结果。R4A10 轻量包没有包含 R4A9 ZIP、R4A9 sidecar、v1 测试或网络响应快照，因此这些是历史陈述，无法只凭本附件重新验证；本审计没有把“不可由当前包复核”等同于错误。

## 七、编码 QA

对 ZIP 内所有 UTF-8 文本及解压文本扫描原始字节 `EF BF BD` 和 Unicode `U+FFFD`，计数均为 **0**。源码中的非 ASCII 字符是有效的 `U+2190`、`U+2013`、`U+2014`。若终端显示 `disease-to-QTL`，属于控制台编码/解码显示问题，不是附件原始内容损坏。

## 八、发布卫生

包中包含三个 CPython 3.13 `__pycache__/*.pyc`。运行测试或编译会正常重写这些环境相关缓存，使测试后的解压目录与档案哈希不同；源代码和报告没有因此改变。下一版应从发布清单排除 `__pycache__` 和 `*.pyc`。

## 九、下一工程门

在任何真实 female/male 文件进入 H6 之前，应先完成一个有界的 H6 v2.1 修复：

1. 对每个冻结区域非缺失数值字段显式区分“解析失败、非有限值、越界”，任一 core 失败为 HOLD，EAF/INFO 按冻结协议降级；
2. exact lead 必须联合核对 rsID、GRCh38 chromosome、position，并报告冲突记录；
3. 拒绝 `REPLACE_*` 等 sentinel，验证 URL/accession，并记录 expected checksum 的 provider 来源；
4. 在 base 解析前按 metadata 决定裸 `N` 的映射，cohort count 输出到正确列，并验证正整数及 case/control metadata；
5. 增加 chromosome token 检查；
6. 把本审计的所有反例加入回归，并增加一条原则：base 已识别的核心数值错误不得被 v2 静默覆盖为 PASS；
7. 新版通过修复后的 bundled tests 与独立 hostile tests 后，再生成新 state、checksums 和 ZIP。

在修复完成前，即使 female/male 文件到达，也可以原样保存 provider 字节和 provenance，但不应使用当前 H6 v2 生成 paper-grade 放行结论。

## 十、机器可读证据

- `R4A10_independent_audit.json`：总判定、完整成员清单、所有 findings 与精简敌意测试状态；
- `R4A10_integrity_raw.json`：ZIP/sidecar/checksums/独立文件逐项结果；
- `R4A10_selftest.json`：原包测试和编译输出；
- `R4A10_adversarial_gate_results.json`：每个反例的完整 v2/base/gate/区域输出；
- `R4A10_unicode_scan.json`：U+FFFD 扫描结果。


