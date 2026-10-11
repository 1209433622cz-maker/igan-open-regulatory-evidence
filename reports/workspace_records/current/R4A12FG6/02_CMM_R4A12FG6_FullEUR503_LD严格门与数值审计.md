# CMM R4A12FG6：Full EUR503 LD 严格门与数值审计

## 1. 参考面板身份

Canonical prefix：`1_data/reference/ld/1000G_Phase3_v5a_EUR503/legacy_chr1_IL12RB2/1000G_Phase3_v5a_EUR503_IL12RB2_GRCh37`

| 文件 | 大小 | SHA-256 |
|---|---:|---|
| BED | 3,410,445 | e6ea7cd7c852414534fb5a98a4a4d2c835259047dcc383a85754552560d94b74 |
| BIM | 779,076 | 6d4a6fe209c16b3d6b23e9331688d770f70dd16807d3b9f96cf12a8ad6470744 |
| FAM | 12,575 | 1a25d5ec4dba807e049831290805ef04275be1c3dd3706a2e400ab901cec5cc6 |

BIM 为 27,067 行，FAM 为 503 人；BED 大小与 SNP-major 编码期望完全相符。

## 2. 映射结果

- current exact set：891
- 单一合法 rsID：839
- 复用 rsID 的输入行：4 行，对应两个多等位位点
- rsID+allele-set 精确匹配并为多态：764
- 最终 LD 覆盖：85.746%

该提升证明 FG5 的 36.92% 主要是旧 1,555 子集限制，而不是完整区域面板完全无效。

## 3. 数值和方向质控

- 样本数：503
- signed R 维度：764×764
- 最大不对称：2.22e-16
- 最大对角偏差：2.22e-16
- 最小特征值：-5.69e-14，在 -1e-7 容差内
- rank（tol=1e-10）：316，符合区域 LD 高相关结构，不被误判为损坏
- FinnGen AF vs EUR503：r=0.98897；median |ΔAF|=0.02353；P95=0.09619
- TenK10K AF vs EUR503：r=0.99919；median |ΔAF|=0.00668；P95=0.02926

precision residual 的最大绝对值较大（GWAS 48.59，QTL 91.02），说明 external EUR503 与 summary z 结构仍有错配或多信号影响。该指标按冻结规则只报告，未用于删除、翻转或降权任何变异。

## 4. 冻结门结果

NK CS1 只保留 9/12 个成员、61.74% PIP mass；CS2 只保留 2/4 个成员、72.73% PIP mass。`rs17129789` 缺失，`rs6662198` 和 `rs1954118` 存在。

因此总覆盖、方向、数值结构虽然通过，source-CS 和三 anchor 条件失败。最终为：

> `FAIL_INPUT_COVERAGE_FOR_MULTISIGNAL`

没有运行 external-LD SuSiE-RSS/coloc.susie。该停止点由看结果前冻结的 FG5 规则决定。
