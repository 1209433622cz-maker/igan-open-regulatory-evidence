# CMM R5A2A3 执行摘要：chr18 coloc.abf smoke gate

**日期：2026-09-14**

```text
MG_MAIN_PROJECT = CONDITIONAL_GO
R5A2A3_COLOC_ABF_SMOKE = COMPLETE
N_TESTS = 213
ROBUST_SHARED_SIGNAL = 0
TARGETED_SOURCE_LD_TRIGGER = 1
TRIGGER = NK_R / ZCCHC2
TENK10K_REPLICATION = HOLD
TISSUE_ANALYSIS = HOLD
NEXT_STAGE = R5A2A4_NKR_ZCCHC2_SOURCE_LD_AND_MULTISIGNAL_ADJUDICATION
```

完成 overall MG、EOMG、LOMG × 71 个 OneK1K cell–gene 组合。没有任何组合达到冻结的 `PP.H4>=0.80` 且 `H4/(H3+H4)>=0.80` 的稳健共享门。

唯一 targeted source-LD 触发为 **NK_R × ZCCHC2**：

- LOMG: H3=0.1658, H4=0.3363, H4/(H3+H4)=0.6698
- H4 @ p12=1e-6 / 1e-5 / 1e-4 = 0.0482 / 0.3363 / 0.8352
- overall MG 同组合 default H4=0.4273
- QTL min P≈4.96e-05; rs7239261 QTL P≈0.0051

这不是阳性共定位，而是 prior-sensitive 的 H1/H3/H4 混合状态。只允许为该组合建立一次 cell-specific source LD，判断是否存在与 rs7239261 对齐的次级 ZCCHC2 eQTL。

`Mono_NC/PIGN` 的 QTL 很强（min P≈1.09e-7），但 LOMG H3≈0.625、H4≈0.020，更支持不同信号，不触发 LD。TNFRSF11A 5 个可测细胞均无稳健共享证据，OneK1K 当前不支持 TNFRSF11A expression mediation。
