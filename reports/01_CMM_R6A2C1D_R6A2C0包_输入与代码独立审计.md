# CMM R6A2C1D：R6A2C0 包、输入与代码独立审计

日期：2026-09-14

## R6A2C0 交付包

输入包：`CMM_R6A2C0_REEP3_AsianSpecific_Falsification_ExecutionPack_2026-09-14.zip`

- bytes：22,195；
- SHA-256：`fabb11c0d8359a81b75594400b28b60d7f6b0e9037f8e5c9d6cf96ef4401a3e5`；
- ZIP CRC：PASS；
- 内部 checksum：15/15 PASS。

该包是规范、代码和 frozen baseline 的执行准备包，不含真实 source-LD matrix、SuSiE fits 或终裁结果。随附文字中的“正式执行闭环”不能替代实际输出。本轮重新部署并执行，而没有继承未发生的计算结论。

## 本地输入重验收

| object | bytes | SHA-256 |
|---|---:|---|
| OneK1K 8-locus QTL | 11,914,612 | `3226495312289c0ce9f4165adcd4e0df85dfe94d7e454d224ad0667ba416782f` |
| Asian REEP3 GWAS | 36,909 | `4d810eb60c20cc375fcb32d04c130d5d43c71e3b103667e94459d510e4c01a68` |
| combined REEP3 GWAS | 42,563 | `bfbb9856d162175d289a9fd6e583af9b6e1a6f6a494240fdb41bca448203dd8d` |
| European REEP3 GWAS | 42,477 | `0d37e1170775eaa87e38d115d3999849b77d5c23ffcc612da1458c0bb65061da` |
| OneK PLINK BED | 1,305,096,628 | `75a2ebd613b9c63b7a283722180aeef871d08490cb75ba1bce52deec6a19eb63` |
| OneK PLINK BIM | 155,979,658 | `6e28edad34d5930ca99f7be873e4684a885e26433d13ddba3d970bb8f8ad0bb6` |
| OneK PLINK FAM | 18,597 | `774c0c1c7491e892520c5c645fd790ba6f7ee0204467260fcf6088b68eb428ad` |
| CD4_NC PF50 covariates | 1,075,903 | `10113f4dc88fe11ecf5590fcc41279e3181697d46c958ef2631e9ca7375ac6ae` |
| CD4_NC donor list | 8,797 | `10c95a887cd055564d968a820e36fcfb938264e10674952015bc3dc2c102fd7a` |

## 执行前修正

原脚本把疾病 lead `10:65363048` 在 OneK QTL/genotype 交集中的存在设成 source-LD PASS 必要条件。实际检查发现该位点不在交集中，最近可用变异 `10:65363166` 距 118 bp；冻结 protocol 的技术要求是共享候选 `10:65376395` 在场，不要求疾病 lead 必须可测。已改为：

- 疾病 lead 缺失作为覆盖限制记录；
- 不把它错误升级为 LD 技术失败；
- 共享候选缺失仍会 fail closed。

修正中首次使用了错误列名 `pos`，真实表中为 `position_GRCh37`，触发 KeyError 并停止，未产生半成品科学结论；随后按实际 schema 修正并从第一步重跑。

TenK 摘要 ZIP 内成员虽以 `.tsv` 命名，实际是逗号分隔。首次 schema 显示单列后立即改为 CSV 解析并重跑。最终冻结结果来自正确的六列表/四列表，不来自单列误解析。

所有 Python 脚本通过 `py_compile`，Jaccard synthetic test PASS；R 使用 4.6.1、susieR 0.14.2、coloc 5.2.3。项目根目录已改为支持 `IGAN_PROJECT_ROOT` 环境变量，同时保留本机默认路径。

