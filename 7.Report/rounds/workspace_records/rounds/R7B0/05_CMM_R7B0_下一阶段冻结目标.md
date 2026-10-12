# CMM R7B0：下一阶段冻结目标

## 当前目标

下一阶段不是 R7B1，也不是直接运行 784 个扩展 posterior。当前冻结为：

```text
R7B0_NEXT = PF10_SOURCE_IDENTITY_RECOVERY
R7B1 = HOLD
FULL_PBCWIDE_POSTERIOR = HOLD
```

## 必须先完成的动作

1. 获取或恢复历史 `*_covar_peer_factors_PF10.txt` 的真实字节、sample order 和 checksum；
2. 对 FCRL3 B_IN、B_MEM、NK_R 及 CD4_NC 重新执行 PF10 exact reproduction；
3. 对 7 个目标完成 source summary、PF10 LD、PF50 summary、PF50 LD 的 z–LD consistency diagnostics；
4. 只有 G1 通过，才将 56×14 scaffold 进入全量 QTL eligibility 和 coloc.abf screen；
5. 若无法恢复 PF10 文件，则把历史 PF10 作为 archived primary、当前 PF50 作为 model-sensitivity，并将 R7B0 结论封顶为 `SOURCE_MODEL_UNRESOLVED`，不得声称 fully matched robustness。

## 不允许的捷径

不因 IL12RB2 的 FinnGen `PP.H4≈0.97` 就跳过 OneK source audit；不因 FCRL3–CD8_ET 的 PF50 H4 恢复就选择对自己有利的模型；不扩大位点、细胞或研究病种来掩盖 source-model unresolved。

## R7B1 触发条件

R7B1 只有在 PF10 identity、corrected PF50、PBC-wide eligibility、simulation benchmark 和 external replication 五项均有可审计结果后才启动。若任一核心门失败，按计划保留 PBC 但降低 claim ceiling，或回到有限的 source-recovery，而不是进入投稿资产生产。
