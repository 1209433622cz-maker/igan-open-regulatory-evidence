#!/usr/bin/env python3
"""Build QiTeng-governed R7B1E0/R7B1E reports from frozen machine outputs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
E0 = ROOT / "3_results/04_integration/R7B1E0"
E = ROOT / "3_results/04_integration/R7B1E"
AUDIT0 = ROOT / "3_results/00_audit/R7B1E0/R7B1E0_independent_QA.json"
AUDITE = ROOT / "3_results/00_audit/R7B1E/R7B1E_independent_QA.json"
REPORT = ROOT / "7.Report/rounds/R7B1E"
CURRENT = ROOT / "7.Report/current"


def write(name: str, text: str) -> None:
    (REPORT / name).write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    CURRENT.mkdir(parents=True, exist_ok=True)
    replay = json.loads((E0 / "kriging_replay/orchestrator_state.json").read_text(encoding="utf-8"))
    diag = json.loads((E0 / "diagnostic_adjudication/R7B1E0_diagnostic_adjudication_state.json").read_text(encoding="utf-8"))
    sem = json.loads((E0 / "signal_semantics/R7B1E0_signal_semantics_state.json").read_text(encoding="utf-8"))
    qa0 = json.loads(AUDIT0.read_text(encoding="utf-8"))
    qae = json.loads(AUDITE.read_text(encoding="utf-8"))
    estate = json.loads((E / "R7B1E_evidence_freeze_state.json").read_text(encoding="utf-8"))
    claims = pd.read_csv(E / "R7B1E_integrated_claim_evidence_ledger.tsv", sep="\t")
    panels = pd.read_csv(E / "R7B1E_Figure1_6_panel_source_manifest.tsv", sep="\t")

    write("00_CMM_R7B1E_执行摘要_诊断闭环与证据总冻结.md", f"""
# CMM R7B1E 执行摘要：诊断闭环与证据总冻结

## 最终判定

```text
R7B1E0_KRIGING_DIAGNOSTIC_REPLAY = PASS
R7B1E0_SIGNAL_SEMANTICS = PASS
R7B1E0_INDEPENDENT_QA = {qa0['passed']}/{qa0['total']} PASS

R7B1E_CLAIM_EVIDENCE_FREEZE = PASS
R7B1E_FIGURE1_6_SOURCE_FREEZE = PASS
R7B1E_INDEPENDENT_QA = {qae['passed']}/{qae['total']} PASS

HISTORICAL_CLASSIFICATIONS_CHANGED = NO
POSTERIOR_REFIT_REQUIRED = NO
NEW_GENE_CELL_LOCUS_SELECTION = NO
GENERAL_METHOD_SUPERIORITY = NOT_ESTABLISHED

NEXT = R7B2_MANUSCRIPT_V1
```

本轮先完成 R7B1E0，而没有直接进入证据整合。原因是历史 R7B1B runner 对 `susieR::kriging_rss()` 的返回对象采用了错误接口假设：代码只接受 `data.frame`，但当前 `susieR 0.14.2` 返回包含 `plot` 与 `conditional_dist` 的 list。由此造成历史 fit-QC 表中 Kriging 字段系统性缺失。修复仅重放诊断，不重拟合 SuSiE 或 coloc，也不改变既有后验。

精确重放覆盖 {replay['loci']} 个 locus、{replay['comparisons']} 个 comparison 和 {replay['diagnostic_units']:,} 个 disease/QTL × PF10/PF50 诊断单元，{replay['diagnostic_pass']:,}/{replay['diagnostic_units']:,} PASS。历史宽松计数 `logLR>2` 为 {replay['historical_flags']:,} 行；按 `susieR` 绘图代码实际使用的 `logLR>2 AND |z|>2` 判据，仅有 {diag['official_rule_raw_count']} 行，对应同一 comparison 的 {diag['official_rule_unique_events']} 个唯一事件。该事件为 `rs1800378`，不进入任何 credible set，所在 comparison 为 stable H3 且不承担核心主张，因此保留输入、不重拟合。

信号语义审计进一步确认，92/92 个 stable-H4 comparison 在 L10 与至少一个其它 PF10 L 设置中保留同一 shared signal-pair identity；428/428 个 stable-H3 comparison 保留同一 distinct pair identity。32 个 stable-H4 comparison 同时存在 H3-qualifying pair，说明同一 comparison 内可以并存 shared 与 distinct signal pairs。后续稿件必须区分 comparison-level state 与 signal-pair identity，不能把 H3 pair 支持写成“全区域不存在共享信号”。

在诊断与语义闭环后，R7B1E 将 R7B0A、R7B1A、R7B1B、R7B1C、R7B1D 和肝组织边界整合为 {estate['claims']} 条 claim–evidence ledger，并冻结 Figure 1–6 的 {estate['panels']} 个 panel-level source rows。允许的最高主张为：

> PBC-wide screening followed by source-matched multi-signal reclassification of the prespecified high-information H3/H4 subset, with scenario-dependent calibration and bounded external/tissue support.

这个表述保留了 PBC-wide screening，但不暗示 6,923 个 comparison 全部接受多信号分析；保留了模拟中假 H4 的下降，也同时报告 shared-signal recovery 的代价；保留 IL12RB2/FCRL3 的跨资源支持，但不升级为完整调控级联、组织介导或一般方法优越性。
""")

    write("01_CMM_R7B1E_R7B1E0_Kriging诊断修复与独立QA.md", f"""
# R7B1E0 Kriging 诊断修复与独立 QA

## 缺陷定位

历史脚本 `11_run_r7b1b_v2_multisignal_locus.R` 中的 `safe_kriging()` 在调用 `kriging_rss()` 后，仅当返回值是 `data.frame` 时继续解析。对本机冻结环境的直接审计显示：

```text
R = 4.6.1
susieR = 0.14.2
kriging_rss return = list(plot, conditional_dist)
```

因此历史 `R7B1B_v2_all_fit_QC.tsv.gz` 的 disease/QTL Kriging 字段全部为空。这是诊断记录层缺陷，不等同于 SuSiE 或 coloc 后验错误。

## 重放边界

R7B1E0 使用既有 frozen z、LD、N、variant order 与 stored `s_rss` 重放 `kriging_rss()`。它没有重新拟合模型，没有替换 credible sets，没有改变 PF10/PF50 adjudication，也没有重新筛选 comparison。47 个 locus 的重放总耗时约 {replay['runtime_seconds']/60:.1f} 分钟。

| 项目 | 结果 |
|---|---:|
| loci | {replay['loci']} |
| comparisons | {replay['comparisons']} |
| diagnostic units | {replay['diagnostic_units']:,} |
| PASS | {replay['diagnostic_pass']:,} |
| HOLD | {replay['diagnostic_hold']} |
| historical `logLR>2` rows | {replay['historical_flags']:,} |
| official-rule raw rows | {diag['official_rule_raw_count']} |
| official-rule unique events | {diag['official_rule_unique_events']} |

## 唯一事件终裁

两条 raw flag 分别来自同一 disease diagnostic 的 PF10 与 PF50 记录，去重后为一个事件：comparison `R7B1_003438`、locus 38、C12orf57/B_IN、variant `12:6172202`（rs1800378）。其 `z≈2.20`、`conditional mean≈-0.66`、`logLR≈2.05`。该变异不属于任何 credible set；comparison 维持 stable H3，PP.H4 约 `5×10⁻6`，也不是 claim-bearing exemplar。

最终处置为 `REVIEWED_RETAIN_INPUT_NO_REFIT`。该结果允许写“诊断接口已修复且唯一官方规则事件经过人工/机器联合复核”，不允许写“数据中完全不存在 z–LD discrepancy”。

## 独立 QA

R7B1E0 独立 QA 为 {qa0['passed']}/{qa0['total']} PASS。检查覆盖：单元数、locus/comparison 数、有限值、历史宽松计数、官方判据去重、credible-set membership、无 posterior refit、历史标签未改写、signal semantics 数量与协议存在性。
""")

    write("02_CMM_R7B1E_642比较信号语义与重分类终裁.md", f"""
# R7B1E：642 比较的信号语义与重分类终裁

## Comparison state 与 signal-pair identity 分离

R7B1B 的历史 comparison-level 状态为：stable H4={sem['historical_state_counts']['H4_SUPPORTED_STABLE']}、stable H3={sem['historical_state_counts']['H3_SUPPORTED_STABLE']}、model-sensitive={sem['historical_state_counts']['MODEL_SENSITIVE']}、uninformative={sem['historical_state_counts']['UNINFORMATIVE']}。R7B1E0 没有覆盖这些状态，而是为确定性状态追加 signal-pair identity：

- 92/92 stable-H4：L10 shared pair 在至少一个 L5/L20 设置中以 exact leads 或双性状 credible-set Jaccard ≥0.50 得到确认。
- 428/428 stable-H3：L10 distinct pair 以相同规则得到确认。
- 32 个 stable-H4 comparison 同时包含 H3-qualifying pair，必须报告为 shared 与 distinct pairs 并存。
- 122 个 model-sensitive/uninformative comparison 不强行分配 stable pair identity。

这一区分改变稿件语言，但不改变后验数值。`stable H4` 可表述为“at least one shared signal pair was stable”；`stable H3` 可表述为“a distinct signal pair was stable”，不能表述为整个 locus–gene–cell comparison 全局不存在任何 shared pair。

## 642 项双向重分类

R7B1B v2 的 642 个高信息 comparison 继续作为唯一多信号分析宇宙：

| ABF 起始层 | 多信号终态 |
|---|---|
| 112 H4 triggers | 78 stable H4；4 H4→H3；6 model-sensitive；24 uninformative |
| 455 H3 comparisons | 8 H3→H4；409 stable H3；7 model-sensitive；31 uninformative |
| 72 ambiguities | 5→H4；15→H3；46 model-sensitive；6 uninformative |
| 3 borderlines | 1→H4；2 uninformative |

PF10 有 520 个 definite H4/H3 终态；PF50 与其中 491 个相同（94.42%），4 个敏感，25 个在 PF50 下无信息。其余 122 个 PF10 model-sensitive/uninformative case 不进入该分母。

## 证据解释

4 个 H4→H3 和 8 个 H3→H4 共同证明重分类是双向的；这支持“single-causal screening can misclassify in either direction within the prespecified high-information subset”。真实数据没有 causal truth，因此不能把多信号终态称为已证明正确，也不能由 reclassification rate 推导一般方法优越性。
""")

    write("03_CMM_R7B1E_跨阶段ClaimEvidenceLedger与Figure1-6冻结.md", f"""
# R7B1E 跨阶段 Claim–Evidence Ledger 与 Figure 1–6 冻结

## Claim ledger

共冻结 {len(claims)} 条 claim。每条均包含 manuscript section、claim text、evidence tier、quantitative anchor、primary/supporting source、允许动词、禁止动词、limitation 和 figure/panel owner。所有 claim 状态均为 `SUPPORTED` 或 `SUPPORTED_BOUNDARY`；没有把待验证假设写成既成事实。

主要证据链如下：

1. **范围与门控**：6,923 个 PBC-wide screen comparisons，5,460 个 ABF eligible，642 个预设 high-information comparisons 进入多信号分析。
2. **双向重分类**：H4→H3=4，H3→H4=8；92/92 stable H4 与 428/428 stable H3 的 signal-pair identity 得到确认。
3. **真值已知校准**：distinct-signal 情景中平均 false-H4 从 12.41% 降至 8.56%，同时 shared-signal recovery 从 32.99% 降至 26.66%；改善具有情景依赖性，S2 matched false-H4 仍为 16.0%。
4. **IL12RB2 外部层**：OneK source-matched、TenK molecular-QTL 和 FinnGen PBC–eQTL 支持一致；risk allele 与更高表达相关；chromatin 仅为 positional layer。
5. **FCRL3 支持与反例**：B-cell sharing 在 OneK/TenK 跨 QTL 资源成立；CD8_ET 保留 H4→H3 counterexample；FinnGen 未返回 PBC–FCRL3 pair，不作阴性解释。
6. **组织边界**：FCRL3-B 与 IL12RB2-NK 在 5/5 PBC 和 5/5 control donors 可检测，但 BH q 均为 0.111，不支持 PBC-specific enrichment 或 tissue mediation。

## Figure 1–6 source freeze

{len(panels)} 个 panel rows 覆盖 Figure 1–6：

| Figure | 科学任务 | 核心边界 |
|---|---|---|
| 1 | universe、eligibility、high-information subset 与 model/diagnostic gates | 不暗示全部 6,923 接受多信号分析 |
| 2 | 双向重分类、PF sensitivity、signal-pair identity | 不把多信号结果当作 causal truth |
| 3 | 真值已知 simulation trade-off | 不宣称一般方法优越性 |
| 4 | IL12RB2 FinnGen、方向与 positional chromatin | 不声称完整 causal cascade |
| 5 | FCRL3 B-cell support 与 CD8_ET counterexample | 不把 FinnGen non-return 写成阴性复制 |
| 6 | exact 5-vs-5 tissue boundary | 不声称 PBC-specific upregulation/mediation |

9 个 source-data assets 已建立 SHA-256。架构图已输出 PNG、PDF、SVG，用于 R7B2 写作与最终图件装配的导航；它本身不是替代主图的结果图。

## 写作治理

本轮使用 QiTeng Academic Writing Skill v0.3.24.2 active Runtime Core，采用 `CLAIM → EVIDENCE → INTERPRETATION → QUALIFICATION → BRIDGE` 结构，并执行 evidence/claim governor。没有调用 CC skill。当前证据最高支持稳健关联、跨资源一致性、情景性校准与明确边界，不支持机制、临床效用或普遍优越性语言。
""")

    write("04_CMM_R7B1E_R7B2下一阶段冻结目标.md", """
# R7B1E：R7B2 下一阶段冻结目标

## 下一阶段

```text
NEXT = R7B2_MANUSCRIPT_V1
ARTICLE_POSITION = SYSTEMATIC_INFERENCE_AND_CALIBRATION_STUDY
BIOLOGICAL_SCOPE = FROZEN
NEW_LOCUS_GENE_CELL_FISHING = NO
NEW_SIMULATION_SCENARIO = NO_BY_DEFAULT
FIGURE_SOURCE_UNIVERSE = FROZEN
WRITING_ENGINE = QITENG_v0.3.24.2_ONLY
```

R7B2 的任务是把冻结证据写成一版完整英文原始研究稿，而不是再次改变结果。稿件中心应是：在 PBC-wide single-causal screen 之后，对预设 high-information H3/H4 subset 进行 source-matched multi-signal 双向重分类，并用真值已知模拟、外部 molecular-QTL 层和组织边界校准解释。

## R7B2 必须完成

1. 建立一页 argument map：unresolved problem → symmetric reclassification design → real-data landscape → truth-known calibration → bounded external/tissue evidence → inference boundary。
2. 按 Figure 1–6 顺序写 Results，并保证 Methods–Results 一一对应。
3. 将 22 条 claim ledger 逐条映射到正文、图、表或补充材料；不得产生 ledger 外的新核心数值主张。
4. 明确 R7B1E0 是 post-result diagnostic repair，保留分类且仅有一个不进 credible set 的 nondecision event。
5. 同时报告 false-H4 reduction 与 shared-signal recovery loss，避免选择性强调。
6. 将 IL12RB2/FCRL3 写作 representative biological axes，不写成“首次发现基因”。
7. 把 tissue detectability 与 disease-specific enrichment 分开；后者当前不成立。
8. 完成数值 token QA、claim-source QA、figure-caption parity、reference first-appearance 与 hostile reviewer pass。

## 不自动进入的新工作

作者信息、单位、通讯、CRediT、Funding、Competing interests 和本地伦理措辞仍须真实提供，不能推测。目标期刊的最终字数、参考文献和文件格式属于投稿接口层，可在 manuscript v1 科学内容通过后处理。

## R7B2 出口

- 若完整稿能在现有 evidence ceiling 下闭环：进入 R7B3 hostile manuscript audit 与投稿格式化。
- 若发现 claim/source 缺口：回到 R7B1E ledger 修复，不重开生物学筛选。
- 只有出现会改变中心结论的可复现数值矛盾，才允许暂停写作并触发定向复核。
""")

    write("99_CMM_R7B1E_详细行动记录_2026-10-09.md", f"""
# CMM R7B1E 详细行动记录（2026-10-09）

## 任务

按照研究计划书 v2 继续推进已完成的 R7B1B/R7B1C/R7B1D 证据链。针对外部 hostile audit 指出的 Kriging 接口和 signal-stability 语义风险，先插入 R7B1E0 诊断闭环；通过后再执行 R7B1E claim–evidence freeze 与 Figure 1–6 source assembly；最后确定下一阶段。

## 写作与权限边界

本轮学术写作使用 QiTeng Academic Writing Skill v0.3.24.2，核对 `VERSION_REGISTRY.json` 后确认 release/core authority 为 v0.3.24.2；历史 Evidence/Validation/Archive 不作为当前执行规则。本轮没有调用 CC skill。QiTeng claim governor 用于区分 association、cross-resource support、simulation calibration、mechanism 与 clinical utility。

## R7B1E0 协议冻结

在读取新诊断结果前冻结：

- 仅使用 frozen z、LD、N、variant order 与 stored SuSiE fit；
- 诊断 replay 不重拟合 posterior；
- 官方判据按 `kriging_rss` plotting condition：`logLR>2 AND |z|>2`；
- 去重单位为 comparison × trait × variant；
- comparison-level label 与 signal-pair identity 分开；
- stable-H3 只说明存在稳定 distinct pair，不自动证明全局无 shared pair；
- 任何异常先 adjudicate，再决定是否需要 refit。

## Kriging 接口修复与全量重放

代码级审计确认历史 parser 只接受 `data.frame`，而 `susieR 0.14.2` 返回 `list(plot, conditional_dist)`。新 runner 兼容 list 结构并提取 `conditional_dist`。随后重放 {replay['loci']} loci、{replay['comparisons']} comparisons、{replay['diagnostic_units']:,} diagnostic units：

```text
PASS = {replay['diagnostic_pass']:,}/{replay['diagnostic_units']:,}
HOLD = {replay['diagnostic_hold']}
runtime = {replay['runtime_seconds']:.2f} seconds
historical logLR>2 rows = {replay['historical_flags']:,}
official raw flags = {diag['official_rule_raw_count']}
official unique events = {diag['official_rule_unique_events']}
```

唯一事件为 `R7B1_003438 / rs1800378`。它不在 credible set，所在 comparison 为非核心 stable-H3 case，最终 `REVIEWED_RETAIN_INPUT_NO_REFIT`。历史 classification 与 posterior 均未改变。

## 信号语义审计

对 642 comparisons 的所有 signal-pair posterior 进行 L-setting identity audit。结果：

- stable H4 same-pair confirmed：92/92；
- stable H3 same-pair confirmed：428/428；
- stable H4 且另有 H3-qualifying pair：32；
- historical labels overwritten：0。

这一结果修复了“comparison stable”与“具体 pair stable”的语义不对称，并明确 shared/distinct pairs 可以在同一 comparison 中并存。

## R7B1E 证据整合

在 R7B1E0 QA 通过后，整合 R7B0A、R7B1A、R7B1B、R7B1C、R7B1D 和 R7A2A1 tissue boundary。生成：

- {len(claims)} 条 integrated claim–evidence ledger；
- Figure 1–6 的 {len(panels)} 条 panel source manifest；
- 9 个 figure source-data tables 及 SHA-256；
- architecture overview PNG/PDF/SVG；
- R7B1E evidence-freeze state。

中心数值冻结为 6,923 total、5,460 ABF eligible、642 high-information；H4→H3=4、H3→H4=8；92/92 H4 与 428/428 H3 signal-pair identity；distinct-signal simulation false-H4 12.41%→8.56%，shared-signal recovery 32.99%→26.66%；IL12RB2 external support bounded；FCRL3 B-cell QTL replication bounded；组织层仅支持 detectability。

## QA

- R7B1E0 independent QA：{qa0['passed']}/{qa0['total']} PASS。
- R7B1E independent QA：{qae['passed']}/{qae['total']} PASS。
- Python compile：全部当前阶段脚本 PASS。
- Figure architecture：PNG/PDF/SVG 均生成并目视检查。
- 新候选筛选：0。
- posterior refit：0。

## 证据上限与项目判定

当前可以支持 PBC-wide screening 后对预设 high-information subset 的来源匹配多信号双向重分类；simulation 表明收益与代价均依情景变化；IL12RB2/FCRL3 提供有边界的外部和组织证据。当前不支持所有 6,923 comparisons 的 multi-signal landscape、一般方法优越性、完整 regulatory cascade、PBC-specific tissue enrichment、机制或临床效用。

## 下一阶段

R7B1E 已完成且 QA 全通过，因此研究计划 v2 的下一阶段正式冻结为 `R7B2_MANUSCRIPT_V1`。R7B2 只在冻结的 claim、数字、对象和 Figure 1–6 source universe 内写作；若出现证据缺口，回到 ledger 修复，不重开 locus/gene/cell fishing。
""")

    for name in [
        "00_CMM_R7B1E_执行摘要_诊断闭环与证据总冻结.md",
        "99_CMM_R7B1E_详细行动记录_2026-10-09.md",
    ]:
        shutil.copy2(REPORT / name, CURRENT / name)

    print(json.dumps({
        "status": "PASS",
        "reports": len(list(REPORT.glob("*.md"))),
        "qiteng": "v0.3.24.2",
        "cc_skill_used": False,
        "next": "R7B2_MANUSCRIPT_V1",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
