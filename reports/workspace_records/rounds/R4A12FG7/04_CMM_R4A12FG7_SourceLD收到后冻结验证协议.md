# CMM R4A12FG7：Source-LD收到后的冻结验证协议

## Phase S0 — receipt

- 保存原始 `.bim/.ld`，记录provider、日期、bytes、SHA-256。
- 不先裁剪、不改allele、不转格式。

## Phase S1 — structural gate

运行 `scripts/validate_received_tenk10k_source_ld.py`：

- square dimensions = BIM variants；
- finite、symmetric、diag=1、PSD tolerance；
- native MarkerID overlap；
- native BIM A1/A2与公开TenK10K MarkerID一致；
- rs17129789、rs6662198、rs1954118 anchors；
- 四细胞所有source CS PIP mass ≥95%。

任何失败：`HOLD_SOURCE_LD_STRUCTURAL_GATE`。

## Phase S2 — source reproduction gate

在**不看FinnGen disease结果**的情况下，用公开TenK10K beta/SE与native LD重跑SuSiE：

- primary：NK；
- secondary：CD8_TEM、CD4_CTL、CD4_TCM；
- 首先要求source CS数量、lead/PIP结构与公开`suSie_summary`合理一致；
- 若不能重现，不进入疾病共定位。

## Phase S3 — bounded disease integration

只有S1+S2通过才允许：

- R13为all-sex primary sensitivity；R12为release-stability；
- disease侧LD仍必须单独标识为external；
- 固定variant set、固定prior sensitivity、固定四细胞；
- 不允许换窗口/更多细胞/删除高residual变异救结果。

## Phase S4 — classification

- `SOURCE_LD_MULTISIGNAL_SUPPORTED`：source eQTL SuSiE复现 + fixed disease sensitivity支持shared结构；仍只是secondary all-sex finding。
- `SUMMARY_ONLY`：source LD到位但disease-LD或multi-signal不稳。
- `STOP_IL12RB2_ALLSEX_BRANCH`：仅在输入充分且四细胞稳定distinct/unshared时。
