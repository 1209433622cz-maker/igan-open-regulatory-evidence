# R7B2A 输入冻结、A0/A1/A2 重算与身份验收

## 冻结对象

- 642 个 comparison；47 loci、200 genes、14 cell types。
- 原分层保持为 184 primary verification、455 H3 rescue/falsification、3 borderline calibration。
- RP v3 SHA-256：`310b307e5463825968ee93e52ca34fb997b6a28b81d79ce791d831fc6f18ed59`。
- 结果前冻结协议 SHA-256：`1295f072d192fa3ec22631c7a0e4ac247576d2bacc56ca32c599622594ef7c03`。

## 支持集与等位基因

每个 comparison 同时保存原 ABF 集 `S_A` 和实际多信号集 `S_M` 的有序成员、数量和 SHA-256。`S_A` 为 243–1,724 个变异，`S_M` 为 224–1,684 个；每项减少 19–114 个，中位减少 65 个。GJOKA A1 与 QTL/BIM 方向共 496,205 个 exact、2,350 个 flipped、0 unresolved。

## 六个输出臂

1. `A0_REPLAY`：GCST beta/SE、`S_A`、历史固定 sdY。
2. `A1_FIXED_SDY`：GCST beta/SE、`S_M`、固定 sdY。
3. `A1_NATIVE_SDY`：A1 的原生 `S_M` sdY 敏感性。
4. `A2_MATCHEDZ_FIXED_SDY`：GJOKA `STAT×SE`、`S_M`、固定 sdY。
5. `A2_MATCHEDZ_NATIVE_SDY`：A2 原生 sdY 敏感性。
6. `A2_ROUNDED_FIXED_SDY`：GJOKA source BETA/SE 舍入敏感性。

所有 3,852 行均为 PASS。A0 posterior 最大绝对误差为 `3.543e-13`，top shared variant 642/642 一致；A1/A2 没有技术失败。固定与原生 sdY、matched-z 与 rounded BETA/SE 均未造成分类变化。

## 边界

A2 与 M 的同输入比较消除了主要支持集和疾病统计定义不对称，但仍比较完整推断程序：单因果 Wakefield ABF 与 SuSiE/coloc.susie 的效应结构、credible set 构建和 posterior 汇总均不同，不能把 A2→M 简化为单一“因果变异个数”效应。
