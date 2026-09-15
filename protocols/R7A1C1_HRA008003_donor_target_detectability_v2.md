# R7A1C1 HRA008003 PBC 肝组织 donor-level target detectability 冻结协议 v2

**冻结日期：2026-09-15**
**结果盲态：冻结时五个完整 BAM 尚未下载或分析。**

## 1. 目的与边界

本门只回答两个有限问题：PBC 肝组织中，`FCRL3` 是否可在 B-lineage called cells 中稳定检测，或 `IL12RB2` 是否可在 NK-lineage called cells 中稳定检测。它不是健康对照差异分析，不替代完整单细胞 QC、整合、重聚类、注释或 donor-level pseudobulk。

遗传/QTL 前提固定为：

```text
FCRL3 = PASS_SIGNAL_SPECIFIC_SHARED_GENE
IL12RB2 = PASS_SIGNAL_SPECIFIC_SHARED_GENE
TENK_REPLICATION_GATE = PASS
```

不得在本门中增加其他基因、细胞谱系或数据集。

## 2. v1 作废原因

HRA008003 BAM 为 Cell Ranger 3.1 输出。`CB` 表示校正后的 barcode/whitelist tag，不等同于最终 called cell。v1 脚本把所有带 `CB` 的记录纳入分析，可能让环境 RNA 和低质量背景 barcode 产生假阳性；同时它以读段集合近似 UMI，而没有使用 `xf` bit 8 的 molecule representative 语义。

因此：

```text
R7A1C1_v1_OUTPUT_ELIGIBILITY = INVALID_FOR_FINAL_ADJUDICATION
R7A1C1_v2_REQUIRED = YES
```

v1 代码只作为审计证据保留，不允许产生项目升级结论。

## 3. 冻结输入

只允许 HRA008003 的五个 PBC liver runs：

```text
HRR1849459
HRR1849460
HRR1849461
HRR1849462
HRR1849463
```

每个 BAM 必须同时通过官方字节数和官方 MD5；本地另计算 SHA-256。运行清单为：

`1_data/scrna/PBC/HRA008003/manifests/HRA008003_PBC_liver_primary_run_manifest_v2.tsv`

五个 BAM 合计约 142 GiB。执行器一次只保留一个 BAM；完成校验和 compact target-panel 输出后，默认删除该 BAM并继续下一供者。

## 4. molecule 与 called-cell 规则

1. 单遍顺序扫描完整 BAM。
2. 只保留 `xf bit 8` 非零的 molecule-representative records。
3. 排除 unmapped、secondary、supplementary、缺失 `CB` 或 `GN` 不唯一的记录。
4. 用每个 barcode 的 unambiguous-gene molecule 数重建 total UMI，同时仅缓存冻结 marker/target panel 的小型计数。
5. expected recovered cells 固定为 6000；called-cell threshold 固定为 top 6000 barcode UMI 的第 99 百分位数的 10%。
6. 技术合理性门：called cells 必须为 2500–7500，called-cell median total UMI 必须至少 500。越界即 fail closed，不输出生物学判定。

## 5. 谱系规则

B marker panel：`CD79A, CD79B, MS4A1, CD37, CD74, HLA-DRA, CD19, CD22`。

NK marker panel：`NKG7, GNLY, KLRD1, PRF1, GZMB, XCL1, XCL2`。
T/myeloid panels 仅用于排除竞争谱系。

B gate：至少 2 个 B marker、B marker UMI 至少 3，且高于 NK/T/myeloid marker UMI。

NK gate：至少 2 个 NK marker、NK marker UMI 至少 3，高于 B/myeloid，且不低于 T marker UMI。

单供者谱系充分性固定为该谱系至少 10 个 called cells；不充分时该供者/谱系不允许记作 target positive。

## 6. 检测与项目升级门

原始 primary 可检测：充分谱系中 target UMI 至少 1。

升级合格的稳健可检测：充分谱系中 target UMI 至少 3，且分布在至少 2 个 target-positive cells。

项目升级必须由同一 target 在至少 3/5 PBC donors 中达到“升级合格的稳健可检测”：

```text
FCRL3_B_promotion_eligible_donors >= 3
OR
IL12RB2_NK_promotion_eligible_donors >= 3
```

通过：`GO_R7A2_PBC_MANUSCRIPT_SCALE`。

失败：`FREEZE_PBC_REGULATORY_MAIN_NO_CED_AUTO_RESUME`。

五个供者全部通过技术 QC 前，不允许作最终判定。任何完整数据结果出现后不得再修改本门阈值。

## 7. 实现与验收

冻结实现：

- `02_hra_bam_target_panel_v2.py`
- `03_adjudicate_HRA008003_liver_gate_v2.py`
- `RUN_R7A1C1_HRA008003_TARGET_PANEL_v2.ps1`

执行前要求 Python 语法检查、PowerShell parser、合成五供者判定测试全部 PASS。最终结果必须包含五个 `CMM_R7A1C1_TARGET_PANEL_2.0` summary 和一个 `CMM_R7A1C1_LIVER_ADJUDICATION_2.0` adjudication。
