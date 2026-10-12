# R4A.1 可复现工作目录

本目录包含本轮实际源文件、浏览器JSON、源元数据、描述性筛查输出和代码。没有SSc共定位结果或可声称C1的后验概率。

## 运行

PowerShell下可使用现有 `D:/bioinfor/python.exe`（网络请求脚本需要requests）。表格离线分析使用本次加载的bundled Python，路径见下。核心审计只用Python标准库。

```powershell
# 下载/网络核查（可改变来源当前快照，非离线复现所必需）
python R4A1/scripts/access_probe.py
python R4A1/scripts/download_tenk10k.py
# 仅在SuSiE整包传输失败时使用已验证的HTTP Range fallback
python R4A1/scripts/download_susie_ranges.py

# 离线重建本轮分析，运行目录H:/SCI2/YR1
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' R4A1/scripts/audit_data.py
python R4A1/scripts/finalize_manifest.py
python R4A1/scripts/test_audit.py
```

`access_probe.py`是初始访问探针，后续纠错查询的确切URL在source_manifest及evidence日志中。重新联网可能得到不同版本；复现本轮结论应使用现有已哈希快照。

## 目录

- `raw/tenk10k/`：两个原始ZIP；分段下载缓存在susie_parts，未混入分析。
- `evidence/`：原始response及HTTP日志；错误响应保留，不能当有效源数据使用。
- `results/`：28细胞gene/CS筛查、精确lead源记录、暂定cell mapping、输入矩阵质控。
- `source_manifest.tsv`：URL/本地路径/字节/SHA256/用途。
- `R4A1_state.json`：科学状态；C1_count=null代表未测试，并非0个阴性。
- `checksums.sha256`：原始数据、代码、结果及本轮MD报告校验。

## 关键限制

gene-level和CS文件均是逗号分隔，虽然后缀.tsv。未列出与模型失败区别记录。BH为本轮探索性重算。cell mapping仅匹配标签，未核实定义和跨队列donor独立性，因此不能直接用作确认性复制。

本轮未运行参考FASTA/indel左对齐、liftOver、LD重建、coloc.susie、MR或疾病组织分析。脚本测试通过仅代表本轮接入/筛查逻辑，不代表生物学pipeline或C1通过。
