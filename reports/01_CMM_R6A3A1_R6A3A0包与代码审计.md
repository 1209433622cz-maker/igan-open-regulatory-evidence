# R6A3A0 输入包与代码审计

日期：2026-09-15

## 包完整性

- 输入：`CMM_R6A3A0_IgAN_CompletionDesignGate_ExecutionPack_2026-09-14.zip`
- 外层 SHA-256：`7acfd7cca97598550e9ec9c90daf37104e6164fe14478661f33829c71ec8f479`
- ZIP CRC：PASS
- 内部 `CHECKSUMS.sha256`：29/29 PASS
- 性质：`COMPLETE_EXECUTION_PREPARATION`，未包含本轮的真实 pQTL/肾组织结果。

附件内的说明与脚本被视为待审计输入；用户请求是继续执行和判断下一阶段，两者没有混为同一层级。

## 发现并修正的实现问题

| 问题 | 原实现影响 | 修正 |
|---|---|---|
| Sun permutation 表的 Ensembl ID 实际位于 `molecular_trait_object_id` | 原脚本不识别该列，可能把已测蛋白误标为未测 | 显式识别该列并去除 Ensembl version |
| permutation-adjusted 显著性列实际为 `p_beta` | 原脚本只用不存在的 `qval` 判定，source significance 恒为 False | 冻结优先级 `qval → p_beta → pval_beta → p_perm`，本数据实际使用 `p_beta<0.05` |
| 候选 trait 输出包含未达 source signal 的已测 probe | 会违反“小文件先筛，只有 source-supported 才下载/分析”的门 | 只保留 adjusted-P<0.05 或 source-CS 存在的 trait |
| `coloc.bf_bf` 的 `hit2` 被当作 SuSiE 分量名 | `hit2` 实际是 top variant，导致所有 source-CS 都被错误标为缺失 | 使用 `idx2` 映射为 L1–L10；`hit2` 仅保存为 component top variant |
| marker localization 对 3,620 个细胞全部运行 | 835 个 PBMC 单核细胞被混入肾组织定位 | 从 SOFT 逐细胞匹配，严格保留 2,785 个肾细胞 |
| 负链多碱基 allele 只做 complement | indel 需要 reverse-complement | 改为 complement 后反向 |
| Rscript 路径写死为 `<PROJECT_ROOT>` | 破坏 `IGAN_PROJECT_ROOT` 可移植性 | 改为从 `$Root` 拼接 |
| EBI 单连接下载较慢 | 约 1.2 GB 文件耗时过长 | 增加带 byte-range、断点、长度核验和组装核验的 8 连接下载器 |

修正后的 9 个 Python 分析/QA 脚本全部通过 `py_compile`；R 使用 `coloc 5.2.3` 正常完成 60 行 component/prior 结果。

## 冻结目标表的结构问题

`TNFRSF18` 当前 GRCh38 基因坐标约 chr1:1.20 Mb，而它被赋给 chr1:173.15 Mb 的 `rs4916312` locus。如果目标是 cis-pQTL，这不是同一个区域。该蛋白本轮 `p_beta=0.52283` 且无 source CS，因此没有进入稠密分析，也不影响最终判定；问题保留在审计记录中，禁止以后把它当作该 locus 的 cis 候选。

## 独立复核

新增 `14_build_r6a3a1_independent_qa.py`，不读取机器终裁结论，而是重新：

1. 对 10 个公共输入文件逐个重算 SHA-256 与字节数；
2. 重建 source-CS component 映射；
3. 重新执行 H4 三门判定；
4. 重算 13/6 donor 的 ZMIZ1 均值差；
5. 确认 3 个合法 source components 全部 FAIL。

结果为 `PASS_INDEPENDENT_REPRODUCTION`。
