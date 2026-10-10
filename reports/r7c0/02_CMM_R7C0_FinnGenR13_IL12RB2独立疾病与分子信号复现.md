# R7C0 FinnGen R13：IL12RB2 独立疾病与分子信号复现

## 数据入口

- FinnGen R13 phenotype：`CHIRBIL_PRIM`，795 cases / 368,758 controls。
- 官方 summary statistics：`finngen_R13_CHIRBIL_PRIM.gz`，远端对象 787,194,440 bytes。
- 本轮通过远程 Tabix 取得 IL12RB2 完整 ±1 Mb 窗口：14,852 rows，1,483,731 bytes，SHA-256 `d4f80c9a096dba1c6be2e3d1bbeeb2fdcc30aaa72e3aaf5ef6d88747db9d37e7`。
- 官方 R13 SuSiE credible-set files：独立下载、记录 checksum。
- OneK NK/IL12RB2：冻结 PF10 QTL，980 expression donors。

## R12/R13 来源可信集稳定性

R13 credible set 为 R12 credible set 的严格子集：17/17 R13 variants 均在 R12 19-variant CS 中。两版 lead 均为 `1:67336688:A:C`；17 个共享变异的 beta 方向 100% 一致，PIP 相关 `r≈0.833`。

该结果证明 FinnGen 发布版本间信号稳定，不应算成两套参与者独立复制。

## Cordell/GJOKA 与 FinnGen R13 疾病信号

GJOKA primary signal hit `rs6679356`：

```text
GRCh37 1:67820194
A1=C; beta=+0.4433; P=3.11×10^-75
```

同一 rsID 位于 R13 disease CS：

```text
GRCh38 1:67354511:C:T
beta_alt(T)=-0.4125
beta aligned to C=+0.4125
P=2.62×10^-8
CS probability≈0.0220
```

来源描述支持 Cordell international European panels 与 FinnGen Finnish-biobank release 为不同研究系统；但没有 individual IDs，故准确表述为 `study-system independence supported; zero person-level overlap not directly provable`。

## FinnGen R13 × OneK NK/IL12RB2

通过 GJOKA locus-2 rsID 建立 GRCh37→GRCh38 bridge，共获得 1,175 个有效共同变异。Wakefield ABF 沿用冻结先验：`p1=p2=1e-4`，`p12=1e-6/1e-5/1e-4`，疾病 prior SD=0.2，QTL prior SD=0.15×sdY。

| p12 | PP.H3 | PP.H4 | H4/(H3+H4) |
|---:|---:|---:|---:|
| 1e-6 | 0.02239 | 0.97724 | 0.97760 |
| 1e-5 | 0.002286 | 0.99768 | 0.99771 |
| 1e-4 | 0.000229 | 0.99977 | 0.99977 |

共享 top 为 `rs6702599`：OneK 中 A1=A、β=+0.3944；FinnGen 中 ref=A/alt=C、β_alt=-0.4101，因此按 A 对齐后方向一致。

OneK primary QTL CS：

```text
rs6679356 PIP≈0.3244
rs6702599 PIP≈0.6746
2/2 members are in FinnGen R13 disease CS
covered OneK CS PIP mass≈0.99896
```

## 终裁

```text
PASS_INDEPENDENT_DISEASE_X_ONEK_MOLECULAR_SIGNAL
```

允许：independent-disease external molecular-signal validation。
禁止：第二套 source-LD multi-signal proof、已证明因果中介、FinnGen 与 Cordell 的 person-level overlap 为绝对零。
