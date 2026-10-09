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
