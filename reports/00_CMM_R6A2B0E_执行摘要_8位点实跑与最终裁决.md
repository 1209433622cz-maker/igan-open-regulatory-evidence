# CMM R6A2B0E 执行摘要：8 位点实跑与最终裁决

日期：2026-09-14

## 最终判定

```text
R6A2B0_BYTE_LEVEL_EXECUTION = COMPLETE
ONEK_ARCHIVE_IDENTITY = PASS
FROZEN_COMBINATIONS = 183 / 183 TESTABLE
COLOC_TESTS = 549 / 549 COMPLETE
PYTHON_VS_OFFICIAL_R = PASS

ADDITIONAL_COMBINED_IGAN_ROBUST_LOCI = 0
COMBINED_TARGETED_LD_TRIGGERS = 3 COMBINATIONS / 2 LOCI
TARGETED_SOURCE_LD = 3 / 3 PASS
TARGETED_SUSIE_FITS = 12 / 12 CONVERGED
STABLE_95PCT_CREDIBLE_SETS = 0

FULL24_EXPANSION = HOLD
NEXT_STAGE = R6A2C_REEP3_ASIAN_SPECIFIC_FALSIFICATION_AND_DESIGN_REASSESSMENT
```

R6A2B0 的 8-locus bounded positive-yield expansion 已在本机真实字节上完成。combined IgAN 主分析没有新增 robust shared-signal 位点。smoke 阶段触发的 `OVOL1/RELA–SIPA1–CD8_ET`、`TNFSF12/13–EIF4A1–CD4_NC` 和 `TNFSF12/13–SAT2–B_IN` 均完成细胞 donor 匹配、PF10/PF50 协变量残差化 LD 和 SuSiE-RSS；12 个配置全部收敛，但没有任何 95% credible set，因此没有合法的 signal-specific coloc 对象。

这意味着 R6A2B0 不能按“至少两个新增阳性位点”的预注册出口进入 full-24，也不能把高 `p12` 下的 smoke H4 当作阳性。combined 主结论冻结为 `HOLD_FULL24_REASSESS_DESIGN`。

## 主分析结果

OneK1K 原始 cis-eQTL 包完整读取 10,344,009,571 字节，MD5 为 `e42239480f40abd21f221c0d77c82cc3`，SHA-256 为 `63b980c82c234268183205a9cf3c9da96ead1440d7b4b4586652f38ea18039ea`。冻结的 43 个 chr×cell parquet 全部取得；183 个 cell–gene 组合全部可测，共 449,282 条区域 QTL 记录。

三套 IgAN GWAS 在 8 个冻结窗口中全部完成 GRCh37/BIM A1 harmonization。549 个 `coloc.abf` 比较全部运行，Python 与官方 R `coloc 5.2.3` 的最大后验绝对差为 `3.77×10⁻14`。

| 位点 | combined 最佳组合 | 最佳 PP.H4 | H4/(H3+H4) | 主裁决 |
|---|---|---:|---:|---|
| TNFSF12/13 | EIF4A1 × CD4_NC | 0.391 | 0.499 | targeted LD 后无稳定 CS |
| OVOL1/RELA | SIPA1 × CD8_ET | 0.327 | 0.465 | targeted LD 后无稳定 CS |
| REEP3 | REEP3 × CD4_NC | 0.076 | 0.099 | combined 不支持 |
| LIF/OSM | MTFP1 × CD4_NC | 0.068 | 0.078 | distinct signal favored |
| TNFRSF13B | CCDC144A × CD4_NC | 0.032 | 0.101 | distinct signal favored |
| REL | PAPOLG × CD4_NC | 0.029 | 0.090 | distinct signal favored |
| TNFSF8/15 | TNFSF8 × CD4_NC | 0.018 | 0.018 | distinct signal favored |
| TNFSF4/18 | PRDX6 × NK | 0.018 | 0.029 | distinct signal favored |

## 唯一保留的次级信号

预冻结 ancestry-supportive 分析中，`Asian-only IgAN × REEP3 × CD4_NC` 得到：

```text
n SNPs = 2,231
Asian regional disease min P = 4.55e-6
QTL min P = 2.31e-10
PP.H4 = 0.9057
H4/(H3+H4) = 0.9179
p12=1e-6: PP.H4 = 0.4900, H4/(H3+H4) = 0.5278
shared top variant = 10:65376395
conditional SNP.PP.H4 = 0.5305
```

同一组合在 combined 和 European-only 中分别只有 PP.H4≈0.076 和 0.015。该观察来自预冻结数据集、位点、基因和细胞，不属于事后扩展，但疾病关联未达全基因组显著，且存在明显祖源不一致。因此它只触发一个窄的 ancestry-specific falsification gate，不能计入 R6A2B0 的 combined 阳性位点数。

## 下一阶段

R6A2C 只允许：

1. 为 `REEP3 × CD4_NC` 构建 PF10/PF50 OneK1K source-matched LD；
2. 对 Asian-only 疾病信号做 SuSiE/条件分析和 signal-specific coloc；
3. 核查 European 与 combined 的方向、频率、覆盖和 signal overlap；
4. 仅在 Asian signal-specific H4 稳健时查询 TenK10K 对应细胞独立复制；
5. 同时完成主论文设计重评，不启动 full-24、GEO 或稿件规模分析。

如果 REEP3 不能通过 signal-specific 与跨资源门，则停止继续扩 IgAN 免疫细胞 cis-expression 位点。届时应重构问题或换用公开 pQTL/kidney-layer 设计，而不是继续增加第 9、10 个位点。

