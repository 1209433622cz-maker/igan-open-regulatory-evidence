# CMM R4A11 release

本包完成 R4A10 独立复核、H6 v2.1 修复、2026 SSc female/male 公开接入刷新，以及唯一 Master Analysis Manifest v11 的冻结。

## 先读

1. `00_CMM_R4A11_执行摘要_正式接入复核与H6v2.1纠错.md`
2. `99_CMM_R4A11_详细行动记录_2026-09-12.md`
3. `04_CMM_R4A11_MasterProtocol与R4A12目标.md`
4. `h6_v2_1/README_H6_V2_1.md`

## 当前状态

- Project：`CONDITIONAL_GO`
- R4B：`HOLD`
- female/male bytes：`NOT_OBTAINED`
- disease layer：`NOT_TESTED`
- C1_count：`null`
- next：`R4A12_BYTE_ARRIVAL_TRIGGERED_HARMONIZATION_AND_COVERAGE_GATE`

## 目录

- `audit/`：R4A10 package/code hostile audit，以及 H6 v2.1 首轮/终局 QA；
- `h6_v2_1/`：真实文件接入脚本、双性别 metadata 模板和测试；
- `access/`：公开入口复跑、raw/decision/validation 与作者请求草稿；
- `protocol/`：20 基因候选表、v11 JSON/Markdown 母协议和 70-check validator；
- `results/`：最终机器状态和发布文件清单；完整 ZIP validation 与 sidecar 位于发布包旁；
- `scripts/`：状态构建、发布打包和发布验证脚本。

## 一键本地验证

```powershell
powershell -ExecutionPolicy Bypass -File .\h6_v2_1\RUN_TESTS.ps1
python .\protocol\validate_analysis_manifest_v11.py
python .\access\verify_access_results.py
python .\scripts\validate_release.py --directory .
```

预期：H6 73/73、hostile 28 cases/0 false PASS、manifest 70/70、access 19/19、release PASS。

## 数据到达

不要改动 provider 原文件或 checksum sidecar。按 `h6_v2_1/README_H6_V2_1.md` 填 female/male metadata 并运行 H6；只有 exit 0 和 exact PASS 才进入 R4A12。作者请求草稿位于 `access/author_data_request_v11.md`，状态是 DRAFT/NOT SENT。

本包没有 Office/PDF 产物，无需渲染。后续若创建 Office 文档，使用 WPS 后台渲染。
