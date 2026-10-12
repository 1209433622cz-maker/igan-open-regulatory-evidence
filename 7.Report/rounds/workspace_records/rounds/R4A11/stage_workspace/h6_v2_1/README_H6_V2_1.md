# H6 v2.1：2026 SSc 性别分层 GWAS 接入门

H6 v2.1 只负责确认收到的文件是否可以进入 normalization、harmonization 和正式 coverage audit。它不会运行 fine-mapping、coloc 或计算 C1，也不会把 `CONDITIONAL` 当成功。

## 1. 运行环境

- Python 3.11 或更高版本；H6 本体只使用标准库。
- 可选公开入口刷新脚本需要 `requests`：

```powershell
python -m pip install -r H:\SCI2\YR1\R4A11\h6_v2_1\requirements.txt
```

本包没有 Word、Excel、PowerPoint 或 PDF 产物，因此不需要 Office 渲染。后续如生成 Office 文档，按用户要求只使用 WPS 后台渲染。

## 2. 输入冻结

原始下载文件应保持不改名、不解压、不编辑，并同时保存提供方的 checksum sidecar、manifest 或作者随传记录。程序支持 plain、`.gz/.bgz`、`.bz2`、`.xz/.lzma`，会流式扫描大文件。

分别复制并填写：

- `metadata_female_template_v2_1.json`
- `metadata_male_template_v2_1.json`

只从提供方材料填写 `assembly`、`ancestry`、case/control、effect/SE 量纲、样本量语义、URL、accession 和 checksum。文件名或论文图不能作为这些字段的来源。

### Checksum 证据

`expected_sha256` 或 `expected_md5` 必须来自下载前已经存在的提供方/仓库 manifest。另需填写：

- `expected_checksum_source`：manifest 的网页/FTP 地址，或 `author-manifest:<记录标识>`；
- `expected_checksum_evidence_type`：`provider_manifest`、`repository_manifest` 或 `author_manifest`；
- `expected_checksum_evidence_file`：保存到本地的原始 sidecar/manifest；
- `expected_checksum_evidence_sha256`：该证据文件本身的 SHA-256。

下载后才对同一数据文件现算的 hash 只能作为 `receipt_sha256`，不能充当 expected checksum。代码会验证证据文件没有与输入文件重合、证据文件 hash 匹配、且证据正文包含 expected digest；提供方身份仍需人工核对。

## 3. 一键运行

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\R4A11\h6_v2_1\RUN_H6_V2_1.ps1 `
  -InputFile "H:\SCI2\YR1\incoming\female.tsv.gz" `
  -MetadataFile "H:\SCI2\YR1\incoming\female.metadata.json" `
  -Label female `
  -OutputDir "H:\SCI2\YR1\R4A12\intake\female"
```

male 文件把两个 `female` 改成 `male`。不要让输入文件、metadata、checksum evidence 与输出文件同名；程序会在任何写入前拒绝路径冲突。

## 4. 状态与退出码

| exit | JSON status | 含义 |
|---:|---|---|
| 0 | `PASS_FROZEN_REGIONS_INTAKE_READY_FOR_HARMONIZATION` | 仅授权进入下一技术门 |
| 3 | `CONDITIONAL_*` | 信息、support、anchor、区域密度或样本设计不完整；下游停止 |
| 4 | `DIAGNOSTIC_ONLY_*` | `--max-rows` 诊断，不形成接入判定 |
| 2 | `HOLD_*` | schema、build、来源、结构或冻结区域核心字段失败 |
| 1/其他 | 未预期异常 | 检查 stderr；不运行下游 |

runner 同时检查退出码与 JSON exact status。只有 exit 0 且 exact PASS 才允许继续。

## 5. 已实现的关键门

- 目标研究必须锁定 PMID `41999721` 或 DOI `10.1016/S2665-9913(25)00376-5`，phenotype 为 SSc，analysis 为 sex-stratified GWAS；`overall` 被拒绝。
- `--label` 只允许 `female|male`，并与 metadata stratum 一致。
- public-catalog 分支要求 `ebi.ac.uk` 来源与 `GCST` 数字 accession；作者直传走独立 `author_transfer` 证据链。
- 全文件拒绝 malformed 行、缺失/非法 chromosome/position、超出 GRCh38 染色体长度的坐标、UTF-8 replacement 和控制字符。
- 冻结区域的 effect、SE、P、alleles 必须完整、有限且合法；EAF/INFO 不完整降为 `CONDITIONAL`。
- 对 beta/SE/P 或 log(OR)/SE/P 做宽容度为 2 个数量级的 gross coherence sentinel；该检查用于发现列错配，不替代提供方模型说明。
- exact anchors 必须同时满足 rsID、GRCh38 坐标和 allele set，且全文件不能有同 rsID 冲突记录：`rs12203592=chr6:396321 C/T`、`rs66578187=chr22:39328807 A/AT`。
- 每个冻结区域至少 100 行、100 个唯一位置且跨度至少 250 kb，作为明显截断/稀疏输入的 sanity sentinel；它不是正式 reference coverage 结果。
- bare `N` 必须明确声明为 `sample_size`、`cohort_count` 或 `ignore`。cohort count 需正整数、不超过 `total_cohort_count`；sample count、case/control/total 必须自洽。

## 6. 验证

```powershell
powershell -ExecutionPolicy Bypass -File H:\SCI2\YR1\R4A11\h6_v2_1\RUN_TESTS.ps1
```

冻结回归与 hostile suite 包含有效基线、四种文件格式、非数值/非有限/越界字段、错误研究与分层、来源空壳、checksum 证据、裸 N、错误/冲突 anchor、稀疏区域、效应统计矛盾、非法染色体、控制字符、路径穿越和输入覆盖保护。

## 7. 结果边界

H6 PASS 后仍需依次完成 GRCh38 FASTA normalization、allele orientation、共同变异 coverage、ancestry-matched signed LD、RSS diagnostics、D0 正控、fine-mapping 和 signal-level coloc。任一门失败时，疾病层仍为 `NOT_TESTED` 或 `UNINFORMATIVE`，不能写作阴性或 C1=0。
