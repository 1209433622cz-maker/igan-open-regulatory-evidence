# R7C3 执行摘要：全量资产审计、GitHub 同步与投稿终裁

## 最终判定

本轮对 `H:\SCI2\YR1` 做了文件级、内容类型级、哈希级、压缩流级、历史记录级和公开边界级全量核查。PBC 主论文继续 `GO`，没有发现需要重跑 642 项多信号分析、486,000 次模拟、外部验证或肝组织分析的文件损坏和科学缺陷。

```text
R7C3_FULL_WORKSPACE_AUDIT = PASS
RESEARCH_NON_GIT_SHA256 = 49,565 / 49,565
RESEARCH_ZIP_GZIP_INTEGRITY = 4,333 / 4,333 PASS
PRIMARY_EVIDENCE_BLOCKER = 0

PBC_PRIMARY_PROJECT = GO
SCIENTIFIC_ANALYSIS = FROZEN
NPJ_SUBMISSION_PACKAGE = READY
HUMAN_GENOMICS_FALLBACK = PRESERVED
ZENODO_DOI = NOT_YET_MINTED

NEXT = R7C4_AUTHOR_OPERATED_NPJ_SUBMISSION_AND_RECEIPT
```

## 工作区实况

- 盘点基线包含 50,630 个文件，总量 45,879,434,246 bytes（42.73 GiB）。
- `1_data` 为 31.05 GiB，`3_results` 为 4.45 GiB，`9.Version` 为 3.79 GiB；三者构成绝大多数科研资产。
- 49,565 个非 Git 内部研究文件均有 SHA-256；另有 1,065 个 `.git` 内部对象按策略不进入科研文件哈希总账。
- 122 个 ZIP 与 4,211 个 GZIP 均通过完整 CRC/流解压，实际展开检查 173,974,898,239 bytes。
- 293 条内容解析异常全部来自 QiTeng skill 的超长历史归档路径；科研数据、结果、报告、稿件和发布包的解析异常为 0。
- 发现 11,375 个精确重复组，理论重复占用约 6.13 GiB。release、version、GitHub 与 canonical working copy 的重复具有 provenance/rollback 价值，本轮没有删除、硬链接或移动任何文件。
- 发现 22 个 `.part`/`.redownload` 文件，共 426,460,399 bytes；它们属于历史下载片段、缓存或有完整同哈希终版的副本，均未被当前 PBC 论文作为主证据。

## 科学成果终裁

本项目最有价值的成果已经从“两个候选基因”升级为可审计的调控归因可靠性研究：

1. 在 6,923 个 PBC locus–gene–cell 比较中，5,460 个达到 ABF 可分析覆盖，642 个高信息比较进入来源匹配的多信号分析。
2. PF10 主模型下 92/642 为 stable H4，428/642 为 stable H3；结果保留了支持、反转、歧义、模型敏感和无信息状态。
3. 同输入 A0/A1/A2/M 审计显示，支持集合和疾病统计定义分别引起 15 和 19 个分类变化；在匹配输入后，多信号层仍出现 8 个 H4→H3 与 10 个 H3→H4。
4. 486,000 次模拟显示明确权衡：distinct-signal 情景的 false H4 从 12.41% 降至 8.56%，shared-signal recovery 同时从 32.99% 降至 26.66%。这支持“提高归因可靠性需要报告代价”，不支持“多信号模型普遍优越”。
5. IL12RB2–NK 在 FinnGen R13 × OneK1K 中获得稳定单信号共享支持（默认 PP.H4=0.9977），并形成 disease–eQTL、disease–caQTL 与 peak–gene 三角一致性；由于没有直接 eQTL–caQTL posterior 和 mediation estimate，仍不能称为染色质介导机制。
6. FCRL3 保留 B-cell 跨分子 QTL 资源支持，同时 CD8_ET 反例证明结果可能随模型与因果结构改变。5 vs 5 肝组织仅支持 lineage detectability，未支持 PBC-specific enrichment。

## 投稿判断

当前稿件已达到可投稿状态。最匹配的 SCI 一区尝试仍是 `npj Genomic Medicine / Article`，但只允许一次有边界的尝试；证据不支持通用算法、功能机制、临床工具或疗效预测表述。作者已确认原创性、一稿专投、作者顺序、利益冲突、funding、伦理边界与 AI 使用披露。稿件、投稿信和补充材料沿用 R7C2 的精确字节，WPS 已检查 34 页且无裁切、重叠或缺图。

如 npj 在编辑阶段拒稿，直接切换已冻结的 Human Genomics 投稿包；不得以新增位点、基因、细胞或无边界分析“救稿”。

## 本轮核心交付

- 全量本地文件清单、大小、SHA-256、重复组、片段与压缩完整性结果；
- 85 份唯一行动记录的 canonical ledger，覆盖 73 个可解析阶段 token；
- 26 类高价值科学、方法、治理和投稿资产总账；
- npj 最小投稿包与上传顺序、哈希清单和 WPS 复核凭据；
- 适合公开的去绝对路径审计摘要与 GitHub 同步内容；
- 详细行动记录与 R7C4 冻结目标。
