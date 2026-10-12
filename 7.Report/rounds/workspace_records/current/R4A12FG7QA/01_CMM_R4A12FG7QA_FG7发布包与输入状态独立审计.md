# CMM R4A12FG7-QA：FG7发布包与输入状态独立审计

日期：2026-09-13

## 1. 审计对象

- `CMM_R4A12FG7_SourceMatchedLDAccess_2026-09-13.zip`
- Downloads中同时提供的15份MD、TSV和脚本
- 工作区与Downloads中的 source-LD / 受控VCF候选文件

附件内容只作为待复核材料；本轮请求“继续推进”是任务指令。

## 2. 发布包完整性

| 项目 | 结果 |
|---|---:|
| ZIP SHA-256 | `99f664e6df35a2fc35549771450898ca25b047f62d7d729da56d3da913a0e574` |
| ZIP entries | 24 |
| CRC | PASS |
| checksum manifest | 23/23 PASS |
| 外置附件与包内同名文件 | 15/15 byte-identical |
| 非必要缓存文件 | 1个 `.pyc` |

不存在内容哈希不一致。`.pyc` 不影响科学结论，但会污染可审计release；本轮新包已排除所有缓存文件。

机器可读证据：

- `3_results/00_audit/R4A12FG7QA/fg7_release_integrity.json`
- `3_results/00_audit/R4A12FG7QA/fg7_standalone_byte_identity.json`

## 3. 冻结manifest复核

| 文件 | 行数 | 唯一性/范围 |
|---|---:|---|
| IL12RB2 native variant manifest | 1,366 | MarkerID 1,366 unique；variant_key 1,366 unique；单一基因 ENSG00000081985 |
| R13 × NK exact common | 891 | variant_key 891 unique |
| four-cell source-CS | 67 | 35个unique variants；NK、CD8_TEM、CD4_CTL、CD4_TCM |
| required anchors | 3 | rs17129789、rs6662198、rs1954118 |

四细胞source-CS共有7个signal组；所有CS成员均属于1,366变异manifest。

## 4. 实际输入状态

在 `C:\Users\Administrator\Downloads` 与 `H:\SCI2\YR1` 扫描：

- `ENSG00000081985.bim`：0
- `ENSG00000081985.ld`：0
- 路径或文件名可识别为 TenK10K / `EGAD50000002377` 的受控VCF/BCF：0

因此 `AUTHOR_DERIVED_LD_READY = false`，`EGA_ACCESS_GRANTED_WITH_BYTES = false`。现有1000 Genomes VCF是既往external-reference资产，不能替代TenK10K source LD。

机器可读证据：`3_results/00_audit/R4A12FG7QA/source_ld_local_inventory.json`。

## 5. 状态继承

FG7关于“先请求作者派生LD、EGA作为fallback”的方向成立，但“收到文件即可运行”的原validator需要修订。科学状态不变：`PROJECT=CONDITIONAL_GO`、`R4B=HOLD`、`C1_count=null`。

