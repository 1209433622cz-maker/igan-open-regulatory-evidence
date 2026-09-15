# CMM R7A1B1：R7A1B0 包与代码修正审计

**日期：2026-09-15**

## 1. 输入包验收

用户提供：`CMM_R7A1B0_PBC_3Control_SignalGate_Hardening_2026-09-15.zip`。

```text
bytes = 77,006
SHA-256 = 3345fa585ccd57d2b36c529ee4c6335169328cda168635d3ee29148565fe1dd0
ZIP CRC = PASS
internal checksums = 37/37 PASS
```

包内是冻结协议、脚本和空结果骨架，不含真实 OneK/GJOKA 信号结果。因此本轮把其中结论视为执行设计，未把它当作完成证据。

## 2. 运行前发现并修正的问题

### 2.1 GJOKA 效应字段

原 `09_run_pbc_multisignal_coloc.R` 使用：

```r
beta = log(OR)
se = abs(beta / STAT)
```

真实 `sumstats_i.assoc.logistic` 表头是 `BETA, SE, STAT`，没有 `OR`。正式代码改为直接读取原始 `BETA`、`SE` 与 `STAT`，并检查 `BETA/SE` 与 `STAT` 的一致性。locus 2/4 的相关系数均大于 0.99999996；最大差 0.00611，符合源表约四位有效数字造成的舍入范围，冻结容差为 0.01。

### 2.2 LD 变异位置列

`LD_variants.tsv` 的实际位置字段是 `position_GRCh37`，原 R 脚本引用不存在的 `pos`。改为显式转换 `position_GRCh37`，并继续要求 rsID 与坐标同时匹配。

### 2.3 `annotate_susie` 的 LD 维度名

当前 `coloc 5.2.3` 会按 SNP 名称索引 LD。原矩阵没有行列名，导致 `subscript out of bounds`。修复为在疾病/QTL 两侧均设置 `dimnames(LD)=variant_id`，保证可信集和 LD 使用同一排序。

### 2.4 可信集 purity 计数

原 QC 再调用 `susie_get_cs()` 时没有传入 LD，因此只按 posterior coverage 计数，未应用 `min_abs_corr=0.5` purity 门。修复为分别传入 GJOKA 与 OneK 残差 LD。IL12RB2 疾病侧最终是 2 个经过 purity 筛选的可信信号，而不是未筛选时的 5–6 个。该修正不改变 `coloc.susie` 的信号后验，也不改变至少一个可信集的通过条件。

### 2.5 可移植性与序列化

runner 的 R 路径改为优先读取 `R7_RSCRIPT`，否则使用项目内 R。最终 JSON 禁止 `NaN`，不可用值写为标准 JSON `null`。新增逐变异可信集成员导出和独立 QA。

## 3. 环境修复

项目 R library 中 `coloc` 因缺少 `farver` 无法加载。本轮从 CRAN 安装 `farver 2.1.2`，随后验证：

```text
R = 4.6.1
coloc = 5.2.3
susieR = 0.14.2
data.table/jsonlite = LOAD PASS
```

启动时的 `C.UTF-8` locale 警告不影响数值运行或 UTF-8 文件输出。

## 4. 防污染原则

所有错误均在终裁结果写出前触发。修复后完整执行第 9/10 步，并在最终代码上重新生成 SuSiE、可信集、终裁、图和 QA。核心 `R7A1B_signal_coloc_susie.tsv` 最终 SHA-256 为：

```text
a9777791d0046625613293b3aea740337b8d5300976752ba20b475d5346d65cc
```
