# R7A1B0 GitHub 发布状态

日期：2026-09-15

仓库：`1209433622cz-maker/igan-open-regulatory-evidence`

本轮通过 GitHub connector 独立读取并确认 R7A1A 公共发布 commit：

`ccd8b93f56a38f640a76801249b178dc1a7d8c74`

其 commit message 为 `Record R7A1A public release provenance`。

R7A1B0 当前首先作为执行/协议加固包交付，不包含第三方 OneK genotype、raw cis-eQTL、PBC GWAS 或 GJOKA LD 大字节。

包内提供 `code/SYNC_R7A1B0_TO_GITHUB.ps1`，仅同步代码、协议、报告和小型结果；要求 local main 与 origin/main 完全一致，拒绝 >10MB 文件，并在 push 后核对远端 HEAD。

如果当前 ChatGPT GitHub integration 对写入返回 403，则远端写入状态必须记为 `PENDING_LOCAL_SYNC`，不得声称已发布。

## 本轮实际写入测试

通过当前 GitHub connector 尝试新建：

`results/r7a1b0/R7A1B0_state.json`

GitHub 返回：

`403 Resource not accessible by integration`

因此本轮没有声称 R7A1B0 已远端发布；必须使用包内 `SYNC_R7A1B0_TO_GITHUB.ps1` 或其它已有本机授权完成同步。
