# R7A1C0 输入与代码独立复核

## 发布包完整性

- 外部 SHA-256：`f1241b7b68a7f924d0e0625329c5f549aa0bf1f66ab80e93ead61ef357cc135b`，与 sidecar 一致。
- ZIP members：27；CRC 全部通过。
- 内部 checksums：26/26 PASS。

因此 R7A1C0 的报告和静态结果可作为审计输入，但代码必须经过运行时复核后才能执行。

## 运行时缺陷

`01_recompute_IL12RB2_TenK_NK_fullPBC.py` 将含点号的 `p.value` 列通过 `itertuples()` 读取后，仍按字典形式访问 `qr["p.value"]`，首次运行即报错。语法编译无法发现该错误。本轮部署版在读取后显式重命名为 `p_value`，并增加 required-column、finite value、SE、AF、overlap 和最终 posterior 断言。

修复后实际得到 396 个精确 allele overlap，去除了原包 292-rsID bridge 的限制。结论仍保留 source-CS 不在精确交集内、需要外部 EUR503 LD 支持的边界。

## HRA v1 的科学缺陷

对 HRA008003 首个 BAM 的前 64 MiB 探针显示：

- 926,729 个可读 alignment records；
- 912,424 个带 `CB`；
- 仅该局部已有 45,117 个不同 `CB`；
- `xf bit 8` molecule records 覆盖 14,315 个不同 `CB`。

原研究每样本约 5,194 cells、建库目标 6,000 cells。因此 `CB` 数远高于真实细胞数，直接证明 `CB` 是 whitelist/corrected barcode 层，不能代替 called-cell filtering。v1 结果资格被作废，代码只保留为审计对照。

## 加固实现

v2 对完整 BAM 单遍扫描，并同时重建 total UMI 和冻结 panel 计数，不再创建大型未压缩中间 BAM。执行链使用官方字节数、MD5、本地 SHA-256，一次只保留一个供者 BAM；供者通过 compact panel 校验后默认删除，支持 aria2 断点续传。

独立 QA：12/12 项 PASS。五供者真实结果尚不存在，因此项目状态必须保持 HOLD。
