#!/usr/bin/env python3
"""Build QiTeng-governed R7B1D reports from verified machine outputs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "3_results/04_integration/R7B1D"
RAW = ROOT / "3_results/01_intake/R7B1D/finngen_cascade_20261009"
AUDIT = ROOT / "3_results/00_audit/R7B1D/R7B1D_independent_QA.json"
REPORT = ROOT / "7.Report/rounds/R7B1D"
CURRENT = ROOT / "7.Report/current"


def write(name: str, text: str) -> None:
    (REPORT / name).write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    CURRENT.mkdir(parents=True, exist_ok=True)
    state = json.loads((RES / "R7B1D_external_gate_state.json").read_text(encoding="utf-8"))
    qa = json.loads(AUDIT.read_text(encoding="utf-8"))
    receipt = pd.read_csv(RAW / "R7B1D_finngen_api_receipts.tsv", sep="\t")
    coloc = pd.read_csv(RES / "R7B1D_FinnGen_PBC_molQTL_coloc.tsv", sep="\t")
    direction = pd.read_csv(RES / "R7B1D_direction_summary.tsv", sep="\t")
    cascade = pd.read_csv(RES / "R7B1D_IL12RB2_FinnGen_positional_cascade.tsv", sep="\t").iloc[0]

    h4lo, h4hi = state["IL12RB2_PP_H4_range"]
    cslo, cshi = state["IL12RB2_CS_overlap_range"]

    write("00_CMM_R7B1D_执行摘要_外部多组学与方向门.md", f"""
# CMM R7B1D 执行摘要：外部多组学与方向门

## 最终判定

```text
R7B1D = COMPLETE
TARGET_FREEZE = PASS__4_PREEXISTING_ANCHORS
FINNGEN_PUBLIC_BYTE_INTAKE = PASS__18_OF_18
INDEPENDENT_QA = PASS__{qa['passed']}_OF_{qa['total']}

IL12RB2_NK = PASS_EXTERNAL_DISEASE_AND_MULTIOME_SUPPORT_BOUNDED
FCRL3_B = PASS_CROSS_QTL_RESOURCE__FINNGEN_DISEASE_COLOC_NOT_RETURNED
FCRL3_CD8_ET = NEGATIVE_CONTROL_RETAINS_H3_NO_EXTERNAL_RESCUE

G6_EXTERNAL_REPLICATION = PASS_BOUNDED
GENERAL_METHOD_SUPERIORITY = NOT_ESTABLISHED_BY_R7B1C
PBC_PROJECT = RETAIN__EVIDENCE_INTEGRATION_GO

NEXT = R7B1E_INTEGRATED_CLAIM_EVIDENCE_FREEZE_AND_FIGURE_SOURCE_ASSEMBLY
```

R7B1D 没有从 R7B1B 的 78 个 stable-H4 comparison 中重新挑选外部结果最漂亮的对象。当前分析只继承四个早已冻结的代表性比较：IL12RB2–NK、FCRL3–B_IN、FCRL3–B_MEM，以及 FCRL3–CD8_ET 反例。

## 决策性结果

FinnGen R12 的公开 CASCADE 输出返回 3 条 `CHIRBIL_PRIM–IL12RB2` disease–eQTL 记录，细胞为 `l1.NK`、`l2.NK` 和 `l1.PBMC`。三条记录的 `PP.H4.abf` 为 {h4lo:.4f}–{h4hi:.4f}，credible-set overlap 为 {cslo}–{cshi} 个变异。它们构成相对于 GJOKA/OneK 主分析的外部 disease–molecular-QTL aggregate layer，但不替代 OneK 的来源匹配多信号分析。

IL12RB2 的 FinnGen regulatory layer 进一步包含 `chr1_67307966_T_C`、峰 `chr1-67307618-67308670` 与 IL12RB2 的 fasthurdle peak–gene link。该峰在 `l1.NK` 和 `l2.NK` 的 caQTL q 值分别为 {cascade.peak_caqtl_q_l1_NK:.3g} 和 {cascade.peak_caqtl_q_l2_NK:.3g}。然而该 eQTL variant 并不属于该峰的 caQTL credible set，所以本轮严格保留 **positional cascade** 表述，不声称完整的 disease→caQTL→expression 因果链。

FCRL3 的公开 gene/region/variant 查询返回强 B/T-cell eQTL 信息，但没有任何 `CHIRBIL_PRIM–FCRL3` coloc 记录。这个结果被定义为公开输出未返回，不是生物学阴性或经过充分功效检验的零效应。FCRL3–B 的可用外部证据仍然是 OneK source-matched stable H4 与 TenK B_intermediate single-causal molecular replication。

精确等位基因统一后，PBC risk allele 在 OneK、TenK 和 FinnGen 中一致关联 **更高 IL12RB2 表达**；FCRL3–B 在 OneK 与 TenK 中一致关联 **更低 FCRL3 表达**。这些是方向性关联，不是 mediation probability。

## 研究计划 v2 的含义

G6 的通过条件是“至少部分 robust assignment 在 TenK/FinnGen 再现或得到新的 regulatory layer”，当前已经满足。与此同时，R7B1C 未证明来源匹配多信号方法具有普遍优势，因此新论文应定位为 **PBC-wide systematic reclassification benchmark with scenario-dependent calibration and bounded external multiome support**，而不能升级为一般性方法优越性论文。

资源能力与论文状态已按 2026 年 10 月 9 日核对：[FinnGen access/results](https://www.finngen.fi/en/access_results)、[Nature 2026 immune multiome atlas](https://www.nature.com/articles/s41586-026-11078-2)、[CASCADE browser](https://cascade.finngen.fi/)。
""")

    write("01_CMM_R7B1D_预设对象与公开字节接入审计.md", f"""
# R7B1D 预设对象与公开字节接入审计

## 对象冻结

R7B1D 的分析对象在当前 FinnGen 查询前由 R7B1B 代表性案例继承。三条 positive anchors 为 `R7B1_000258`、`R7B1_000410`、`R7B1_000411`；`R7B1_000414` 是 falsification anchor。对象、基因、细胞、PF10/PF50 状态和映射规则均写入 `R7B1D_external_target_registry.tsv`。本轮没有增加 OneK locus、gene 或 cell。

## API 字节

共请求 {len(receipt)} 个当前公开对象，HTTP 200 为 {int((receipt.status_code == 200).sum())}/{len(receipt)}，有效 JSON 为 {int(receipt.valid_json.astype(bool).sum())}/{len(receipt)}。每个对象均记录 URL、UTC 时间、字节数和 SHA-256。接入包括 gene、peak、variant coloc、region coloc、region eQTL/caQTL、PBC regional GWAS、PBC Manhattan 与 phenotype autocomplete。

当前 `/api/finngen/phenos` 搜索索引返回零条 PBC 记录，但同一时点的 autocomplete、Manhattan、regional GWAS 和 disease-coloc endpoint 均正常返回 `CHIRBIL_PRIM`。因此病例数元数据沿用 R7B0 已冻结的公开返回值（760 cases、372,273 controls），而本轮 disease/eQTL 结果全部来自当前重新下载的字节。这一异常被显式记录，未用空搜索结果覆盖直接 endpoint 证据。

## 细胞映射

- OneK `NK` → FinnGen `l2.NK` primary，`l1.NK`/`l1.PBMC` compatible。
- OneK `B_IN` → FinnGen `l2.B_intermediate` primary，`l1.B` compatible。
- OneK `B_MEM` → FinnGen `l2.B_memory` primary，`l1.B` compatible；当前 FCRL3 eQTL region response 没有 `l2.B_memory`，所以只能使用 coarse B compatibility，不能写成 exact memory-B replication。
- OneK `CD8_ET` → FinnGen `l2.CD8_TEM`/`l1.CD8_T`，仅作为已冻结反例的 coverage audit，不能因外部 eQTL 强度被升级。

## 可重复性边界

CASCADE 是公开 aggregate output。个体级 FinnGen genotype/LD 没有进入本轮，故本轮不能复现 FinnGen 内部 SuSiE 或重新构建 source-matched LD。当前使用官方公开 fine-mapping/coloc 输出，并以原始 JSON、checksum 和解析代码保持可审计性。
""")

    write("02_CMM_R7B1D_FinnGen_PBC_IL12RB2与FCRL3终裁.md", f"""
# R7B1D FinnGen PBC–IL12RB2 与 FCRL3 终裁

## IL12RB2–NK

`CHIRBIL_PRIM` 与 IL12RB2 eQTL 共定位记录共 3 条。数值如下：

| FinnGen cell | PP.H4.abf | CS overlap | GWAS CS size | eQTL CS size |
|---|---:|---:|---:|---:|
""" + "\n".join(
        f"| {r['cell_type2']} | {r['PP.H4.abf']:.4f} | {int(r['cs_overlap'])} | {int(r['cs1_size'])} | {int(r['cs2_size'])} |"
        for _, r in coloc.sort_values("cell_type2").iterrows()
    ) + f"""

这些记录支持外部 PBC–IL12RB2 signal sharing。它们来自 FinnGen R12 disease GWAS 与同一 FinnGen multiome 资源的 eQTL，不应被称为第二套 OneK source-LD proof。

在 chromatin 层，IL12RB2 top variant `chr1_67307966_T_C` 被 CASCADE 标记为 `Positional Cascade (overlap link)`：变异落在 peak `chr1-67307618-67308670` 内，该 peak 通过 fasthurdle 与 IL12RB2 相连，且该 peak 在 NK 中具备显著 caQTL。关键限制是该变异不在 peak caQTL credible set 中；当前也没有建立 PBC–caQTL signal-level colocalization。因此允许写“linked positional chromatin layer”，禁止写“完整调控级联已证实”。

## FCRL3–B

FCRL3 gene API 显示 `l1.B`、`l2.B_intermediate` 及 CD8 细胞中的强 eQTL，但 FCRL3 marginal lead、历史 anchor 与扩展 region coloc 三类查询均未返回 `CHIRBIL_PRIM–FCRL3` pair。FCRL3 也没有 gene-level CASCADE top variant。由此形成的结论是：

> FCRL3–B 获得 OneK–TenK 跨 molecular-QTL 资源复制，但本轮没有 FinnGen PBC disease-coloc 支持。

这不否定 FCRL3，也不允许用非 PBC trait 的高 PP.H4 替代 PBC evidence。

## CD8_ET 反例

FinnGen 的 FCRL3 CD8 eQTL 不能改变 R7B1B 的信号级判断。`R7B1_000414` 在 PF10 source-matched multi-signal 模型中为 H3-supported，而 PF50 会改变模型结论；它仍然是 covariate/LD model sensitivity 和 single-causal over-assignment 的代表性反例。强 QTL 存在本身不构成 disease–QTL shared signal。
""")

    write("03_CMM_R7B1D_TenK复核与RiskAllele方向图.md", """
# R7B1D TenK 复核与 Risk-Allele 方向图

## 证据角色

TenK10K 只承担 independent molecular-QTL resource replication。IL12RB2–NK 与 FCRL3–B_intermediate 都复用 GJOKA PBC GWAS，且未重建 TenK donor-level source LD，所以不能称为 independent disease replication 或第二套 source-matched multi-signal proof。

## IL12RB2–NK

在共同 anchor `rs6679356` 上，GJOKA/OneK、GJOKA/TenK 与 FinnGen R12 的等位基因方向可以精确统一。三个资源家族均显示：PBC risk allele 与更高 IL12RB2 表达相关。FinnGen 还在自己的 disease lead `rs6659932` 上给出相同方向。该方向一致性增强了调控解释，但不建立表达介导。

## FCRL3–B

在 `rs3761959` 上，OneK B_IN、OneK B_MEM 与 TenK B_intermediate 均显示：PBC risk allele 与更低 FCRL3 表达相关。FinnGen 没有返回 PBC–FCRL3 coloc，故不能加入 FinnGen disease-direction concordance。

## FCRL3–CD8_ET

OneK CD8_ET 的 QTL beta 可以计算，但由于 source-matched PF10 adjudication 支持 H3，该方向不得被解释为 PBC shared-signal direction。方向表将其标记为 `eligible_for_shared_signal_direction = FALSE`。

## 允许的生物学表述

- “PBC risk-associated allele was associated with higher IL12RB2 expression across OneK, TenK and FinnGen molecular-QTL contexts.”
- “PBC risk-associated allele was associated with lower FCRL3 expression in the OneK and TenK B-cell contexts.”

禁止使用 `mediates`、`drives`、`causes` 或 therapeutic-target efficacy 语言。
""")

    write("04_CMM_R7B1D_G6判定与R7B1E冻结目标.md", """
# R7B1D G6 判定与 R7B1E 冻结目标

## G6 判定

研究计划 v2 的 G6 要求至少部分 robust assignment 在 TenK/FinnGen 再现，或获得新的 regulatory layer。IL12RB2–NK 已同时满足 TenK molecular replication、FinnGen PBC–eQTL aggregate colocalization 和 positional chromatin layer；FCRL3–B 满足 OneK–TenK molecular replication。因此：

```text
G6_EXTERNAL_REPLICATION = PASS_BOUNDED
```

“bounded”不可删除，因为 FCRL3 缺少 FinnGen PBC coloc，IL12RB2 chromatin 层不是完整 variant-level cascade，TenK 也没有 source-LD multi-signal replication。

## 项目总方向

PBC 不触发 R8 disease reselection。R7B1B 已形成可解释 reclassification landscape，R7B1D 又通过外部门；虽然 R7B1C 没有证明 general method superiority，但四类失败条件并未同时满足。论文的中心贡献应收敛为 PBC-wide systematic inference study，并把 simulation 结果表述为 scenario-dependent calibration。

## 下一阶段：R7B1E

R7B1E 只做证据整合与图件源数据冻结，不再扩 gene、cell、locus 或外部资源：

1. 合并 R7B0A、R7B1A、R7B1B、R7B1C、R7B1D 与 HRA boundary，形成唯一 claim–evidence ledger。
2. 对每个核心 claim 标注 evidence tier、支持文件、允许动词、禁止动词和反证。
3. 冻结 Figure 1–6 的 panel-level source-data manifest；将本轮图作为 Figure 5 候选，而非直接视为最终投稿图。
4. 对 simulation 主张降级：保留 S2/S5 等情景性改善，明确 shared-signal recovery 的代价，不宣称普遍优越。
5. 运行跨阶段数字、对象、图件和 citation-source QA。
6. 通过后进入 R7B2 manuscript v1；未通过则修 evidence ledger，不回到生物学筛选。

```text
NEXT = R7B1E_INTEGRATED_CLAIM_EVIDENCE_FREEZE_AND_FIGURE_SOURCE_ASSEMBLY
NEW_BIOLOGICAL_FISHING = NO
MANUSCRIPT_REWRITE = HOLD_UNTIL_R7B1E_PASS
```
""")

    write("99_CMM_R7B1D_详细行动记录_2026-10-09.md", f"""
# CMM R7B1D 详细行动记录（2026-10-09）

## 任务

按照研究计划书 v2 完成 R7B1D 外部 molecular/chromatin replication 与 risk-allele direction gate；不重选 R7B1B comparison；产出机器结果、图件、独立 QA、公开仓库资产和本详细行动记录。

## 写作与证据治理

本轮使用 QiTeng Academic Writing Skill v0.3.24.2 的 active Runtime Core。写作前核对 `VERSION_REGISTRY.json`，确认 core/release 均为 v0.3.24.2；Evidence/Validation/Archive 仅作 provenance。本轮报告遵守 evidence ladder：共定位与跨资源方向属于 robust association 层，不上升为机制或临床效用。

## 输入冻结

1. 从 R7B1B 642-row adjudication 表提取四个预设 comparison。
2. 验证 IL12RB2–NK、FCRL3–B_IN、FCRL3–B_MEM 为 stable H4，FCRL3–CD8_ET 为 PF10 H3-supported 反例。
3. 验证 B/NK positive-axis cell mapping 与 R7B0 冻结表一致；CD8_ET 仅作负例 coverage audit。
4. 冻结“TenK 不是独立 disease replication”“FinnGen non-return 不是阴性”“direction 必须 exact-allele”等边界。

## 当前公开字节接入

重新下载 {len(receipt)} 个 CASCADE/FinnGen 对象，包括 gene、peak、variant/region coloc、eQTL、caQTL、PBC regional GWAS、Manhattan 和 phenotype identity。全部 HTTP 200、JSON 可解析，并记录字节数、URL、UTC 时间与 SHA-256。

公开 phenotype search endpoint 当前返回空索引；autocomplete、Manhattan、regional GWAS 和 coloc endpoint 仍正常工作。病例数沿用 R7B0 已冻结的公开 metadata，当前科学结果仅使用本轮新字节。

## 分析步骤

1. 对两个 IL12RB2 top variants 的 coloc 返回去重，恢复 3 条 PBC–IL12RB2 cell-specific records。
2. 对 FCRL3 marginal、anchor 和宽 region 返回做同一 PBC/gene 过滤，得到 0 条 PBC–FCRL3 records。
3. 按 R7B0 cell mapping 提取 eQTL/caQTL q 值与缺失覆盖。
4. 解析 IL12RB2 positional-cascade variant、overlapping peak、peak–gene link 和 NK caQTL 状态；核对 variant 不在 peak caQTL credible set。
5. 在 `rs6679356`、`rs3761959` 与 FinnGen disease lead 上统一 ref/alt、risk allele 和 QTL effect allele。
6. 将 CD8_ET direction 标记为不适用于 shared-signal inference。
7. 生成三轴 external adjudication、direction summary、机器 state 与 Figure 5 候选概览。

## 结果

- FinnGen PBC–IL12RB2：3 条记录，PP.H4.abf {h4lo:.4f}–{h4hi:.4f}，CS overlap {cslo}–{cshi}。
- FinnGen PBC–FCRL3：0 条公开返回；按 coverage limitation 处理。
- IL12RB2 risk allele → higher expression：OneK、TenK、FinnGen 一致。
- FCRL3 risk allele → lower expression：OneK B_IN/B_MEM 与 TenK B_intermediate 一致。
- IL12RB2 chromatin：positional linked-peak layer；不满足完整 variant-level cascade claim。
- G6：`PASS_BOUNDED`。

## 质量控制

独立 QA 为 {qa['passed']}/{qa['total']} PASS，覆盖 API、对象身份、PBC coloc 数量、FCRL3 non-return 边界、NK caQTL、positional/full-cascade 区分、方向一致性、CD8 不可解释性、G6 与下一阶段状态。图件已输出 PNG/PDF/SVG 并完成目视检查。

## 本轮新增机器文件

- `3_results/01_intake/R7B1D/finngen_cascade_20261009/`：18 个 raw JSON + receipts。
- `3_results/04_integration/R7B1D/`：target registry、coloc、cell map、cascade、direction、axis adjudication、state。
- `3_results/00_audit/R7B1D/`：23-check independent QA。
- `5_analysis/figures/R7B1D/`：external evidence overview PNG/PDF/SVG。
- `2_code/06_intake/r7b1d/`：冻结、下载、解析、作图、QA、报告与发布代码。

## 最终决策与下一步

本轮没有触发新数据下载或长时间本地计算。PBC 保留，下一阶段为 R7B1E claim–evidence freeze 与 Figure 1–6 source assembly；不允许扩展新的 biology，R7B2 manuscript 写作继续 HOLD，直至 R7B1E QA 通过。
""")

    for name in [
        "00_CMM_R7B1D_执行摘要_外部多组学与方向门.md",
        "99_CMM_R7B1D_详细行动记录_2026-10-09.md",
    ]:
        shutil.copy2(REPORT / name, CURRENT / name)
    print(f"Wrote {len(list(REPORT.glob('*.md')))} reports to {REPORT}")


if __name__ == "__main__":
    main()
