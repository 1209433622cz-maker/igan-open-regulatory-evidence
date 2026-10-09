#!/usr/bin/env python3
"""Build QiTeng-governed R7B2A reports and deterministic release package."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"H:\SCI2\YR1")
REPORT = ROOT / "7.Report/rounds/R7B2A"
RELEASE = ROOT / "6_release/R7B2A"
DOWNLOADS = Path(r"C:\Users\Administrator\Downloads")
ZIP_NAME = "CMM_R7B2A_MatchedInputAttribution_ManuscriptLock_2026-10-09.zip"
ACTION_NAME = "99_CMM_R7B2A_详细行动记录_2026-10-09.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(name: str, text: str) -> Path:
    path = REPORT / name
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.mkdir(parents=True)

    summary = write("00_CMM_R7B2A_执行摘要_同输入归因与稿件锁定.md", r"""
# CMM R7B2A 执行摘要：同输入归因与稿件锁定

## 最终判定

```text
PBC_PRIMARY_PROJECT = GO
R7B2A = COMPLETE

V3-G0_INPUT_LOCK = PASS
V3-G1_CONTRAST_VALID = PASS
V3-G2_COVERAGE = PASS
V3-G3_SIMULATION_INTERPRETABLE = PASS_WITH_SCOPE_LIMIT
V3-G4_ATTRIBUTION = PASS
V3-G5_MANUSCRIPT_LOCK_ASSETS = PASS

NEW_LOCUS_GENE_CELL_SELECTION = 0
NEW_BIOLOGICAL_ANALYSIS_REQUIRED = NO

NEXT = R7B2_FULL_ENGLISH_MANUSCRIPT_V1
```

R7B2A 按 RP v3 固定的 642 个 comparison 完成 A0/A1/A2/M 桥接。A0 是历史 GCST + 原支持集 ABF；A1 只把支持集改为实际多信号集合；A2 再把疾病统计改为 GJOKA matched-z；M 为历史冻结的来源匹配多信号结果。没有按结果增加或删除位点、基因、细胞或比较。

## 中心结果

- 实际多信号支持集相对原 ABF 每项少 19–114 个变异，中位少 65 个，中位减少 7.67%。
- A0 可在最大绝对误差 `3.543e-13` 内重放，642/642 top shared variant 一致。
- 支持集变化 A0→A1 改变 15/642 个分类，但历史 112 个 H4 全部保留。
- 疾病统计变化 A1→A2 改变 19/642 个分类。
- 同输入 A2→M 中，79 个 H4 和 413 个 H3 保持；8 个 H4→H3，10 个 H3→H4。
- 历史 12 个方向反转中，10 个仍是严格方向反转；IL12RB1/NK 与 SYNGR1/NK 应改写为 A2 歧义态经 M 解析。
- 固定/原生 sdY 及 GJOKA matched-z/rounded BETA-SE 敏感性均为 0 个分类变化。

## 模拟解释

486,000 次主模拟没有技术错误。325,218 次没有 signal pair 的原因可定位为一侧或两侧未形成 credible set；两侧均有 credible set 却没有 pair 的次数为 0；160,782 次形成可评价 pair。模拟必须同时报告无条件性能与 pair-conditional 性能。次级 mismatch 分支没有保存逐侧 CS 计数，因此其 69,346 个 zero-pair fit 不作 no-CS 机制归因，也不为此重跑 81,000 次拟合。

## 稿件定位

最稳健的中心表述为：PBC-wide single-causal screening 之后，对预设 high-information subset 进行同输入、来源匹配的多信号重分类，并用真值已知模拟区分信号发现充分性与已形成 signal pair 后的判定行为。真实数据支持双向重分类，但不能证明哪种方法在真实对象中“正确”或普遍优越。
""")

    write("01_CMM_R7B2A_输入冻结_A0A1A2重算与身份验收.md", r"""
# R7B2A 输入冻结、A0/A1/A2 重算与身份验收

## 冻结对象

- 642 个 comparison；47 loci、200 genes、14 cell types。
- 原分层保持为 184 primary verification、455 H3 rescue/falsification、3 borderline calibration。
- RP v3 SHA-256：`310b307e5463825968ee93e52ca34fb997b6a28b81d79ce791d831fc6f18ed59`。
- 结果前冻结协议 SHA-256：`1295f072d192fa3ec22631c7a0e4ac247576d2bacc56ca32c599622594ef7c03`。

## 支持集与等位基因

每个 comparison 同时保存原 ABF 集 `S_A` 和实际多信号集 `S_M` 的有序成员、数量和 SHA-256。`S_A` 为 243–1,724 个变异，`S_M` 为 224–1,684 个；每项减少 19–114 个，中位减少 65 个。GJOKA A1 与 QTL/BIM 方向共 496,205 个 exact、2,350 个 flipped、0 unresolved。

## 六个输出臂

1. `A0_REPLAY`：GCST beta/SE、`S_A`、历史固定 sdY。
2. `A1_FIXED_SDY`：GCST beta/SE、`S_M`、固定 sdY。
3. `A1_NATIVE_SDY`：A1 的原生 `S_M` sdY 敏感性。
4. `A2_MATCHEDZ_FIXED_SDY`：GJOKA `STAT×SE`、`S_M`、固定 sdY。
5. `A2_MATCHEDZ_NATIVE_SDY`：A2 原生 sdY 敏感性。
6. `A2_ROUNDED_FIXED_SDY`：GJOKA source BETA/SE 舍入敏感性。

所有 3,852 行均为 PASS。A0 posterior 最大绝对误差为 `3.543e-13`，top shared variant 642/642 一致；A1/A2 没有技术失败。固定与原生 sdY、matched-z 与 rounded BETA/SE 均未造成分类变化。

## 边界

A2 与 M 的同输入比较消除了主要支持集和疾病统计定义不对称，但仍比较完整推断程序：单因果 Wakefield ABF 与 SuSiE/coloc.susie 的效应结构、credible set 构建和 posterior 汇总均不同，不能把 A2→M 简化为单一“因果变异个数”效应。
""")

    write("02_CMM_R7B2A_四臂轨迹归因与历史12项重判.md", r"""
# R7B2A 四臂轨迹归因与历史 12 项重判

## 相邻阶段变化

| 对照 | 被隔离的主要变化 | 分类变化 |
|---|---|---:|
| A0→A1 | 支持集 `S_A→S_M` | 15/642 |
| A1→A2 | GCST→GJOKA 疾病统计定义 | 19/642 |
| A2→M | 单因果 ABF→来源匹配多信号程序 | 139/642 全状态变化 |

相邻变化不是可加的因果分解。139 包含歧义、model-sensitive 与 uninformative 的迁移；论文的方向性主终点应单独报告严格 H4↔H3。

## 同输入方向性结果

```text
A2 H4 = 113
  stable H4      79
  H4 -> H3        8
  model-sensitive 4
  uninformative  22

A2 H3 = 452
  stable H3     413
  H3 -> H4       10
  model-sensitive 6
  uninformative  23
```

因此同输入主结果为 8 个 H4→H3 与 10 个 H3→H4。它们说明判定会随推断模型改变，不等于真实数据中存在 8 个假阳性或 10 个真阳性恢复。

## 历史 12 项

历史 4 个 H4→H3 和 8 个 H3→H4 中，10 个仍保持严格方向：FCRL3/CD8_ET、COLCA2/B_IN、IL12RB1/CD4_NC，以及 ELMO1/CD4_NC、IFITM2/NK、IFITM3/NK、RP11-326C3.12/CD4_NC、RIN3/Mono_NC、IFI30/Mono_NC、RPL3/NK。

IL12RB1/NK 在 A2 为 ambiguous，M 为 H3；SYNGR1/NK 在 A2 为 ambiguous，M 为 H4。这两项以后应写作 ambiguity resolution，不再写成严格 H4→H3 或 H3→H4。

## 论文含义

支持集和疾病统计来源确实解释了一部分历史状态变化，但没有消除模型差异。论文仍可保留“来源匹配多信号推断改变部分高信息比较的归因”，同时必须把旧的 4/8 更新为同输入 8/10，并保存旧分析作为方法演化记录。
""")

    write("03_CMM_R7B2A_R7B1C模拟错误_noCS_noPair终裁.md", r"""
# R7B2A：R7B1C 模拟错误、no-CS 与 no-pair 终裁

## 全量迭代审计

对 486,000 个原始迭代逐行重判：

| 通道 | 次数 |
|---|---:|
| technical error / nonconvergence | 0 |
| 两侧均无 credible set | 130,994 |
| disease 无 credible set | 16,819 |
| QTL 无 credible set | 177,405 |
| 两侧有 credible set 但无 pair | 0 |
| pair 可评价 | 160,782 |

主分析 pair-evaluable 比例为 33.08%。不同情景差异显著：S1 57.54%、S2 59.79%、S3 39.10%、S4 14.35%、S5 13.29%、S6 14.43%。

## 解释规则

无条件 H4 率同时反映“是否发现足够稳定的 credible set”和“形成 pair 后如何判定”。pair-conditional H4 率只描述已形成 pair 后的 estimator behavior。例如 S2 的无条件 H4 为 16.0%，但在可评价 pair 中为 26.76%；S5 分别为 1.12% 与 8.45%。二者都需报告，不能只选有利分母。

主模拟没有软件错误；大量 uninformative 是信号发现/可识别性不足。它也不应被写成生物学阴性。

## 次级 mismatch 分支

S6 mismatch 共有 81,000 次，技术错误为 0，其中 69,346 次没有 pair。历史 worker 没有保存 mismatch disease/QTL 的 CS 数量，无法再区分是哪一侧无 CS。该分支只用于有限的 matched-vs-mismatched decision sensitivity，不用于 no-CS 机制归因。由于主 matched 分支已能完成 RP v3 所需分解，且此缺口不改变中心结论，本轮不重复 81,000 次拟合。
""")

    write("04_CMM_R7B2A_ClaimLedger_MethodsResults与Figure1-6锁定.md", r"""
# R7B2A Claim Ledger、Methods–Results 与 Figure 1–6 锁定

## 更新资产

- 27 条 claim–evidence ledger：继承 22 条 R7B1E claim，修订同输入转移和模拟边界，新增 5 条 R7B2A claim。
- 10 条 Methods–Results mirror：输入冻结、支持集重构、A0 replay、A1/A2、A2→M、敏感性、模拟通道和外部/组织边界一一对应。
- Figure 1–6 manifest：Figure 2 更新为输入归因和同输入转移；Figure 3 更新为发现充分性与 pair-conditional 判定；Figure 4–6 的 IL12RB2、FCRL3 和肝组织边界保持不变。
- Figure 2/3 各生成 PNG、PDF、SVG 原型和独立 source-data TSV。

## 允许的中心主张

PBC-wide screen 包含 6,923 个比较，其中 5,460 个达到 ABF 可分析门；预设 642 个高信息比较接受来源匹配多信号重分类。同输入以后仍存在 8 个 H4→H3、10 个 H3→H4，并有 79 个 stable H4、413 个 stable H3。模拟说明误归因改善与 shared-signal recovery 损失依情景而变，并受 credible-set discovery 限制。

## 禁止的扩张

- 不写成全部 6,923 个比较都接受多信号分析。
- 不把真实数据重分类写成 truth-proven correction。
- 不声称多信号方法普遍优越。
- 不把 no-CS、no-pair、技术失败混写。
- 不把 IL12RB2/FCRL3 写成首次发现或完整调控级联。
- 不把 5 vs 5 肝组织 detectability 写成 PBC-specific enrichment 或组织介导。

## 稿件接口

下一稿按 Figure 1–6 顺序写 Results，并从同一 claim ledger 提取摘要、讨论和图注。缺少作者、单位、通讯、CRediT、Funding 与 Competing interests 的真实信息仍不填充，也不影响科学正文 v1 的启动。
""")

    write("05_CMM_R7B2A_R7B2完整英文稿下一阶段冻结目标.md", r"""
# R7B2A：R7B2 完整英文稿下一阶段冻结目标

## 下一阶段

```text
NEXT = R7B2_FULL_ENGLISH_MANUSCRIPT_V1
WRITING_ENGINE = QITENG_v0.3.24.2_ONLY
ARTICLE_TYPE = ORIGINAL_RESEARCH
POSITION = DISEASE_FOCUSED_EMPIRICAL_METHODS_EVALUATION
BIOLOGICAL_SCOPE = FROZEN
NEW_LOCUS_GENE_CELL_FISHING = NO
NEW_SIMULATION_SCENARIO = NO_BY_DEFAULT
```

## 必须完成

1. 以 unresolved attribution problem → A0/A1/A2/M matched-input design → PBC real-data reclassification → truth-known calibration → bounded external/tissue evidence → inference limits 构建英文 argument map。
2. 更新 Methods，使 `S_A`、`S_M`、GCST、GJOKA matched-z、fixed/native sdY、rounded sensitivity 和 M 的接口可复算。
3. Results 使用同输入主数值 15、19、8、10、79、413，并保留历史 12 的审计说明。
4. 模拟同时报告无条件与 pair-conditional 结果，明确 0 technical error、325,218 no-CS 和 160,782 pair-evaluable。
5. Figure 2/3 使用 R7B2A source data；Figure 4–6 继承冻结外部/组织边界。
6. 完成 numeric-token QA、claim-source QA、Methods–Results mirror、图注一致性和 hostile review。

## 不触发新计算的事项

次级 mismatch zero-pair 的逐侧 CS 计数缺失不构成重跑理由；作者信息和投稿接口字段等待真实信息；目标期刊格式在科学正文 v1 通过后确定。

## 出口

- 完整英文稿在 27 条 claim ledger 内闭环：进入 hostile manuscript audit 与期刊格式化。
- 出现可复现数字矛盾：仅回到对应 R7B2A source/ledger 修复。
- 不因行文困难重新打开疾病、位点、基因或细胞筛选。
""")

    action = write(ACTION_NAME, r"""
# CMM R7B2A 详细行动记录（2026-10-09）

## 本轮任务

按照 `PBC_研究计划书_RP_v3_调控归因可靠性与同输入方法对照_20261009.docx` 执行 `R7B2A_MATCHED_INPUT_ATTRIBUTION_AND_MANUSCRIPT_LOCK`。本轮目标是修复历史 ABF 与多信号分析存在的支持集和疾病统计输入不对称，核清模拟中的 technical-error/no-CS/no-pair 语义，并在不重开生物学筛选的前提下锁定完整英文稿接口。

学术写作与报告组织使用 QiTeng Academic Writing Skill v0.3.24.2，没有调用 CC skill。RP v3 作为计划与约束来源，不作为结果证明。DOCX 本轮只读取和核验，没有修改或重新渲染，因此没有调用 LibreOffice；后续如生成 DOCX，按用户要求使用 WPS 后台渲染。

## 结果前冻结

在读取 A1/A2 新结果前建立 `R7B2A_matched_input_attribution_freeze_2026-10-09.md`，固定：

- 642 IDs 和 184/455/3 角色；
- A0/A1/A2/M 的唯一变量；
- fixed sdY 主分析和 native sdY 敏感性；
- GJOKA matched-z 主定义和 rounded BETA/SE 敏感性；
- ABF prior、分类门和失败状态；
- simulation error/no-CS/no-pair 分离规则；
- V3-G0–G5 通过条件。

协议 SHA-256 为 `1295f072d192fa3ec22631c7a0e4ac247576d2bacc56ca32c599622594ef7c03`。RP v3 SHA-256 为 `310b307e5463825968ee93e52ca34fb997b6a28b81d79ce791d831fc6f18ed59`。

## 输入身份恢复

对每个 comparison 复原原 ABF 支持 `S_A` 和历史多信号 runner 实际使用的 `S_M`，并保存有序成员、数量及 SHA-256。身份结果为：

```text
comparisons = 642
loci = 47
genes = 200
cells = 14

S_A = 243–1,724
S_M = 224–1,684
removed = 19–114
median removed = 65
median reduction = 7.67%

GJOKA A1 exact = 496,205
GJOKA A1 flipped = 2,350
GJOKA unresolved = 0
```

V3-G0 PASS。

## A0/A1/A2 重算

使用历史 Wakefield ABF 公式、`p1=p2=1e-4`、`p12=1e-6/1e-5/1e-4`、疾病 prior SD 0.2、QTL prior SD `0.15×sdY`，运行 642×6=3,852 行。

- A0 replay 最大 posterior 绝对差 `3.543e-13`；top shared variant 642/642 一致。
- A1/A2 技术失败为 0。
- A1 fixed/native 分类变化 0。
- A2 fixed/native 分类变化 0。
- A2 matched-z/rounded 分类变化 0。

V3-G1 与 V3-G2 PASS。

## 四臂轨迹归因

A0→A1 的支持集变化造成 15 个分类变化，但 112 个历史 H4 全部保留。A1→A2 的疾病统计定义变化造成 19 个分类变化。A2→M 的同输入 full-procedure 对照中：

```text
stable H4 = 79
stable H3 = 413
H4 -> H3 = 8
H3 -> H4 = 10
model/other state changes included in all-state total = 139
```

历史 12 个方向变化有 10 个严格保留。IL12RB1/NK 与 SYNGR1/NK 在 A2 为 ambiguous，分别被 M 解析为 H3 与 H4，后续不再列入严格方向反转。

这支持“输入协调解释一部分历史变化，但不能解释全部模型差异”。真实数据没有真值，8/10 不能写作纠错率。V3-G4 PASS。

## 模拟通道审计

逐行读取 486,000 次原始迭代。主 matched 分支：

```text
technical errors = 0
no CS both = 130,994
no disease CS = 16,819
no QTL CS = 177,405
both CS but no pair = 0
pair evaluable = 160,782 (33.08%)
```

因此现有迭代输出足以区分主分析 error/no-CS/no-pair，无需重跑。次级 mismatch 分支的 69,346 个 zero-pair fit 缺少逐侧 CS 数量；该缺口通过限制 mismatch 机制主张处理，不重复 81,000 次拟合。V3-G3 为 `PASS_WITH_SCOPE_LIMIT`。

## 稿件锁定资产

在 R7B1E 22 条 ledger 基础上更新为 27 条；生成 10 条 Methods–Results mirror；更新 Figure 1–6 source manifest；Figure 2/3 生成 TSV、PNG、PDF 和 SVG 原型。FCRL3/CD8_ET 在 A0、A1、A2 均为 H4，在 M 为 H3，因此继续作为同输入模型反例。IL12RB2/FCRL3 外部证据与 5 vs 5 tissue boundary 不改变。

V3-G5 manuscript assets PASS。独立 QA 53/53 PASS；两个 PNG 已目视检查，标签、计数和图例可读。

## 本轮代码

```text
01_freeze_r7b2a_inputs.py
02_run_r7b2a_matched_input_abf.py
03_adjudicate_r7b2a_trajectories.py
04_audit_r7b1c_simulation_channels.py
05_build_r7b2a_manuscript_lock_assets.py
06_independent_qa_r7b2a.py
07_build_r7b2a_reports_release.py
```

Python 脚本全部通过 `py_compile`。绘图脚本使用本地具备 matplotlib 的 `D:\bioinfor\python.exe`；统计与 QA 使用 Codex bundled Python。没有新增下载、没有改动第三方原始大文件、没有 posterior refit、没有候选扩张。

## 异常与边界

1. 历史 ABF 与 M 不仅方法不同，支持集和疾病统计也不同；已由四臂设计修复。
2. 历史 mismatch simulation 未存逐侧 CS 计数；只限制次级主张，不影响主 matched 通道审计。
3. A2→M 是 full-procedure 对照，不是“只改变 causal count”。
4. 真实 PBC 数据的状态转移没有真值，不能用于声称普遍方法优越性。
5. 作者、单位、通讯、CRediT、Funding 和 Competing interests 仍未由真实人员信息补齐。

## 最终状态与下一阶段

```text
R7B2A = COMPLETE
PBC_PRIMARY_PROJECT = GO
R7B2_FULL_ENGLISH_MANUSCRIPT_V1 = GO

NEW_BIOLOGICAL_ANALYSIS = HOLD
NEW_LOCUS_GENE_CELL_FISHING = NO
SIMULATION_RERUN = NO
```

下一阶段直接按 27 条 ledger、10 条 Methods–Results mirror 和更新的 Figure 1–6 source universe 写完整英文原创研究稿。若写作中出现证据缺口，只修复对应 ledger/source，不重新扩展候选。
""")

    # Keep the user-requested per-round record in the workspace root as well.
    shutil.copy2(action, ROOT / ACTION_NAME)

    readme = RELEASE / "README_R7B2A.md"
    readme.write_text(
        "# R7B2A release\n\n"
        "Matched-input A0/A1/A2/M attribution, R7B1C channel audit, manuscript-lock assets and 53-check independent QA.\n\n"
        "This package contains derived/openly shareable code, manifests, aggregate outputs, reports and figures. It does not redistribute third-party raw GWAS/QTL/genotype data.\n",
        encoding="utf-8",
    )

    include = []
    include.extend(REPORT.glob("*.md"))
    include.append(ROOT / "0_admin/protocols/R7B2A/R7B2A_matched_input_attribution_freeze_2026-10-09.md")
    include.extend(sorted((ROOT / "2_code/06_intake/r7b2a").glob("*.py")))
    include.extend(sorted((ROOT / "3_results/00_audit/R7B2A/input_freeze").glob("*")))
    include.extend(sorted((ROOT / "3_results/00_audit/R7B2A/final_qa").glob("*")))
    include.extend(sorted((ROOT / "3_results/04_integration/R7B2A/matched_input_abf").glob("*")))
    include.extend(sorted((ROOT / "3_results/04_integration/R7B2A/adjudication").glob("*")))
    include.extend(sorted((ROOT / "3_results/04_integration/R7B2A/manuscript_lock").glob("*")))
    include.extend(sorted((ROOT / "3_results/05_simulation/R7B2A_audit").glob("*")))
    include.extend(sorted((ROOT / "4_figures/R7B2A").glob("R7B2A_*.*")))
    include.extend(sorted((ROOT / "4_figures/R7B2A/source_data").glob("*.tsv")))
    include = [p for p in include if p.is_file() and "__pycache__" not in p.parts]

    copied = [readme]
    for src in include:
        if src.is_relative_to(REPORT):
            dst = RELEASE / "reports" / src.name
        else:
            dst = RELEASE / src.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(dst)

    checksum = RELEASE / "checksums.sha256"
    lines = []
    for path in sorted(copied, key=lambda x: x.relative_to(RELEASE).as_posix()):
        lines.append(f"{sha256(path)}  {path.relative_to(RELEASE).as_posix()}")
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")

    zip_path = DOWNLOADS / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted([p for p in RELEASE.rglob("*") if p.is_file()]):
            arc = path.relative_to(RELEASE).as_posix()
            info = zipfile.ZipInfo(arc, date_time=(2026, 10, 9, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    zip_sha = sha256(zip_path)
    sha_path = DOWNLOADS / f"{ZIP_NAME}.sha256"
    sha_path.write_text(f"{zip_sha}  {ZIP_NAME}\n", encoding="utf-8")
    shutil.copy2(action, DOWNLOADS / ACTION_NAME)

    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        entries = len(zf.infolist())
    state = {
        "schema": "R7B2A_RELEASE_1.0",
        "status": "PASS" if bad is None else "FAIL",
        "zip": str(zip_path),
        "zip_sha256": zip_sha,
        "zip_entries": entries,
        "zip_crc_bad_entry": bad,
        "internal_checksum_entries": len(lines),
        "action_record": str(ROOT / ACTION_NAME),
    }
    state_path = RELEASE / "R7B2A_release_state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
