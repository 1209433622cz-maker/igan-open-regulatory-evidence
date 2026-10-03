# CMM R7B1B v2：下一阶段冻结目标

## 项目判定

PBC 项目继续，定位保持为 methods/inference benchmark。R7B1B v2 已补齐 real-data 双向 reclassification；它仍不能替代已知真值下的方法学校准。

## R7B1C — Simulation Engine Validation and Frozen-grid Launch

下一阶段只执行 R7B0 已冻结的 6 个 scenario、486 个 parameter rows 与固定 seeds。总计划为 486,000 replicates，不得根据 R7B1B 结果删减不利场景。

执行顺序：

1. 锁定真实 GJOKA/OneK LD templates 与 source/mismatched pairing；
2. 对每个 scenario 先做 deterministic replay、真值恢复与小规模 engine QA；
3. 通过后分 shard 启动 frozen full grid；
4. 输出 false H4、shared-signal recovery、H3/H4 reclassification、credible-set coverage、convergence 与 LD mismatch distortion；
5. 独立 QA 后才决定是否进入 manuscript rewrite。

```text
NEXT = R7B1C_SIMULATION_ENGINE_VALIDATION_AND_FROZEN_GRID_LAUNCH
SIMULATION_GRID = 486_ROWS / 486000_REPLICATES
MANUSCRIPT_REWRITE = HOLD
FINNGEN_EXPANSION = HOLD
NEW_BIOLOGICAL_FISHING = NO
```
