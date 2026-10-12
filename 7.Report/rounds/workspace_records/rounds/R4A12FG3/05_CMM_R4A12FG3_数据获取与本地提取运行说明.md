# CMM R4A12FG3：TenK10K 100-kb 数据获取与本地提取说明

日期：2026-09-13。基于用户提供的 R4A12FG2 真实区域结果，并结合本轮公开数据源复核。外部信息均与附件证据分层记录。

## 下载策略

只下载：

`common_all_cis_pvalues_100kb.zip` — 16.6 GB

不要在当前阶段下载七个±1Mb包（约129.8 GB）。

PowerShell dry-run：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\DOWNLOAD_TENK10K_100KB.ps1
```

实际下载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\DOWNLOAD_TENK10K_100KB.ps1 -Execute
```

脚本支持curl续传并强制MD5校验。

## NK-first流式提取

```powershell
D:\bioinfor\python.exe .\scripts\extract_il12rb2_from_tenk10k_100kb.py `
  --zip H:\SCI2\YR1\1_data\qtl\eqtl\tenk10k\raw\common_all_cis_pvalues_100kb.zip `
  --outdir H:\SCI2\YR1\1_data\qtl\eqtl\tenk10k\derived\IL12RB2_full `
  --cells NK
```

验收NK后再运行默认11个CS-positive cell types。脚本通过ZIP流读取，不把每个2–3 GB成员全部解压到磁盘。

## 预计资源

- 下载磁盘：至少20 GB空闲空间；建议25–30 GB；
- 不整包解压，可避免约60–75 GB额外展开空间；
- 运行时间主要由Zenodo下载和压缩成员顺序扫描决定；
- 若只做NK，应先只扫描一个约2.3 GB uncompressed member。

## 不应做的事情

- 不用`common_all_cis_pvalues_1Mb`救阴性；
- 不从SuSiE PIP反推beta/SE；
- 不把SAIGE文档字段名当作真实下载文件schema而跳过header验收；
- 不把外部LD“能计算”当作“匹配良好”。
