# CMM R4A12FG5：FG4输入完整性与状态对齐审计

## 输入

本轮主要输入：
1. `CMM_R4A12FG4_TenK10K_NK接入与信号门_2026-09-13.zip`
2. 历史项目归档 `YR1.zip` 中 R4A8B/R4A9 EUR503 engineering outputs

## FG4 release独立核验

- ZIP SHA-256：`f2f500cae52b83a77bba55f9d1455d9eabad1c63f1320833716494c8f818ab53`
- ZIP CRC：PASS
- 成员数：46
- `checksums.sha256`记录：45
- 逐成员SHA-256：45/45 PASS

没有发现需要推翻FG4状态的归档损坏。

## 历史EUR503资产身份

`YR1.zip` SHA-256：`1ce8916155f19422483a30d93e468d22bec574188b94f068a5ee44e5d0baa338`。

可复核的历史资产包括：
- `IL12RB2_G_source_A1.npy`：503×1555
- `IL12RB2_signed_r.npy`：1555×1555
- `IL12RB2_order.tsv`
- R4A8B/R4A9 reference audit

R4A9历史审计证明该1555-variant工程矩阵来自1000 Genomes Phase3 v5a EUR503，并在当时与PLINK2 dosage逐单元一致。

但是该1555集合是围绕 **GCST009131旧overall GWAS** harmonization之后的保留集合，不是27,067个区域参考变异全集。因此本轮只允许把它称为：

> `ARCHIVED_OLD_GWAS_MATCHED_EUR503_SUBSET`

禁止写成：

> `FULL_EUR503_IL12RB2_REFERENCE`

## 状态继承

FG4的下列状态保持：
- `PROJECT=CONDITIONAL_GO`
- `R4B=HOLD`
- `C1_count=null`
- 2026 female/male主anchor未取得
- IL12RB2 all-sex分支只能作为secondary/sensitivity
- NK为primary molecular cell
- secondary固定为 `CD8_TEM / CD4_CTL / CD4_TCM`

本轮没有让附件里的历史“next stage”文字自动覆盖机器状态，而是依据可复核字节执行FG5门。
