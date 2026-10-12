# CMM R5A2A：R5A2A1 下一阶段冻结目标

下一阶段：`R5A2A1_MG_CHR18_INPUT_CLOSURE`

## 必做任务

1. 下载 OneK1K `OneK1K_TensorQTL_raw_eQTL_summary.tar.gz`：10,344,009,571 bytes，MD5 `e42239480f40abd21f221c0d77c82cc3`；
2. 先验收 byte、MD5、archive member inventory 和 schema，再编写实际字段驱动的区域提取器；
3. 仅提取 rs7239261 主区域和真实出现的 cell–gene pairs；
4. 将 OneK1K GRCh37 genotype、OneK1K eQTL 与三套 GRCh38 MG GWAS做可追溯 build/allele harmonization；
5. 对实际共享变异生成 980-donor source-aware LD；
6. 运行 disease–eQTL 信号检测、coloc/多信号分析以及 prior、窗口、覆盖敏感性分析；
7. 只有 OneK1K 结果为 `GO_TENK10K_REPLICATION` 或 `HOLD_TESTABLE`，才下载 TenK10K 16.56 GB 全量区域 eQTL。

## 本地运行方式

在 PowerShell 中运行：

```powershell
Set-Location 'H:\SCI2\YR1'
& '.\2_code\06_intake\mg_r5a2a\RUN_R5A2A1_CHR18_INPUT_CLOSURE.ps1' -Mode OneKPrimary -Concurrency 2
```

脚本使用 Python 标准库下载器，可断点续传，不需要新增 Python 包。若网络稳定可把 `-Concurrency` 提高到 4；再次运行同一命令会复用已完成分片。

`-Mode FullReplication` 会继续下载 TenK10K 16.56 GB 文件，但当前不建议提前执行，因为顺序门控要求先看到 OneK1K chr18 信号。

## 阶段出口

- `GO_TENK10K_REPLICATION`：充分覆盖且 chr18 存在稳定信号级共享证据；
- `HOLD_TESTABLE`：缺口可以由预注册补充步骤解决；
- `FAIL_CHR18_PRIMARY`：充分覆盖下无共享信号，按冻结顺序转 chr5；
- chr18 与 chr5 都失败后，重新判断 MG 主论文，不用 chr2/chr8 无限救援。

完整统计和 claim 边界见 `0_admin/protocol/current/R5A2A1_MG_chr18_input_closure_protocol.md`。
