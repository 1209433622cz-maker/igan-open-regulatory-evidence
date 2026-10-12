# R7C3H0 GitHub 复现修复与 Clean Clone QA

## 修复对象

R7C3G 公共仓库的科学内容与八目录结构是完整的，但两个当前入口脚本仍引用本机绝对路径和重构前的 `results`、`protocols` 根目录：

- `2_code/11_manuscript/R7C3G/01_inspect.py`
- `2_code/11_manuscript/R7C3G/02_evidence_audit.py`

这会让 GitHub 下载者无法在独立目录运行聚合复现。

## 已实施修复

1. 新增 `repo_layout.py`，从脚本位置解析仓库根目录；
2. 当前稿件固定为 `5_manuscript/current/R7C3H`，历史 R7C3G 保留；
3. 结果与协议入口分别改为 `3_results` 和 `0_admin/protocols`；
4. 运行输出默认写入仓库外的临时目录，也可用 `R7_RUNTIME_OUT` 指定；
5. 删除对未发布本机审计文件的依赖；
6. 添加 `requirements-portable-qa.txt`，明确 python-docx、PyMuPDF、Pillow、pandas 和 numpy；
7. 添加 `.github/workflows/portable-reproducibility.yml`。

## 本机便携重放

```text
current manuscript assets read = PASS
submission PNG figures read = 9
portable result/protocol objects inventoried = 760
Source Data archive CRC = PASS
scientific endpoint replay = 38/38 PASS
```

重放端点包括 6,923/5,460/642 身份、92/428/59/63 状态、8 个 H4→H3、10 个 H3→H4、486,000 次模拟聚合端点、PF10/PF50 491/4/25、肝组织 exact permutation 以及外部 IL12RB2 证据。

## Clean clone 门

最终提交在本地临时 clean clone 中重新运行：

```text
compileall = PASS
01_inspect.py = PASS
02_evidence_audit.py = PASS_38_OF_38
working tree after replay = CLEAN
```

GitHub Actions 只声明“聚合端点与文档身份重放”。原始 GWAS、BAM、PLINK、donor matrices、完整 LD 和 486,000 次模拟不会在 CI 中重跑，避免夸大可复现层级。

## 远端终裁

```text
scientific content commit = f40207890c225d3922d3bb60b282719682d570eb
tree = 97f072365c708439a0069ad65384c189e4a7f0d4
manifest = 2652/2652 PASS
portable replay = 38/38 PASS
working tree after replay = CLEAN
release-receipt commit = a64b4fb8b8a82eff023e4a242e0244d8715bc927
GitHub Actions content commit = SUCCESS
GitHub Actions receipt commit = SUCCESS
release tag = r7c3h0-statistical-reproducibility-closure-2026-10-13
release ZIP identity = EXTERNAL_SHA256_AND_GITHUB_RECEIPT
```

- Content Actions：<https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/actions/runs/38283799570>
- Receipt Actions：<https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/actions/runs/38284424100>
- Release：<https://github.com/1209433622cz-maker/igan-open-regulatory-evidence/releases/tag/r7c3h0-statistical-reproducibility-closure-2026-10-13>

Git Smart HTTP 曾短暂无法连接 `github.com:443`；对象上传改用 GitHub Git Database API。远端 tree SHA 与本地 HEAD tree SHA 完全一致，随后从远端独立浅克隆并复跑，因此传输替代没有改变仓库内容。

