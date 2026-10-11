# CMM R4A12FG2：大文件下载与本地运行说明

执行窗口：2026-09-12—2026-09-13（Asia/Hong_Kong）

以下命令均在 PowerShell 中运行。下载器默认 dry-run，不会因误执行说明文件而开始 1.48 GiB 下载。

## 1. 查看主对象清单

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\2_code\06_intake\finngen_r12_r13\RUN_DOWNLOAD.ps1 -Selection primary
```

预期：4 个对象、1,587,342,434 bytes。

## 2. 正式下载 R13/R12 主 endpoint

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\2_code\06_intake\finngen_r12_r13\RUN_DOWNLOAD.ps1 -Selection primary -Execute
```

机制：

- 使用 `.part`；中断后重复同一命令续传；
- 下载前检查剩余空间 ≥计划 bytes×1.10；
- 完成后核对 content length；
- 核对 GCS provider MD5；
- 计算 local SHA-256；
- 全部通过后才把 `.part` 原子改名为正式文件；
- receipt 写入 `3_results\00_audit\R4A12FG2\R4A12FG2_full_download_receipt.json`。

不要使用 `-Selection all`，除非确实需要 strict/CREST sensitivity；该选择约 4.72 GB。

## 3. 从完整对象重新提取 IL12RB2 region

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\2_code\06_intake\finngen_r12_r13\RUN_EXTRACT_IL12RB2.ps1 -Release R13
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\2_code\06_intake\finngen_r12_r13\RUN_EXTRACT_IL12RB2.ps1 -Release R12
```

脚本使用 WSL Ubuntu-22.04 的本地 `tabix`，随后自动运行 P0-FG。完整对象重提取的结果应与本轮 remote Tabix 文件做 SHA/row/key 对比。

## 4. 重新运行 TenK10K IL12RB2 审计

```powershell
D:\bioinfor\python.exe H:\SCI2\YR1\2_code\06_intake\tenk10k_il12rb2\extract_and_audit_il12rb2.py --workspace H:\SCI2\YR1
```

## 5. 运行工程回归测试

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\2_code\06_intake\finngen_r12_r13\RUN_TESTS.ps1
node --check H:\SCI2\YR1\2_code\06_intake\finngen_fg2_remote\query_finngen_region.mjs
```

## 6. R12 sex-specific exclusion list

只有收到 FinnGen access email 且该 Google account 获得 Green Library 权限后运行：

```powershell
gcloud auth login
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\2_code\06_intake\finngen_r12_r13\RUN_R12_SEX_DROP_LIST.ps1 -Execute
```

脚本会精确判断 `M13_SYSTSLCE` 是否在 262-endpoint drop list。没有这个真实文件前，不要按病例数推断 sex-specific endpoint 可用。

## 7. 环境说明

- Python 3.13.7
- Node.js 24.19.0
- `@gmod/tabix` 3.8.2，`pnpm-lock.yaml` 已锁定
- Google Cloud SDK 573.0.0
- WSL Ubuntu-22.04：本地 tabix 可用

Windows Python 3.12/3.13 当前没有可直接安装的 `pysam 0.23.3` wheel，两次失败环境已移入 `9.Version\quarantine\dependency_attempts`。因此 remote range query 使用锁定 Node 实现；不需要重复安装失败的 pysam 环境。

本轮只生成 MD/JSON/TSV/ZIP，不含 Office 文件，因此 WPS 渲染不适用；后续若生成 DOCX/PPTX，将按用户要求使用 WPS 后台渲染。


