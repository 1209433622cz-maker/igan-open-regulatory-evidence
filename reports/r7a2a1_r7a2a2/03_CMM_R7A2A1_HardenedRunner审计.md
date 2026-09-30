# R7A2A1 Hardened Runner 审计

## 变更范围

transport-hardened runner 相对 2026-09-28 冻结 runner 只改变传输可靠性：

- aria2 默认并发从 16 降到 2；
- 加入最多 50 次进程级重启；
- 第四次尝试起把并发降到 1；
- 保留同一个 `.part` 文件断点续传；
- 在每次重启后重新检查 observed bytes；
- 超过 expected bytes 时 fail closed。

manifest、MD5/SHA、samtools、schema、target-panel、called-cell、B/NK gate、target threshold、comparison statistics 和删除门均未改变。

## 发现并修复的问题

下载目录中的脚本 SHA-256 为 `b966e5ed...`，其中错误信息字符串写成 `$run:`。PowerShell parser 将冒号解释为变量作用域语法，导致整个脚本出现 1 个 parse error。

工作区版本改为 `${run}:`，SHA-256 为 `b0b2335d00ab782715c7ee7d0c82d0b684c78cdae554dfe22403ddf566ca041f`，PowerShell parser 为 0 error。除 UTF-8 BOM 与该插值修复外，两份 hardened 文件一致。

该修复只影响异常分支的字符串语法，不改变任何科学结果。R7A2A1 已有的 summaries、receipts、called-cell tables 与比较输出均已独立重算通过，因此科学 closure 不依赖对执行过程的推测。
