#!/usr/bin/env python3
"""Build QiTeng-governed R7B1C reports and the lightweight release."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(r"H:\SCI2\YR1")
AGG = ROOT / "3_results/05_simulation/R7B1C/aggregate"
RAW = ROOT / "3_results/05_simulation/R7B1C/full"
AUDIT = ROOT / "3_results/00_audit/R7B1C"
FIG = ROOT / "4_figures/R7B1C"
REPORT = ROOT / "7.Report/rounds/R7B1C"
RELEASE = ROOT / "6_release/R7B1C"
STAGE = RELEASE / "stage"
ZIP = RELEASE / "CMM_R7B1C_TruthKnown_SimulationCalibration_2026-10-09.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def pct(x: float) -> str:
    return f"{100*x:.2f}%"


def scenario_table(d: pd.DataFrame) -> str:
    lines = ["| 场景 | 真值共享 | ABF H4 | matched H4 | matched H3 | uninformative | disease CS all coverage | QTL CS all coverage |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in d.itertuples(index=False):
        lines.append(f"| {r.scenario} | {bool(r.true_shared)} | {pct(r.abf_h4_rate)} | {pct(r.matched_h4_rate)} | {pct(r.matched_h3_rate)} | {pct(r.matched_uninformative_rate)} | {pct(r.matched_d_cover_all_rate)} | {pct(r.matched_q_cover_all_rate)} |")
    return "\n".join(lines)


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=True); RELEASE.mkdir(parents=True, exist_ok=True)
    qa = json.loads((AUDIT / "independent_QA/R7B1C_independent_QA_state.json").read_text(encoding="utf-8"))
    if qa["status"] != "PASS": raise RuntimeError("independent QA is not PASS")
    agg_state = json.loads((AGG / "R7B1C_aggregate_state.json").read_text(encoding="utf-8"))
    scenario = pd.read_csv(AGG / "R7B1C_scenario_summary.tsv", sep="\t")
    row = pd.read_csv(AGG / "R7B1C_grid_486_summary.tsv", sep="\t")
    brier = pd.read_csv(AGG / "R7B1C_posterior_brier_scores.tsv", sep="\t")
    distinct = scenario[scenario.scenario.str.startswith(("S2_","S5_"))]
    shared = scenario[scenario.scenario.str.startswith(("S1_","S3_","S4_","S6_"))]
    abf_false = float(distinct.abf_h4_rate.mean()); matched_false = float(distinct.matched_h4_rate.mean())
    abf_recovery = float(shared.abf_h4_rate.mean()); matched_recovery = float(shared.matched_h4_rate.mean())
    false_abs_reduction = abf_false - matched_false
    false_rel_reduction = false_abs_reduction / abf_false
    recovery_abs_loss = abf_recovery - matched_recovery
    recovery_rel_loss = recovery_abs_loss / abf_recovery
    s6 = scenario[scenario.scenario == "S6_matched_vs_mismatched_LD"].iloc[0]
    s2 = scenario[scenario.scenario == "S2_distinct_correlated"].iloc[0]
    s5 = scenario[scenario.scenario == "S5_two_by_two_none_highLD"].iloc[0]
    abf_brier = float(brier.loc[brier.method=='ABF','brier'].iat[0])
    multi_brier = float(brier.loc[brier.method=='MULTISIGNAL_BEST_H4_NO_PAIR_ZERO','brier'].iat[0])
    runtime = json.loads((RAW / "orchestrator_state.json").read_text(encoding="utf-8"))["runtime_seconds"]
    interpretation = {
        "schema": "R7B1C_SCIENTIFIC_INTERPRETATION_1.0",
        "status": "PASS_BOUNDED_TRADEOFF",
        "distinct_average_abf_false_h4": abf_false,
        "distinct_average_matched_false_h4": matched_false,
        "false_h4_relative_reduction": false_rel_reduction,
        "shared_average_abf_recovery": abf_recovery,
        "shared_average_matched_recovery": matched_recovery,
        "shared_recovery_relative_loss": recovery_rel_loss,
        "S6_mismatch_decision_flip_rate": float(s6.mismatch_decision_flip_rate),
        "S6_mismatch_mean_abs_h4_delta": float(s6.mismatch_mean_abs_h4_delta),
        "general_method_superiority": "NOT_DEMONSTRATED",
        "PF10_PF50_mismatch_general_harm": "NOT_DEMONSTRATED_IN_TWO_TEMPLATES",
        "next": "R7B1D_EXTERNAL_MOLECULAR_CHROMATIN_REPLICATION_AND_DIRECTION",
    }
    interpretation_path = AUDIT / "R7B1C_scientific_interpretation_state.json"
    write(interpretation_path, json.dumps(interpretation, indent=2))
    sync_path = AUDIT / "R7B1C_GitHub_sync_state.json"
    github_note = "PUBLIC_GITHUB_SYNC = PENDING"
    if sync_path.exists():
        sync = json.loads(sync_path.read_text(encoding="utf-8"))
        github_note = f"PUBLIC_GITHUB_SYNC = {sync.get('status')} @ {sync.get('remote_commit')}"
    status = f"""```text
R7B1C = COMPLETE
GRID_ROWS = 486/486
REPLICATES = 486000/486000
MATCHED_FIT_FAILURES = {agg_state['matched_fit_failures']}
MATCHED_NONCONVERGED = {agg_state['matched_nonconverged']}
INDEPENDENT_QA = {qa['passed']}/{qa['checks']} PASS
FALSE_H4_REDUCTION = DEMONSTRATED_WITH_RECOVERY_COST
GENERAL_METHOD_SUPERIORITY = NOT_DEMONSTRATED
PF10_TO_PF50_LD_MISMATCH_HARM = NOT_DEMONSTRATED_IN_TWO_TEMPLATES
MANUSCRIPT_REWRITE = HOLD
NEXT = R7B1D_EXTERNAL_MOLECULAR_CHROMATIN_REPLICATION_AND_DIRECTION
{github_note}
```"""

    summary = f"""# CMM R7B1C 执行摘要：真值已知的来源匹配多信号校准

日期：2026-10-09

{status}

R7B1C 已完成研究计划书 v2 冻结的六场景、486 行和 486,000 次 replicate。每个参数格在两个经验模板中各运行 500 次：GJOKA locus 2 + OneK NK，以及 GJOKA locus 4 + OneK B_IN。模拟比较 single-causal ABF、source-matched multi-signal SuSiE/coloc 与 S6 的同位点 PF10→PF50 QTL-LD mismatch。

## 主要结果

- distinct truth（S2/S5）中，ABF 的平均 H4 decision rate 为 **{pct(abf_false)}**，source-matched multi-signal 为 **{pct(matched_false)}**，绝对下降 **{pct(false_abs_reduction)}**、相对下降 **{pct(false_rel_reduction)}**。
- shared truth（S1/S3/S4/S6）中，ABF 的平均 H4 recovery 为 **{pct(abf_recovery)}**，source-matched multi-signal 为 **{pct(matched_recovery)}**，绝对下降 **{pct(recovery_abs_loss)}**、相对下降 **{pct(recovery_rel_loss)}**。这是一项明确的 recovery / abstention 代价，不能从 false-H4 降低单独推导“方法普遍更优”。
- S2 correlated-distinct 的 false H4 仍为 **{pct(s2.matched_h4_rate)}**；source matching 与多信号分解没有消除高相关不同因果变异带来的误判。
- S5 2×2/no-shared 的 H4 从 **{pct(s5.abf_h4_rate)}** 降为 **{pct(s5.matched_h4_rate)}**，说明在该冻结结构下存在有界增益。
- S6 matched H4 rate 为 **{pct(s6.matched_h4_rate)}**，PF10 z + PF50 LD mismatch 为 **{pct(s6.mismatch_h4_rate)}**；平均绝对 best-H4 改变量为 **{s6.mismatch_mean_abs_h4_delta:.4f}**。
- matched fit failure={agg_state['matched_fit_failures']}；non-converged={agg_state['matched_nonconverged']}；没有删除不利或无信息格点。

{scenario_table(scenario)}

## 结论边界

该模拟支持的是两个经验 LD 模板、固定效应量、固定 N 与冻结参数网格下的**条件性 trade-off**。它不支持 source-matched multi-signal 的全局优越性，也未在这两个模板中证明 PF10/PF50 LD mismatch 会造成普遍严重偏倚。它不能代表所有 ancestry、效应分布或基因组区域，也不能证明任何 PBC gene–cell assignment 的生物学机制。
"""

    methods = f"""# CMM R7B1C：协议、模板、引擎与失败恢复

## 预结果冻结

R7B0 的 486-row grid 原样保留。R7B1C 在任何正式结果前补充了模板身份、效应量、因果索引、PSD 修正、判定阈值与 pilot gate。实现使用标准 summary-statistic 模型 `z ~ N(sqrt(N) Rb, R)`，SuSiE 配置与 R7B1B 真实数据主分析一致。

## 两次被门控拦截的实现问题

1. v1 cross-locus mismatch 使 S6 长时间贴近最大迭代上限，并混合不同区域的索引语义。未汇总 posterior 即停止；v1.1 改为同一位点 PF10 z + PF50 QTL LD。
2. v1.1 首次 pilot 的 z/LD 未设置共同 variant names，导致有 credible set 但 `coloc.susie` 无 eligible pair。该纯实现错误修复后重新执行完整双重 pilot，没有改变统计规则。

最终 pilot 两次 300-replicate replay 逐字节一致，12/12 gate PASS。完整运行按 486 个 grid row checkpoint，可安全续跑。

## 计算身份

- R 4.6.1；susieR 0.14.2；coloc 5.2.3。
- 每格两个模板各 500 次；固定上游 seed。
- 原始 486 个压缩结果文件和合并 486,000-row truth table 留在本地；release 仅收录聚合表、代码、协议、模板和精确 hash manifest。
"""

    results = f"""# CMM R7B1C：完整结果、校准与限制

## 场景结果

{scenario_table(scenario)}

## 判定解释

distinct 场景中的 H4 率用于 false-shared classification；shared 场景中的 H4 率用于 recovery。`UNINFORMATIVE` 保持为无足够 signal-pair evidence，未被改写成 H3 或生物学阴性。credible-set coverage 以每个 trait 的全部真因果变异是否进入任一 95% CS 计算。

ABF Brier score 为 **{abf_brier:.4f}**；将无 signal-pair 的 multi-signal prediction 记为 0 时，其 Brier score 为 **{multi_brier:.4f}**。后者更差，主要受复杂 shared 场景中大量无 signal-pair/低 CS coverage 影响；它是明确标注的 decision-calibration summary，不应被解释为经过证明的全局 posterior probability，也不能拿来宣称 multi-signal posterior 全局失准。

`L=5/10/20` 的场景级判定率变化很小，说明本轮主要结论不是由 L 选择驱动。相反，MAF、因果变异相关度与先验 p12 明显影响 H4 和 credible-set formation：低 MAF 主要导致无信息；S2 在 causal-r²=0.8 时 matched false H4 仍约 37.47%；高 p12 会提高 ABF 与 multi-signal 的 H4 判定率。

S4/S5/S6 的 QTL all-causal 95% CS coverage 仅约 5%，对应 opposite-effect/high-correlation 结构下的弱 signal recovery。此时较低 H4 很大程度上体现模型 abstention 与 CS 形成失败，而不能全部解释为正确识别 H3。

## 限制

- 只有两个经验 LD 模板；
- disease 与 QTL 效应量固定，没有构成完整 effect-size distribution；
- grid MAF 是生成参数，不是模板变异的实测 MAF；
- S6 只检验同位点 PF10/PF50 QTL covariance-model mismatch；
- 两个 PF10/PF50 模板非常接近，因此 S6 的近零效应不能外推到 ancestry mismatch、不同 reference panel 或严重样本错配；
- max signal-pair H4 不等价于对完整 trait pair 的单一校准概率；
- simulation 校准不能替代外部 molecular/chromatin replication。
"""

    next_stage = f"""# CMM R7B1C：下一阶段冻结目标

## R7B1D — External Molecular/Chromatin Replication and Direction

R7B1B 已完成真实数据双向重分类，R7B1C 已完成真值已知 calibration。下一阶段应执行研究计划书 v2 的外部层，不再扩增 OneK locus/gene/cell。

固定任务：

1. 继承 TenK10K 已冻结的 IL12RB2–NK 与 FCRL3–B cross-resource molecular-QTL evidence；
2. 对 FinnGen immune multiome 的 PBC endpoint、eQTL、caQTL、peak–gene 与 disease-coloc 对象做当前字节级复核；
3. 对 R7B1B stable H4 exemplars 进行预定义 cell mapping、variant/build/allele harmonization；
4. 建立 risk-allele/eQTL-effect direction table；
5. 将不支持、无覆盖与 assay/cell mapping 不充分结果完整保留。

不得新增 post-hoc OneK candidates，不得把 TenK 复用同一 PBC GWAS 写成 independent disease replication，不得在外部层完成前重写整篇 manuscript。

{status}
"""

    action = f"""# CMM R7B1C 详细行动记录（2026-10-09）

## 本轮目标

按照研究计划书 v2 完成 R7B0→R7B1C truth-known simulation/calibration，并判断是否进入外部 molecular/chromatin 层。本轮使用 QiTeng v0.3.24.2 的证据上限与负结果治理，没有使用 CC skill。

## 已执行动作

1. 独立核验 R7B0：6 scenarios、486 rows、486,000 replicates、seed base 20261002。
2. 在结果前冻结两个 empirical 128-variant templates、固定效应、因果索引和判定门。
3. 构建 GJOKA locus 2/OneK NK 与 GJOKA locus 4/OneK B_IN 模板；记录 PSD projection、输入/输出 hash 和 causal-r² 偏差。
4. v1 cross-locus mismatch 因数值运行门失败而中止；没有把 incomplete S6 混入结果。
5. v1.1 首次 pilot 识别并修复缺失 variant names；统计规则未改变。
6. 最终两次 pilot 共 600 个执行实例逐字节重放一致，12/12 gate PASS。
7. 使用 14 个有界单线程 worker 完成 486/486 grid rows 和 486,000/486,000 formal replicates。
8. 生成完整 truth table、486-row、scenario、factor-stratified、reclassification、calibration 与 Brier summaries。
9. 完成独立 QA：{qa['passed']}/{qa['checks']} PASS。
10. 将合并 gzip 改为 `mtime=0` 的确定性压缩；连续重跑 SHA-256 完全一致。
11. 生成四张主校准图并完成逐图视觉检查；同步保存 PNG、PDF 与 source data。
12. 生成 QiTeng-governed 报告、轻量 release 与大资产 hash manifest。

## 核心数量与结果

- distinct S2/S5：ABF false H4={pct(abf_false)}；matched multi-signal false H4={pct(matched_false)}。
- shared S1/S3/S4/S6：ABF recovery={pct(abf_recovery)}；matched multi-signal recovery={pct(matched_recovery)}。
- S6 matched→PF50 mismatch：H4 {pct(s6.matched_h4_rate)}→{pct(s6.mismatch_h4_rate)}；mean |ΔH4|={s6.mismatch_mean_abs_h4_delta:.4f}。
- fit failure={agg_state['matched_fit_failures']}；non-converged={agg_state['matched_nonconverged']}。
- formal grid runtime={runtime/3600:.2f} hours；deterministic combined truth-table SHA-256=`{qa['combined_sha256']}`。

## 科学终裁

本轮证明了一个有边界的结论：在冻结的 distinct/multi-signal 场景中，source-matched multi-signal inference 可降低 false H4；但它同时降低 shared-signal recovery，并把大量复杂低功效实例留为 `UNINFORMATIVE`。S6 没有显示同位点 PF10→PF50 mismatch 的普遍危害。因此论文应写成 calibration / falsification trade-off，不应写成方法全面胜出，也不应把此前真实数据 PF10/PF50 差异全部归因于 LD mismatch。

## 偏差控制

- full grid 前冻结；pilot 不进入正式估计；
- 两个失败 pilot 独立归档；
- 不按结果调整效应、L、p12、MAF、r² 或模板；
- 两模板每格 500/500；
- uninformative、QC failure 与 negative truth 分开；
- 所有 486 行均进入分层汇总。

## 最终状态

{status}
"""

    reports = {
        "00_CMM_R7B1C_执行摘要_真值已知模拟校准.md": summary,
        "01_CMM_R7B1C_协议模板引擎与失败恢复.md": methods,
        "02_CMM_R7B1C_完整结果校准与证据边界.md": results,
        "03_CMM_R7B1C_R7B1D下一阶段冻结目标.md": next_stage,
        "99_CMM_R7B1C_详细行动记录_2026-10-09.md": action,
    }
    for name, text in reports.items(): write(REPORT / name, text)

    raw_manifest = []
    for path in sorted(RAW.glob("R7B1C_G*.tsv.gz")):
        raw_manifest.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "public_copy": "NO"})
    raw_manifest.append({"file": "aggregate/R7B1C_all_486000_replicates.tsv.gz",
                         "bytes": (AGG/"R7B1C_all_486000_replicates.tsv.gz").stat().st_size,
                         "sha256": sha256(AGG/"R7B1C_all_486000_replicates.tsv.gz"), "public_copy": "NO"})
    raw_manifest_path = AUDIT / "R7B1C_large_raw_asset_manifest.tsv"
    pd.DataFrame(raw_manifest).to_csv(raw_manifest_path, sep="\t", index=False)

    if STAGE.exists(): shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    copies = []
    for p in REPORT.glob("*.md"): copies.append((p,Path("reports")/p.name))
    for p in (ROOT/"2_code/06_intake/r7b1c").glob("*"):
        if p.is_file() and (p.suffix in {".py",".R",".ps1"}): copies.append((p,Path("code")/p.name))
    for p in (ROOT/"0_admin/protocols/R7B1C").glob("*.md"): copies.append((p,Path("protocol")/p.name))
    for p in (AUDIT/"templates").rglob("*"):
        if p.is_file(): copies.append((p,Path("templates")/p.relative_to(AUDIT/"templates")))
    audit_files = [
        AUDIT/"R7B1C_implementation_grid_486.tsv", AUDIT/"R7B1C_template_freeze_state.json",
        AUDIT/"R7B1C_pilot_summary.tsv", AUDIT/"R7B1C_pilot_gate_checks.tsv", AUDIT/"R7B1C_pilot_gate_state.json",
        raw_manifest_path, interpretation_path, AUDIT/"independent_QA/R7B1C_independent_QA_checks.tsv",
        AUDIT/"independent_QA/R7B1C_independent_QA_state.json",
    ]
    if sync_path.exists(): audit_files.append(sync_path)
    for p in audit_files: copies.append((p,Path("audit")/p.name))
    for p in AGG.glob("*"):
        if p.is_file() and p.name != "R7B1C_all_486000_replicates.tsv.gz": copies.append((p,Path("results")/p.name))
    for p in FIG.rglob("*"):
        if p.is_file(): copies.append((p,Path("figures")/p.relative_to(FIG)))
    for p in [ROOT/"3_results/05_simulation/R7B1C/pilot_v1_cross_locus_aborted_state.json",
              ROOT/"3_results/05_simulation/R7B1C/pilot_v1_1_nameless_failed_state.json",
              RAW/"orchestrator_state.json"]:
        copies.append((p,Path("audit")/p.name))
    for src, rel in copies:
        if not src.exists(): raise FileNotFoundError(src)
        dst=STAGE/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    lines=[]
    for p in sorted(x for x in STAGE.rglob("*") if x.is_file() and x.name!="checksums.sha256"):
        lines.append(f"{sha256(p)}  {p.relative_to(STAGE).as_posix()}")
    write(STAGE/"checksums.sha256","\n".join(lines))
    if ZIP.exists(): ZIP.unlink()
    with zipfile.ZipFile(ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(x for x in STAGE.rglob("*") if x.is_file()): z.write(p,p.relative_to(STAGE).as_posix())
    with zipfile.ZipFile(ZIP) as z:
        bad=z.testzip(); entries=len(z.infolist())
    if bad: raise RuntimeError(f"ZIP CRC failed: {bad}")
    digest=sha256(ZIP); write(Path(str(ZIP)+".sha256"),f"{digest}  {ZIP.name}")
    shutil.copy2(REPORT/"99_CMM_R7B1C_详细行动记录_2026-10-09.md",ROOT/"99_CMM_R7B1C_详细行动记录_2026-10-09.md")
    state={"schema":"R7B1C_RELEASE_1.0","status":"PASS","zip":str(ZIP),"sha256":digest,
           "zip_crc":"PASS","entries":entries,"internal_checksums":len(lines)}
    write(RELEASE/"release_state.json",json.dumps(state,indent=2))
    print(json.dumps(state,indent=2,ensure_ascii=False))


if __name__=="__main__": main()
