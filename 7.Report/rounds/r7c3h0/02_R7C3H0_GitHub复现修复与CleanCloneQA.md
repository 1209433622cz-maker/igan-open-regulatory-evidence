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
02_evidence_audit.py = PASS_37_OF_37
working tree after replay = CLEAN
```

GitHub Actions 只声明“聚合端点与文档身份重放”。原始 GWAS、BAM、PLINK、donor matrices、完整 LD 和 486,000 次模拟不会在 CI 中重跑，避免夸大可复现层级。

## 待最终写入字段

本文件随最终 Git 提交补写 commit、remote HEAD、tag 和 release URL。若远端 CI 未完成，不将本机 PASS 写成远端 CI PASS。

