# CMM R4A2：YR1包完整性与复现审计

**审计对象：`YR1.zip`**  
**日期：2026-09-08**

## 1. 结论

科学结果包总体**可审计、可复现到R4A1所声称的描述性筛查层级**，但存在一个明确的交付层缺陷和一个可优化的体积问题。

### 1.1 根目录报告缺失1份

`R4A1/checksums.sha256`声明共有8份根目录Markdown报告，但实际ZIP中只有7份内容可匹配：

- 哈希匹配：7/8
- 缺失：`01_CMM_R4A1_历史文件逐项审计与项目逻辑重构.md`

其余7份报告的**内容SHA256与manifest完全一致**，只是归档传输后中文文件名被转成`#Uxxxx`形式。因此这是**文件打包遗漏**，不是内容篡改或科学结果不一致。本轮不伪造缺失的原始01报告，只在R4A2中建立新的完整包审计报告取代其交付职责。

## 2. 内部哈希与脚本测试

- `checksums.sha256`中R4A1内部文件：**83/83 项当前字节哈希PASS**。
- YR1自带单元测试：**6/6 PASS**。
- 测试覆盖：BH排序、missing≠0、IRF4原始CS独立性、rsID回归、PIP不被错误提升为coloc、非阈值区域endpoint防止选择性输入。

这些PASS只证明**接入/筛查代码行为符合当前协议**；它们不意味着SSc共定位、C1 regulatory cascade或生物学pipeline已经通过。

## 3. 归档结构审计

### 做得好的部分

1. 原始TenK10K主ZIP与SuSiE ZIP均进入source/checksum体系；
2. 错误HTTP response被保留，而不是静默覆盖；
3. `R4A1_state.json`把`C1_count=null`与“0个C1”区分；
4. source_manifest、results、scripts、evidence层级清晰；
5. README明确指出本轮没有运行liftOver、LD重建、coloc.susie、MR或疾病组织分析。

### 需要修复的部分

1. **缺失01报告**：README/checksum与实际ZIP不一致；
2. **文件名编码**：中文Markdown名转义为`#Uxxxx`，降低Windows/人工审阅体验；
3. **下载缓存膨胀**：
   - `susie_summary.zip`：59,669,579 bytes
   - `susie_parts/`：59,669,579 bytes
   - `susie_summary.zip.part`：33,554,432 bytes
   
   `susie_parts/`基本重构了完整SuSiE ZIP，同时又保留32 MiB未完成`.part`。这些缓存对于科学复现没有新增价值，不应进入最终handoff主包。

## 4. R4A3建议的release结构

```text
R4A3/
  README.md
  state.json
  source_manifest.tsv
  checksums.sha256
  raw/
    gwas/
    finngen/
    tenk10k/          # 只保留最终已验证archive
  derived/
  results/
  scripts/
  tests/
  evidence/
_download_cache/      # 不进入release或单独打包
reports/
```

原则：**source bytes、derived tables、human-facing reports、transfer cache必须分层。**

## 5. 本轮机器可读审计文件

见 `R4A2_package_audit.tsv`。其中对checksum manifest中的每一项标记PASS / MISSING / HASH_MISMATCH，并单独记录根目录报告的content-hash映射。

## 6. 判定

> **PACKAGE_SCIENCE_CONTENT_PASS_WITH_DELIVERY_DEFECT**

不需要因为缺失01报告重跑R4A1科学筛查；需要在R4A3交付时修复manifest与归档结构。
