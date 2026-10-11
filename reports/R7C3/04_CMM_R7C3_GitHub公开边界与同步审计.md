# R7C3 GitHub 公开边界与同步审计

## 推送前状态

审计开始时，公共仓库 `main` 与 `origin/main` 均为 `da89eb81b33ed912eba404e00ae8d3037b450920`，worktree clean，`git fsck --full --no-dangling` 无错误。1,335 个 tracked files 中没有超过 10 MiB 的文件，未发现 GitHub token、Zenodo token、AWS key 或 private key 模式。

旧 `MANIFEST.sha256` 的 1,410 个条目全部能通过现存文件哈希，但其中 75 个条目不是当前 Git 跟踪文件：主要是 `__pycache__/*.pyc` 和三个本地 supplement ZIP。该问题不会改变科研结果，却使 manifest 的含义不够精确。本轮同步将重建为：

> 对除 `MANIFEST.sha256` 自身外的全部 Git tracked files 逐一列出 SHA-256，不纳入 ignored/untracked local artifacts。

## 允许公开

- 原创 Python/R/PowerShell 代码与冻结协议；
- 聚合/派生的比较级、posterior、simulation 和 QA 表；
- 稿件、投稿信、图、补充表与作者已批准的 source-data package；
- 相对路径资产总账、阶段记录索引和 audit summary；
- MIT code license、CC BY 4.0 content license、CITATION.cff 和 Zenodo metadata。

## 禁止公开或仅记录 receipt

- OneK1K genotype、pseudobulk、raw cis-eQTL；
- 第三方 GWAS 全量字节、GJOKA LD matrix、TenK10K source archive；
- HRA donor-level BAM/cell-level matrices；
- 用户配置目录、完整 absolute-path inventory、credential、token、私密审批凭据；审计脚本保留非个人化的工作区根路径 `H:\\SCI2\\YR1` 作为可修改默认值；
- QiTeng skill 与 `tools` 运行时；
- 无必要的版本快照、缓存和 interrupted-download fragments。

## Zenodo 状态

仓库包含 `.zenodo.json`、`CITATION.cff` 与 fail-closed 发布脚本，但本地没有可用 Zenodo authenticated credential。因此当前不能真实生成 Zenodo record 或 DOI，GitHub release/tag 和 SHA-256 仍是可引用公开身份。不得写成 DOI 已生成。

## 同步策略

本轮只向 GitHub 增加去绝对路径的审计摘要、工作记录索引、价值资产总账、阶段时间线、投稿包说明与 R7C3 详细记录。完整 50,630 文件 inventory 留在本地；第三方和大文件仅在公开 ledger 中记录 source role、大小或 checksum receipt。

最终 commit、tag、release URL 和 release asset digest 由本轮结束时生成的 `R7C3_github_release_receipt.json` 记录。
