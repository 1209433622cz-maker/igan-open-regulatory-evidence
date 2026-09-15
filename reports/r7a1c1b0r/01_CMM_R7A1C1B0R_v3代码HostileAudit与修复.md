# R7A1C1B0 v3 代码 Hostile Audit 与修复

## 输入完整性

- SHA-256：`1f83ea190bd053a457a50e652c45ebdec3d4dde316a67190ffdf5b6b219f64b0`
- ZIP CRC：PASS
- internal checksum：17/17 PASS

完整性通过不代表代码可执行；本轮继续做运行路径审计。

## 缺陷一：最终 adjudicator 三路径赋值

原 v3 结尾把 `03_adjudicate...py`、`07_validate...py` 和 `08_check...py` 以逗号连接后交给单个 `Convert-ToWslPath([string])`。PowerShell parser 可通过，但五个供者完成后无法形成唯一可执行脚本路径。v3.1 恢复为单一 adjudicator 路径。

## 缺陷二：固定前 500k coordinate-sorted 记录会假失败

在真实 HRR1849459 前 64 MiB 上按原默认读取 500,000 records，仅观察到 15 个 `xf bit 8`，低于 `min-xf8=1000`。继续扫描至 649,995 records 即达到 1,000 个；这些 records 的 CB、GN、UB 和 unambiguous GN 比例均为 1.0。

v3.1 改为：至少 500k；若 molecule representatives 不足则继续；达到 1,000 后停止；最大 5M。这样保留 fail-closed 上限，也适应 coordinate sorting。

## 缺陷三：resume receipt 不充分

原 v3 发现有效 schema summary 后，即使没有历史 receipt 也会在内存中伪造 `RECORDED_IN_PRIOR_VALIDATED_RUN` 并跳过；而该 receipt 没有立即落盘。v3.1 要求：

- summary run/schema/technical QC/bytes/SHA 全部匹配；
- 恰好一个历史 receipt；
- receipt status、bytes、official MD5、observed MD5、SHA 与 summary 全部匹配。

不满足即停止，不能静默复用。

## 缺陷四：轻量下载端点返回 HTML

原 PMC `articles/instance/.../bin/...xlsx` URL 返回 HTTP 200 `text/html`。v2 轻量 runner 已改用 Springer 官方二进制 URL，并冻结 exact bytes、SHA-256 和 XLSX ZIP signature。

## 验收

- Python compile：PASS；
- PowerShell parser：PASS；
- v3.1 `-PreflightOnly` 真实运行：PASS；
- manifest exact five runs / total bytes：PASS；
- HRR1849459 真实 BAM 前缀 adaptive schema：PASS；
- 独立 QA：16/16 PASS。
