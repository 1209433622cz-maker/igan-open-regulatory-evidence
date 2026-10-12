# CMM R4A12FG4 执行摘要：TenK10K NK 接入与信号门

日期：2026-09-13

## 最终判定

- 总项目：`CONDITIONAL_GO`
- 正式 R4B：`HOLD`
- `C1_count=null`；2026 female/male SSc 主数据仍未取得
- FinnGen all-sex IL12RB2 分支：`SUMMARY_ONLY_AMBIGUOUS_LD_AWARE_ADJUDICATION_REQUIRED`
- 下一阶段：`R4A12FG5_EXTERNAL_LD_AND_THREE_CELL_REPLICATION_GATE`

## 本轮新证据

TenK10K 16.56 GB 远程 ZIP 的中央目录确认有 28 个细胞文件。本轮没有下载整个归档，而是以 HTTP Range 只取得 NK 成员 556,881,415 个压缩字节；完整 DEFLATE 流展开为 2,272,841,254 字节，成员 CRC32 `25f9b199` PASS。从 15,588,167 行中精确提取 1,366 条 `ENSG00000081985/IL12RB2` 记录。真实表头确认含 `Allele1/Allele2/AF_Allele2/BETA/SE/p.value/N`，其中 SAIGE-QTL 的 BETA 对应 Allele2。

R12 与 R13 各有 891 个 exact GRCh38 REF/ALT 重叠，占 QTL 变异 65.23%；5 个反向等位基因位置因多等位/重复序列歧义被排除。AF 绝对差中位数约 0.02994、P95 约 0.12226，QTL top、rs6662198 和 disease regional lead 全部保留且效应方向一致。

exact coverage 仍未通过：CS1 仅覆盖 11/12 成员、72.07% PIP mass；缺失的 rs5022165 自身 PIP=0.2833。外部 1000G EUR503 显示它与已精确覆盖的 rs11209050 `r²≈1.0`，所以允许一次明确标注的 post-gate 诊断，但 exact coverage 与 source-matched LD 仍保持 HOLD。

`coloc.abf` 结果明显依赖 p12。主 `p12=10^-5` 时 R12 `PP.H4=0.8467`、R13 `PP.H4=0.8319`；降至 `10^-6` 时分别为 0.3558 和 0.3311。两版均判定 `AMBIGUOUS_SINGLE_CAUSAL_SENSITIVITY`。由于 NK 有两个 source SuSiE signals、精确覆盖不足且 R12/R13 不是独立队列，该结果不能升级 C1，也不能判 IL12RB2 阴性。
