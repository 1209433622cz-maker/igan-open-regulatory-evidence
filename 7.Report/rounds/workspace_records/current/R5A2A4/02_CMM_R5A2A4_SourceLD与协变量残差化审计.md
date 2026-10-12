# R5A2A4 Source LD 与协变量残差化审计

## Source LD 身份

分析严格使用 NK_R 的 750 个 active donors，而非 980 个全体 covariate donors。ZCCHC2 固定窗口 3,827 个 QTL 变异全部按原顺序映射至 OneK1K BIM，效应等位基因统一为 BIM A1。

| 检查 | 结果 |
|---|---:|
| FAM donors | 980 |
| NK_R active donors | 750 |
| QTL/BIM 共同变异 | 3,827 / 3,827 |
| 缺失 genotype | 0 |
| 零方差变异 | 0 |
| 最大 AF 差 | `3.33×10^-8` |
| minor count/carrier 不一致 | 0 |
| finite / symmetry / unit diagonal | PASS |
| PSD 数值门 | PASS |
| rs7239261 / QTL top | 均存在 |

raw genotype LD 中，rs7239261 与 `18:60243208` 的 signed `r=-0.1088`、`r²=0.01184`。两者不是同一高 LD block。

## 与源分析模型匹配

公开 OneK1K TensorQTL 脚本在关联模型中使用 sex、6 个 genotype PCs、age 和 PF10。为使 summary-statistic RSS 的 LD 更接近同一设计矩阵，本轮把 PF10 残差化 LD 设为主分析；raw genotype LD 和更新 covariate 的 PF50 残差化 LD作为敏感性分析。

| LD | 设计秩 | 残差自由度 | lead–top r² | 数值门 |
|---|---:|---:|---:|---|
| raw | — | — | 0.01184 | PASS |
| PF10 | 19 | 731 | 0.01241 | PASS |
| PF50 | 59 | 691 | 0.00931 | PASS |

PF10 对 raw 的最大绝对相关系数变化为 0.0389，中位数 0.00387；PF50 对 raw 的最大变化为 0.0528。结论在三种 LD 下相同。

三个完整 3,827×3,827 LD 矩阵和标准化 dosage 保留在本地结果目录，通过 QC JSON 中的 SHA-256 引用，不纳入轻量发布包。发布包包含变异顺序、750 donor 列表、anchor LD、QC 和全部构建代码。
