# CMM R4A12FG2：IL12RB2 区域与 TenK10K 描述性 Smoke Test

执行窗口：2026-09-12—2026-09-13（Asia/Hong_Kong）

## 1. Disease 区域

R12 与 R13 的 6,855 个区域变异键完全共同。两版 lead 均为：

`1:67448804:T:A / rs1954118`

R12 P=2.62404×10^-5，R13 P=2.84564×10^-5。该信号没有达到 P≤5×10^-8，因此不能写成 FinnGen genome-wide significant replication，也不能假定 FinnGen native fine-mapping 在这里产生了 credible set。官方说明 native fine-mapping 面向 GWS regions。

旧 2019 overall SSc 工程正控中 rs6662198 为 GRCh37 1:67,806,207，A1=T，recovered A2=C，OR=1.1779，P=6.134×10^-9。NCBI GRCh38 对应键为 `1:67340524:T:C`。FinnGen 两版 C-ALT beta 均为负，因此风险 T 方向相容。

## 2. 跨 release 结构

| 指标 | 结果 |
|---|---:|
| exact common variant keys | 6,855 |
| beta Pearson r | 0.956607756 |
| ALT AF Pearson r | 0.9999999975 |
| 全部变异 beta 方向一致 | 95.244% |
| 任一版本 P<0.05 的变异数 | 497 |
| 上述变异方向一致 | 99.799% |

R12/R13 的样本与数据冻结高度嵌套，所以上述结果只能说明 release 更新后区域结构稳定。

## 3. TenK10K 原始包复核

两个输入 archive 的 SHA-256 与 v11 registry 一致：

- gene-level：`fcb99a4454a2a5f0feb11c56bcedad667400ebbeead2b39f256a25f48b71ae74`
- SuSiE summary：`0a2e2cb0dec4b76d18e42b29c36b243a9ccd67b8761f17d20a83ae51f656e7ff`

Gene-level 结果在 28 个 cell-type files 中找到 26 个 IL12RB2 行。最强 ACAT 信号出现在 NK：ACAT P=3.42337×10^-118，top marker `1:67324915:T:C`，top P=6.80524×10^-121。CD14 Mono 与 CD16 Mono 没有返回 IL12RB2 行；这按 `NOT_RETURNED` 处理。

SuSiE summary 在 11 个 cell types 中返回 17 个 CS、201 条成员、76 个唯一精确键。每个成员保留 source ZIP member 和 source line，可追溯到压缩包内部。

## 4. 精确变异重叠

R12 与 R13 都能精确匹配 68/76 个 TenK10K IL12RB2 CS 变异，覆盖 89.47%。R13 中 CS 成员的最小 disease P 为 3.04902×10^-4，对应 `1:67324915:T:C / rs17129789`；R12 最小为 3.15319×10^-4，对应 `1:67322008:A:T / rs17129778`。

关键不一致：

- FinnGen disease lead `rs1954118` 不在 IL12RB2 CS。
- 2019/FinnGen anchor `rs6662198` 不在 IL12RB2 CS。
- disease signal 与 QTL CS 有许多区域成员重叠，但没有完成 LD-aware signal matching。

因此不能从“68/76 覆盖”推出共定位；高覆盖只证明输入组合在 variant identity 层面有希望进入下一门。

## 5. 为什么没有立即跑 coloc / SMR / RSS

现有 TenK10K 两个小包分别只有：

- gene-level ACAT P、top marker、top P；
- source SuSiE CS member、PIP、CS id。

它们没有完整 per-variant beta、SE、AF/N 或完整 signal likelihood/Bayes-factor 对象。FinnGen region 也尚未配套冻结 INFO、reference normalization 与 matched LD。强行从 CS PIP 反算 coloc 输入会制造不可验证的后验，因此本轮没有这样做。

机器分类：

`DESCRIPTIVE_EXACT_VARIANT_OVERLAP_AND_INPUT_AVAILABILITY_ONLY`


