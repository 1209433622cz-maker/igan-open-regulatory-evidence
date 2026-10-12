# CMM R4A12FG6：R4A12FG7 下一阶段冻结目标

## 阶段名称

> **R4A12FG7 — Source-matched LD Access Package + Primary-data Trigger**

## 为什么停止继续换 external panel

FG6 使用工作区最完整的 27,067-variant EUR503 区域面板后，总覆盖已超过 80%，但 NK source CS PIP mass、QTL top anchor 和所有 secondary cell 的 source-CS 覆盖仍未达到冻结线。继续选择另一个 external panel会形成结果驱动的 reference shopping，不能提高证据等级。

## Track A：source-LD 最小请求包

先准备可直接提交、但不代替 PI/机构签署的材料：

- 研究摘要≤500词；
- dataset：`EGAS50000001654 / EGAD50000002377`；
- 目的：仅对 IL12RB2 100-kb 区间做 source-matched LD 与已公开 summary statistics 的多信号判定；
- 申请人、PI、机构、伦理/数据安全字段清单；
- 最小衍生物边界和销毁/撤权计划；
- 优先请求作者提供 1,366 variants correlation matrix，以避免不必要获取 475.1 GB 数据。

任何外部提交或邮件仍需用户提供身份/机构信息并明确授权；在此之前只生成草稿和本地脚本。

## Track B：获批后流水线

冻结目标区间和变异名单，脚本必须：

1. 验证 GRCh38、样本数和 VCF header；
2. 精确 REF/ALT 映射 1,366 个 TenK10K 变异；
3. 输出每个 cell 实际分析样本口径；
4. 构建 source-matched signed ALT LD；
5. 每个 source CS PIP mass≥95%，QTL top/disease lead/rs6662198 均存在；
6. 通过 AF、对称、diag、PSD、z–LD 诊断后才运行 SuSiE-RSS/coloc.susie；
7. 受控数据及敏感衍生文件隔离，不进入公开包。

## Track C：主线触发器

每次正式推进前先检查 2026 female/male SSc summary-statistics。任何候选字节必须经过 H6 接入；通过即返回 chr22/SYNGR1 主线。

## 决策出口

- `SOURCE_LD_READY`：受控/作者矩阵通过全部门，进入 R4A12FG8 多信号判定；
- `ACCESS_PENDING`：材料已备但未获批，IL12RB2 保持 summary-only，不继续扩大细胞或窗口；
- `PRIMARY_BYTES_READY`：立即切回 sex-specific chr22/SYNGR1；
- `STOP_IL12RB2_ALLSEX_BRANCH`：只允许在 source-matched LD 充分且四细胞稳定支持 distinct/unshared 时触发。
