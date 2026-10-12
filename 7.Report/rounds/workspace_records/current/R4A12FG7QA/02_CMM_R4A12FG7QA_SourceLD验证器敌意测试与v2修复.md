# CMM R4A12FG7-QA：Source-LD验证器敌意测试与v2修复

日期：2026-09-13

## 1. 发现的判定级缺陷

FG7原脚本先计算：

```text
requested_1366_fraction = |manifest ∩ BIM| / 1366
```

但最终 `core` 列表没有 `requested_1366_fraction == 1` 或等价条件。只要残留变异覆盖全部source-CS与anchor，极小的不完整矩阵也能PASS。

本轮从真实manifest构造了一个37变异单位矩阵：它只覆盖 `37/1366 = 2.7086%`，但包含全部四细胞CS成员和三个anchor。原脚本返回：

```text
exit_code = 0
status = PASS_SOURCE_LD_STRUCTURAL_GATE
requested_1366_fraction = 0.027086...
```

这是可复现的 false PASS。该脚本从当前入口撤下，只保留在 `2_code/snapshots/R4A12FG7` 作为历史证据。

## 2. v2核心门槛

新版 `validate_received_tenk10k_source_ld_v2.py` 把以下项目全部纳入核心：

1. manifest必须有冻结schema、1,366行、MarkerID/variant_key唯一且一致；
2. CS必须恰为NK、CD8_TEM、CD4_CTL、CD4_TCM，行级组合唯一，PIP为有限正数；
3. BIM SNP ID唯一；LD必须与BIM同维、方阵、finite、对称、对角线为1，并在容差内PSD；
4. 冻结的1,366个变异必须全部出现；额外作者原生窗口变异可以保留；
5. 冻结变异的A1/A2必须全部按native manifest精确一致，不允许静默翻转；
6. 三个必需anchor全部存在；每个source-CS保留PIP ≥95%；
7. PASS退出0，科学/结构HOLD退出2，执行或输入错误退出3；任何结局均原子写JSON收据；
8. PASS时可选输出按manifest顺序排列的1,366变异子矩阵。

## 3. 回归测试

| 用例 | 原脚本 | v2 | 期望 |
|---|---|---|---|
| 37变异部分矩阵 | 错误PASS | HOLD / exit 2 | v2正确拒绝 |
| 37变异且含NaN | HOLD | HOLD / exit 2并写JSON | v2稳定拒绝 |
| 1,366变异单位矩阵正控 | 未作为本轮判据 | PASS / exit 0 | v2结构正控通过 |

敌意测试总判定：`PASS`，4/4断言PASS（当前测试集不把原脚本对NaN的具体实现作为修复断言）。完整结果：`3_results/00_audit/R4A12FG7QA/source_ld_validator_hostile_tests.json`。

## 4. 适用边界

单位矩阵只验证validator的结构逻辑，不是生物学LD正控，也不能触发FG8。真实数据必须来自作者派生对象或获批TenK10K基因型重建。
